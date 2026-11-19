# GitHub 上傳風險評估與資料去敏清單

本報告針對目前工作區內所有規劃文件、原始參考資料、Demo 程式碼、基準資料集與輸出圖表，依照 **版權合規、個人隱私、資訊安全與跨環境可攜性** 四大面向進行紅／黃／綠燈盤點。

---

## 一、總結結論：哪些東西絕對不能放上 GitHub？

1. **禁止上傳父層教科書資料夾（`課本_pdf/` 與 `課本_文字/`）**：內含 Cambridge University Press 版權之 *Networks, Crowds, and Markets* 原文 PDF，且帶有大學端下載來源與使用條款浮水印；轉出的文字與圖檔亦屬衍生原文複本。**正確做法是僅將 `期未/` 設為 Git 根目錄**。
2. **禁止上傳 `期未/網路社群資料取得方法與技術.pdf`**：該 PDF（28 頁）頁首／頁尾與超連結內含個人 Gemini 對話分享網址（`https://gemini.google.com/app/<SHARE_ID>`），公開上傳會暴露個人帳號對話記錄。**已透過 `.gitignore` 自動排除**。
3. **禁止上傳未去敏實測資料與身分憑證**：未來若擴充為真實爬蟲抓取（非目前 Synthetic Demo），任何真實臉書／IG／Threads 用戶原始帳號名稱、貼文原文 PII、`cookies.txt`、`auth_state.json`、`.env` 與 `raw_unmasked/` 皆禁止進 Git。
4. **已順手修復兩處黃燈風險**：
   - `demo/plain/05_驗收規劃與交付檢核表.md`：原指令含本機使用者名稱路徑，已改為跨機器可用的相對指令 `python3 demo/src/run_demo_pipeline.py`。
   - `demo/src/run_demo_pipeline.py`：原寫死 `SALT` 固定字串，已改為優先讀取環境變數 `os.environ.get("TAIGI_PII_SALT", "ncm_taigi_2026_demo_only_salt")`。

---

## 二、逐檔風險評估清單（紅 / 黃 / 綠燈）

### 🔴 紅燈：禁止上傳 GitHub（須留置父層或由 `.gitignore` 阻擋）

| 檔案／資料夾 | 所在位置 | 實測風險證據 | 處置狀態與建議 |
| :--- | :--- | :--- | :--- |
| `課本_pdf/`（37 個 PDF，約 24 MB+） | 父層目錄（`期未/` 外） | 帶有 `Downloaded from https://www.cambridge.org/core` 與 `National Yang Ming Chiao Tung University`、`Cambridge Core terms of use` 版權浮水印。 | **勿納入 Git**；僅在 `期未/` 執行 `git init`，且已於 `.gitignore` 與 `pre_push_security_check.py` 雙重防呆。 |
| `課本_文字/`（29 個 MD + `images/`） | 父層目錄（`期未/` 外） | 由上述版權 PDF 抽取的章節全文與圖表，屬教材重製內容。 | **勿納入 Git**；若須引用理論，請在規劃書中使用章節編號與自我摘要，勿貼整段原文。 |
| `網路社群資料取得方法與技術.pdf`（1.49 MB，28 頁） | `期未/` 內 | 每頁頁首／頁尾與連結含個人對話網址 `https://gemini.google.com/app/<SHARE_ID>`。 | **已加入 `.gitignore`**；`[SEC-03]` 規則會主動偵測並確認其處於被忽略狀態。 |
| `.DS_Store` | 父層目錄（未來亦可能於 `期未/` 產生） | macOS 資料夾檢視中繼檔，屬環境雜訊。 | **已加入 `.gitignore`**，禁止追蹤。 |
| `raw_unmasked/`、`cookies.txt`、`auth_state.json`、`.env`（未來實作可能產生） | 尚未產生（預先防護） | 若未來執行真實爬蟲卻未隔離原始資料或儲存 Session Cookie，會造成嚴重隱私與帳號盜用風險。 | **已預先列入 `.gitignore`、`.gitleaks.toml` 與 AI PR Reviewer 阻擋規則**。 |

---

### 🟡 黃燈：已修復或屬非機敏連結提醒（可上傳，僅需留意使用邊界）

