# Work Item Registry

## Current Assignment

- **CURRENT_WORK_ITEM:** `WO-M0-001`
- **REVISION:** `R2`
- **TYPE:** `BOUNDED_WORK_ORDER`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **WORKER:** MAIN Own Worker (Codex)
- **STATUS:** `COMMAND_DISPATCHED`
- **AUTHORIZED_BY:** STUDENT
- **RETURN_TO:** STUDENT-MAIN Brain

## Scope

**AUTHORIZED_FILES:**

- `AGENTS.md`
- `ROADMAP.md`
- `WORK_ITEM.md`
- `DECISIONS.md`

**READ_ONLY:**

- `data/`
- NASA C-MAPSS FD001
- 所有原始 CSV

**INPUT:** 學生核准的 WO-M0-001 Revision R2、工作單恢復命令，以及既有但尚無 Commit 的本地 Git Repository。

**EXPECTED_OUTPUT:** 四份完整治理文件、Git Commit、公開 GitHub Repository `ntust-nasa-ai-lab`、`main` 遠端分支及遠端驗證證據。

**COMMIT_MESSAGE:** `chore(M0): initialize AI team governance and roadmap`

## Acceptance Criteria

- 專案根目錄及 GitHub 帳號正確。
- 四份治理文件完整且僅修改授權檔案。
- 權責邊界、唯讀政策、Git 治理及 M0-M5 Roadmap 可執行、可查核。
- `data/` 保持唯讀且未加入 Git。
- Commit 訊息正確，僅含四份授權文件。
- 公開 Repository 建立成功並 Push 至 `main`。
- 本地與遠端 Commit 一致，遠端四份文件可讀取。
- File SHA-256、Exit Code、Repository URL 及 Commit URL 均有記錄。

## Stop If

- 專案根目錄、GitHub CLI 登入或 GitHub 帳號不正確。
- 目標 Repository 已存在或 Git 歷史、origin 發生衝突。
- 暫存區包含未授權檔案。
- 作業需要讀取、修改、移動、刪除或提交 `data/` 或原始 CSV。
- 文件建立、Commit、Push 或遠端驗證失敗。
- 作業需要執行 M1-M5 或任何未授權操作。

## Evidence Required

- WORK_ITEM_ID、Revision、實際命令及 Exit Code。
- Git Commit 完整 ID、Commit Object Format 及 Commit 訊息。
- 四份治理文件 SHA-256。
- GitHub Repository URL、Commit URL、可見性及預設分支。
- 本地與遠端 `main` Commit 比對結果。
- 遠端四份檔案及無未授權檔案的驗證結果。
- `data/` 唯讀保留狀態及測試結果。

## Return Format

回報必須包含 STATUS、PROJECT_ROOT、GITHUB_ACCOUNT、GITHUB_REPOSITORY、GITHUB_COMMIT_URL、BRANCH、COMMIT_MESSAGE、COMMIT_OBJECT_FORMAT、COMMIT_SHA、COMMIT_SHA256、FILE_SHA256、EXIT_CODES、FILES_CREATED、FILES_MODIFIED、REMOTE_FILES_VERIFIED、DATA_DIRECTORY_STATUS、TEST_RESULT、EVIDENCE、LIMITATIONS、BLOCKERS 及 NEXT_ACTION。

Worker 完成並 Push 成功後，狀態為 **SUBMITTED**。Worker SUBMITTED 不等於 Brain PASS；只有 MAIN Brain 從 GitHub 獨立讀取並驗證成果後，才能將工作狀態更新為 **PASS**。M0 PASS 前不得開始 M1。
