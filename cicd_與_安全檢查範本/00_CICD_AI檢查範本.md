# CI/CD 與 Push 前 AI 自動檢查範本（`ci/cd.md` 規則與審查 Prompt 範本）

> 本檔案為「純文字 Markdown 規格與 AI Prompt 檢查範本（`ci/cd.md` 風格）」，可直接提供給組員、Antigravity / Cursor / Claude / Gemini 等 AI 助理閱讀執行，並與資料夾內的自動化程式（`pre_push_security_check.py`、`ai_pr_reviewer.py`、`install_git_hooks.sh` 及 `.github/workflows/ci_ai_security_and_gates.yml`）一一對應。

---

## 一、為什麼同時有 `.md` 範本與 `.py` / `.sh` / `.yml`？

| 類型 | 檔案 | 在系統中的角色 |
| :--- | :--- | :--- |
| **Markdown 規範與 Prompt 範本（`ci/cd.md`）** | 本檔 `00_CICD_AI檢查範本.md` | **給「人與 AI 助理」看**：定義檢查標準、可上傳／禁上傳判定準則、可直接貼給 AI 審查程式碼與 Diff 的 Prompt。 |
| **本地端 Push 前自動卡控** | `.gitignore`、`.gitleaks.toml`、`install_git_hooks.sh`、`pre_push_security_check.py` | **給「本機 Git Hook」跑**：在 `git commit` / `git push` 按下 Enter 的瞬間自動掃描並阻擋誤推機敏檔或版權 PDF。 |
| **本地＋雲端 AI Diff 審查腳本** | `ai_pr_reviewer.py` | **給「Push 前與 Pull Request」跑**：有設定 `GEMINI_API_KEY` 時呼叫 Gemini 進行語意審查，離線時自動改用規則備援。 |
| **GitHub Actions CI/CD 管線** | `.github/workflows/ci_ai_security_and_gates.yml` | **給「GitHub 雲端伺服器」跑**：組員推上分支或開 PR 時，自動重跑安全審計、執行 `run_demo_pipeline.py` 驗證 `G1–G6`，並自動在 PR 留言。 |

---

## 二、可直接複製使用的 AI Pre-Push 審查 Prompt 範本

每次準備執行 `git push` 或發起 Pull Request 與組員討論前，可將以下 Prompt 貼給 AI 助理執行檢查：

```markdown
請擔任本專題（Networks, Crowds, and Markets：台語世代傳承與海外隱形連結）的 CI/CD 與資安合規審查員。
請依序檢查即將推上 GitHub 的變更清單與 Git Diff，並逐項回報 `PASS` / `WARNING` / `BLOCK`：

1. [CHECK-01] 金鑰與憑證檢查：
   - 確認無 API Key（AIza... / sk-... / ghp_... / AKIA...）、Private Key、.env 檔。
2. [CHECK-02] 登入狀態與 Cookie 檢查：
   - 確認無真實社群登入 Cookie（c_user= / xs= / sessionid=）、cookies.txt、auth_state.json、session.json，且爬蟲程式碼沒有注入私人 Cookie。
3. [CHECK-03] 個人對話連結檢查：
   - 確認無包含個人 Gemini 對話網址（如 https://gemini.google.com/app/...）的 PDF（例如參考筆記 PDF 須留在 .gitignore）。
4. [CHECK-04] 課程版權教材隔離檢查：
   - 確認 Git 根目錄僅在 `期未/` 內，未誤將父層受版權保護的 `課本_pdf/`、`課本_文字/` 或含 Cambridge Core / 校方下載浮水印之原文 PDF 納入版本控制。
5. [CHECK-05] 本機路徑與環境變數檢查：
   - 確認無硬編碼本機帳號路徑（如 `/Users/<local_user>/` 或 `C:\Users\<local_user>\`）。
   - 確認程式內的去識別鹽值優先透過環境變數 `os.environ.get("TAIGI_PII_SALT", ...)` 注入，而非寫死正式環境密碼。
6. [CHECK-06] 合法合成基準、引用資料與教學偽碼辨識（避免誤判）：
   - 規劃書內的演算法說明（例如 `hash_user_id` 教學偽碼、防範私人 Cookie 的文字規範）屬安全內容，判定為 `PASS`。
   - 有明確引用來源、去識別雜湊化之合成基準資料（`demo/data/`）與演算法算出之統計結果／圖表（`demo/output/`）皆屬可公開討論與再現之內容，判定為 `PASS`。
   - 僅當發現「未去敏的真實平台個資（Email、電話、未雜湊原始帳號）」或「`raw_unmasked/`」時才觸發 `BLOCK`。
7. [CHECK-07] 演算法與驗收閘門同步（若修改了程式或資料）：
   - 若此次變更包含 `demo/src/` 或 `demo/data/`，確認已執行 `python3 demo/src/run_demo_pipeline.py` 且 `G1–G6` 全數為 `PASS`。

請輸出格式：
- 整體結論：`READY TO PUSH` 或 `BLOCKED`
- `[BLOCK]` 清單（若無請寫 None）
- `[WARNING]` 清單（例如外部斷鏈提醒、環境注意事項）
- `[RECOMMENDATION]` 給組員 PR 討論的建議事項
```

---

## 三、組員協作 GitHub Pull Request（PR）檢查表

當你或同組同學開 Pull Request 討論研究進度時，GitHub Actions 會自動檢查；平時討論也可對照以下清單：

- [ ] 確認本次新增或修改的檔案不包含個人參考 PDF、教科書原文檔案或 `.DS_Store`。
- [ ] 若調整了 HITS、Strong/Weak Ties 或取樣參數，已附上更新後的 `demo/output/figures/*.png` 或確認 CI `automated-verification-gates` 綠燈。
- [ ] 若未來串接公開真實資料源，已設定 `.gitignore` 隔離原始爬蟲暫存，且匯出 CSV/SQLite 均經過 `TAIGI_PII_SALT` 雜湊去敏並明確標註引用來源。
- [ ] 若只是補充研究文獻討論或修改 `demo/plain/` 規劃書，經 [pre_push_security_check.py](pre_push_security_check.py) 掃描確認 `0 BLOCK` 後即可直接 Push／Merge。

---

## 四、對應的本地一鍵檢查指令

```bash
# 1. 執行純規則與去敏、版權掃描（不需 API Key）
python3 cicd_與_安全檢查範本/pre_push_security_check.py --strict-ci

# 2. 執行 AI Diff 合規審查（支援 GEMINI_API_KEY 或離線啟發式模式）
python3 cicd_與_安全檢查範本/ai_pr_reviewer.py --diff-mode workspace --strict

# 3. 驗證專題運算與 G1-G6 驗收閘門
python3 demo/src/run_demo_pipeline.py
```
