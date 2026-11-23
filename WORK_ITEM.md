# Work Item Registry

## WO-M0-001

- **WORK_ITEM_ID:** `WO-M0-001`
- **TYPE:** `BOUNDED_WORK_ORDER`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PENDING_BRAIN_REVIEW`
- **RETURN_TO:** STUDENT-MAIN Brain

## INPUT

- STUDENT 核准的 `WO-M0-001` 正式工作單。
- 學生指定的本地專案根目錄。
- 學生已授權使用的 GitHub 帳號與目標 Repository `ntust-nasa-ai-lab`。

## AUTHORIZED_SCOPE

- 建立或修訂 `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`。
- 初始化或安全沿用 Git，確保正式分支為 `main`。
- 建立或檢查必要且安全的 `.gitignore`。
- 建立公開 GitHub Repository（僅在不存在且帳號已確認時），或安全驗證既有同名 Repository。
- 將本工作單授權成果 Commit、Push 至 `main` 並執行遠端驗證。

## READ_ONLY

- `data/`、NASA C-MAPSS FD001、`synthetic_sensor.csv`、其他五筆合成 CSV 及所有原始資料。
- 非本工作單授權的既有程式碼、設定檔、其他 Repository 與 Brain 工作區。

## OUTPUT

- 四份完整且可獨立閱讀的治理文件。
- 安全的 `.gitignore`（如有必要）。
- Git `main` Commit、公開 GitHub Repository、Push 與遠端驗證證據。
- 完整 Worker 執行報告；最終僅能回報 `PENDING_BRAIN_REVIEW`、`BLOCKED` 或 `FAILED`。

## ACCEPTANCE_CRITERIA

1. 四個 Markdown 文件完整存在，治理規則一致且無相互矛盾。
2. Git `main` 分支存在，Commit 成功且暫存內容僅含授權檔案。
3. GitHub Repository 為公開，Push 成功，遠端 `main` 與本地 HEAD 一致。
4. 四份治理文件可從 GitHub `main` 實際讀取。
5. 未提交 NASA 原始資料、合成 CSV、憑證、金鑰或私人資訊。
6. Worker 提供命令、Exit Code、測試、完整 Commit ID、Object Format、四份文件 SHA-256、Repository 與 Commit URL。
7. STUDENT-MAIN Brain 從 GitHub 獨立審查後，才可決定 `PASS`。

## STATUS_FLOW

`COMMAND_DISPATCHED` → `IN_PROGRESS` → `WORKER_COMPLETED` → `PENDING_BRAIN_REVIEW` → `PASS / REWORK / BLOCKED`

`WORKER_COMPLETED` 與 `PENDING_BRAIN_REVIEW` 均不等於 `PASS`。

## STOP_IF

- 無法確認專案根目錄、授權 GitHub 帳號、工作範圍或資料來源。
- 必須覆寫既有重要檔案、破壞 Git 歷史或解決無法安全處理的遠端衝突。
- GitHub 驗證、Commit、Push、遠端 SHA 比對或遠端檔案讀取失敗。
- 暫存區包含未授權檔案，或發現公開資料、憑證、金鑰或私人資訊的風險。
- 工作需要讀取、分析、修改、刪除、移動或上傳原始資料，或執行 M1-M5。

## EVIDENCE

- 工作目錄、Git/GitHub 工具、GitHub 登入帳號、Repository visibility 與 default branch 的實際檢查結果。
- `git diff --check`、`git diff --cached --check`、staged file 清單與安全檢查。
- 完整 Commit ID、Commit Object Format、Commit 訊息及本地/遠端 `main` SHA。
- 四份治理文件的 SHA-256、GitHub 遠端檔案 URL 與可讀取驗證。
- 所有必要命令的實際 Exit Code、測試結果、blocker 與未提交變更。

## COMMIT_MESSAGE

`chore(M0): initialize AI team governance and roadmap`

## RETURN_TO

提交 STUDENT-MAIN Brain 進行 GitHub 遠端獨立審查。M0 即使通過，仍須 STUDENT 另行授權才能派發 M1。
