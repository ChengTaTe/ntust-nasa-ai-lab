# Work Item Registry

## WO-M0-001

- **WORK_ITEM_ID:** `WO-M0-001`
- **TYPE:** `BOUNDED_WORK_ORDER`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
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

## M0 Acceptance Record for WO-M0-001

- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **BRAIN_REVIEW_RECORDED_DATE:** `2026-11-23`
- **ACCEPTED_SOURCE_COMMIT:** `c3742e3b332d77d17b32881776467492777647d9`
- **COMMIT_OBJECT_FORMAT:** `sha1`
- **GITHUB_REPOSITORY:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab>
- **GITHUB_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/c3742e3b332d77d17b32881776467492777647d9>

### M0_ACCEPTANCE_EVIDENCE

STUDENT-MAIN Brain 已確認：

- GitHub Repository 為公開，預設分支為 `main`。
- 遠端 Commit SHA 符合 WO-M0-001 Worker 回報。
- 遠端 `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md` 可讀。
- 治理文件主要內容符合 WO-M0-001，包括角色與權限邊界、M0-M5 循序 Roadmap、正式工作單及 GitHub 遠端驗收規則。
- 原始 Commit 僅涉及 `.gitignore`、`AGENTS.md`、`DECISIONS.md`、`ROADMAP.md`、`WORK_ITEM.md` 五份授權檔案。
- 遠端檔案樹未包含原始 CSV。

STUDENT-MAIN Brain 未獨立確認：

- WO-M0-001 完成時的本地工作樹狀態。
- 四份治理文件的 SHA-256 是否由 Brain 獨立重新計算。

上述未獨立確認項目保留為驗收限制，不得改寫為已驗證通過。此 PASS 為 STUDENT-MAIN Brain 對 WO-M0-001 的驗收決議；原始 Worker 執行與提交紀錄由來源 Commit 及既有工作單內容持續保留。

---

## WO-M0-002

- **WORK_ITEM_ID:** `WO-M0-002`
- **TYPE:** `BOUNDED_WORK_ORDER`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RETURN_TO:** STUDENT-MAIN Brain
- **OBJECTIVE:** Synchronize M0 acceptance evidence.
- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **ACCEPTED_COMMIT:** `1b40db6e7657ba2062298a625d174ce2effd288c`
- **ACCEPTED_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/1b40db6e7657ba2062298a625d174ce2effd288c>

### WO-M0-002 Brain Acceptance Evidence

STUDENT-MAIN Brain 已確認：

- 已從 GitHub 獨立讀取 Commit `1b40db6e7657ba2062298a625d174ce2effd288c`。
- 該 Commit 僅修改 `WORK_ITEM.md`。
- WO-M0-001 的 `CURRENT_STATUS` 為 `PASS`。
- WO-M1-001 的 `DISPATCH_STATUS` 為 `CREATED_NOT_DISPATCHED`，尚未正式派送。
- 驗收時遠端 `main` SHA 與 Worker 回報一致。

STUDENT-MAIN Brain 驗收限制：

- `WORK_ITEM.md` SHA-256 尚未由 Brain 獨立重新計算。
- Worker 本地執行命令及 Exit Code 以 Worker 回報為據。

上述限制不得改寫為已由 Brain 驗證通過。

### WO-M0-002 Scope and Result Boundary

- 僅同步 WO-M0-001 Brain PASS 驗收決議、追溯資訊及後續工作單登錄。
- 僅允許修改 `WORK_ITEM.md`，不得修改其他治理文件、資料、程式碼或設定。
- Worker 完成 Commit 與 Push 後仍須 STUDENT-MAIN Brain 從 GitHub 獨立驗收；`PENDING_BRAIN_REVIEW` 不等於 `PASS`。

---

## WO-M0-003

- **WORK_ITEM_ID:** `WO-M0-003`
- **TYPE:** `GOVERNANCE_STATUS_SYNC_AND_DATASET_PATH_INVENTORY`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RETURN_TO:** STUDENT-MAIN Brain
- **OBJECTIVE:** 同步 WO-M0-002 Brain PASS，並唯讀盤點本地合成 CSV 路徑。
- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **ACCEPTED_COMMIT:** `10967948bdabfb99d9811443ef6a042013df315b`
- **ACCEPTED_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/10967948bdabfb99d9811443ef6a042013df315b>

