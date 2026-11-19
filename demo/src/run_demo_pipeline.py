#!/usr/bin/env python3
"""
End-to-End Execution & Verification Pipeline for:
「台語：從世代傳承的困境，到海外社群的隱形連結」

Zero missing dependencies: uses Python standard library + numpy + pandas + sqlite3.
Implements:
  - Multi-channel synthetic dataset & SQLite ingestion with Salted SHA-256 PII masking (G1)
  - Sampling Quality Validation: Heaps' Law, Marginal SNR Slope Rejection, Shannon Entropy (G2)
  - Signed Network Filtering, HITS (Matrix & Exact Eigenvector Check), Scaled PageRank,
    Brandes Betweenness, BridgeHub, InvisibleLinkScore, Perturbation & Ablation Tests (G3, G4)
  - Ch 19.7B Bilingual Diffusion & Buffer Zone Simulator (G4)
  - Time-Slicing Topological Dimensional Reduction & Survival Counting Process Table (G5)
"""

import csv
import hashlib
import json
import math
import os
import sqlite3
from collections import deque

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["PingFang HK", "Heiti TC", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "output")
FIG_DIR = os.path.join(OUT_DIR, "figures")

SALT = os.environ.get("TAIGI_PII_SALT", "ncm_taigi_2026_demo_only_salt")


def mask_pii(raw_id: str) -> str:
    """Salted SHA-256 hash (16 hex chars) for PII Masking (PDF p. 3, 18)."""
    return hashlib.sha256(f"{SALT}:{raw_id}".encode("utf-8")).hexdigest()[:16]


def shannon_entropy_normalized(counts: dict) -> float:
    """Normalized Shannon diversity index H / ln(C) in [0, 1] (PDF p. 21)."""
    total = sum(counts.values())
    k = len(counts)
    if total == 0 or k <= 1:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    h = -sum(p * math.log(p) for p in probs)
    return float(h / math.log(k))


def gini_coefficient(values: np.ndarray) -> float:
    """Gini coefficient of centrality/hub scores (PDF p. 27)."""
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n == 0 or np.sum(x) == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2.0 * np.sum(idx * x)) / (n * np.sum(x)) - (n + 1) / n)


def spearman_rank_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Spearman rank correlation using pandas rank (average ties)."""
    rx = pd.Series(x).rank(method="average").to_numpy()
    ry = pd.Series(y).rank(method="average").to_numpy()
    if np.std(rx) == 0 or np.std(ry) == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


# ---------------------------------------------------------------------------
# 1. Dataset Generation & SQLite Ingestion (G1)
# ---------------------------------------------------------------------------
def build_demo_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 24 representative nodes spanning 4 platforms and 3 regions + Pre-mortem adversarial nodes
    nodes = [
        # Core cultural & digital tools (resource)
        ("res_chhoetaigi", "ChhoeTaigi台語辭典生態", "website", "resource", "youth_digital", "web_threads"),
        ("res_moedict_taigi", "萌典/教育部台語辭典", "website", "resource", "general", "web_threads"),
        ("res_pts_taigi", "公視台語台數位頻道", "channel", "resource", "general", "youtube"),
        ("res_itaigi", "iTaigi愛台語共筆詞庫", "website", "resource", "youth_digital", "web_threads"),
        # Local Authorities (local)
        ("auth_podcast_taigi", "青年台語Podcast台語開講", "channel", "local", "youth_digital", "youtube"),
        ("auth_twlang_scholar", "PTT_TW-language考據核心", "author", "local", "traditional", "ptt"),
        ("auth_indie_band", "台語獨立音樂與歌詞創作", "channel", "local", "youth_digital", "youtube"),
        ("auth_parent_co_study", "台灣親子台語共學團", "organization", "local", "youth_digital", "web_threads"),
        # Diaspora Authorities (diaspora)
        ("auth_na_association", "北美台灣同鄉會文化線", "organization", "diaspora", "overseas_diaspora", "web_threads"),
        ("auth_overseas_church", "海外台語長老教會禮拜網", "organization", "diaspora", "overseas_diaspora", "web_threads"),
        ("auth_reddit_ohtaigi", "Reddit_r_ohtaigi海外學習精華", "author", "diaspora", "overseas_diaspora", "reddit"),
        ("auth_tokyo_taigi", "東京台灣人台語沙龍", "organization", "diaspora", "overseas_diaspora", "web_threads"),
        # Cross-border Invisible Link Bridges (BridgeHubs: low in-degree, high hub + high betweenness)
        ("hub_bridge_student", "留美台生跨海策展帳號", "author", "diaspora", "overseas_diaspora", "reddit"),
        ("hub_bridge_curator", "台文懶人包跨國轉發站", "website", "local", "youth_digital", "web_threads"),
        ("hub_bridge_yt_mod", "台語頻道跨區字幕志工", "author", "diaspora", "overseas_diaspora", "youtube"),
        # Pure Local Hubs
        ("hub_local_ptt_1", "PTT母語版推文整理者A", "author", "local", "youth_digital", "ptt"),
        ("hub_local_yt_2", "本土台語音樂清單整理者B", "author", "local", "youth_digital", "youtube"),
        # Pure Diaspora Hubs
        ("hub_diaspora_1", "海外二三代活動轉發志工C", "author", "diaspora", "overseas_diaspora", "reddit"),
        ("hub_diaspora_2", "歐洲台人社團週報整理D", "author", "diaspora", "overseas_diaspora", "web_threads"),
        # Dual Leader (High Auth & High Hub)
        ("dual_taigi_podcaster", "跨國台語雙棲訪談主持人", "channel", "local", "youth_digital", "youtube"),
        # Periphery Learners
        ("peri_learner_1", "台北上班族台語初學者", "author", "local", "youth_digital", "ptt"),
        ("peri_learner_2", "加州台裔二代學習者", "author", "diaspora", "overseas_diaspora", "reddit"),
        # Pre-Mortem Adversarial & Noise Controls
        ("noise_troll_baiter", "政治引戰嘲諷釣魚帳號", "author", "local", "general", "ptt"),
        ("noise_viral_youtuber", "百萬娛樂大號偶發台語短片", "channel", "local", "general", "youtube"),
        ("noise_passerby_bot", "演算法推播一次性路人", "author", "local", "general", "youtube"),
    ]

    nodes_df = pd.DataFrame(
        nodes,
        columns=["node_id", "display_label", "node_type", "region", "generation_tag", "platform"],
    )
    nodes_df["node_hash"] = nodes_df["node_id"].apply(mask_pii)
    nodes_df.to_csv(os.path.join(DATA_DIR, "nodes_metadata.csv"), index=False, encoding="utf-8")

    # Helper to assign slices cleanly across 2024Q1..2025Q4
    slices = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]

    # Directed interactions: (source, target, platform, edge_type, weight, sentiment, slice_idx)
    raw_edges = [
        # --- Dual Leader: receives endorsements AND curates across local & diaspora ---
        ("hub_local_ptt_1", "dual_taigi_podcaster", "ptt", "citation", 3.0, 1, 0),
        ("hub_local_yt_2", "dual_taigi_podcaster", "youtube", "reply_endorse", 3.0, 1, 1),
        ("hub_bridge_student", "dual_taigi_podcaster", "reddit", "citation", 3.0, 1, 2),
        ("hub_bridge_curator", "dual_taigi_podcaster", "web_threads", "hyperlink", 3.0, 1, 3),
        ("dual_taigi_podcaster", "res_chhoetaigi", "youtube", "hyperlink", 4.0, 1, 0),
        ("dual_taigi_podcaster", "auth_podcast_taigi", "youtube", "citation", 3.0, 1, 1),
        ("dual_taigi_podcaster", "auth_na_association", "youtube", "citation", 2.0, 1, 4),

        # --- Pure Local Hubs endorsing Local Authorities & Core Resources ---
        ("hub_local_ptt_1", "res_chhoetaigi", "ptt", "hyperlink", 4.0, 1, 0),
        ("hub_local_ptt_1", "res_moedict_taigi", "ptt", "hyperlink", 3.0, 1, 0),
        ("hub_local_ptt_1", "res_itaigi", "ptt", "hyperlink", 3.0, 1, 1),
        ("hub_local_ptt_1", "auth_twlang_scholar", "ptt", "reply_endorse", 4.0, 1, 1),
        ("hub_local_ptt_1", "auth_podcast_taigi", "ptt", "citation", 2.0, 1, 2),
        ("hub_local_ptt_1", "auth_parent_co_study", "ptt", "citation", 2.0, 1, 3),

        ("hub_local_yt_2", "res_pts_taigi", "youtube", "hyperlink", 4.0, 1, 1),
        ("hub_local_yt_2", "auth_indie_band", "youtube", "reply_endorse", 5.0, 1, 2),
        ("hub_local_yt_2", "auth_podcast_taigi", "youtube", "reply_endorse", 4.0, 1, 3),
        ("hub_local_yt_2", "res_chhoetaigi", "youtube", "hyperlink", 3.0, 1, 4),

        # --- Pure Diaspora Hubs endorsing Overseas Authorities ---
        ("hub_diaspora_1", "auth_na_association", "reddit", "hyperlink", 4.0, 1, 2),
        ("hub_diaspora_1", "auth_reddit_ohtaigi", "reddit", "reply_endorse", 4.0, 1, 3),
        ("hub_diaspora_1", "auth_overseas_church", "reddit", "citation", 3.0, 1, 4),

        ("hub_diaspora_2", "auth_overseas_church", "web_threads", "hyperlink", 3.0, 1, 3),
        ("hub_diaspora_2", "auth_tokyo_taigi", "web_threads", "hyperlink", 3.0, 1, 5),
        ("hub_diaspora_2", "auth_na_association", "web_threads", "hyperlink", 2.0, 1, 6),

        # --- Cross-Border Invisible Link Bridges (BridgeHubs): link local + resource + diaspora ---
        ("hub_bridge_student", "res_chhoetaigi", "reddit", "curated_list", 4.0, 1, 1),
        ("hub_bridge_student", "auth_podcast_taigi", "reddit", "curated_list", 3.0, 1, 2),
        ("hub_bridge_student", "auth_parent_co_study", "reddit", "citation", 2.0, 1, 3),
        ("hub_bridge_student", "auth_na_association", "reddit", "curated_list", 3.0, 1, 4),
        ("hub_bridge_student", "auth_reddit_ohtaigi", "reddit", "curated_list", 4.0, 1, 5),
        ("hub_bridge_student", "auth_overseas_church", "reddit", "citation", 2.0, 1, 6),

        ("hub_bridge_curator", "res_chhoetaigi", "web_threads", "curated_list", 5.0, 1, 0),
        ("hub_bridge_curator", "res_itaigi", "web_threads", "curated_list", 3.0, 1, 2),
        ("hub_bridge_curator", "res_pts_taigi", "web_threads", "curated_list", 3.0, 1, 3),
        ("hub_bridge_curator", "auth_twlang_scholar", "web_threads", "citation", 3.0, 1, 4),
        ("hub_bridge_curator", "auth_na_association", "web_threads", "hyperlink", 3.0, 1, 5),
        ("hub_bridge_curator", "auth_tokyo_taigi", "web_threads", "hyperlink", 3.0, 1, 6),
        ("hub_bridge_curator", "auth_overseas_church", "web_threads", "hyperlink", 2.0, 1, 7),

        ("hub_bridge_yt_mod", "res_pts_taigi", "youtube", "curated_list", 4.0, 1, 2),
        ("hub_bridge_yt_mod", "res_chhoetaigi", "youtube", "curated_list", 4.0, 1, 3),
        ("hub_bridge_yt_mod", "auth_podcast_taigi", "youtube", "reply_endorse", 4.0, 1, 4),
        ("hub_bridge_yt_mod", "auth_indie_band", "youtube", "reply_endorse", 3.0, 1, 5),
        ("hub_bridge_yt_mod", "auth_reddit_ohtaigi", "youtube", "hyperlink", 4.0, 1, 6),
        ("hub_bridge_yt_mod", "auth_tokyo_taigi", "youtube", "citation", 3.0, 1, 7),
        ("hub_bridge_yt_mod", "auth_na_association", "youtube", "citation", 3.0, 1, 7),

        # --- Core Authorities inter-referencing & Periphery Learners connecting ---
        ("auth_podcast_taigi", "res_chhoetaigi", "youtube", "hyperlink", 3.0, 1, 1),
        ("auth_parent_co_study", "res_itaigi", "web_threads", "hyperlink", 3.0, 1, 2),
        ("auth_na_association", "res_moedict_taigi", "web_threads", "hyperlink", 2.0, 1, 5),
        ("auth_reddit_ohtaigi", "res_chhoetaigi", "reddit", "hyperlink", 3.0, 1, 6),
        ("peri_learner_1", "hub_local_ptt_1", "ptt", "reply_endorse", 2.0, 1, 4),
        ("peri_learner_1", "auth_podcast_taigi", "youtube", "reply_endorse", 2.0, 1, 5),
        ("peri_learner_2", "hub_bridge_student", "reddit", "reply_endorse", 2.0, 1, 6),
        ("peri_learner_2", "hub_bridge_yt_mod", "youtube", "reply_endorse", 2.0, 1, 7),
        ("peri_learner_2", "auth_reddit_ohtaigi", "reddit", "reply_endorse", 2.0, 1, 7),

        # --- Pre-Mortem Case 2: Conflict Troll Baiter receiving 12 negative rebuttals (sentiment = -1) ---
        ("hub_local_ptt_1", "noise_troll_baiter", "ptt", "conflict_reply", 3.0, -1, 3),
        ("auth_twlang_scholar", "noise_troll_baiter", "ptt", "conflict_reply", 3.0, -1, 3),
        ("hub_bridge_curator", "noise_troll_baiter", "ptt", "conflict_reply", 2.0, -1, 4),
        ("peri_learner_1", "noise_troll_baiter", "ptt", "conflict_reply", 2.0, -1, 4),
        ("hub_bridge_student", "noise_troll_baiter", "ptt", "conflict_reply", 2.0, -1, 5),
        ("hub_local_yt_2", "noise_troll_baiter", "ptt", "conflict_reply", 2.0, -1, 5),

        # --- Pre-Mortem Case 3: One-off Algorithmic Passerby Noise (weight = 1, filtered by tau >= 2) ---
        ("noise_passerby_bot", "noise_viral_youtuber", "youtube", "reply_endorse", 1.0, 1, 6),
        ("peri_learner_1", "noise_viral_youtuber", "youtube", "reply_endorse", 1.0, 1, 6),
    ]

    slice_dates = {
        "2024Q1": "2024-02-15 10:00:00",
        "2024Q2": "2024-05-15 14:20:00",
        "2024Q3": "2024-08-15 09:30:00",
        "2024Q4": "2024-11-15 18:45:00",
        "2025Q1": "2025-02-15 11:10:00",
        "2025Q2": "2025-05-15 16:00:00",
        "2025Q3": "2025-08-15 20:15:00",
        "2025Q4": "2025-11-15 12:30:00",
    }

    edge_rows = []
    for idx, (src, dst, plat, etype, w, sent, s_idx) in enumerate(raw_edges, start=1):
        sid = slices[s_idx]
        edge_rows.append({
            "edge_id": f"E{idx:04d}",
            "source_id": src,
            "target_id": dst,
            "source_hash": mask_pii(src),
            "target_hash": mask_pii(dst),
            "platform": plat,
            "edge_type": etype,
            "weight": w,
            "sentiment": sent,
            "slice_id": sid,
            "timestamp": slice_dates[sid],
        })

    edges_df = pd.DataFrame(edge_rows)
    edges_df.to_csv(os.path.join(DATA_DIR, "interactions_raw.csv"), index=False, encoding="utf-8")

    # 8 sequential corpus sampling batches (Batch 7 injects high-noise political gossip to verify SQV-2!)
    # True Heaps' Law K=45, beta=0.49 for clean batches
    batches = [
        {"batch_id": 1, "platform": "ptt", "region": "local", "doc_count": 300, "batch_tokens": 2400, "cum_tokens_N": 2400, "cum_vocab_V": 2030, "valid_signal_rate": 0.90},
        {"batch_id": 2, "platform": "youtube", "region": "resource", "doc_count": 350, "batch_tokens": 3100, "cum_tokens_N": 5500, "cum_vocab_V": 3045, "valid_signal_rate": 0.89},
        {"batch_id": 3, "platform": "web_threads", "region": "local", "doc_count": 400, "batch_tokens": 4200, "cum_tokens_N": 9700, "cum_vocab_V": 4040, "valid_signal_rate": 0.87},
        {"batch_id": 4, "platform": "reddit", "region": "diaspora", "doc_count": 420, "batch_tokens": 5300, "cum_tokens_N": 15000, "cum_vocab_V": 4990, "valid_signal_rate": 0.91},
        {"batch_id": 5, "platform": "youtube", "region": "local", "doc_count": 480, "batch_tokens": 6000, "cum_tokens_N": 21000, "cum_vocab_V": 5890, "valid_signal_rate": 0.88},
        {"batch_id": 6, "platform": "web_threads", "region": "diaspora", "doc_count": 500, "batch_tokens": 6500, "cum_tokens_N": 27500, "cum_vocab_V": 6120, "valid_signal_rate": 0.88},
        # Batch 7: Polluted political gossip spillover -> must be REJECTED by SQV-2!
        {"batch_id": 7, "platform": "ptt", "region": "local", "doc_count": 600, "batch_tokens": 8000, "cum_tokens_N": 35500, "cum_vocab_V": 8900, "valid_signal_rate": 0.38},
        # Batch 8: Clean diaspora + resource convergence batch (after rejecting Batch 7)
        {"batch_id": 8, "platform": "reddit", "region": "diaspora", "doc_count": 450, "batch_tokens": 6500, "cum_tokens_N": 34000, "cum_vocab_V": 6310, "valid_signal_rate": 0.90},
    ]
    with open(os.path.join(DATA_DIR, "corpus_batches.json"), "w", encoding="utf-8") as f:
        json.dump(batches, f, ensure_ascii=False, indent=2)

    # Write normalized SQLite database (with hashed IDs stored in clean relational tables)
    db_path = os.path.join(DATA_DIR, "taigi_network.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE nodes (
            node_hash TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            region TEXT NOT NULL,
            generation_tag TEXT NOT NULL,
            platform TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE interactions (
            edge_id TEXT PRIMARY KEY,
            source_hash TEXT NOT NULL,
            target_hash TEXT NOT NULL,
            platform TEXT NOT NULL,
            edge_type TEXT NOT NULL,
            weight REAL NOT NULL,
            sentiment INTEGER NOT NULL,
            slice_id TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE corpus_batches (
            batch_id INTEGER PRIMARY KEY,
            platform TEXT NOT NULL,
            region TEXT NOT NULL,
            doc_count INTEGER NOT NULL,
            batch_tokens INTEGER NOT NULL,
            cum_tokens_N INTEGER NOT NULL,
            cum_vocab_V INTEGER NOT NULL,
            valid_signal_rate REAL NOT NULL,
            accepted_flag INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE community_time_slices (
            community_id TEXT NOT NULL,
            start_time INTEGER NOT NULL,
            stop_time INTEGER NOT NULL,
            event INTEGER NOT NULL,
            clustering_avg REAL NOT NULL,
            hub_gini REAL NOT NULL,
            authority_gini REAL NOT NULL,
            mir_rule_ratio REAL NOT NULL,
            bridge_edge_ratio REAL NOT NULL,
            PRIMARY KEY (community_id, start_time)
        )
    """)

    for _, row in nodes_df.iterrows():
        cur.execute(
            "INSERT INTO nodes VALUES (?, ?, ?, ?, ?)",
            (row["node_hash"], row["node_type"], row["region"], row["generation_tag"], row["platform"]),
        )
    for _, row in edges_df.iterrows():
        cur.execute(
            "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (row["edge_id"], row["source_hash"], row["target_hash"], row["platform"], row["edge_type"],
             float(row["weight"]), int(row["sentiment"]), row["slice_id"], row["timestamp"]),
        )
    conn.commit()
    conn.close()
    return nodes_df, edges_df, batches, db_path


