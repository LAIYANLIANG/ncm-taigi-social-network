# 台語：從世代傳承的困境，到海外社群的隱形連結

> *Networks, Crowds, and Markets* Final Project: **Taigi — From Intergenerational Transmission Challenges to Invisible Diaspora Ties**  
> **Networks, Crowds, and Markets** 期末專題規劃、演算法驗證 Demo 管線與 CI/CD AI 安全防護範本

**語言切換 / Language / 言語 / 언어：**
[繁體中文（台灣）](#zh-tw) | [English (US)](#en-us) | [日本語](#ja) | [한국어](#ko)

---

<a id="zh-tw"></a>

## 🇹🇼 繁體中文（台灣）

### 一、專題簡介與理論架構

本目錄（`期未/`）為課程 *Networks, Crowds, and Markets*（Easley & Kleinberg）期末專題之完整實作倉庫，聚焦研究題目：**「台語：從世代傳承的困境，到海外社群的隱形連結」**（見 [題目.md](題目.md)）。

本專題將社會網絡理論與社群資料工程結合，實作並驗證以下核心模型：
1. **網路核心意見領袖與資訊集散節點（Ch. 14, HITS）**：區分本土與海外語料中的高權威資源節點（Authorities）與跨語境聚合轉發節點（Hubs），並透過 **BridgeHub** 指標與譜分解檢核辨識海外「隱形橋接節點」。
2. **圖論結構與強弱連結雙刃劍（Ch. 2, Ch. 3, Ch. 19.4）**：計算鄰居重疊度（Neighborhood Overlap）、局部橋樑（Local Bridges）、Onnela 滲流拆解（強連結優先 vs. 弱連結優先對最大連通分量 Giant Component 之影響），說明弱連結在資訊跨海觸及與行為門檻擴散上的張力。
3. **符號網路過濾與正負向關係消融（Ch. 5）**：利用正負向互動邊權重過濾低可信／酸民雜訊節點（Signed HITS 消融驗證）。
4. **雙語緩衝區與世代擴散模擬（Ch. 19.7B）**：模擬 $q$ 與雙語報酬差異對母語維持與群體共存邊界之影響（滅絕區 / 雙語緩衝共存區 / 直接取代區）。
5. **取樣飽和品質與存活分析管線**：以 Heaps' Law（$\beta < 0.5$）、SNR 邊際坡度、Normalized Shannon Entropy 管控批次語料品質，並輸出 Counting Process 長格式供後續存活分析使用。

---

### 二、合成基準資料、隱私保護與版權排除聲明

- **合成基準資料（Synthetic Benchmark）**：`demo/data/` 內的所有檔案（`nodes_metadata.csv`、`interactions_raw.csv`、`corpus_batches.json`、`taigi_network.sqlite`）皆為 **25 個模擬社群節點、128 條跨 4 平台與 3 地域的有向加權邊**，僅供演算法邏輯驗證與圖表再現之用，**不含任何真實網友帳號個資、未遮罩原始貼文或個人登入 Cookie**。
- **去識別化機制（Salted SHA-256）**：節點 ID 全面採 16 碼小寫十六進位雜湊值，且 [demo/src/run_demo_pipeline.py](demo/src/run_demo_pipeline.py) 透過環境變數讀取鹽值：
  ```bash
  export TAIGI_PII_SALT="your-private-production-salt"
  ```
- **紅燈檔案排除（`.gitignore`）**：受版權保護的課程原文教材（上層 `課本_pdf/`、`課本_文字/`）、含個人 Gemini 分享連結的參考 PDF（`網路社群資料取得方法與技術.pdf`）、本機系統檔 `.DS_Store`，以及未來實作產生的未去敏資料（`raw_unmasked/`、`cookies.txt`、`auth_state.json`、`.env`）皆已透過 [.gitignore](.gitignore) 排除於 Git 之外。

---

### 三、資料夾與檔案總覽（`期未/`）

```text
期未/
├── README.md                                        # 本說明文件（台灣繁體 / 美式英文 / 日文 / 韓文）
├── 題目.md                                           # 原始期末題目發想
├── 期末專題規劃_台語世代傳承與海外隱形連結.md            # 課程理論全景與研究問題規劃書
├── 社群資料取得與Hubs_Authorities辨識計算計畫.md         # 社群資料取得規範、HITS 與整合計算藍圖
├── .gitignore / .gitleaks.toml / .pre-commit-config.yaml  # Git 排除規則與 Push 前機敏防護設定
├── .github/workflows/ci_ai_security_and_gates.yml   # GitHub Actions 三階段 AI 安全檢查與 G1–G6 驗證
├── cicd_與_安全檢查範本/                             # CI/CD AI 審查範本、Pre-Push 腳本與風險評估報告
│   ├── 00_CICD_AI檢查範本.md                         # ci/cd.md 風格純文字規範與 AI Prompt 檢查範本
│   ├── 01_CICD_與_PrePush_AI安全檢查使用指南.md       # 雙層防護架構與 GitHub 操作 SOP
│   ├── 02_GitHub上傳風險評估與資料去敏清單.md         # 工作區全檔案紅／黃／綠燈風險評估
│   ├── pre_push_security_check.py                   # [SEC-01]–[SEC-07] 零相依本地與 CI 安全掃描器
│   ├── ai_pr_reviewer.py                            # AI Diff 合規審查器（Gemini API + 離線啟發式備援）
│   └── install_git_hooks.sh                         # 一鍵安全初始化期未/ Git 與 Push 前自動掛鉤
└── demo/
    ├── 執行成果與驗收報告.md                         # 完整實跑數據、消融實驗與驗收結論報告
    ├── plain/                                       # 分章節執行規劃規格（00–06）
    │   ├── 00_執行規劃總覽與目錄.md
    │   ├── 01_資料源與參考資料規劃.md
    │   ├── 02_演算法設計與數學模型.md
    │   ├── 03_取樣品質驗證與演算法驗證.md
    │   ├── 04_研究限制與PreMortem分析及案例.md
    │   ├── 05_驗收規劃與交付檢核表.md
    │   └── 06_圖論與強弱連結深度解析.md
    ├── src/run_demo_pipeline.py                     # 完整資料建庫、演算法、繪圖與 G1–G6 驗收主程式
    ├── data/                                        # 合成基準資料集與 SQLite 資料庫
    └── output/                                      # 7 份定量分析 CSV/JSON 與 6 張視覺化 PNG 圖表
        └── figures/ (fig1 ～ fig6.png)
```

---

### 四、快速開始與自動化檢查指令

```bash
# 1. 執行完整演算法 Demo、生成 6 張視覺化圖表並檢查 G1–G6 是否全數 PASS
python3 demo/src/run_demo_pipeline.py

# 2. （僅限期未/ 內）初始化 Git 並安裝 Commit / Push 前自動安全＋AI 檢查掛鉤
bash cicd_與_安全檢查範本/install_git_hooks.sh --init

# 3. 手動執行 Push 前七大資安與去敏掃描（須為 0 BLOCK）
python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci

# 4. 手動執行 AI 合規審查（支援 GEMINI_API_KEY 或離線啟發式模式）
python3 cicd_與_安全檢查範本/ai_pr_reviewer.py --diff-mode workspace --strict
```

驗收報告預設輸出於 [demo/output/05_acceptance_verification_report.json](demo/output/05_acceptance_verification_report.json) 與 [demo/執行成果與驗收報告.md](demo/執行成果與驗收報告.md)，6 張圖表則輸出於 `demo/output/figures/`。

---

### 五、視覺化分析成果圖表（圖 1 – 圖 6）

#### 圖 1｜台語社群跨本土與海外「明確網路關係拓撲圖」（Strong/Weak Ties 與 BridgeHubs）
顯示本土社群（Local）、核心台語數位資源（Resource）、海外社群（Diaspora）、跨海隱形連結樞紐（BridgeHubs）與 Pre-Mortem 過濾隔離區之結構分布；實線為 Strong Ties，橘色虛線為跨圈層 Weak Ties／Local Bridges。

![圖 1：台語社群跨本土與海外明確網路關係拓撲圖](demo/output/figures/fig1_network_relationship_graph.png)

#### 圖 2｜HITS Authorities vs. Hubs 四象限散佈圖（氣泡大小＝BridgeHub 分數）
左上方 `Q4` 集中高 Hub／高 Bridge 分數之跨海隱形橋接節點（如跨區字幕志工 `Bridge=0.74`、留美台生跨海策展帳號 `Bridge=0.71`、台文懶人包跨國轉發站 `Bridge=0.50`），右下方 `Q2` 則為高權威核心資源（Core Authorities）。

![圖 2：HITS Authorities vs. Hubs 四象限散佈圖](demo/output/figures/fig2_authority_vs_hub_scatter.png)

#### 圖 3｜Strong/Weak Ties 與跨海隱形連結（Invisible Links）結構散佈分析
左圖（邊層級）顯示跨本土–海外邊之平均鄰居重疊度（`0.0943`）低於非跨海邊（`0.1445`），並存在 `22` 條 `O_uv = 0` 之 Local Bridges；右圖（節點層級）凸顯「低表面被引用量（In-Degree）＋高中介中心性（Betweenness）」的隱形橋接區。

![圖 3：Strong/Weak Ties 與跨海隱形連結結構散佈分析](demo/output/figures/fig3_tie_strength_vs_overlap_scatter.png)

#### 圖 4｜課本 Ch 3.3 滲流測試：強連結鞏固局部，弱連結／局部橋樑維繫全域連通
依 Onnela et al. 實驗策略移除 `42.3%`（`k=22` 條）邊時，優先移除弱連結／橋樑會使 Giant Component 驟降至 `63.6%` 並碎裂為 `9` 個分量（AUC = `0.6098`），而優先移除強連結仍維持 `90.9%` 與 `3` 個分量（AUC = `0.7393`）。

![圖 4：課本 Ch 3.3 滲流測試曲線](demo/output/figures/fig4_percolation_curve.png)

#### 圖 5｜課本 Ch 19.7B 雙語擴散模擬相圖散點圖（625 組 `(a, c)` 參數演化終態）
呈現四種平衡區域：台語固守區（`B Maintained`）、雙語緩衝存續區（`Bilingual Buffer Zone`，如實測點 `(1.5, 0.8)`）、滲透淘汰區（`Infiltration`，如實測點 `(1.5, 0.3)`）與直接征服區（`Direct Conquest`，如實測點 `(1.5, 1.5)`）。

![圖 5：課本 Ch 19.7B 雙語擴散模擬相圖散點圖](demo/output/figures/fig5_bilingual_phase_diagram.png)

#### 圖 6｜取樣品質驗證（Heaps' Law + SNR 截斷）與時間切片存活演化軌跡
左圖顯示語料批次回歸符合 Heaps' Law（$\beta = 0.4446, R^2 = 0.9856$）並自動攔截 `Batch 7` 雜訊批（SNR 斜率 `-0.1143`）；右圖追蹤 `2024Q1 → 2025Q4` 活躍跨海台語社群（往去中心化橋接移動）與老化封閉孤島（往消亡演化）之差異軌跡。

![圖 6：取樣品質驗證與時間切片存活演化散點軌跡](demo/output/figures/fig6_sampling_saturation_and_survival.png)

---

<a id="en-us"></a>

## 🇺🇸 English (US)

### 1. Project Overview & Theoretical Foundation

This directory (`期未/`) is the repository root for the *Networks, Crowds, and Markets* (Easley & Kleinberg) final course project: **"Taigi: From Intergenerational Transmission Challenges to Invisible Diaspora Ties."**

The project integrates computational social science methods with graph theory and algorithmic verification:
1. **Authorities & Hubs (Ch. 14, HITS)**: Identifies authoritative Taigi cultural/educational sources (Authorities) and cross-community aggregators (Hubs), augmented with a **BridgeHub** metric and spectral decomposition checks to uncover "invisible diaspora bridges" connecting local Taiwanese speakers and overseas communities.
2. **Graph Theory, Strong/Weak Ties & Local Bridges (Ch. 2, Ch. 3, Ch. 19.4)**: Measures Embeddedness, Neighborhood Overlap, Local Bridges, and Onnela-style percolation curves (removing strong ties first vs. weak ties first) to contrast information reachability with high-threshold language retention.
3. **Signed Network Filtering (Ch. 5)**: Performs ablation testing showing how signed filtering suppresses adversarial/troll nodes from distorting Authority scores.
4. **Bilingual Diffusion & Threshold Buffers (Ch. 19.7B)**: Simulates three equilibrium regimes (extinction, bilingual buffer coexistence, and direct replacement) across varying coordination thresholds and bilingual incentives.
5. **Sampling Saturation & Survival Preparation**: Validates batch corpus acquisition using Heaps' Law ($\beta < 0.5$), SNR marginal slopes, and Normalized Shannon Entropy, exporting counting-process time slices (`G5`).

---

### 2. Synthetic Benchmark, PII Masking & Copyright Notice

- **Synthetic Benchmark Data**: All files inside `demo/data/` (`nodes_metadata.csv`, `interactions_raw.csv`, `corpus_batches.json`, `taigi_network.sqlite`) represent **25 simulated community nodes and 128 weighted directed interactions** across 4 platforms and 3 regions. They contain **zero real user accounts, zero unmasked personal posts, and zero browser cookies**.
- **Salted SHA-256 PII Masking**: Node identifiers are 16-character lowercase hex hashes generated via environment variable `TAIGI_PII_SALT` inside [demo/src/run_demo_pipeline.py](demo/src/run_demo_pipeline.py):
  ```bash
  export TAIGI_PII_SALT="your-private-production-salt"
  ```
- **Copyright & Privacy Exclusions (`.gitignore`)**: Copyrighted course textbook files (parent `課本_pdf/` and `課本_文字/`), the personal reference PDF containing a private Gemini conversation link (`網路社群資料取得方法與技術.pdf`), macOS `.DS_Store`, and any future `raw_unmasked/` or cookie files are strictly excluded via [.gitignore](.gitignore).

---

### 3. Directory Structure

- **Root Planning & Prompt Specs**:
  - `題目.md` — Initial research topic statement
  - `期末專題規劃_台語世代傳承與海外隱形連結.md` — Textbook-grounded research roadmap
  - `社群資料取得與Hubs_Authorities辨識計算計畫.md` — Ethical data acquisition & HITS computation blueprint
- **`demo/plain/` (Modular Execution Specifications `00`–`06`)**:
  - `00_執行規劃總覽與目錄.md` — Master index mapping specs to outputs & gates `G1–G6`
  - `01_資料源與參考資料規劃.md` — Multi-channel public data design, L1–L4 lexicons, SQLite schema
  - `02_演算法設計與數學模型.md` — Formal definitions for Signed HITS, `BridgeHub`, PageRank, Ch. 19.7B, and time slicing
  - `03_取樣品質驗證與演算法驗證.md` — SQV-1..4 quality metrics & AV-1..5 validation protocols
  - `04_研究限制與PreMortem分析及案例.md` — Methodological limitations & 6 Pre-Mortem failure mitigations
  - `05_驗收規劃與交付檢核表.md` — Quantitative acceptance thresholds (`G1–G6`)
  - `06_圖論與強弱連結深度解析.md` — Graph theory metrics & Strong vs. Weak Ties percolation analysis
- **`demo/src/`, `demo/data/`, `demo/output/` & `demo/執行成果與驗收報告.md`**:
  - Self-contained pipeline script (`run_demo_pipeline.py`, standard Python + NumPy/Pandas/Matplotlib), synthetic SQLite/CSV benchmark, 7 tabular verification outputs, 6 PNG visualizations (`fig1`–`fig6`), and final acceptance report.
- **CI/CD & Pre-Push Security Templates**:
  - `.github/workflows/ci_ai_security_and_gates.yml` — 3-stage GitHub Actions pipeline (Gitleaks + `[SEC-01..07]` audit → `G1–G6` pipeline verification → AI PR compliance review)
  - `cicd_與_安全檢查範本/` — Includes Markdown prompt rules (`00_CICD_AI檢查範本.md`), setup guide (`01_...md`), repository risk matrix (`02_...md`), `pre_push_security_check.py`, `ai_pr_reviewer.py`, and `install_git_hooks.sh`.

---

### 4. Quickstart

```bash
# Run full benchmark pipeline & verify gates G1-G6 pass
python3 demo/src/run_demo_pipeline.py

# Initialize Git safely inside this directory only and install pre-commit / pre-push hooks
bash cicd_與_安全檢查範本/install_git_hooks.sh --init

# Run pre-push security, PII & copyright audit manually
python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci

# Run AI PR compliance review (uses GEMINI_API_KEY if set, otherwise offline heuristic mode)
python3 cicd_與_安全檢查範本/ai_pr_reviewer.py --diff-mode workspace --strict
```

---

### 5. Visual Results & Network Graphs (Figures 1–6)

#### Figure 1 | Cross-Border Taigi Network Topology (Strong/Weak Ties & BridgeHubs)
Maps Local Taiwan, Core Digital Resource, Overseas Diaspora, cross-border `BridgeHubs`, and Pre-Mortem filtered periphery nodes, distinguishing embedded strong ties (solid lines) from local bridges / weak ties (dashed lines).

![Figure 1: Cross-Border Taigi Network Topology](demo/output/figures/fig1_network_relationship_graph.png)

#### Figure 2 | HITS Authorities vs. Hubs Quadrant Scatter Plot (Bubble Size = BridgeHub Score)
Highlights `Q4` pure cross-border aggregators / invisible hubs (e.g., subtitle volunteer `Bridge=0.74`, US student curator `Bridge=0.71`, infographic hub `Bridge=0.50`) versus `Q2` Core Authorities.

![Figure 2: HITS Authorities vs. Hubs Scatter Plot](demo/output/figures/fig2_authority_vs_hub_scatter.png)

#### Figure 3 | Strong/Weak Ties & Invisible Cross-Border Links Structure
Edge-level scatter (left) contrasts lower average overlap on cross-border ties (`0.0943`) vs. non-cross-border ties (`0.1445`) with `22` local bridges (`O_uv = 0`); node-level scatter (right) pinpoints low In-Degree, high Betweenness "invisible links."

![Figure 3: Strong/Weak Ties and Invisible Links Scatter](demo/output/figures/fig3_tie_strength_vs_overlap_scatter.png)

#### Figure 4 | Ch. 3.3 Percolation Test: Strong Ties Cohese Locally, Weak Ties Connect Globally
Removing `42.3%` (`k=22`) weak/bridge ties drops the Giant Component to `63.6%` (`9` components, AUC = `0.6098`), whereas removing strong/high-overlap ties retains `90.9%` (`3` components, AUC = `0.7393`).

![Figure 4: Ch. 3.3 Percolation Test](demo/output/figures/fig4_percolation_curve.png)

#### Figure 5 | Ch. 19.7B Bilingual Diffusion Phase Diagram (625 `(a, c)` Parameter Pairs)
Illustrates four equilibrium regimes: `B Maintained`, `Bilingual Buffer Zone` (`(1.5, 0.8)`), `Infiltration` (`(1.5, 0.3)`), and `Direct Conquest` (`(1.5, 1.5)`).

![Figure 5: Ch. 19.7B Bilingual Diffusion Phase Diagram](demo/output/figures/fig5_bilingual_phase_diagram.png)

#### Figure 6 | Sampling Quality Validation (Heaps' Law + SNR Cutoff) & Time-Slice Survival Trajectories
Shows Heaps' Law saturation fit ($\beta = 0.4446, R^2 = 0.9856$) with automated rejection of noisy `Batch 7` (SNR slope `-0.1143`) alongside `2024Q1 → 2025Q4` Hub Gini vs. Global Clustering trajectories.

![Figure 6: Sampling Quality Validation & Survival Trajectories](demo/output/figures/fig6_sampling_saturation_and_survival.png)

---

<a id="ja"></a>

## 🇯🇵 日本語

### 1. プロジェクト概要と理論的枠組み

本ディレクトリ（`期未/`）は、講座 *Networks, Crowds, and Markets*（Easley & Kleinberg）の期末プロジェクト **「台湾語（台語）：世代間継承の課題から海外コミュニティとの見えないつながりへ」** の設計書、実証デモパイプライン、および CI/CD AI セキュリティ検査テンプレート一式を格納するリポジトリです。

主な理論・実装要素：
1. **Authorities & Hubs（第14章 HITS）**：台湾国内および海外コミュニティにおける権威ある一次リソース（Authorities）と情報集約・媒介ノード（Hubs）を抽出し、**BridgeHub** 指標および固有値分解検証によって「海外との見えない橋渡しノード」を特定します。
2. **グラフ理論と強い結びつき／弱い結びつき（第2章・第3章・第19.4節）**：近傍重複度（Neighborhood Overlap）、局所ブリッジ（Local Bridges）、パーコレーション解析（強い結びつき優先削除 vs. 弱い結びつき優先削除）を通じ、情報の越境拡散と高閾値行動（言語継承）における構造的トレードオフを定量化します。
3. **符号付きネットワーク（第5章）**：正負のインタラクション重みによるノイズ・荒らしノード除去のアブレーション検証を実施します。
4. **バイリンガル普及・閾値モデル（第19.7B節）**：協調閾値とバイリンガル利得の変化による 3 つの均衡相（消滅・バイリンガル緩衝共存・直接置換）をシミュレーションします。
5. **サンプリング飽和検証と生存分析前処理**：Heaps' Law（$\beta < 0.5$）、SNR 限界勾配、正規化シャノンエントロピーでバッチ品質を管理し、時間スライス形式（Counting Process）を出力します。

---

### 2. 合成ベンチマーク・プライバシー保護・著作権に関する注意

- **合成ベンチマークデータ**：`demo/data/` 内のデータ（25 ノード、128 本の有向エッジ、4 プラットフォーム、3 地域）はアルゴリズム再現用の**合成模擬データ**であり、**実在の SNS アカウント情報、未マスク投稿、個人用 Cookie は一切含まれていません**。
- **Salted SHA-256 による匿名化**：すべてのノード ID は 16 桁の 16 進ハッシュ値で保護され、[demo/src/run_demo_pipeline.py](demo/src/run_demo_pipeline.py) は環境変数 `TAIGI_PII_SALT` を参照します。
- **GitHub 除外対象（`.gitignore`）**：著作権で保護された教科書ファイル（親ディレクトリの `課本_pdf/`・`課本_文字/`）、個人の Gemini 共有リンクを含む PDF（`網路社群資料取得方法與技術.pdf`）、`.DS_Store`、および今後の未加工データ（`raw_unmasked/`、`cookies.txt`、`.env` 等）は [.gitignore](.gitignore) によりアップロード対象から除外されています。

---

### 3. ディレクトリ構成

- **企画・研究計画書**：`題目.md`、`期末專題規劃_台語世代傳承與海外隱形連結.md`、`社群資料取得與Hubs_Authorities辨識計算計畫.md`
- **`demo/plain/`（章別仕様書 `00`～`06`）**：データソース設計、数理モデル、サンプリング／アルゴリズム検証、研究限界と Pre-Mortem 分析、受け入れ基準（`G1–G6`）、グラフ理論・強弱連結解析
- **`demo/src/`, `demo/data/`, `demo/output/`, `demo/執行成果與驗收報告.md`**：パイプライン本体（`run_demo_pipeline.py`）、SQLite/CSV データ、定量出力 7 ファイル、可視化図表 PNG 6 点（`fig1`～`fig6`）、最終検証レポート
- **CI/CD・Pre-Push AI セキュリティ検査一式**：
  - `.github/workflows/ci_ai_security_and_gates.yml`（3 段階自動 CI/CD ワークフロー）
  - `cicd_與_安全檢查範本/`（Markdown 検査プロンプト `00_CICD_AI檢查範本.md`、利用ガイド `01_...md`、リスク評価表 `02_...md`、`pre_push_security_check.py`、`ai_pr_reviewer.py`、`install_git_hooks.sh`）

---

### 4. クイックスタート

```bash
# デモパイプラインを実行し、受け入れゲート G1–G6 (PASS) と図表 6 点を生成
python3 demo/src/run_demo_pipeline.py

# 本ディレクトリ内のみで Git を安全に初期化し、Pre-Commit / Pre-Push フックを導入
bash cicd_與_安全檢查範本/install_git_hooks.sh --init

# 機密情報・PII・著作権チェックを実行
python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci

# AI コンプライアンスレビューを実行（GEMINI_API_KEY 未設定時はオフライン規則モードで動作）
python3 cicd_與_安全檢查範本/ai_pr_reviewer.py --diff-mode workspace --strict
```

---

### 5. 可視化分析結果（図 1 ～ 図 6）

#### 図 1｜台湾語コミュニティの国内・海外「ネットワーク関係トポロジー図」（Strong/Weak Ties・BridgeHubs）
台湾国内（Local）、デジタル中核リソース（Resource）、海外（Diaspora）、越境ブリッジハブ（BridgeHubs）、Pre-Mortem ノイズ隔離区の構造と強・弱連結の分布を可視化しています。

![図 1：台湾語コミュニティのネットワーク関係トポロジー図](demo/output/figures/fig1_network_relationship_graph.png)

#### 図 2｜HITS Authorities vs. Hubs 4 象限散布図（バブルサイズ＝BridgeHub スコア）
左上 `Q4` に位置する越境仲介ハブ（字幕ボランティア `Bridge=0.74`、在米留学生キュレーター `Bridge=0.71` 等）と、右下 `Q2` の中核権威ノード（Core Authorities）を対比しています。

![図 2：HITS Authorities vs. Hubs 4 象限散布図](demo/output/figures/fig2_authority_vs_hub_scatter.png)

#### 図 3｜Strong/Weak Ties と越境「見えないつながり」の構造散布分析
エッジ単位（左）では越境エッジの低い近傍重複度（平均 `0.0943` vs. 非越境 `0.1445`）と `22` 本の局所ブリッジ（`O_uv = 0`）を、ノード単位（右）では低被参照・高媒介中心性の隠れた架け橋を抽出しています。

![図 3：Strong/Weak Ties と越境見えないつながりの構造散布分析](demo/output/figures/fig3_tie_strength_vs_overlap_scatter.png)

#### 図 4｜第 3.3 節パーコレーション実験：強い結びつきは局所結束、弱い結びつきは全体連結を維持
`42.3%`（`k=22` 本）削除時点で、弱い結びつき優先削除は Giant Component が `63.6%` まで急落し `9` 成分に分裂（AUC = `0.6098`）する一方、強い結びつき優先削除は `90.9%`・`3` 成分（AUC = `0.7393`）を保ちます。

![図 4：第 3.3 節パーコレーション曲線](demo/output/figures/fig4_percolation_curve.png)

#### 図 5｜第 19.7B 節バイリンガル普及相図散布図（625 通りの `(a, c)` パラメータ均衡）
言語維持区（`B Maintained`）、バイリンガル緩衝共存区（`(1.5, 0.8)`）、浸透淘汰区（`(1.5, 0.3)`）、直接置換区（`(1.5, 1.5)`）の 4 相を示しています。

![図 5：第 19.7B 節バイリンガル普及相図散布図](demo/output/figures/fig5_bilingual_phase_diagram.png)

#### 図 6｜サンプリング品質検証（Heaps' Law + SNR 遮断）と時系列生存軌跡
Heaps' Law 飽和曲線（$\beta = 0.4446, R^2 = 0.9856$）によるノイズバッチ `Batch 7`（SNR 勾配 `-0.1143`）自動除外と、`2024Q1 → 2025Q4` の Hub Gini／クラスタリング推移を比較しています。

![図 6：サンプリング品質検証と時系列生存軌跡](demo/output/figures/fig6_sampling_saturation_and_survival.png)

---

<a id="ko"></a>

## 🇰🇷 한국어

### 1. 프로젝트 개요 및 이론적 배경

이 디렉터리(`期未/`)는 *Networks, Crowds, and Markets*(Easley & Kleinberg) 강의 기말 프로젝트 **「대만어(타이위): 세대 전승의 난관에서 해외 커뮤니티의 보이지 않는 연결까지」** 의 연구 기획서, 알고리즘 검증 데모 파이프라인, 그리고 CI/CD AI 보안 점검 템플릿을 담은 저장소입니다.

핵심 이론 및 구현 요소:
1. **Authorities & Hubs (14장 HITS)**: 대만 현지 및 해외 커뮤니티의 권위 있는 핵심 출처(Authorities)와 정보 중계·집약 노드(Hubs)를 식별하고, **BridgeHub** 지표 및 스펙트럼 분해 검증을 통해 국경을 넘는 '보이지 않는 가교 노드'를 탐지합니다.
2. **그래프 이론과 강한/약한 연결의 양면성 (2장, 3장, 19.4절)**: 이웃 중복도(Neighborhood Overlap), 국소 브리지(Local Bridges), Onnela 퍼콜레이션 분석(강한 연결 우선 제거 vs. 약한 연결 우선 제거)을 통해 정보 도달 범위와 고임계 언어 전승 간의 구조적 트레이드오프를 분석합니다.
3. **부호 네트워크 필터링 (5장)**: 긍정/부정 상호작용 가중치를 활용해 악성·노이즈 노드를 제거하는 절제 실험(Ablation Study)을 수행합니다.
4. **이중언어 확산 및 임계치 완충 모델 (19.7B절)**: 조정 임계값과 이중언어 보상에 따른 3가지 균형 국면(소멸 / 이중언어 완충 공존 / 직접 대체)을 시뮬레이션합니다.
5. **표본 포화 검증 및 생존 분석 전처리**: Heaps' Law($\beta < 0.5$), SNR 한계 기울기, 정규화 섀넌 엔트로피로 수집 품질을 검증하고 Counting Process 포맷 데이터를 생성합니다.

---

### 2. 합성 벤치마크, 개인정보 비식별화 및 저작권 제외 안내

- **합성 벤치마크 데이터(Synthetic Benchmark)**: `demo/data/` 내의 데이터(25개 모의 노드, 4개 플랫폼·3개 지역 간 128개 방향성 가중 엣지)는 알고리즘 검증 및 재현용 **합성 데이터**이며, **실제 SNS 계정, 비식별 처리되지 않은 원문 게시물, 개인 브라우저 쿠키는 전혀 포함되어 있지 않습니다**.
- **Salted SHA-256 마스킹**: 모든 노드 ID는 환경 변수 `TAIGI_PII_SALT`를 참조하는 16자리 16진수 해시값으로 처리됩니다([demo/src/run_demo_pipeline.py](demo/src/run_demo_pipeline.py)).
- **GitHub 업로드 제외 항목(`.gitignore`)**: 저작권이 있는 강의 교재 파일(상위 폴더의 `課本_pdf/`, `課本_文字/`), 개인 Gemini 대화 링크가 포함된 참고 PDF(`網路社群資料取得方法與技術.pdf`), `.DS_Store`, 향후 실측 시 생성될 수 있는 비마스크 원본(`raw_unmasked/`, `cookies.txt`, `.env` 등)은 [.gitignore](.gitignore)에 의해 엄격히 차단됩니다.

---

### 3. 폴더 및 파일 구조

- **최상위 연구 기획 문서**: `題目.md`, `期末專題規劃_台語世代傳承與海外隱形連結.md`, `社群資料取得與Hubs_Authorities辨識計算計畫.md`
- **`demo/plain/` (장별 실행 명세 `00`–`06`)**: 데이터 소스 설계, 수학적 모델, 표본·알고리즘 검증, 연구 한계 및 Pre-Mortem 사례, 검수 기준(`G1–G6`), 그래프 이론 및 강약 연결 심층 분석
- **`demo/src/`, `demo/data/`, `demo/output/`, `demo/執行成果與驗收報告.md`**: 실행 파이프라인(`run_demo_pipeline.py`), 합성 SQLite/CSV 데이터, 7개 정량 분석 산출물, 시각화 PNG 6종(`fig1`–`fig6`), 최종 검수 보고서
- **CI/CD 및 Push 전 AI 보안 점검 도구**:
  - `.github/workflows/ci_ai_security_and_gates.yml` (3단계 GitHub Actions 자동 검증 워크플로우)
  - `cicd_與_安全檢查範本/` (Markdown 규칙·프롬프트 템플릿 `00_CICD_AI檢查範本.md`, 사용 가이드 `01_...md`, 업로드 위험 평가표 `02_...md`, `pre_push_security_check.py`, `ai_pr_reviewer.py`, `install_git_hooks.sh`)

---

### 4. 빠른 실행 및 보안 점검 명령어

```bash
# 1. 전체 데모 파이프라인 실행, 시각화 6종 생성 및 G1–G6 검증
python3 demo/src/run_demo_pipeline.py

# 2. 현재(期未/) 폴더 내부에서만 안전하게 Git 초기화 및 Pre-Commit / Pre-Push 훅 설치
bash cicd_與_安全檢查範本/install_git_hooks.sh --init

# 3. Push 전 보안·PII·저작권 감사 수동 실행
python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci

# 4. AI PR/Diff 규정 준수 검토 실행 (GEMINI_API_KEY 미설정 시 오프라인 휴리스틱 모드로 자동 동작)
python3 cicd_與_安全檢查範本/ai_pr_reviewer.py --diff-mode workspace --strict
```

---

### 5. 시각화 분석 결과 (그림 1 – 그림 6)

#### 그림 1 | 대만어 커뮤니티 국내외 '네트워크 관계 토폴로지' (Strong/Weak Ties & BridgeHubs)
대만 현지(Local), 핵심 디지털 자원(Resource), 해외(Diaspora), 국경 간 가교 허브(BridgeHubs) 및 Pre-Mortem 필터링 노드의 분포와 강/약 연결 구조를 나타냅니다.

![그림 1: 대만어 커뮤니티 네트워크 관계 토폴로지](demo/output/figures/fig1_network_relationship_graph.png)

#### 그림 2 | HITS Authorities vs. Hubs 4분면 산점도 (버블 크기 = BridgeHub 점수)
좌상단 `Q4`의 국경 간 중계 허브(자막 봉사자 `Bridge=0.74`, 재미 유학생 큐레이터 `Bridge=0.71` 등)와 우하단 `Q2`의 핵심 권위 노드(Core Authorities)를 대비합니다.

![그림 2: HITS Authorities vs. Hubs 4분면 산점도](demo/output/figures/fig2_authority_vs_hub_scatter.png)

#### 그림 3 | Strong/Weak Ties 및 국경 간 '보이지 않는 연결' 구조 산점 분석
엣지 수준(좌)에서는 초국적 엣지의 낮은 이웃 중복도(평균 `0.0943` vs. 비초국적 `0.1445`)와 `22`개의 국소 브리지(`O_uv = 0`)를, 노드 수준(우)에서는 낮은 인용량 대비 높은 매개 중심성을 지닌 숨은 연결 노드를 포착합니다.

![그림 3: Strong/Weak Ties 및 보이지 않는 연결 구조 산점 분석](demo/output/figures/fig3_tie_strength_vs_overlap_scatter.png)

#### 그림 4 | 3.3절 퍼콜레이션 테스트: 강한 연결은 지역 결속, 약한 연결은 전역 연결 유지
엣지 `42.3%`(`k=22`개) 제거 시 약한 연결 우선 제거는 Giant Component가 `63.6%`(`9`개 컴포넌트, AUC = `0.6098`)로 급락하는 반면, 강한 연결 우선 제거는 `90.9%`(`3`개 컴포넌트, AUC = `0.7393`)를 유지합니다.

![그림 4: 3.3절 퍼콜레이션 곡선](demo/output/figures/fig4_percolation_curve.png)

#### 그림 5 | 19.7B절 이중언어 확산 상평형 산점도 (625개 `(a, c)` 파라미터 조합)
언어 유지 구역(`B Maintained`), 이중언어 완충 공존 구역(`(1.5, 0.8)`), 침투 도태 구역(`(1.5, 0.3)`), 직접 대체 구역(`(1.5, 1.5)`)의 4가지 균형 상태를 시각화합니다.

![그림 5: 19.7B절 이중언어 확산 상평형 산점도](demo/output/figures/fig5_bilingual_phase_diagram.png)

#### 그림 6 | 표본 품질 검증(Heaps' Law + SNR 차단) 및 시계열 생존 궤적
Heaps' Law 포화 적합($\beta = 0.4446, R^2 = 0.9856$)을 통한 노이즈 배치 `Batch 7`(SNR 기울기 `-0.1143`) 자동 차단과 `2024Q1 → 2025Q4` 허브 지니계수·군집계수 변화 궤적을 보여줍니다.

![그림 6: 표본 품질 검증 및 시계열 생존 궤적](demo/output/figures/fig6_sampling_saturation_and_survival.png)