### Local CSV Path Inventory

- **INVENTORY_SCOPE:** 僅列舉 `data/` 下 CSV 的檔名、相對路徑及存在狀態。
- **EXPECTED_CSV_COUNT:** `6`
- **ACTUAL_CSV_COUNT:** `1`
- **CSV_INVENTORY_STATUS:** `INCOMPLETE`
- **CONFIRMATION_STATUS:** `PENDING_MAIN_STUDENT_CONFIRMATION`
- **CSV_CONTENT_READ:** `NO`
- **CSV_ANALYSIS_EXECUTED:** `NO`

盤點結果：

- **REQUIRED_RELATIVE_PATH:** `data/intro/synthetic_sensor.csv`
- **REQUIRED_PATH_EXISTS:** `NO`
- **CANDIDATE_1_RELATIVE_PATH:** `data/._synthetic_sensor.csv`
- **CANDIDATE_1_EXISTS:** `YES`

實際數量不等於六，且指定路徑不存在。以上僅為唯讀路徑盤點結果；未指定候選檔案為正式資料、未補造缺少的檔案、未讀取 CSV 內容，亦不得將本盤點視為 M1 資料驗收。

---

## WO-M0-004

- **WORK_ITEM_ID:** `WO-M0-004`
- **TYPE:** `GOVERNANCE_STATUS_SYNC_AND_DATASET_PATH_INVENTORY`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RETURN_TO:** STUDENT-MAIN Brain
- **OBJECTIVE:** 同步 WO-M0-003 Brain PASS，並重新盤點 STUDENT 指定的正確 DATA_ROOT。
- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **ACCEPTED_COMMIT:** `ee71838b045ab591dc762067cf005bb453d4e2ee`
- **ACCEPTED_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/ee71838b045ab591dc762067cf005bb453d4e2ee>

### DATA_ROOT Re-Inventory

- **STUDENT_SPECIFIED_DATA_ROOT:** `C:\Users\user\OneDrive\文件\ChatGPT\NTUST_261123\data`
- **DATA_ROOT_EXISTS:** `YES`
- **INVENTORY_SCOPE:** 僅在上述 DATA_ROOT 及其子目錄列舉 `.csv` 檔名、相對路徑、存在狀態與 `._` 前綴分類。
- **CSV_COUNT:** `1`
- **CSV_INVENTORY_STATUS:** `INCOMPLETE`
- **DATASET_IDENTITY_STATUS:** `UNCONFIRMED`
- **CSV_CONTENT_READ:** `NO`
- **CSV_ANALYSIS_EXECUTED:** `NO`

本次實際盤點結果：

- **CSV_1_NAME:** `synthetic_sensor.csv`
- **CSV_1_RELATIVE_PATH:** `data/synthetic_sensor.csv`
- **CSV_1_EXISTS:** `YES`
- **CSV_1_IS_DOT_UNDERSCORE:** `NO`

`._` 前綴候選中繼資料檔：`NONE_FOUND`。

本次檢查未預設任何檔案存在，亦未以 WO-M0-003 的先前盤點取代實際檢查。實際找到一份 CSV，少於預期六份；未自行補造、挑選或認定其為正式 M1 資料集。檔案內容、欄位、資料列、Length、LastWriteTime 與內容雜湊均未讀取或計算，本紀錄不代表 M1 PASS。

---

## WO-M0-005

- **WORK_ITEM_ID:** `WO-M0-005`
- **TYPE:** `DATA_CONTRACT_GOVERNANCE_SYNC`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RETURN_TO:** STUDENT-MAIN Brain
- **OBJECTIVE:** 同步 WO-M0-004 Brain PASS，並修正 M1 資料契約治理文件。
- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **ACCEPTED_COMMIT:** `07f256744307c177f1d8720c74c69b584cb6ec40`
- **ACCEPTED_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/07f256744307c177f1d8720c74c69b584cb6ec40>

### Approved M1 Data Contract