# ---------------------------------------------------------------------------
# 2. Sampling Quality Validation (SQV 1–4, G2)
# ---------------------------------------------------------------------------
def run_sampling_quality_validation(batches: list, db_path: str):
    clean_records = []
    cum_clean_tokens = 0
    cum_weighted_quality = 0.0
    prev_avg_q = None
    prev_clean_v = None

    batch_report = []
    for b in batches:
        btok = b["batch_tokens"]
        q = b["valid_signal_rate"]
        # Trial cumulative quality if this batch is included
        trial_tokens = cum_clean_tokens + btok
        trial_avg_q = (cum_weighted_quality + btok * q) / trial_tokens
        delta_q = 0.0 if prev_avg_q is None else (trial_avg_q - prev_avg_q)

        # SQV-2 Automatic Rejection Gate: reject if quality < 0.60 or negative marginal slope < -0.02
        accepted = not (q < 0.60 or (prev_avg_q is not None and delta_q < -0.02))

        if accepted:
            cum_clean_tokens = trial_tokens
            cum_weighted_quality += btok * q
            prev_avg_q = trial_avg_q
            vocab_gain = None if prev_clean_v is None else (b["cum_vocab_V"] - prev_clean_v) / prev_clean_v
            prev_clean_v = b["cum_vocab_V"]
            status = "ACCEPT"
            clean_records.append(b)
        else:
            vocab_gain = None
            status = "REJECT_BATCH"

        batch_report.append({
            "batch_id": b["batch_id"],
            "platform": b["platform"],
            "region": b["region"],
            "doc_count": b["doc_count"],
            "batch_tokens": btok,
            "cum_tokens_N": b["cum_tokens_N"],
            "cum_vocab_V": b["cum_vocab_V"],
            "valid_signal_rate": q,
            "trial_cum_avg_quality": round(trial_avg_q, 4),
            "marginal_snr_slope": round(delta_q, 4),
            "marginal_vocab_gain": None if vocab_gain is None else round(vocab_gain, 4),
            "status": status,
        })

    # Write batch status to SQLite
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for b, rep in zip(batches, batch_report):
        cur.execute(
            "INSERT INTO corpus_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (b["batch_id"], b["platform"], b["region"], b["doc_count"], b["batch_tokens"],
             b["cum_tokens_N"], b["cum_vocab_V"], b["valid_signal_rate"], 1 if rep["status"] == "ACCEPT" else 0),
        )
    conn.commit()
    conn.close()

    # SQV-1 Heaps' Law log-log regression on accepted batches: ln(V) = ln(K) + beta * ln(N)
    accept_df = pd.DataFrame([r for r in batch_report if r["status"] == "ACCEPT"])
    log_n = np.log(accept_df["cum_tokens_N"].to_numpy(dtype=float))
    log_v = np.log(accept_df["cum_vocab_V"].to_numpy(dtype=float))
    beta, log_k = np.polyfit(log_n, log_v, 1)
    pred_log_v = log_k + beta * log_n
    ss_res = np.sum((log_v - pred_log_v) ** 2)
    ss_tot = np.sum((log_v - np.mean(log_v)) ** 2)
    r2 = float(1.0 - ss_res / ss_tot)

    last3_gains = accept_df["marginal_vocab_gain"].dropna().tail(3).to_numpy(dtype=float)
    # Check convergence of final accepted batches (< 5% growth in final accepted batch)
    final_vocab_gain = float(last3_gains[-1])

    # SQV-3 Shannon Entropy on accepted batches
    plat_counts = accept_df.groupby("platform")["doc_count"].sum().to_dict()
    reg_counts = accept_df.groupby("region")["doc_count"].sum().to_dict()
    h_platform = shannon_entropy_normalized(plat_counts)
    h_region = shannon_entropy_normalized(reg_counts)

    report_df = pd.DataFrame(batch_report)
    report_df.to_csv(os.path.join(OUT_DIR, "01_sampling_quality_batches.csv"), index=False, encoding="utf-8")

    sqv_metrics = {
        "heaps_beta": round(float(beta), 4),
        "heaps_K": round(float(math.exp(log_k)), 4),
        "heaps_r2": round(r2, 4),
        "final_accepted_vocab_gain": round(final_vocab_gain, 4),
        "rejected_batches": [r["batch_id"] for r in batch_report if r["status"] == "REJECT_BATCH"],
        "shannon_entropy_platform": round(h_platform, 4),
        "shannon_entropy_region": round(h_region, 4),
    }
    return report_df, sqv_metrics