| 檔案／資料夾 | 原先風險或需注意項目 | 已完成調整與 GitHub 上傳說明 |
| :--- | :--- | :--- |
| [`demo/plain/05_驗收規劃與交付檢核表.md`](../demo/plain/05_驗收規劃與交付檢核表.md) | 原第 24 行寫有執行機本機絕對路徑（曝露 macOS 使用者目錄名稱），且在他人電腦無法直接執行。 | **已修正**：改為相對路徑 `python3 demo/src/run_demo_pipeline.py`（現已安全可上傳）。 |
| [`demo/src/run_demo_pipeline.py`](../demo/src/run_demo_pipeline.py) | 原第 41 行硬編碼 `SALT` 固定常數；公開 repo 中暴露生產環境鹽值會削弱去識別保護。 | **已修正**：改為 `os.environ.get("TAIGI_PII_SALT", "ncm_taigi_2026_demo_only_salt")`，同時明確標示 `demo_only`。正式抓真實個資時請以環境變數注入獨立 Production Salt。 |
| [`期末專題規劃_台語世代傳承與海外隱形連結.md`](../期末專題規劃_台語世代傳承與海外隱形連結.md) | 內含連往 `../課本_文字/...` 的相對 Markdown 連結。無個資或金鑰外洩，但因 `課本_文字/` 不會上傳至 GitHub，點擊會產生 404 斷鏈。 | **可上傳（無資安風險）**：已於 `ai_pr_reviewer.py` 列出 Warning 提醒；可視需求日後手動改為純文字章節引用。 |

---

### 🟢 綠燈：完全安全，建議隨專題一起上傳 GitHub（與組員討論／再現驗證）

- [`README.md`](../README.md)（首頁說明、合成基準與隱私聲明）
- [`題目.md`](../題目.md)
- [`社群資料取得與Hubs_Authorities辨識計算計畫.md`](../社群資料取得與Hubs_Authorities辨識計算計畫.md)、[`demo/plain/01_資料源與參考資料規劃.md`](../demo/plain/01_資料源與參考資料規劃.md)、[`demo/plain/04_研究限制與PreMortem分析及案例.md`](../demo/plain/04_研究限制與PreMortem分析及案例.md)（規劃書內的 `hash_user_id` 範例函式與「禁止使用私人 Cookie」屬學術防呆規範與教學偽碼，不含真實憑證；僅須知道部分通用關鍵字掃描器有時會對 `salt` / `Cookie` 字眼敏感，本專案的 `.gitleaks.toml` 與 `pre_push_security_check.py` 已排除此類誤判）
- [`demo/plain/00_總覽與執行架構規劃.md`](../demo/plain/00_總覽與執行架構規劃.md) ～ [`06_圖論與Strong_Weak_Ties視覺化解析.md`](../demo/plain/06_圖論與Strong_Weak_Ties視覺化解析.md)（其中 `05` 已去除本機路徑）
- **`demo/data/` 合成基準與去敏資料集**（`nodes_metadata.csv`、`interactions_raw.csv`、`corpus_batches.json`、`taigi_network.sqlite`）：全數為合成模擬角色（25 節點、128 條邊）與 16 碼 hex SHA-256 雜湊 ID，並於 `README.md` 明確標示來源與合成聲明；任何經過清楚引用與去敏處理的計算基礎資料皆可放心推上 GitHub 供組員檢視討論（僅禁推 `raw_unmasked/` 未去敏真實個資）
- **`demo/output/` 演算法輸出與計算結果**（`*.csv`、`*.json`、`demo/執行成果與驗收報告.md` 與 `demo/output/figures/fig1..fig6.png`，單張圖檔最高約 1.06 MB，安全可上傳）
- 整套防護與 CI/CD 範本：`.gitignore`、`.gitleaks.toml`、`.pre-commit-config.yaml`、`.github/workflows/ci_ai_security_and_gates.yml` 與 `cicd_與_安全檢查範本/` 內所有檔案（含純文字版 [`00_CICD_AI檢查範本.md`](00_CICD_AI檢查範本.md)）。

---

## 三、正式推上 GitHub 前的最後 3 步檢查

1. 確認工作目錄在 `期未/`（**不是**上一層 `Networks, Crowds, and Markets/`）。
2. 重新執行 Pipeline，確認更新環境變數讀法後的雜湊與 `G1–G6` 門檻全數通過：
   ```bash
   python3 demo/src/run_demo_pipeline.py
   ```
3. 執行 Push 前安全掃描，確認推播清單 `block_count == 0`：
   ```bash
   python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci
   ```