- **DATASET_PATH:** `data/synthetic_sensor.csv`
- **DATASET_TYPE:** `Synthetic Sensor Data`
- **EXPECTED_CSV_COUNT:** `1`
- **EXPECTED_DATA_ROWS:** `6`
- **HEADER_INCLUDED_IN_ROW_COUNT:** `NO`
- **ACTUAL_DATA_ROWS:** `NOT_VERIFIED`
- **CSV_CONTENT_READ:** `NO`
- **CSV_ANALYSIS_EXECUTED:** `NO`

本工作單僅同步 STUDENT 核准的資料契約，未驗證實際資料列數、欄位、格式或資料內容。WO-M0-003 與 WO-M0-004 的原始盤點證據保留不變；舊有「六份 CSV」假設已由 STUDENT 修正為「一份 CSV、預期六筆資料列」。

---

## M0 Final Closure Record

- **M0_GATE:** `PASS`
- **M0_CLOSURE_STATUS:** `COMPLETED`
- **M0_ACCEPTED_WORK_ITEMS:** `WO-M0-001 THROUGH WO-M0-005`
- **M1_GATE:** `AUTHORIZED_PENDING_RESEARCH_RECHECK`

M0 已依 STUDENT 與 STUDENT-MAIN Brain 的驗收決議完成治理結案。GitHub 同步完成後，Research Brain 必須重新讀取最新 `AGENTS.md` 與 `WORK_ITEM.md`，重新執行治理 preflight；不得直接假定 Research Own Worker 已啟動或 M1 已完成。

---

## WO-M0-006

- **WORK_ITEM_ID:** `WO-M0-006`
- **TYPE:** `FINAL_M0_GOVERNANCE_CLOSURE`
- **MILESTONE:** `M0`
- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **AUTHORIZED_BY:** STUDENT
- **AUTHORIZATION_SCOPE:** `FINAL_M0_CLOSURE`
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RETURN_TO:** STUDENT-MAIN Brain
- **OBJECTIVE:** 一次完成 M0 最終治理狀態同步，解除 M1 Research Brain 的治理狀態阻擋。
- **BRAIN_REVIEW:** `COMPLETED`
- **BRAIN_DECISION:** `PASS`
- **REVIEWER:** STUDENT-MAIN Brain
- **ACCEPTED_COMMIT:** `e5114d833cec7a6a7ae82a85c62bbabd7fc83271`
- **ACCEPTED_COMMIT_URL:** <https://github.com/ChengTaTe/ntust-nasa-ai-lab/commit/e5114d833cec7a6a7ae82a85c62bbabd7fc83271>

WO-M0-006 的 Worker 完成與 GitHub Push 不等於 Brain PASS。STUDENT-MAIN Brain 將從 GitHub 獨立驗收後正式結案；不要求另開工作單同步 WO-M0-006 的 PASS。

---

## WO-M1-001

- **WORK_ITEM_ID:** `WO-M1-001`
- **MILESTONE:** `M1`
- **OWNER:** STUDENT-MAIN Brain
- **TARGET:** STUDENT-RESEARCH Brain
- **AUTHORIZED_BY:** STUDENT
- **AUTHORIZATION_STATUS:** `APPROVED`
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **CURRENT_STATUS:** `PASS`
- **RESEARCH_BRAIN_ACK:** `ACK`
- **GOVERNANCE_PREFLIGHT:** `PASS`
- **RESEARCH_WORKER_WORK_ITEM_ID:** `WO-M1-001-RW-001`
- **RESEARCH_WORKER_REVISION:** `2`
- **RESEARCH_WORKER_DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **RESEARCH_WORKER_EXECUTION_STATUS:** `COMPLETED`
- **RESEARCH_BRAIN_REVIEW:** `COMPLETED`
- **RESEARCH_BRAIN_DECISION:** `PASS`
- **RESEARCH_DOMAIN_ACCEPTANCE:** `PASS`
- **GITHUB_REMOTE_VERIFICATION:** `PASS`
- **MAIN_BRAIN_REVIEW:** `COMPLETED`
- **MAIN_BRAIN_DECISION:** `PASS`
- **M1_COMPLETION_STATUS:** `COMPLETED`
- **ACCEPTED_COMMIT:** `0ba0a16c1e6904a389fef87b66389662cf0737b3`
- **RETURN_TO:** STUDENT-MAIN Brain
- **DATASET_PATH:** `data/synthetic_sensor.csv`
- **DATASET_TYPE:** `Synthetic Sensor Data`
- **EXPECTED_CSV_COUNT:** `1`
- **EXPECTED_DATA_ROWS:** `6`
- **HEADER_INCLUDED_IN_ROW_COUNT:** `NO`
- **ACTUAL_DATA_ROWS:** `6`
- **COLUMN_COUNT:** `4`
- **MISSING_VALUE_COUNT:** `1`
- **DUPLICATE_ADDITIONAL_ROW_COUNT:** `1`
- **CONTRACT_RESULT:** `MATCH`
- **FORMAT_VALIDATION:** `PASS`
- **DATASET_PROFILE:** `outputs/INTRO_PROFILE.md`
- **REPRODUCIBLE_PROFILER:** `tools/profile_intro.py`