# ---------------------------------------------------------------------------
# 3. Graph Algorithms Implemented Directly with NumPy (Zero Missing Deps)
# ---------------------------------------------------------------------------
def compute_hits_matrix(M: np.ndarray, max_iter: int = 500, tol: float = 1e-10):
    """Easley & Kleinberg Ch 14.2 & 14.6A: a <- M^T h, h <- M a with L1 normalization."""
    n = M.shape[0]
    if n == 0 or M.sum() == 0:
        return np.zeros(n), np.zeros(n)
    h = np.ones(n, dtype=float)
    a = np.ones(n, dtype=float)
    for _ in range(max_iter):
        a_new = M.T @ h
        if a_new.sum() > 0:
            a_new /= a_new.sum()
        h_new = M @ a_new
        if h_new.sum() > 0:
            h_new /= h_new.sum()
        diff = np.abs(a_new - a).sum() + np.abs(h_new - h).sum()
        a, h = a_new, h_new
        if diff < tol:
            break
    return a, h


def compute_hits_eigh_exact(M: np.ndarray):
    """Exact spectral solution via symmetric matrices M^T M and M M^T (Ch 14.6A)."""
    mtm = np.einsum("ki,kj->ij", M, M)
    mmt = np.einsum("ik,jk->ij", M, M)
    vals_a, vecs_a = np.linalg.eigh(mtm)
    vals_h, vecs_h = np.linalg.eigh(mmt)
    a_eig = np.abs(vecs_a[:, np.argmax(vals_a)])
    h_eig = np.abs(vecs_h[:, np.argmax(vals_h)])
    if a_eig.sum() > 0:
        a_eig /= a_eig.sum()
    if h_eig.sum() > 0:
        h_eig /= h_eig.sum()
    return a_eig, h_eig


def compute_scaled_pagerank(M: np.ndarray, s: float = 0.85, max_iter: int = 500, tol: float = 1e-10):
    """Scaled PageRank (Ch 14.3, p. 361-363)."""
    n = M.shape[0]
    if n == 0:
        return np.zeros(n)
    row_sums = M.sum(axis=1)
    dangling = (row_sums == 0)
    P = np.zeros_like(M, dtype=float)
    non_dangling = ~dangling
    P[non_dangling] = M[non_dangling] / row_sums[non_dangling, None]

    p = np.ones(n, dtype=float) / n
    for _ in range(max_iter):
        dangling_mass = p[dangling].sum()
        p_new = s * (P.T @ p + dangling_mass / n) + (1.0 - s) / n
        if np.abs(p_new - p).sum() < tol:
            p = p_new
            break
        p = p_new
    return p


def brandes_betweenness_undirected(adj: list):
    """Exact Brandes (2001) [77] algorithm for normalized undirected betweenness centrality."""
    n = len(adj)
    cb = np.zeros(n, dtype=float)
    for s in range(n):
        stack = []
        pred = [[] for _ in range(n)]
        sigma = np.zeros(n, dtype=float)
        sigma[s] = 1.0
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            stack.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    q.append(w)
                    dist[w] = dist[v] + 1
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = np.zeros(n, dtype=float)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    # Undirected graph: divide by 2, and normalize by (n-1)(n-2)/2
    cb /= 2.0
    if n > 2:
        cb /= ((n - 1) * (n - 2) / 2.0)
    return cb


def clustering_metrics_undirected(adj_sets: list):
    """Compute local clustering coefficients and global transitivity (Ch 3.1)."""
    n = len(adj_sets)
    local_c = np.zeros(n, dtype=float)
    triangles_times_2 = 0
    triads = 0
    for u in range(n):
        nbrs = list(adj_sets[u])
        k = len(nbrs)
        if k < 2:
            continue
        triads += k * (k - 1) // 2
        links = 0
        for i in range(k):
            for j in range(i + 1, k):
                if nbrs[j] in adj_sets[nbrs[i]]:
                    links += 1
        local_c[u] = links / (k * (k - 1) / 2.0)
        triangles_times_2 += links
    global_transitivity = (triangles_times_2 / triads) if triads > 0 else 0.0
    return local_c, float(global_transitivity)


def build_adjacency_matrix(node_list: list, edges_df: pd.DataFrame):
    idx = {nid: i for i, nid in enumerate(node_list)}
    n = len(node_list)
    M = np.zeros((n, n), dtype=float)
    for _, row in edges_df.iterrows():
        u, v = row["source_id"], row["target_id"]
        if u in idx and v in idx and u != v:
            M[idx[u], idx[v]] += float(row["weight"])
    return M


def analyze_network(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, min_weight: float = 2.0):
    node_list = nodes_df["node_id"].tolist()
    node_meta = nodes_df.set_index("node_id").to_dict("index")

    # ALG-1: Signed network filtering (sentiment > 0) + min_weight threshold tau >= 2.0
    pos_df = edges_df[(edges_df["sentiment"] > 0)].copy()
    agg_pos = pos_df.groupby(["source_id", "target_id"], as_index=False)["weight"].sum()
    filtered_pos = agg_pos[agg_pos["weight"] >= min_weight]

    M_signed = build_adjacency_matrix(node_list, filtered_pos)
    a_signed, h_signed = compute_hits_matrix(M_signed)
    pagerank = compute_scaled_pagerank(M_signed, s=0.85)

    # Unsigned baseline (includes sentiment = -1 and noise weight=1 for AV-3 ablation)
    agg_all = edges_df.groupby(["source_id", "target_id"], as_index=False)["weight"].sum()
    M_unsigned = build_adjacency_matrix(node_list, agg_all)
    a_unsigned, _ = compute_hits_matrix(M_unsigned)

    # Undirected projection for Betweenness & Clustering
    n = len(node_list)
    adj_sets = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if M_signed[i, j] > 0 or M_signed[j, i] > 0:
                adj_sets[i].add(j)
                adj_sets[j].add(i)
    adj_list = [sorted(s) for s in adj_sets]
    betweenness = brandes_betweenness_undirected(adj_list)
    local_clust, global_transitivity = clustering_metrics_undirected(adj_sets)

    in_deg = M_signed.sum(axis=0)
    out_deg = M_signed.sum(axis=1)
    max_in = float(in_deg.max()) if in_deg.max() > 0 else 1.0
    max_h = float(h_signed.max()) if h_signed.max() > 0 else 1.0
    max_b = float(betweenness.max()) if betweenness.max() > 0 else 1.0

    # ALG-3: BridgeHub & InvisibleLinkScore
    rows = []
    for i, nid in enumerate(node_list):
        s_local = 0.0
        s_diaspora = 0.0
        s_resource = 0.0
        for j, tgt_id in enumerate(node_list):
            if M_signed[i, j] > 0:
                contrib = M_signed[i, j] * a_signed[j]
                reg = node_meta[tgt_id]["region"]
                if reg == "local":
                    s_local += contrib
                elif reg == "diaspora":
                    s_diaspora += contrib
                else:
                    s_resource += contrib

        bridge_ld = math.sqrt(s_local * s_diaspora)
        flows = [s_local, s_diaspora, s_resource]
        total_flow = sum(flows)
        if total_flow > 0:
            probs = [f / total_flow for f in flows if f > 0]
            hub_div = -sum(p * math.log(p) for p in probs) / math.log(3.0)
        else:
            hub_div = 0.0

        inv_link = ((h_signed[i] / max_h) * (betweenness[i] / max_b)) / (1.0 + in_deg[i] / max_in)

        rows.append({
            "node_id": nid,
            "node_hash": node_meta[nid]["node_hash"],
            "display_label": node_meta[nid]["display_label"],
            "region": node_meta[nid]["region"],
            "platform": node_meta[nid]["platform"],
            "generation_tag": node_meta[nid]["generation_tag"],
            "in_degree_signed": round(float(in_deg[i]), 2),
            "out_degree_signed": round(float(out_deg[i]), 2),
            "authority_signed": round(float(a_signed[i]), 6),
            "authority_unsigned_ablation": round(float(a_unsigned[i]), 6),
            "hub_signed": round(float(h_signed[i]), 6),
            "pagerank": round(float(pagerank[i]), 6),
            "betweenness": round(float(betweenness[i]), 6),
            "local_clustering": round(float(local_clust[i]), 4),
            "flow_to_local": round(s_local, 4),
            "flow_to_diaspora": round(s_diaspora, 4),
            "bridge_hub_score": round(bridge_ld, 6),
            "hub_diversity": round(hub_div, 4),
            "invisible_link_score": round(inv_link, 6),
        })

    df = pd.DataFrame(rows)
    a_pos = df.loc[df["authority_signed"] > 0, "authority_signed"]
    h_pos = df.loc[df["hub_signed"] > 0, "hub_signed"]
    theta_a = float(a_pos.quantile(0.65)) if len(a_pos) else 0.0
    theta_h = float(h_pos.quantile(0.65)) if len(h_pos) else 0.0

    def role_label(r):
        is_a = r["authority_signed"] >= theta_a and r["authority_signed"] > 0
        is_h = r["hub_signed"] >= theta_h and r["hub_signed"] > 0
        if is_a and is_h:
            return "Q1_Dual_Leader"
        if is_a:
            return "Q2_Core_Authority"
        if is_h:
            return "Q4_Pure_Hub_Curator"
        return "Q3_Periphery_or_Filtered"

    df["role_quadrant"] = df.apply(role_label, axis=1)
    df = df.sort_values(["authority_signed", "hub_signed", "bridge_hub_score"], ascending=False)
    df.to_csv(os.path.join(OUT_DIR, "02_node_hits_and_bridging_metrics.csv"), index=False, encoding="utf-8")
    return df, M_signed, M_unsigned, a_signed, h_signed, global_transitivity


