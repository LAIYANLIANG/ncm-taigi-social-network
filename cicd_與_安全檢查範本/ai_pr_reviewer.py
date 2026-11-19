#!/usr/bin/env python3
"""AI-assisted Pre-Push & Pull-Request Compliance Reviewer for the Taigi NCM project.

Supports two review engines:
  1. Gemini LLM Review (when GEMINI_API_KEY env var is set and reachable)
  2. Offline Deterministic Heuristic Reviewer fallback (always available offline/pre-push)

Focuses on domain-specific risks beyond regex:
  - Social scraping ethics & platform ToS compliance (no browser cookies / storageState)
  - PII hashing hygiene (Salted SHA-256 via environment variable, not hardcoded prod salt)
  - Methodological & Gate alignment (G1-G6 verification & figure/report synchronization)
  - Copyright & documentation hygiene (no textbook dumps or broken parent links)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_REVIEW_MODEL", "gemini-2.5-flash")
MAX_DIFF_CHARS = 24000


def resolve_root(start: Optional[Path] = None) -> Path:
    base = start or Path(__file__).resolve().parent.parent
    return base.resolve()


def run_git(root: Path, git_args: List[str]) -> Tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *git_args],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout
    except Exception as exc:
        return 1, str(exc)


def collect_diff(root: Path, mode: str, base_sha: Optional[str], head_sha: Optional[str]) -> Tuple[str, List[str]]:
    """Collect unified diff and changed file list across git modes or non-git fallback."""
    has_git = (root / ".git").exists()
    if has_git:
        if mode == "pr" and base_sha and head_sha:
            rc, diff = run_git(root, ["diff", f"{base_sha}...{head_sha}"])
            _, files_out = run_git(root, ["diff", "--name-only", f"{base_sha}...{head_sha}"])
            if rc == 0 and diff.strip():
                return diff[:MAX_DIFF_CHARS], [f for f in files_out.splitlines() if f.strip()]
        elif mode == "staged":
            rc, diff = run_git(root, ["diff", "--cached"])
            _, files_out = run_git(root, ["diff", "--cached", "--name-only"])
            if rc == 0 and diff.strip():
                return diff[:MAX_DIFF_CHARS], [f for f in files_out.splitlines() if f.strip()]

        # Workspace fallback inside git repo
        _, status_out = run_git(root, ["status", "--short"])
        _, diff_wt = run_git(root, ["diff", "HEAD"])
        if not diff_wt.strip():
            _, diff_wt = run_git(root, ["diff"])
        changed = [line[3:].strip() for line in status_out.splitlines() if len(line) > 3]
        if diff_wt.strip():
            return diff_wt[:MAX_DIFF_CHARS], changed

    # Non-git fallback: summarize key tracked/deliverable files so dry-run works pre-init
    key_files = [
        "demo/src/run_demo_pipeline.py",
        "demo/plain/05_驗收規劃與交付檢核表.md",
        "README.md",
        ".gitignore",
        ".gitleaks.toml",
    ]
    snippets: List[str] = ["[Workspace Snapshot Mode — .git not initialized or working tree clean]"]
    present: List[str] = []
    for rel in key_files:
        fp = root / rel
        if fp.exists():
            present.append(rel)
            head = fp.read_text(encoding="utf-8", errors="replace").splitlines()[:60]
            snippets.append(f"--- {rel} (first 60 lines) ---\n" + "\n".join(head))
    return "\n".join(snippets)[:MAX_DIFF_CHARS], present


def _extract_python_code_text(root: Path, diff_text: str, changed_files: List[str]) -> str:
    """Return text strictly from changed/targeted non-scanner Python files."""
    chunks: List[str] = []
    if "diff --git " in diff_text:
        current_file = ""
        for line in diff_text.splitlines():
            if line.startswith("diff --git "):
                parts = line.split(" b/")
                current_file = parts[-1].strip() if len(parts) > 1 else ""
                continue
            if (
                current_file.endswith(".py")
                and not current_file.startswith("cicd_與_安全檢查範本/")
                and line.startswith("+")
                and not line.startswith("+++")
            ):
                chunks.append(line[1:])
        return "\n".join(chunks)

    for rel in changed_files:
        if rel.endswith(".py") and not rel.startswith("cicd_與_安全檢查範本/"):
            fp = root / rel
            if fp.exists():
                chunks.append(fp.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def heuristic_review(root: Path, diff_text: str, changed_files: List[str]) -> Dict[str, object]:
    """Deterministic domain-aware compliance review (offline fallback or pre-check)."""
    blockers: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []

    py_scope_text = _extract_python_code_text(root, diff_text, changed_files)

    # 1. Check for Playwright/Selenium/requests cookie injection in Python scraper/pipeline code
    if py_scope_text and re.search(r"(storage_state|add_cookies|load_cookies|cookies\.txt)", py_scope_text, re.IGNORECASE):
        blockers.append("Detected cookie/storage_state session injection pattern in Python code; violates public-only ethical scraping policy.")

    # 2. Check SALT hygiene in run_demo_pipeline.py
    pipeline_path = root / "demo/src/run_demo_pipeline.py"
    if pipeline_path.exists():
        ptext = pipeline_path.read_text(encoding="utf-8", errors="replace")
        if 'os.environ.get("TAIGI_PII_SALT"' not in ptext:
            warnings.append("`run_demo_pipeline.py` should read `TAIGI_PII_SALT` from environment variables instead of a fixed constant.")

    # 3. Check if relative links point outside 期未/ (e.g., ../課本_文字/)
    for md_rel in ("期末專題規劃_台語世代傳承與海外隱形連結.md",):
        md_fp = root / md_rel
        if md_fp.exists() and "../課本_文字/" in md_fp.read_text(encoding="utf-8", errors="replace"):
            warnings.append(f"`{md_rel}` contains relative links to `../課本_文字/`, which will 404 on GitHub because `課本_文字/` is excluded for copyright.")

    # 4. Check acceptance report synchronization
    acc_path = root / "demo/output/05_acceptance_verification_report.json"
    if acc_path.exists():
        try:
            acc = json.loads(acc_path.read_text(encoding="utf-8"))
            if acc.get("overall_status") != "PASS":
                blockers.append(f"Acceptance report overall_status is `{acc.get('overall_status')}`, expected PASS.")
        except Exception:
            warnings.append("Unable to parse `demo/output/05_acceptance_verification_report.json`.")
    else:
        warnings.append("Acceptance verification JSON report is missing; run `python3 demo/src/run_demo_pipeline.py`.")

    # 5. If code/data changed, advise re-running G1-G6 verification
    if any(f.startswith("demo/src/") or f.startswith("demo/data/") for f in changed_files):
        recommendations.append("Code or data changed under `demo/`; verify `python3 demo/src/run_demo_pipeline.py` passes G1-G6 after final edits.")

    if not blockers and not warnings:
        recommendations.append("All automated security, PII-hashing, and repository hygiene checks look clean.")

    risk_level = "HIGH" if blockers else ("MEDIUM" if warnings else "LOW")
    return {
        "engine": "offline-heuristic-compliance-reviewer",
        "risk_level": risk_level,
        "blockers": blockers,
        "warnings": warnings,
        "recommendations": recommendations,
        "summary": (
            f"Inspected {len(changed_files)} file(s). "
            f"Risk level: {risk_level} ({len(blockers)} blocker(s), {len(warnings)} warning(s))."
        ),
    }


def call_gemini_review(api_key: str, diff_text: str, changed_files: List[str]) -> Optional[Dict[str, object]]:
    """Invoke Gemini REST API for semantic privacy, ethics, and methodology PR review."""
    prompt = (
        "You are a senior security, research-ethics, and graph-algorithms reviewer auditing a GitHub change "
        "for a Computational Social Science project (*Networks, Crowds, and Markets*: Taigi intergenerational transmission, "
        "Hubs & Authorities via HITS, Strong vs Weak Ties).\n\n"
        "Review the changed files and diff below strictly for:\n"
        "1. PII leaks, API secrets, authenticated social cookies, or hardcoded local home paths (/Users/...).\n"
        "2. Copyrighted textbook text or personal Gemini URLs accidentally introduced.\n"
        "3. Ethical scraping compliance (publicly observable posts/APIs only, rate limits, salted SHA-256 hashing via env var).\n"
        "4. Logical bugs affecting HITS, Shannon entropy, weak-tie bridging, or acceptance gates G1-G6.\n\n"
        f"Changed files: {json.dumps(changed_files, ensure_ascii=False)}\n\n"
        f"Diff / Snapshot:\n```\n{diff_text}\n```\n\n"
        "Reply ONLY with valid JSON matching this schema:\n"
        '{"risk_level": "LOW|MEDIUM|HIGH", "blockers": [str], "warnings": [str], "recommendations": [str], "summary": str}'
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_GEMINI_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        parsed["engine"] = f"gemini-llm ({DEFAULT_GEMINI_MODEL})"
        return parsed
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError, TimeoutError):
        return None


def format_markdown(review: Dict[str, object], changed_files: List[str]) -> str:
    lines = [
        "## AI 安全、去敏與專題規範審查報告 (AI PR Compliance Review)",
        "",
        f"- **審查引擎 (Engine)**: `{review.get('engine', 'unknown')}`",
        f"- **綜合風險等級 (Risk Level)**: **{review.get('risk_level', 'UNKNOWN')}**",
        f"- **涵蓋檔案數**: {len(changed_files)}",
        "",
        f"> {review.get('summary', '')}",
        "",
    ]
    for title, key in (
        ("### Blockers (必須修復才能合併 / Push)", "blockers"),
        ("### Warnings (建議注意 / 評估)", "warnings"),
        ("### Recommendations (最佳實務建議)", "recommendations"),
    ):
        items = review.get(key) or []
        lines.append(title)
        if items:
            for item in items:
                lines.append(f"- {item}")
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AI Pre-Push & PR Compliance Reviewer")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--diff-mode", choices=["staged", "workspace", "pr"], default="workspace")
    parser.add_argument("--base-sha", default=None)
    parser.add_argument("--head-sha", default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when risk_level is HIGH")
    parser.add_argument("--require-llm", action="store_true", help="Fail if GEMINI_API_KEY is missing or unreachable")
    parser.add_argument("--dry-run", action="store_true", help="Always exit 0 after printing review")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    diff_text, changed_files = collect_diff(root, args.diff_mode, args.base_sha, args.head_sha)

    heuristic = heuristic_review(root, diff_text, changed_files)
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    final_review = heuristic
    if api_key and not args.dry_run:
        llm_res = call_gemini_review(api_key, diff_text, changed_files)
        if llm_res:
            # Merge heuristic blockers so deterministic checks are never lost
            llm_res["blockers"] = list(dict.fromkeys([*heuristic["blockers"], *(llm_res.get("blockers") or [])]))
            if llm_res["blockers"]:
                llm_res["risk_level"] = "HIGH"
            final_review = llm_res
        elif args.require_llm:
            print("ERROR: GEMINI_API_KEY set or required, but Gemini API call failed.", file=sys.stderr)
            return 2
    elif args.require_llm:
        print("ERROR: --require-llm specified but GEMINI_API_KEY is unset.", file=sys.stderr)
        return 2

    md = format_markdown(final_review, changed_files)
    if args.output_md:
        out = args.output_md if args.output_md.is_absolute() else (root / args.output_md)
        out.write_text(md, encoding="utf-8")

    print(md)
    if args.strict and not args.dry_run and final_review.get("risk_level") == "HIGH":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