### Research Brain Blocked History — Historical Record

Research Brain 曾因 GitHub 治理狀態尚未同步 M0 結案與 M1 正式授權而停止派工。該 BLOCKED 回報保留為歷史證據，不得改寫為已完成的 PASS。

其後 Research Worker 工作單 `WO-M1-001-RW-001` 已正式派送，但執行狀態回報為 `BLOCKED`。本同步保留該 BLOCKED 歷史，不將其改寫為 PASS，亦不宣稱 Research Worker 已恢復執行。

以上敘述為已過期但必須保留的歷史執行狀態。其後 Research Brain 已完成獨立審查並決定 PASS，STUDENT-MAIN Brain 亦已接受 M1 實質成果；目前狀態以本節上方的正式狀態欄位為準。

### Accepted Evidence and Research Limitations

- **ACCEPTED_RESEARCH_COMMIT:** `0ba0a16c1e6904a389fef87b66389662cf0737b3`
- **ACCEPTED_RESEARCH_WORKER:** `WO-M1-001-RW-001`
- **WORK_ORDER_REVISION:** `2`
- **ACCEPTED_DELIVERABLES:** `outputs/INTRO_PROFILE.md`, `tools/profile_intro.py`
- Dataset Profile 與可重現 profiler 為 Research Brain 及 STUDENT-MAIN Brain 接受之證據來源。
- 原始 CSV 維持本地唯讀且未提交 GitHub；GitHub 僅保存分析文件與可重現工具。
- 本資料為合成 Sensor 資料，不等於 NASA C-MAPSS FD001，亦不得外推為真實 FD001 整合成果。
- 合成資料的生成來源限制已於 Dataset Profile 揭露並由 Brain 接受；該限制仍適用於後續解讀。

---

## M1 Final Closure Record

- **CLOSURE_WORK_ITEM_ID:** `WO-M1-001-CLOSURE`
- **TYPE:** `FINAL_M1_GOVERNANCE_CLOSURE`
- **AUTHORIZED_BY:** STUDENT
- **AUTHORIZATION_STATUS:** `APPROVED`
- **DISPATCH_STATUS:** `COMMAND_DISPATCHED`
- **AUTHORIZED_WRITE_SCOPE:** `WORK_ITEM.md`, `ROADMAP.md`
- **CLOSURE_BASIS:** Research Brain PASS and STUDENT-MAIN Brain M1 substantive-result PASS
- **M0_GATE:** `PASS`
- **M0_CLOSURE:** `FINAL`
- **M1_GATE:** `PASS`
- **M1_CLOSURE_STATUS:** `COMPLETED`
- **M2_AUTHORIZATION:** `NOT_GRANTED`
- **M2_EXECUTION:** `NOT_STARTED`
- **SYNC_WORKER_STATUS:** `PENDING_MAIN_BRAIN_REVIEW`

本工作單僅同步既有 M1 驗收決議，不屬於新的研究分析工作。Worker 完成 Commit 與 Push 不等於本同步工作單的 Brain PASS；由 STUDENT-MAIN Brain 完成遠端驗證後正式結案，且不另建立僅為同步本工作單 PASS 的後續工作單。