# ---------------------------------------------------------------------------
# 4. Ch 19.7B Bilingual Diffusion & Buffer Zone Simulator (ALG-5, G4)
# ---------------------------------------------------------------------------
def simulate_bilingual_path(n_nodes: int = 40, seed_len: int = 5, a: float = 1.5, b: float = 1.0, c: float = 0.8, steps: int = 80):
    """
    Exact Easley & Kleinberg Ch 19.7B (pp. 526-531) 1D path coordination simulator
    with strategies {A (Mandarin/Global), B (Taigi), AB (Bilingual)} and cost c.
    """
    states = ["B"] * n_nodes
    for i in range(seed_len):
        states[i] = "A"

    def edge_payoff(s1: str, s2: str) -> float:
        shared_a = ("A" in s1) and ("A" in s2)
        shared_b = ("B" in s1) and ("B" in s2)
        if shared_a and shared_b:
            return max(a, b)
        if shared_a:
            return a
        if shared_b:
            return b
        return 0.0

    for _ in range(steps):
        new_states = states.copy()
        for i in range(seed_len, n_nodes):
            nbrs = [j for j in (i - 1, i + 1) if 0 <= j < n_nodes]
            best_s = states[i]
            best_u = -1e9
            # Tie-breaking keeps current strategy if strictly not improved, else A > AB > B
            for cand in ["B", "AB", "A"]:
                u = sum(edge_payoff(cand, states[j]) for j in nbrs) - (c if cand == "AB" else 0.0)
                if u > best_u + 1e-12:
                    best_u = u
                    best_s = cand
            new_states[i] = best_s
        if new_states == states:
            break
        states = new_states

    non_seed = states[seed_len:]
    total_ns = len(non_seed)
    f_a = non_seed.count("A") / total_ns
    f_b = non_seed.count("B") / total_ns
    f_ab = non_seed.count("AB") / total_ns

    if f_b > 0 and f_ab > 0:
        regime = "Bilingual_Buffer_B_Survives"
    elif f_b > 0 and f_ab == 0:
        regime = "B_Maintained"
    elif f_b == 0 and f_ab == 0 and c < a - b + 1e-9:
        regime = "Infiltration_B_Extinct"
    else:
        regime = "Direct_Conquest"

    return {
        "a_payoff_global": a,
        "b_payoff_taigi": b,
        "c_bilingual_cost": c,
        "f_A": round(f_a, 4),
        "f_B": round(f_b, 4),
        "f_AB": round(f_ab, 4),
        "regime": regime,
    }


def run_bilingual_simulations():
    configs = [
        (1.5, 1.0, 0.1),
        (1.5, 1.0, 0.3),  # Infiltration (vestigial B eliminated via AB wave)
        (1.5, 1.0, 0.6),
        (1.5, 1.0, 0.8),  # Bilingual Buffer Zone (triangular cutout!)
        (1.5, 1.0, 0.95),
        (1.5, 1.0, 1.2),  # Direct Conquest
        (1.5, 1.0, 1.5),  # Direct Conquest
        (2.2, 1.0, 0.8),  # High global payoff a > 2 breaks buffer -> A cascade
    ]
    sim_rows = [simulate_bilingual_path(a=a, b=b, c=c) for a, b, c in configs]
    sim_df = pd.DataFrame(sim_rows)
    sim_df.to_csv(os.path.join(OUT_DIR, "03_bilingual_cascade_simulation.csv"), index=False, encoding="utf-8")
    return sim_df


# ---------------------------------------------------------------------------
# 5. Time-Slicing & Survival Analysis Long Format (ALG-6, G5)
# ---------------------------------------------------------------------------
def build_survival_counting_process(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, db_path: str):
    node_list = nodes_df["node_id"].tolist()
    node_reg = nodes_df.set_index("node_id")["region"].to_dict()
    slices = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]

    records = []
    # Community 1: Active Cross-Border Taigi Community (cumulative evolving network up to slice t)
    for t_idx, sid in enumerate(slices):
        sub_edges = edges_df[(edges_df["slice_id"].isin(slices[: t_idx + 1])) & (edges_df["sentiment"] > 0)]
        agg = sub_edges.groupby(["source_id", "target_id"], as_index=False)["weight"].sum()
        M = build_adjacency_matrix(node_list, agg[agg["weight"] >= 2.0])
        a_vec, h_vec = compute_hits_matrix(M)

        n = len(node_list)
        adj_sets = [set() for _ in range(n)]
        bridge_edges = 0
        total_edges = 0
        for i in range(n):
            for j in range(n):
                if M[i, j] > 0:
                    total_edges += 1
                    if node_reg[node_list[i]] != node_reg[node_list[j]]:
                        bridge_edges += 1
                    adj_sets[i].add(j)
                    adj_sets[j].add(i)
        _, c_glob = clustering_metrics_undirected(adj_sets)
        conflict_cnt = len(edges_df[(edges_df["slice_id"] == sid) & (edges_df["sentiment"] < 0)])
        pos_cnt = max(1, len(edges_df[(edges_df["slice_id"] == sid) & (edges_df["sentiment"] > 0)]))

        records.append({
            "community_id": "taigi_active_crossborder",
            "slice_id": sid,
            "start_time": t_idx,
            "stop_time": t_idx + 1,
            "event": 0,  # Right-censored: still active
            "clustering_avg": round(c_glob, 4),
            "hub_gini": round(gini_coefficient(h_vec), 4),
            "authority_gini": round(gini_coefficient(a_vec), 4),
            "mir_rule_ratio": round(conflict_cnt / pos_cnt, 4),
            "bridge_edge_ratio": round(bridge_edges / max(1, total_edges), 4),
        })

    # Community 2: Control Dialect Community (rising clustering + rising Gini monopoly + zero bridge -> event=1 at Q8)
    aging_trajectory = [
        (0.32, 0.58, 0.60, 0.08, 0.06, 0),
        (0.38, 0.63, 0.64, 0.12, 0.05, 0),
        (0.45, 0.69, 0.68, 0.18, 0.03, 0),
        (0.52, 0.74, 0.73, 0.25, 0.02, 0),
        (0.61, 0.80, 0.78, 0.34, 0.01, 0),
        (0.68, 0.85, 0.83, 0.42, 0.00, 0),
        (0.75, 0.90, 0.88, 0.55, 0.00, 0),
        (0.82, 0.94, 0.92, 0.68, 0.00, 1),  # Collapsed / dormant at stop_time=8
    ]
    for t_idx, (c_avg, hg, ag, mir, br, ev) in enumerate(aging_trajectory):
        records.append({
            "community_id": "dialect_aging_control",
            "slice_id": slices[t_idx],
            "start_time": t_idx,
            "stop_time": t_idx + 1,
            "event": ev,
            "clustering_avg": c_avg,
            "hub_gini": hg,
            "authority_gini": ag,
            "mir_rule_ratio": mir,
            "bridge_edge_ratio": br,
        })

    surv_df = pd.DataFrame(records)
    # Forward-fill missing values per community & Z-score normalize covariates (PDF p. 28)
    cov_cols = ["clustering_avg", "hub_gini", "authority_gini", "mir_rule_ratio", "bridge_edge_ratio"]
    surv_df[cov_cols] = surv_df.groupby("community_id")[cov_cols].ffill()
    for col in cov_cols:
        std_val = surv_df[col].std(ddof=0)
        surv_df[f"z_{col}"] = (surv_df[col] - surv_df[col].mean()) / (std_val if std_val > 0 else 1.0)

    # Persist to SQLite community_time_slices
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for _, r in surv_df.iterrows():
        cur.execute(
            "INSERT INTO community_time_slices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (r["community_id"], int(r["start_time"]), int(r["stop_time"]), int(r["event"]),
             float(r["clustering_avg"]), float(r["hub_gini"]), float(r["authority_gini"]),
             float(r["mir_rule_ratio"]), float(r["bridge_edge_ratio"])),
        )
    conn.commit()
    conn.close()

    surv_df.to_csv(os.path.join(OUT_DIR, "04_survival_counting_process.csv"), index=False, encoding="utf-8")
    return surv_df


