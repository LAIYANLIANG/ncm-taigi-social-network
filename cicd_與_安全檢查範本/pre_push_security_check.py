#!/usr/bin/env python3
"""Pre-push security, PII, copyright, and local-leak audit for the Taigi NCM project.

Checks 7 security & compliance rules ([SEC-01] .. [SEC-07]) across:
  1. Pushable / Tracked project files inside `期未/`
  2. Ignored files inside `期未/` (verifying risky files stay `.gitignore`d)
  3. Parent workspace directory (advising against initializing git in parent dir)

Works both before `git init` (simulating `.gitignore` rules) and inside an active Git repo.
Zero third-party dependencies required (uses Python standard library only).
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import os
import re
import sqlite3
import subprocess
import sys
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB GitHub friendly limit
TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".json", ".csv", ".yml", ".yaml",
    ".toml", ".sh", ".ini", ".cfg", ".html", ".js", ".ts",
}

# Files that define security patterns or documentation templates and are allowlisted
# from scanning rule-definition literals inside them.
SCANNER_SELF_ALLOWLIST = {
    "cicd_與_安全檢查範本/00_CICD_AI檢查範本.md",
    "cicd_與_安全檢查範本/pre_push_security_check.py",
    "cicd_與_安全檢查範本/ai_pr_reviewer.py",
    "cicd_與_安全檢查範本/01_CICD_與_PrePush_AI安全檢查使用指南.md",
    "cicd_與_安全檢查範本/02_GitHub上傳風險評估與資料去敏清單.md",
    ".gitleaks.toml",
}

FORBIDDEN_SENSITIVE_FILENAMES = {
    ".env", ".ds_store", "cookies.txt", "auth_state.json", "session.json",
    "credentials.json", "secrets.json", "secrets.yaml",
}

# Build regexes cleanly so literal prefixes avoid naive self-hits even if copied.
SECRET_PATTERNS: List[Tuple[str, str, re.Pattern[str]]] = [
    ("SEC-01", "Google/Gemini API Key", re.compile(r"AIza" + r"[0-9A-Za-z\-_]{35}")),
    ("SEC-01", "OpenAI/Anthropic-style Secret Key", re.compile(r"\bsk-" + r"(?:proj-|ant-)?[A-Za-z0-9\-_]{20,}\b")),
    ("SEC-01", "GitHub Personal Access Token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_" + r"[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("SEC-01", "AWS Access Key ID", re.compile(r"\bAKIA" + r"[0-9A-Z]{16}\b")),
    ("SEC-01", "Private Key Block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("SEC-02", "Authenticated Session Cookie Header/Token", re.compile(r"(?:c_user=\d{6,}|xs=[A-Za-z0-9%_-]{12,}|sessionid=[A-Za-z0-9%_-]{12,}|ds_user_id=\d{6,}|Cookie:\s*[^\r\n]*(?:c_user=|xs=|sessionid=|csrftoken=))")),
    ("SEC-03", "Personal Gemini Conversation Share URL", re.compile(r"https://gemini\.google\.com/(?:app|share)/[A-Za-z0-9_-]{8,}")),
    ("SEC-04", "Copyrighted Cambridge Core Watermark", re.compile(r"(?:Downloaded from https://www\.cambridge\.org/core|Cambridge Core terms of use)")),
    ("SEC-05", "Local macOS/Windows Home Directory Path Leak", re.compile(r"(?:/Users/[A-Za-z0-9._-]+/|C:\\Users\\[A-Za-z0-9._-]+\\)")),
    ("SEC-06", "Hardcoded Production Privacy Salt", re.compile(r"""SALT\s*=\s*["'][^"']*privacy_salt["']""")),
]

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TW_PHONE_RE = re.compile(r"\b09\d{2}-?\d{3}-?\d{3}\b")
HEX16_RE = re.compile(r"^[0-9a-f]{16}$")


@dataclass
class Finding:
    severity: str  # BLOCK | IGNORED_OK | ADVISORY
    rule_id: str
    path: str
    detail: str
    remediation: str


def find_project_root(start: Path) -> Path:
    """Resolve `期未/` root directory containing demo/ or cicd_與_安全檢查範本/."""
    for candidate in (start, start.parent, Path.cwd()):
        if (candidate / "demo").exists() and (candidate / "cicd_與_安全檢查範本").exists():
            return candidate.resolve()
    return Path(__file__).resolve().parent.parent


def load_gitignore_patterns(root: Path) -> List[str]:
    """Parse non-empty, non-comment patterns from .gitignore."""
    gi = root / ".gitignore"
    if not gi.exists():
        return []
    patterns: List[str] = []
    for raw in gi.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        patterns.append(line)
    return patterns


def is_ignored_by_rules(rel_posix: str, patterns: List[str]) -> bool:
    """Approximate gitignore matching when .git is not initialized yet."""
    parts = rel_posix.split("/")
    if ".git" in parts:
        return True
    name = parts[-1]
    for pat in patterns:
        clean = pat.rstrip("/")
        if clean.startswith("/"):
            clean = clean.lstrip("/")
            if rel_posix == clean or rel_posix.startswith(clean + "/") or fnmatch.fnmatch(rel_posix, clean):
                return True
            continue
        # Match folder prefix, full rel path, or basename
        if pat.endswith("/"):
            if clean in parts[:-1] or rel_posix == clean or rel_posix.startswith(clean + "/"):
                return True
        if fnmatch.fnmatch(name, clean) or fnmatch.fnmatch(rel_posix, clean):
            return True
        if "/" in clean and rel_posix.startswith(clean + "/"):
            return True
    return False


def list_repo_files(root: Path, patterns: List[str]) -> Tuple[List[Path], List[Path], bool]:
    """Return (pushable_files, ignored_files, has_git)."""
    has_git = (root / ".git").exists()
    pushable: List[Path] = []
    ignored: List[Path] = []

    if has_git:
        try:
            out = subprocess.check_output(
                ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                stderr=subprocess.DEVNULL,
            )
            pushable_set = {
                (root / p).resolve()
                for p in out.decode("utf-8", errors="replace").split("\x00")
                if p
            }
            for p in sorted(pushable_set):
                if p.is_file():
                    pushable.append(p)
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d != ".git"]
                for fn in filenames:
                    fp = (Path(dirpath) / fn).resolve()
                    if fp not in pushable_set and fp.is_file():
                        ignored.append(fp)
            return pushable, ignored, True
        except Exception:
            pass

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            fp = (Path(dirpath) / fn).resolve()
            rel = fp.relative_to(root).as_posix()
            if is_ignored_by_rules(rel, patterns):
                ignored.append(fp)
            else:
                pushable.append(fp)
    return sorted(pushable), sorted(ignored), has_git


def extract_pdf_text(path: Path) -> str:
    """Extract ASCII/UTF printable strings and FlateDecode streams from PDF using stdlib only."""
    data = path.read_bytes()
    chunks: List[str] = [data.decode("latin-1", errors="ignore")]
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
        raw_stream = match.group(1)
        try:
            decompressed = zlib.decompress(raw_stream)
            chunks.append(decompressed.decode("utf-8", errors="ignore"))
        except Exception:
            continue
    return "\n".join(chunks)


def check_text_content(rel: str, text: str, severity: str) -> List[Finding]:
    """Scan text against SEC-01 .. SEC-06 patterns."""
    findings: List[Finding] = []
    seen = set()
    for rule_id, desc, pattern in SECRET_PATTERNS:
        m = pattern.search(text)
        if m and (rule_id, desc) not in seen:
            seen.add((rule_id, desc))
            snippet = m.group(0)
            if len(snippet) > 64:
                snippet = snippet[:32] + "..." + snippet[-12:]
            findings.append(
                Finding(
                    severity=severity,
                    rule_id=rule_id,
                    path=rel,
                    detail=f"{desc} (matched `{snippet}`)",
                    remediation="Remove secret/local path/copyrighted string or exclude file via .gitignore.",
                )
            )
    return findings


def check_tabular_or_db_pii(path: Path, rel: str, severity: str) -> List[Finding]:
    """Check CSV & SQLite files for unmasked emails, phone numbers, or non-hashed node IDs."""
    findings: List[Finding] = []
    suffix = path.suffix.lower()

    if suffix == ".csv":
        text = path.read_text(encoding="utf-8", errors="replace")
        if EMAIL_RE.search(text) or TW_PHONE_RE.search(text):
            findings.append(
                Finding(
                    severity=severity,
                    rule_id="SEC-05",
                    path=rel,
                    detail="Potential unmasked email or TW phone number detected in CSV.",
                    remediation="Mask or remove direct identifiers before committing CSV data.",
                )
            )
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            id_cols = [c for c in (reader.fieldnames or []) if c in {"node_hash", "source_hash", "target_hash"}]
            if id_cols:
                bad_vals = []
                for row in reader:
                    for col in id_cols:
                        val = (row.get(col) or "").strip()
                        if val and not HEX16_RE.match(val):
                            bad_vals.append(f"{col}={val}")
                            break
                    if bad_vals:
                        break
                if bad_vals:
                    findings.append(
                        Finding(
                            severity=severity,
                            rule_id="SEC-05",
                            path=rel,
                            detail=f"Non-16-hex masked ID found in hash column ({bad_vals[0]}).",
                            remediation="Ensure all node_hash/source_hash/target_hash fields use salted 16-hex SHA-256.",
                        )
                    )

    elif suffix in {".sqlite", ".db"}:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            for tbl in tables:
                cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
                hash_cols = [c for c in cols if c in {"node_hash", "source_hash", "target_hash"}]
                for hcol in hash_cols:
                    rows = conn.execute(f"SELECT {hcol} FROM {tbl} LIMIT 50").fetchall()
                    for (val,) in rows:
                        if val and not HEX16_RE.match(str(val)):
                            findings.append(
                                Finding(
                                    severity=severity,
                                    rule_id="SEC-05",
                                    path=rel,
                                    detail=f"SQLite table `{tbl}`.{hcol} contains unmasked ID `{val}`.",
                                    remediation="Re-run pipeline with Salted SHA-256 PII masking before committing SQLite.",
                                )
                            )
                            break
        finally:
            conn.close()

    return findings


def scan_file(path: Path, root: Path, severity: str) -> List[Finding]:
    """Run metadata, filename, binary-size, and content checks on a single file."""
    rel = path.relative_to(root).as_posix()
    findings: List[Finding] = []
    fname_lower = path.name.lower()

    if fname_lower in FORBIDDEN_SENSITIVE_FILENAMES or fname_lower.endswith(".cookies") or "unmasked" in fname_lower:
        findings.append(
            Finding(
                severity=severity,
                rule_id="SEC-07" if fname_lower == ".ds_store" else "SEC-02",
                path=rel,
                detail=f"Sensitive or OS junk filename `{path.name}` should never be committed.",
                remediation="Keep excluded in .gitignore and remove from git index (`git rm --cached`).",
            )
        )

    size_bytes = path.stat().st_size
    if size_bytes > MAX_FILE_BYTES:
        findings.append(
            Finding(
                severity=severity,
                rule_id="SEC-07",
                path=rel,
                detail=f"File size {size_bytes / (1024 * 1024):.2f} MB exceeds 5 MB GitHub threshold.",
                remediation="Exclude large raw data or binaries via .gitignore or Git LFS.",
            )
        )

    if rel in SCANNER_SELF_ALLOWLIST or rel.startswith(".github/"):
        return findings

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = extract_pdf_text(path)
        findings.extend(check_text_content(rel, text, severity))
    elif suffix in TEXT_EXTENSIONS:
        text = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(check_text_content(rel, text, severity))

    if suffix in {".csv", ".sqlite", ".db"}:
        findings.extend(check_tabular_or_db_pii(path, rel, severity))

    return findings


def check_parent_workspace_advisory(root: Path) -> List[Finding]:
    """Advise user if copyrighted folders or OS junk exist in the parent directory."""
    parent = root.parent
    advisories: List[Finding] = []
    if (parent / ".git").exists():
        advisories.append(
            Finding(
                severity="BLOCK",
                rule_id="SEC-04",
                path=f"../.git",
                detail="Git repository detected in parent directory containing copyrighted textbook folders!",
                remediation="Remove parent .git and initialize git strictly inside `期未/` only.",
            )
        )
    for risky_name, desc in (
        ("課本_pdf", "Copyrighted Easley & Kleinberg PDFs (~24MB+, Cambridge Core watermark)"),
        ("課本_文字", "Extracted textbook chapters & figures from copyrighted PDFs"),
    ):
        target = parent / risky_name
        if target.exists():
            advisories.append(
                Finding(
                    severity="ADVISORY",
                    rule_id="SEC-04",
                    path=f"../{risky_name}/",
                    detail=f"{desc} resides in parent directory outside `期未/`.",
                    remediation="Do NOT move into `期未/` or run `git init` in parent folder; push `期未/` only.",
                )
            )
    return advisories


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Pre-Push Security, PII & Copyright Audit")
    parser.add_argument("--root", type=Path, default=None, help="Project root (default: 期未/)")
    parser.add_argument("--strict-ci", action="store_true", help="Exit 1 on any BLOCK finding in pushable files")
    parser.add_argument("--report-json", type=Path, default=None, help="Optional JSON output path")
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root else find_project_root(Path(__file__).resolve().parent)
    patterns = load_gitignore_patterns(root)
    pushable, ignored, has_git = list_repo_files(root, patterns)

    block_findings: List[Finding] = []
    ignored_findings: List[Finding] = []
    advisory_findings = check_parent_workspace_advisory(root)

    # Escalate any BLOCK inside parent advisory (e.g. parent .git)
    real_advisories: List[Finding] = []
    for f in advisory_findings:
        if f.severity == "BLOCK":
            block_findings.append(f)
        else:
            real_advisories.append(f)

    for fp in pushable:
        block_findings.extend(scan_file(fp, root, severity="BLOCK"))

    for fp in ignored:
        ignored_findings.extend(scan_file(fp, root, severity="IGNORED_OK"))

    summary = {
        "root": str(root),
        "git_initialized": has_git,
        "pushable_file_count": len(pushable),
        "ignored_file_count": len(ignored),
        "block_count": len(block_findings),
        "ignored_risk_count": len(ignored_findings),
        "parent_advisory_count": len(real_advisories),
        "status": "FAIL" if block_findings else "PASS",
        "block_findings": [asdict(f) for f in block_findings],
        "ignored_findings": [asdict(f) for f in ignored_findings],
        "parent_advisories": [asdict(f) for f in real_advisories],
    }

    if args.report_json:
        out_path = args.report_json if args.report_json.is_absolute() else (root / args.report_json)
        out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 72)
    print(f"Taigi NCM Pre-Push Security & PII Audit | Root: {root.name}/ | Git active: {has_git}")
    print(f"Pushable files scanned: {len(pushable)} | Ignored files checked: {len(ignored)}")
    print("=" * 72)

    if block_findings:
        print(f"\n[BLOCK] {len(block_findings)} issue(s) found in pushable scope:")
        for idx, f in enumerate(block_findings, 1):
            print(f"  {idx}. [{f.rule_id}] {f.path} -> {f.detail}")
            print(f"     Fix: {f.remediation}")
    else:
        print("\n[PASS] 0 BLOCK findings in pushable files!")

    if ignored_findings:
        print(f"\n[IGNORED BY .gitignore] {len(ignored_findings)} risky item(s) safely excluded from GitHub push:")
        for f in ignored_findings:
            print(f"  - [{f.rule_id}] {f.path} -> {f.detail}")

    if real_advisories:
        print(f"\n[PARENT WORKSPACE ADVISORY] {len(real_advisories)} parent-folder item(s) MUST stay outside GitHub:")
        for f in real_advisories:
            print(f"  - [{f.rule_id}] {f.path} -> {f.detail}")

    print("\nOverall Security Status:", summary["status"])
    return 1 if block_findings else 0


if __name__ == "__main__":
    sys.exit(main())