# ---------------------------------------------------------------------------
# 5B. Graph Theory & Strong/Weak Ties Analysis (Ch 2 & Ch 3, G6)
# ---------------------------------------------------------------------------
def bfs_components_and_distance(adj_sets: list, active_nodes: list, src: int = None, dst: int = None):
    """BFS helper for connected components (Ch 2.2) and shortest-path distance (Ch 2.3)."""
    if src is not None and dst is not None:
        if src == dst:
            return 0
        visited = {src}
        q = deque([(src, 0)])
        while q:
            u, d = q.popleft()
            for v in adj_sets[u]:
                if v == dst:
                    return d + 1
                if v not in visited:
                    visited.add(v)
                    q.append((v, d + 1))
        return -1  # Unreachable (disconnected)

    visited = set()
    comps = []
    for start in active_nodes:
        if start in visited:
            continue
        comp = []
        q = deque([start])
        visited.add(start)
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj_sets[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        comps.append(comp)
    return comps


def analyze_edge_ties_and_bridges(nodes_df: pd.DataFrame, M_signed: np.ndarray):
    """
    Ch 3.2-3.5 Edge-level Graph Theory metrics:
      - Strong vs. Weak Tie classification (weight >= median -> Strong, else Weak)
      - Embeddedness e_uv = |N(u) ∩ N(v)|
      - Neighborhood Overlap O_uv = |N(u) ∩ N(v)| / |(N(u) ∪ N(v)) \ {u, v}| (Eq. 3.1)
      - Span without edge (BFS shortest path after deleting edge) & Local Bridge detection
    """
    node_list = nodes_df["node_id"].tolist()
    node_meta = nodes_df.set_index("node_id").to_dict("index")
    n = len(node_list)

    adj_sets = [set() for _ in range(n)]
    undir_edges = []
    for i in range(n):
        for j in range(i + 1, n):
            w = float(M_signed[i, j] + M_signed[j, i])
            if w > 0:
                adj_sets[i].add(j)
                adj_sets[j].add(i)
                undir_edges.append((i, j, w))

    weights = [e[2] for e in undir_edges]
    w_median = float(np.median(weights)) if weights else 0.0

    edge_records = []
    for i, j, w in undir_edges:
        ni = adj_sets[i]
        nj = adj_sets[j]
        common = ni & nj
        union_excl = (ni | nj) - {i, j}
        emb = len(common)
        overlap = (emb / len(union_excl)) if len(union_excl) > 0 else 0.0

        # Temporarily remove (i, j) to compute Span via BFS
        adj_sets[i].remove(j)
        adj_sets[j].remove(i)
        span = bfs_components_and_distance(adj_sets, [], src=i, dst=j)
        adj_sets[i].add(j)
        adj_sets[j].add(i)

        u_id, v_id = node_list[i], node_list[j]
        reg_u, reg_v = node_meta[u_id]["region"], node_meta[v_id]["region"]
        tie_class = "Strong_Tie" if w >= w_median else "Weak_Tie"
        is_cross_ld = {reg_u, reg_v} == {"local", "diaspora"}

        edge_records.append({
            "u_idx": i,
            "v_idx": j,
            "u_id": u_id,
            "v_id": v_id,
            "u_label": node_meta[u_id]["display_label"],
            "v_label": node_meta[v_id]["display_label"],
            "u_region": reg_u,
            "v_region": reg_v,
            "is_cross_region": reg_u != reg_v,
            "is_cross_local_diaspora": is_cross_ld,
            "undirected_weight": round(w, 2),
            "tie_class": tie_class,
            "embeddedness": emb,
            "neighborhood_overlap": round(overlap, 4),
            "span_without_edge": span,
            "is_bridge": (span == -1),
            "is_local_bridge": (emb == 0),
        })

    edge_df = pd.DataFrame(edge_records).sort_values(
        ["neighborhood_overlap", "undirected_weight"], ascending=[True, True]
    )
    edge_df.drop(columns=["u_idx", "v_idx"]).to_csv(
        os.path.join(OUT_DIR, "06_edge_ties_and_bridges.csv"), index=False, encoding="utf-8"
    )
    return edge_df, adj_sets


def simulate_tie_removal_percolation(nodes_df: pd.DataFrame, edge_df: pd.DataFrame):
    """
    Reproduce Ch 3.3 (p. 53) Onnela et al. [334] Giant Component Percolation Test:
      Compare removing Strong / High-Overlap Ties first vs. Weak / Low-Overlap Local Bridges first.
    """
    node_list = nodes_df["node_id"].tolist()
    node_reg = nodes_df.set_index("node_id")["region"].to_dict()
    active_nodes = sorted(set(edge_df["u_idx"]).union(set(edge_df["v_idx"])))
    local_idx = {i for i in active_nodes if node_reg[node_list[i]] == "local"}
    diaspora_idx = {i for i in active_nodes if node_reg[node_list[i]] == "diaspora"}
    n_total = len(node_list)
    n_active = len(active_nodes)
    total_edges = len(edge_df)

    # Order A: Strongest & highest neighborhood overlap first
    order_strong = edge_df.sort_values(
        ["undirected_weight", "neighborhood_overlap"], ascending=[False, False]
    )[["u_idx", "v_idx"]].to_records(index=False).tolist()

    # Order B: Weakest & lowest neighborhood overlap (local bridges) first
    order_weak = edge_df.sort_values(
        ["neighborhood_overlap", "undirected_weight"], ascending=[True, True]
    )[["u_idx", "v_idx"]].to_records(index=False).tolist()

    perc_rows = []
    for strategy_name, removal_order in [
        ("Remove_Strong_HighOverlap_First", order_strong),
        ("Remove_Weak_LowOverlap_First", order_weak),
    ]:
        adj = [set() for _ in range(n_total)]
        for u, v in removal_order:
            adj[u].add(v)
            adj[v].add(u)

        for k in range(total_edges + 1):
            if k > 0:
                u_rem, v_rem = removal_order[k - 1]
                adj[u_rem].discard(v_rem)
                adj[v_rem].discard(u_rem)

            comps = bfs_components_and_distance(adj, active_nodes)
            max_comp = max((len(c) for c in comps), default=0)
            ld_connected = any(bool(set(c) & local_idx) and bool(set(c) & diaspora_idx) for c in comps)

            perc_rows.append({
                "strategy": strategy_name,
                "edges_removed_k": k,
                "edges_removed_frac": round(k / max(1, total_edges), 4),
                "num_components": len(comps),
                "giant_component_size": max_comp,
                "giant_component_fraction": round(max_comp / max(1, n_active), 4),
                "local_diaspora_connected": ld_connected,
            })

    perc_df = pd.DataFrame(perc_rows)
    perc_df.to_csv(os.path.join(OUT_DIR, "07_tie_removal_percolation.csv"), index=False, encoding="utf-8")
    return perc_df


# ---------------------------------------------------------------------------
# 6. Automated Acceptance Verification Suite (Gates G1–G6)
# ---------------------------------------------------------------------------
def verify_gates(nodes_df, edges_df, db_path, sqv_metrics, metrics_df, M_signed, a_signed, h_signed, sim_df, surv_df, edge_tie_df, perc_df):
    results = {}

    # --- G1: Data & PII Compliance ---
    conn = sqlite3.connect(db_path)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    node_hashes = [r[0] for r in conn.execute("SELECT node_hash FROM nodes").fetchall()]
    conn.close()
    pii_all_hex16 = all(len(x) == 16 and all(c in "0123456789abcdef" for c in x) for x in node_hashes)
    g1_pass = (
        {"nodes", "interactions", "corpus_batches", "community_time_slices"}.issubset(tables)
        and edges_df["platform"].nunique() >= 4
        and nodes_df["region"].nunique() == 3
        and pii_all_hex16
    )
    results["G1_data_and_privacy_compliance"] = {
        "passed": bool(g1_pass),
        "platforms_count": int(edges_df["platform"].nunique()),
        "regions_count": int(nodes_df["region"].nunique()),
        "pii_masked_count": len(node_hashes),
        "sqlite_tables": sorted(tables),
    }

    # --- G2: Sampling Quality Validation ---
    g2_pass = (
        0.35 <= sqv_metrics["heaps_beta"] <= 0.65
        and sqv_metrics["heaps_r2"] >= 0.90
        and sqv_metrics["final_accepted_vocab_gain"] < 0.05
        and 7 in sqv_metrics["rejected_batches"]
        and sqv_metrics["shannon_entropy_platform"] >= 0.75
        and sqv_metrics["shannon_entropy_region"] >= 0.75
    )
    results["G2_sampling_quality_validation"] = {
        "passed": bool(g2_pass),
        **sqv_metrics,
    }

    # --- G3: AV-1 (Textbook Newspapers + Eigh) & AV-3 (Signed Ablation) & AV-4 (Perturbation) ---
    # AV-1A: Textbook Fig. 14.1-14.5 "newspapers" 9x7 bipartite matrix (pp. 354-358)
    B_news = np.array([
        [1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1],
    ], dtype=float)
    votes = B_news.sum(axis=0)
    list_scores = B_news @ votes
    reweighted = B_news.T @ list_scores
    M_news = np.zeros((16, 16), dtype=float)
    M_news[:9, 9:] = B_news
    a_news_full, _ = compute_hits_matrix(M_news)
    a_news = a_news_full[9:]
    fig_14_5_expected = np.array([0.199, 0.199, 0.304, 0.205, 0.043, 0.042, 0.008])
    news_l1_diff = float(np.abs(a_news - fig_14_5_expected).sum())

    # AV-1B: Spectral eigenvector check on Taigi M_signed
    a_eigh, h_eigh = compute_hits_eigh_exact(M_signed)
    spec_l1_err = float(np.abs(a_signed - a_eigh).sum() + np.abs(h_signed - h_eigh).sum())

    # AV-3: Signed ablation on noise_troll_baiter
    troll_row = metrics_df[metrics_df["node_id"] == "noise_troll_baiter"].iloc[0]
    troll_auth_unsigned = float(troll_row["authority_unsigned_ablation"])
    troll_auth_signed = float(troll_row["authority_signed"])

    # AV-4: Perturbation stability (20 trials, +-15% weight perturbation)
    rng = np.random.default_rng(42)
    rho_auth_list, rho_hub_list = [], []
    for _ in range(20):
        noise = rng.uniform(0.85, 1.15, size=M_signed.shape)
        M_pert = M_signed * noise
        a_p, h_p = compute_hits_matrix(M_pert)
        rho_auth_list.append(spearman_rank_corr(a_signed, a_p))
        rho_hub_list.append(spearman_rank_corr(h_signed, h_p))
    mean_rho_auth = float(np.mean(rho_auth_list))
    mean_rho_hub = float(np.mean(rho_hub_list))

    g3_pass = (
        np.array_equal(reweighted.astype(int), np.array([19, 19, 31, 24, 5, 15, 12]))
        and news_l1_diff < 0.005
        and spec_l1_err < 1e-6
        and troll_auth_unsigned > 0.05
        and troll_auth_signed == 0.0
        and mean_rho_auth >= 0.90
        and mean_rho_hub >= 0.90
    )
    results["G3_hits_and_ablation_verification"] = {
        "passed": bool(g3_pass),
        "textbook_newspapers_reweighted_match": reweighted.astype(int).tolist(),
        "textbook_newspapers_limit_auth": [round(float(x), 3) for x in a_news],
        "textbook_newspapers_l1_diff": round(news_l1_diff, 6),
        "spectral_eigenvector_l1_error": spec_l1_err,
        "ablation_troll_auth_unsigned": round(troll_auth_unsigned, 6),
        "ablation_troll_auth_signed": round(troll_auth_signed, 6),
        "perturbation_mean_spearman_auth": round(mean_rho_auth, 4),
        "perturbation_mean_spearman_hub": round(mean_rho_hub, 4),
    }

    # --- G4: BridgeHub Ground-Truth Recovery & Ch 19.7B Phase Diagram ---
    top5_auth = metrics_df.sort_values("authority_signed", ascending=False).head(5)
    top5_all_valid_auth = bool(top5_auth["region"].isin(["resource", "local", "diaspora"]).all() and not top5_auth["node_id"].str.startswith("noise_").any())

    bridge_nodes = metrics_df[metrics_df["node_id"].isin(["hub_bridge_student", "hub_bridge_curator", "hub_bridge_yt_mod"])]
    single_side_hubs = metrics_df[metrics_df["node_id"].isin(["hub_local_ptt_1", "hub_local_yt_2", "hub_diaspora_1", "hub_diaspora_2"])]
    min_bridge_score = float(bridge_nodes["bridge_hub_score"].min())
    max_single_bridge = float(single_side_hubs["bridge_hub_score"].max())
    min_inv_bridge = float(bridge_nodes["invisible_link_score"].min())
    max_inv_single = float(single_side_hubs["invisible_link_score"].max())

    # Bilingual phase check
    r_infil = sim_df[sim_df["c_bilingual_cost"] == 0.3].iloc[0]
    r_buf = sim_df[sim_df["c_bilingual_cost"] == 0.8].iloc[0]
    r_conq = sim_df[sim_df["c_bilingual_cost"] == 1.5].iloc[0]

    g4_pass = (
        top5_all_valid_auth
        and min_bridge_score > 0.0
        and max_single_bridge == 0.0
        and min_inv_bridge > max_inv_single
        and r_infil["regime"] == "Infiltration_B_Extinct" and r_infil["f_B"] == 0.0
        and r_buf["regime"] == "Bilingual_Buffer_B_Survives" and r_buf["f_B"] > 0.0 and r_buf["f_AB"] > 0.0
        and r_conq["regime"] == "Direct_Conquest" and r_conq["f_B"] == 0.0 and r_conq["f_AB"] == 0.0
    )
    results["G4_bridgehub_and_bilingual_diffusion"] = {
        "passed": bool(g4_pass),
        "top5_authorities": top5_auth["node_id"].tolist(),
        "min_bridgehub_crossborder": round(min_bridge_score, 6),
        "max_bridgehub_single_side": round(max_single_bridge, 6),
        "min_invisible_link_crossborder": round(min_inv_bridge, 6),
        "max_invisible_link_single_side": round(max_inv_single, 6),
        "ch19_c03_regime": r_infil["regime"],
        "ch19_c08_regime": r_buf["regime"],
        "ch19_c15_regime": r_conq["regime"],
    }

    # --- G5: Time-Slicing & Survival Format ---
    nan_count = int(surv_df.isna().sum().sum())
    z_mean = float(surv_df["z_hub_gini"].mean())
    z_std = float(surv_df["z_hub_gini"].std(ddof=0))
    g5_pass = (
        len(surv_df) >= 8
        and surv_df["community_id"].nunique() == 2
        and nan_count == 0
        and abs(z_mean) < 1e-9
        and abs(z_std - 1.0) < 1e-6
    )
    results["G5_time_slicing_and_survival_format"] = {
        "passed": bool(g5_pass),
        "rows_count": len(surv_df),
        "communities": surv_df["community_id"].unique().tolist(),
        "nan_count": nan_count,
        "z_hub_gini_mean": round(z_mean, 8),
        "z_hub_gini_std": round(z_std, 6),
    }

    # --- G6: Graph Theory & Strong/Weak Ties Verification (Ch 2 & Ch 3) ---
    local_bridge_cnt = int(edge_tie_df["is_local_bridge"].sum())
    cross_ld_overlap = float(edge_tie_df.loc[edge_tie_df["is_cross_local_diaspora"], "neighborhood_overlap"].mean())
    non_cross_ld_overlap = float(edge_tie_df.loc[~edge_tie_df["is_cross_local_diaspora"], "neighborhood_overlap"].mean())
    strong_overlap = float(edge_tie_df.loc[edge_tie_df["tie_class"] == "Strong_Tie", "neighborhood_overlap"].mean())
    weak_overlap = float(edge_tie_df.loc[edge_tie_df["tie_class"] == "Weak_Tie", "neighborhood_overlap"].mean())

    p_strong = perc_df[perc_df["strategy"] == "Remove_Strong_HighOverlap_First"]
    p_weak = perc_df[perc_df["strategy"] == "Remove_Weak_LowOverlap_First"]
    auc_strong = float(p_strong["giant_component_fraction"].mean())
    auc_weak = float(p_weak["giant_component_fraction"].mean())

    disc_strong = p_strong.loc[~p_strong["local_diaspora_connected"], "edges_removed_k"].min()
    disc_weak = p_weak.loc[~p_weak["local_diaspora_connected"], "edges_removed_k"].min()

    g6_pass = (
        len(edge_tie_df) > 0
        and local_bridge_cnt >= 1
        and non_cross_ld_overlap > cross_ld_overlap
        and strong_overlap > weak_overlap
        and auc_weak < auc_strong
        and int(disc_weak) < int(disc_strong)
    )
    results["G6_graph_theory_and_strong_weak_ties"] = {
        "passed": bool(g6_pass),
        "undirected_edges_count": len(edge_tie_df),
        "strong_ties_count": int((edge_tie_df["tie_class"] == "Strong_Tie").sum()),
        "weak_ties_count": int((edge_tie_df["tie_class"] == "Weak_Tie").sum()),
        "local_bridges_count": local_bridge_cnt,
        "mean_overlap_strong_ties": round(strong_overlap, 4),
        "mean_overlap_weak_ties": round(weak_overlap, 4),
        "mean_overlap_non_cross_border": round(non_cross_ld_overlap, 4),
        "mean_overlap_cross_local_diaspora": round(cross_ld_overlap, 4),
        "percolation_auc_giant_strong_first": round(auc_strong, 4),
        "percolation_auc_giant_weak_first": round(auc_weak, 4),
        "local_diaspora_disconnect_k_strong_first": int(disc_strong),
        "local_diaspora_disconnect_k_weak_first": int(disc_weak),
    }

    overall = all(v["passed"] for v in results.values())
    final_report = {
        "overall_status": "PASS" if overall else "FAIL",
        "gates": results,
    }
    with open(os.path.join(OUT_DIR, "05_acceptance_verification_report.json"), "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    return final_report


# ---------------------------------------------------------------------------
# 7. High-Resolution Visualizations (Network Relationship Graph + Scatter Plots)
# ---------------------------------------------------------------------------
def generate_visualizations(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    edge_tie_df: pd.DataFrame,
    perc_df: pd.DataFrame,
    batch_report_df: pd.DataFrame,
    sqv_metrics: dict,
    surv_df: pd.DataFrame,
):
    os.makedirs(FIG_DIR, exist_ok=True)
    m_map = metrics_df.set_index("node_id").to_dict("index")
    tie_lookup = {}
    for _, r in edge_tie_df.iterrows():
        tie_lookup[(r["u_id"], r["v_id"])] = r
        tie_lookup[(r["v_id"], r["u_id"])] = r

    # =========================================================================
    # Fig 1: Explicit Multi-Zone Network Relationship Graph
    # =========================================================================
    pos = {
        # Left Zone: Local Taiwan Community (x in [-1.0, -0.35])
        "auth_twlang_scholar": (-0.90, 0.72),
        "auth_podcast_taigi": (-0.65, 0.56),
        "auth_indie_band": (-0.90, 0.30),
        "auth_parent_co_study": (-0.65, 0.12),
        "dual_taigi_podcaster": (-0.42, 0.36),
        "hub_local_ptt_1": (-0.84, -0.18),
        "hub_local_yt_2": (-0.52, -0.22),
        "peri_learner_1": (-0.88, -0.50),

        # Top Center Zone: Core Digital Resources (x in [-0.22, 0.22], y in [0.46, 0.90])
        "res_chhoetaigi": (0.00, 0.86),
        "res_pts_taigi": (-0.18, 0.62),
        "res_itaigi": (0.18, 0.62),
        "res_moedict_taigi": (0.00, 0.45),

        # Middle Bridge Zone: Cross-Border Invisible Links (x in [-0.18, 0.18], y in [-0.36, 0.18])
        "hub_bridge_curator": (-0.14, 0.12),
        "hub_bridge_student": (0.15, 0.04),
        "hub_bridge_yt_mod": (0.00, -0.24),

        # Right Zone: Overseas Diaspora Community (x in [0.42, 0.96])
        "auth_na_association": (0.58, 0.72),
        "auth_reddit_ohtaigi": (0.86, 0.56),
        "auth_overseas_church": (0.58, 0.24),
        "auth_tokyo_taigi": (0.88, 0.18),
        "hub_diaspora_1": (0.58, -0.18),
        "hub_diaspora_2": (0.88, -0.22),
        "peri_learner_2": (0.78, -0.50),

        # Bottom Isolated Zone: Pre-Mortem Filtered Adversarial & Noise Nodes
        "noise_troll_baiter": (-0.28, -0.78),
        "noise_viral_youtuber": (0.04, -0.78),
        "noise_passerby_bot": (0.34, -0.78),
    }

    fig, ax = plt.subplots(figsize=(18, 11.5), dpi=180)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.08, 1.04)
    ax.axis("off")

    # Zone background boxes
    zones = [
        (-1.07, -0.60, 0.72, 1.48, "#EFF6FF", "#93C5FD", "台灣本土社群 (Local)"),
        (-0.29, 0.36, 0.58, 0.61, "#ECFDF5", "#6EE7B7", "核心台語數位資源 (Resource)"),
        (-0.27, -0.40, 0.54, 0.66, "#FFF7ED", "#FDBA74", "跨海隱形連結樞紐 (BridgeHubs)"),
        (0.40, -0.60, 0.66, 1.48, "#F5F3FF", "#C4B5FD", "海外台語社群 (Diaspora)"),
        (-0.48, -0.94, 0.98, 0.30, "#FEF2F2", "#FCA5A5", "Pre-Mortem 過濾隔離區 (引戰 / 路人雜訊)"),
    ]
    for zx, zy, zw, zh, fc, ec, ztitle in zones:
        box = FancyBboxPatch(
            (zx, zy), zw, zh, boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor=fc, edgecolor=ec, linewidth=1.4, linestyle="-", zorder=0
        )
        ax.add_patch(box)
        ax.text(zx + zw / 2.0, zy + zh - 0.035, ztitle, ha="center", va="top", fontsize=11, fontweight="bold", color="#1E293B", zorder=1)

    # Draw directed edges
    for _, row in edges_df.iterrows():
        u, v = row["source_id"], row["target_id"]
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        sent = int(row["sentiment"])
        w = float(row["weight"])

        if sent < 0:
            # Negative conflict edges filtered out by Signed Network
            arr = FancyArrowPatch(
                (x1, y1), (x2, y2), connectionstyle="arc3,rad=0.14",
                arrowstyle="-|>,head_length=5,head_width=3",
                color="#9CA3AF", linewidth=1.0, linestyle=":", alpha=0.65, zorder=2
            )
            ax.add_patch(arr)
            continue

        tinfo = tie_lookup.get((u, v))
        if tinfo is None:
            # Filtered 1-off noise edge (tau < 2)
            arr = FancyArrowPatch(
                (x1, y1), (x2, y2), connectionstyle="arc3,rad=0.08",
                arrowstyle="-|>,head_length=4,head_width=2.5",
                color="#D1D5DB", linewidth=0.9, linestyle=":", alpha=0.6, zorder=2
            )
            ax.add_patch(arr)
            continue

        is_lb = bool(tinfo["is_local_bridge"])
        is_cross = bool(tinfo["is_cross_local_diaspora"]) or (u.startswith("hub_bridge") or v.startswith("hub_bridge"))
        if is_lb or is_cross:
            color = "#EA580C" if is_lb else "#D97706"
            ls = "--"
            lw = 1.1 + 0.35 * w
            alpha = 0.82
        else:
            color = "#1D4ED8"
            ls = "-"
            lw = 1.2 + 0.4 * w
            alpha = 0.72

        arr = FancyArrowPatch(
            (x1, y1), (x2, y2), connectionstyle="arc3,rad=0.08",
            arrowstyle="-|>,head_length=6,head_width=3.5",
            color=color, linewidth=lw, linestyle=ls, alpha=alpha, zorder=3
        )
        ax.add_patch(arr)

    # Draw nodes
    role_colors = {
        "Q2_Core_Authority": "#2563EB",
        "Q4_Pure_Hub_Curator": "#EA580C",
        "Q1_Dual_Leader": "#7C3AED",
        "Q3_Periphery_or_Filtered": "#64748B",
    }
    for nid, (nx_pos, ny_pos) in pos.items():
        info = m_map[nid]
        auth_v = info["authority_signed"]
        hub_v = info["hub_signed"]
        role = info["role_quadrant"]
        is_noise = nid.startswith("noise_")
        is_bridge = nid.startswith("hub_bridge_")
        color = "#DC2626" if is_noise else ("#C2410C" if is_bridge else role_colors.get(role, "#475569"))
        size = 220 if is_noise else (300 + 2600 * (auth_v + hub_v))
        edge_col = "#111827" if is_bridge else "#FFFFFF"
        lw_node = 2.2 if is_bridge else 1.5

        ax.scatter(nx_pos, ny_pos, s=size, c=color, edgecolors=edge_col, linewidths=lw_node, zorder=5)
        short_lbl = info["display_label"]
        score_tag = f"\n(A={auth_v:.2f}, H={hub_v:.2f})" if (auth_v > 0.01 or hub_v > 0.01) else "\n(Filtered / Periphery)"
        y_off = -0.048 if ny_pos > -0.7 else -0.055
        ax.text(
            nx_pos, ny_pos + y_off, f"{short_lbl}{score_tag}",
            ha="center", va="top", fontsize=7.6, fontweight=("bold" if (is_bridge or auth_v > 0.08) else "normal"),
            color="#0F172A",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.78),
            zorder=6
        )

    # Legend
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label="核心意見領袖 (Core Authority)", markerfacecolor="#2563EB", markersize=10),
        plt.Line2D([0], [0], marker="o", color="w", label="跨海隱形連結樞紐 (BridgeHub)", markerfacecolor="#C2410C", markeredgecolor="#111827", markersize=11),
        plt.Line2D([0], [0], marker="o", color="w", label="單邊策展 Hub (Pure Hub)", markerfacecolor="#EA580C", markersize=9),
        plt.Line2D([0], [0], marker="o", color="w", label="邊陲 / 雜訊隔離節點", markerfacecolor="#DC2626", markersize=9),
        plt.Line2D([0], [0], color="#1D4ED8", lw=2.2, ls="-", label="強連結 / 閉合資源邊 (Strong / Embedded)"),
        plt.Line2D([0], [0], color="#EA580C", lw=2.2, ls="--", label="弱連結 / 局部橋樑邊 (Local Bridge, e=0)"),
        plt.Line2D([0], [0], color="#9CA3AF", lw=1.4, ls=":", label="已剔除之負向衝突 / 路人邊"),
    ]
    ax.legend(handles=legend_handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=8.8, frameon=True, facecolor="white", framealpha=0.95)
    ax.set_title("圖 1｜台語社群跨本土與海外「明確網路關係拓撲圖」（含 Strong/Weak Ties 與 BridgeHubs）", fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout()
    p1 = os.path.join(FIG_DIR, "fig1_network_relationship_graph.png")
    fig.savefig(p1, dpi=180)
    plt.close(fig)

    # =========================================================================
    # Fig 2: Authority vs Hub Quadrant Scatter Plot
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10.5, 7.2), dpi=180)
    active_df = metrics_df[~metrics_df["node_id"].str.startswith("noise_")].copy()
    a_pos = active_df.loc[active_df["authority_signed"] > 0, "authority_signed"]
    h_pos = active_df.loc[active_df["hub_signed"] > 0, "hub_signed"]
    theta_a = float(a_pos.quantile(0.65))
    theta_h = float(h_pos.quantile(0.65))

    y_top = 0.205
    ax.axvspan(theta_a, 0.215, ymin=(theta_h + 0.012) / (y_top + 0.012), ymax=1.0, color="#F3E8FF", alpha=0.45)
    ax.axvspan(theta_a, 0.215, ymin=0.0, ymax=(theta_h + 0.012) / (y_top + 0.012), color="#DBEAFE", alpha=0.40)
    ax.axvspan(-0.010, theta_a, ymin=(theta_h + 0.012) / (y_top + 0.012), ymax=1.0, color="#FFEDD5", alpha=0.45)

    reg_colors = {"local": "#2563EB", "diaspora": "#9333EA", "resource": "#059669"}
    for reg, grp in active_df.groupby("region"):
        sizes = 90 + 1300 * grp["bridge_hub_score"]
        ax.scatter(
            grp["authority_signed"], grp["hub_signed"], s=sizes, c=reg_colors.get(reg, "#64748B"),
            alpha=0.85, edgecolors="#0F172A", linewidths=1.1, label=f"區域: {reg}", zorder=4
        )

    ax.axvline(theta_a, color="#475569", linestyle="--", linewidth=1.2)
    ax.axhline(theta_h, color="#475569", linestyle="--", linewidth=1.2)
    ax.text(0.200, 0.192, "Q1 雙棲領袖區", fontsize=9.5, fontweight="bold", color="#6B21A8", ha="right")
    ax.text(0.200, 0.048, "Q2 核心意見領袖\n(Core Authorities)", fontsize=9.5, fontweight="bold", color="#1E40AF", ha="right")
    ax.text(0.075, 0.190, "Q4 純資訊集散樞紐\n(Pure Hubs / 含 BridgeHubs)", fontsize=9.5, fontweight="bold", color="#9A3412", ha="right")
    ax.text(0.005, 0.012, "Q3 邊陲學習者與一般節點", fontsize=8.5, color="#475569", ha="left")

    # Manual label offsets to guarantee zero overlap
    offsets = {
        "res_chhoetaigi": (-0.025, 0.015),
        "auth_podcast_taigi": (0.006, 0.015),
        "auth_na_association": (0.008, 0.016),
        "res_pts_taigi": (-0.005, 0.018),
        "dual_taigi_podcaster": (0.008, 0.012),
        "auth_reddit_ohtaigi": (-0.018, 0.018),
        "hub_bridge_yt_mod": (0.011, 0.004),
        "hub_bridge_curator": (0.011, -0.002),
        "hub_bridge_student": (0.011, -0.006),
        "hub_local_yt_2": (0.011, -0.005),
        "hub_local_ptt_1": (0.011, -0.008),
        "hub_diaspora_1": (0.010, 0.002),
    }
    for _, r in active_df.iterrows():
        nid = r["node_id"]
        if nid in offsets:
            dx, dy = offsets[nid]
            tag = f"{r['display_label']}"
            if r["bridge_hub_score"] > 0.25:
                tag += f" (Bridge={r['bridge_hub_score']:.2f})"
            ax.annotate(
                tag, (r["authority_signed"], r["hub_signed"]),
                xytext=(r["authority_signed"] + dx, r["hub_signed"] + dy),
                fontsize=8.2, color="#0F172A",
                arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.7),
                zorder=6
            )

    ax.set_xlim(-0.010, 0.210)
    ax.set_ylim(-0.012, y_top)
    ax.set_xlabel("Authority Score (Signed HITS — 核心意見領袖分數)", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Hub Score (Signed HITS — 資訊集散與策展樞紐分數)", fontsize=10.5, fontweight="bold")
    ax.set_title("圖 2｜HITS Authorities vs. Hubs 四象限散佈圖（氣泡大小＝跨本土/海外 BridgeHub 分數）", fontsize=12.5, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="center right", fontsize=9, frameon=True)
    plt.tight_layout()
    p2 = os.path.join(FIG_DIR, "fig2_authority_vs_hub_scatter.png")
    fig.savefig(p2, dpi=180)
    plt.close(fig)

    # =========================================================================
    # Fig 3: Dual Scatter Plot — Edge Overlap vs Weight & In-Degree vs Betweenness
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.4), dpi=180)
    rng = np.random.default_rng(7)
    jitter = rng.uniform(-0.14, 0.14, size=len(edge_tie_df))
    x_w = edge_tie_df["undirected_weight"].to_numpy() + jitter
    y_ov = edge_tie_df["neighborhood_overlap"].to_numpy()
    sizes_e = 55 + 45 * edge_tie_df["embeddedness"].to_numpy()

    cross_mask = edge_tie_df["is_cross_local_diaspora"].to_numpy()
    ax1.scatter(x_w[~cross_mask], y_ov[~cross_mask], s=sizes_e[~cross_mask], c="#2563EB", alpha=0.72, edgecolors="white", label=f"非跨海邊 (平均重疊度={y_ov[~cross_mask].mean():.4f})")
    ax1.scatter(x_w[cross_mask], y_ov[cross_mask], s=sizes_e[cross_mask] + 30, c="#EA580C", marker="D", alpha=0.90, edgecolors="#111827", label=f"跨本土—海外邊 (平均重疊度={y_ov[cross_mask].mean():.4f})")
    ax1.axhline(0.0, color="#DC2626", linestyle="--", linewidth=1.0, alpha=0.7)
    ax1.text(4.85, 0.025, f"O_uv = 0 共 {int((y_ov == 0).sum())} 條 Local Bridges\n(跨不同社交圈、Span=3)", ha="right", va="bottom", fontsize=8.5, color="#B91C1C", bbox=dict(boxstyle="round", fc="#FEF2F2", ec="#FCA5A5"))
    ax1.set_xlabel("無向互動邊權重 w_uv (Strong Tie ≥ 3.0 vs Weak Tie = 2.0)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("鄰居重疊度 Neighborhood Overlap (Ch 3.3 Eq. 3.1)", fontsize=10, fontweight="bold")
    ax1.set_title("(a) 邊層級散佈圖：互動強度 vs. 鄰居重疊度", fontsize=11.5, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.5)

    # Right subplot: In-Degree vs Betweenness (Invisible Links Zone!)
    ax2.axvspan(-1.2, 4.5, ymin=0.45, ymax=1.0, color="#FFF7ED", alpha=0.75)
    ax2.text(3.8, 0.145, "「隱形連結」區：\n低表面被引用量 + 高中介橋樑", fontsize=9, fontweight="bold", color="#C2410C", ha="left", va="top")
    for _, r in active_df.iterrows():
        is_br = r["node_id"].startswith("hub_bridge_")
        c = "#EA580C" if is_br else ("#2563EB" if r["authority_signed"] > 0.05 else "#64748B")
        sz = 90 + 350 * r["invisible_link_score"]
        ax2.scatter(r["in_degree_signed"], r["betweenness"], s=sz, c=c, edgecolors="#111827" if is_br else "white", linewidths=1.2, alpha=0.88, zorder=4)

    ann_pts = {
        "hub_bridge_curator": (3.2, 0.006),
        "hub_bridge_yt_mod": (3.2, -0.011),
        "hub_bridge_student": (2.8, 0.005),
        "hub_local_ptt_1": (2.8, -0.013),
        "auth_na_association": (-4.5, 0.008),
        "res_chhoetaigi": (-6.0, 0.014),
        "auth_podcast_taigi": (-2.0, 0.014),
    }
    for nid, (dx, dy) in ann_pts.items():
        r = m_map[nid]
        ax2.annotate(
            r["display_label"], (r["in_degree_signed"], r["betweenness"]),
            xytext=(r["in_degree_signed"] + dx, r["betweenness"] + dy),
            fontsize=8.0, arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.6), zorder=6
        )

    ax2.set_xlim(-1.2, 32.5)
    ax2.set_ylim(-0.008, 0.155)
    ax2.set_xlabel("表面被引用聲量 In-Degree (Signed)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("最短路徑中介中心性 Betweenness Centrality", fontsize=10, fontweight="bold")
    ax2.set_title("(b) 節點散佈圖：如何抓出「低聲量、高橋接」隱形連結？", fontsize=11.5, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    fig.suptitle("圖 3｜Strong/Weak Ties 與跨海隱形連結（Invisible Links）結構散佈分析", fontsize=13.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    p3 = os.path.join(FIG_DIR, "fig3_tie_strength_vs_overlap_scatter.png")
    fig.savefig(p3, dpi=180, bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # Fig 4: Ch 3.3 Percolation Curve (Giant Component & Connected Components)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.5, 5.8), dpi=180)
    ps = perc_df[perc_df["strategy"] == "Remove_Strong_HighOverlap_First"]
    pw = perc_df[perc_df["strategy"] == "Remove_Weak_LowOverlap_First"]

    ax1.plot(ps["edges_removed_frac"] * 100, ps["giant_component_fraction"] * 100, "b-o", markersize=3.5, lw=2.2, label=f"先移除強連結/高重疊邊 (AUC={ps['giant_component_fraction'].mean():.4f})")
    ax1.plot(pw["edges_removed_frac"] * 100, pw["giant_component_fraction"] * 100, "r--s", markersize=3.5, lw=2.2, label=f"先移除弱連結/局部橋樑 (AUC={pw['giant_component_fraction'].mean():.4f})")
    ax1.axvline(42.31, color="#64748B", ls=":", lw=1.2)
    ax1.annotate("移除 42.3% (k=22 邊):\n強連結策略維持 90.9%\n弱連結策略驟降至 63.6%", xy=(42.31, 63.64), xytext=(48, 82), fontsize=8.5, arrowprops=dict(arrowstyle="->", color="#DC2626"), bbox=dict(boxstyle="round", fc="#FFFBEB", ec="#F59E0B"))
    ax1.set_xlabel("移除邊比例 (%)", fontsize=10.5, fontweight="bold")
    ax1.set_ylabel("最大連通分量占比 Giant Component (%)", fontsize=10.5, fontweight="bold")
    ax1.set_title("(a) Giant Component 崩解曲線 (Onnela et al. 實驗)", fontsize=11.5, fontweight="bold")
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.legend(loc="lower left", fontsize=8.5)

    ax2.plot(ps["edges_removed_frac"] * 100, ps["num_components"], "b-o", markersize=3.5, lw=2.2, label="先移除強連結 (緩慢分化)")
    ax2.plot(pw["edges_removed_frac"] * 100, pw["num_components"], "r--s", markersize=3.5, lw=2.2, label="先移除弱連結/橋樑 (快速碎裂)")
    ax2.annotate("k=22 時已碎裂成 9 個孤島\n(強連結策略僅 3 個分量)", xy=(42.31, 9), xytext=(8, 13.5), fontsize=8.5, arrowprops=dict(arrowstyle="->", color="#DC2626"), bbox=dict(boxstyle="round", fc="#FEF2F2", ec="#FCA5A5"))
    ax2.set_xlabel("移除邊比例 (%)", fontsize=10.5, fontweight="bold")
    ax2.set_ylabel("連通分量個數 (# Connected Components)", fontsize=10.5, fontweight="bold")
    ax2.set_title("(b) 網路碎片化速度對比", fontsize=11.5, fontweight="bold")
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.5)
    fig.suptitle("圖 4｜課本 Ch 3.3 滲流測試：強連結鞏固局部，弱連結／局部橋樑維繫全域連通", fontsize=13.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    p4 = os.path.join(FIG_DIR, "fig4_percolation_curve.png")
    fig.savefig(p4, dpi=180, bbox_inches="tight")
    plt.close(fig)

    # =========================================================================
    # Fig 5: Ch 19.7B Bilingual Diffusion Phase Diagram Scatter (625 grid points)
    # =========================================================================
    a_vals = np.linspace(0.80, 2.35, 25)
    c_vals = np.linspace(0.05, 1.55, 25)
    phase_rows = []
    for av in a_vals:
        for cv in c_vals:
            res = simulate_bilingual_path(a=float(av), b=1.0, c=float(cv))
            phase_rows.append(res)
    ph_df = pd.DataFrame(phase_rows)

    fig, ax = plt.subplots(figsize=(10.5, 7.0), dpi=180)
    reg_styles = {
        "B_Maintained": ("#10B981", "o", "台語固守區 (B Maintained)"),
        "Bilingual_Buffer_B_Survives": ("#F59E0B", "s", "雙語緩衝區存續 (Bilingual Buffer Zone — 三角切口)"),
        "Infiltration_B_Extinct": ("#EF4444", "^", "滲透淘汰區 (Infiltration — 雙語過度相容導致 B 滅絕)"),
        "Direct_Conquest": ("#7C3AED", "D", "直接征服區 (Direct Conquest — A 直接取代 B)"),
    }
    for rname, (col, mk, lbl) in reg_styles.items():
        sub = ph_df[ph_df["regime"] == rname]
        if not sub.empty:
            ax.scatter(sub["a_payoff_global"], sub["c_bilingual_cost"], c=col, marker=mk, s=95, alpha=0.82, edgecolors="white", linewidths=0.6, label=lbl, zorder=3)

    # Plot theoretical boundary lines from Textbook Fig. 19.25-19.26
    a_line = np.linspace(1.0, 2.0, 50)
    ax.axvline(1.0, color="#111827", lw=1.6, ls="--")
    ax.plot([1.0, 2.35], [1.0, 1.0], color="#111827", lw=1.2, ls=":")
    ax.plot(a_line, a_line - 1.0, color="#111827", lw=1.5, ls="-.")
    ax.text(1.50, 0.80, "實測點 (1.5, 0.8)\n雙語緩衝區", fontsize=8.5, fontweight="bold", ha="center", va="bottom", bbox=dict(boxstyle="round", fc="white", ec="#111827", alpha=0.9), zorder=6)
    ax.scatter([1.5, 1.5, 1.5], [0.3, 0.8, 1.5], c="black", s=65, zorder=5)
    ax.text(1.50, 0.34, "實測 (1.5, 0.3) 滲透淘汰", fontsize=8.2, fontweight="bold", ha="center", bbox=dict(boxstyle="round", fc="white", alpha=0.85), zorder=6)
    ax.text(1.50, 1.42, "實測 (1.5, 1.5) 直接征服", fontsize=8.2, fontweight="bold", ha="center", bbox=dict(boxstyle="round", fc="white", alpha=0.85), zorder=6)

    ax.set_xlabel("強勢全球語言報酬 a (設定台語基準報酬 b = 1.0)", fontsize=10.5, fontweight="bold")
    ax.set_ylabel("雙語學習／切換成本 c", fontsize=10.5, fontweight="bold")
    ax.set_title("圖 5｜課本 Ch 19.7B 雙語擴散模擬相圖散點圖（625 組 (a, c) 參數演化終態）", fontsize=12.5, fontweight="bold")
    ax.grid(True, ls=":", alpha=0.4)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.94)
    plt.tight_layout()
    p5 = os.path.join(FIG_DIR, "fig5_bilingual_phase_diagram.png")
    fig.savefig(p5, dpi=180)
    plt.close(fig)

    # =========================================================================
    # Fig 6: Dual Scatter — Heaps' Law + SNR Rejection & Survival Trajectory
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.5, 5.8), dpi=180)

    acc = batch_report_df[batch_report_df["status"] == "ACCEPT"]
    rej = batch_report_df[batch_report_df["status"] == "REJECT_BATCH"]
    ax1.scatter(acc["cum_tokens_N"], acc["cum_vocab_V"], s=85, c="#2563EB", edgecolors="#111827", label="通過品質檢核批次 (ACCEPT)", zorder=4)
    ax1.scatter(rej["cum_tokens_N"], rej["cum_vocab_V"], s=140, c="#DC2626", marker="X", edgecolors="#111827", label="Batch 7 雜訊截斷 (SNR斜率=-0.1143)", zorder=5)

    n_grid = np.linspace(2000, 36000, 100)
    v_fit = sqv_metrics["heaps_K"] * (n_grid ** sqv_metrics["heaps_beta"])
    ax1.plot(n_grid, v_fit, "g--", lw=1.8, label=f"Heaps' Law 擬合 (β={sqv_metrics['heaps_beta']}, R²={sqv_metrics['heaps_r2']})")
    for _, br in batch_report_df.iterrows():
        lbl = f"B{int(br['batch_id'])}" + (" (攔截!)" if br["status"] == "REJECT_BATCH" else f" ({br['platform']})")
        dx, dy = (-55, 6) if br["batch_id"] == 7 else ((5, -12) if br["batch_id"] in (6, 8) else (5, 5))
        ax1.annotate(lbl, (br["cum_tokens_N"], br["cum_vocab_V"]), xytext=(dx, dy), textcoords="offset points", fontsize=7.8)
    ax1.set_xlim(500, 41500)
    ax1.set_xlabel("累計詞數 N (Tokens)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("累計不重複詞彙數 V (Vocabulary)", fontsize=10, fontweight="bold")
    ax1.set_title("(a) 取樣品質散佈圖：希普斯飽和曲線與雜訊批自動攔截", fontsize=11.5, fontweight="bold")
    ax1.grid(True, ls=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.3)

    # Right subplot: Time-slicing trajectory in (clustering_avg, hub_gini) plane
    c_act = surv_df[surv_df["community_id"] == "taigi_active_crossborder"]
    c_age = surv_df[surv_df["community_id"] == "dialect_aging_control"]
    ax2.plot(c_act["clustering_avg"], c_act["hub_gini"], "b-o", lw=2.0, markersize=7, label="活躍跨海台語社群 (去中心化、跨海橋接)")
    ax2.plot(c_age["clustering_avg"], c_age["hub_gini"], "r--s", lw=2.0, markersize=7, label="老化對照方言社群 (封閉孤島 → Q8 崩解)")

    for df_sub, col in [(c_act, "#1E40AF"), (c_age, "#991B1B")]:
        for _, rr in df_sub.iterrows():
            if rr["slice_id"] in ("2024Q1", "2024Q4", "2025Q4"):
                txt = rr["slice_id"] + (" (event=1 消亡)" if rr["event"] == 1 else "")
                ox, oy = (-100, -14) if rr["event"] == 1 else (6, 4)
                ax2.annotate(txt, (rr["clustering_avg"], rr["hub_gini"]), xytext=(ox, oy), textcoords="offset points", fontsize=8.0, color=col, fontweight="bold")
    ax2.set_xlim(0.18, 0.90)

    ax2.set_xlabel("全域群聚係數 Global Clustering Avg (同溫層封閉度)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Hub 吉尼係數 Hub Gini (資訊守門人壟斷度)", fontsize=10, fontweight="bold")
    ax2.set_title("(b) 動態社群演化散點軌跡 (2024Q1 → 2025Q4)", fontsize=11.5, fontweight="bold")
    ax2.grid(True, ls=":", alpha=0.5)
    ax2.legend(loc="lower right", fontsize=8.3)
    fig.suptitle("圖 6｜取樣品質驗證（Heaps' Law + SNR 截斷）與時間切片存活演化散點軌跡", fontsize=13.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    p6 = os.path.join(FIG_DIR, "fig6_sampling_saturation_and_survival.png")
    fig.savefig(p6, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return [p1, p2, p3, p4, p5, p6]


def main():
    print("[1/7] Building demo dataset & normalized SQLite DB (PII masked)...")
    nodes_df, edges_df, batches, db_path = build_demo_dataset()

    print("[2/7] Running Sampling Quality Validation (Heaps' Law, SNR Slope, Shannon Entropy)...")
    batch_report_df, sqv_metrics = run_sampling_quality_validation(batches, db_path)

    print("[3/7] Running Signed Network Filtering, HITS, PageRank, Brandes Betweenness & BridgeHub...")
    metrics_df, M_signed, _, a_signed, h_signed, transitivity = analyze_network(nodes_df, edges_df, min_weight=2.0)

    print("[4/7] Analyzing Graph Theory Ties (Embeddedness, Overlap, Span) & Percolation...")
    edge_tie_df, _ = analyze_edge_ties_and_bridges(nodes_df, M_signed)
    perc_df = simulate_tie_removal_percolation(nodes_df, edge_tie_df)

    print("[5/7] Running Ch 19.7B Bilingual Diffusion & Time-Slicing Survival Formatting...")
    sim_df = run_bilingual_simulations()
    surv_df = build_survival_counting_process(nodes_df, edges_df, db_path)

    print("[6/7] Generating Scatter Plots & Network Relationship Graphs...")
    fig_paths = generate_visualizations(
        nodes_df, edges_df, metrics_df, edge_tie_df, perc_df, batch_report_df, sqv_metrics, surv_df
    )

    print("[7/7] Executing Automated Acceptance Gates G1–G6...")
    report = verify_gates(
        nodes_df, edges_df, db_path, sqv_metrics, metrics_df, M_signed,
        a_signed, h_signed, sim_df, surv_df, edge_tie_df, perc_df
    )
    report["figures_generated_count"] = len(fig_paths)
    report["figures"] = [os.path.relpath(p, BASE_DIR) for p in fig_paths]
    with open(os.path.join(OUT_DIR, "05_acceptance_verification_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n=== Acceptance Verification Summary ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nGlobal Transitivity (Signed Network): {transitivity:.4f}")
    if report["overall_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
