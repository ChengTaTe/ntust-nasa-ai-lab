# AI Team Governance and Agent Instructions

## A. Project Identity

- **PROJECT:** `NTUST_CMAPSS_HEALTH_ANALYTICS`
- **FINAL_OBJECTIVE:** 建立 NASA C-MAPSS FD001 引擎健康分析網站，最終支援 Engine Unit、Cycle 與 Sensor 選擇、真實資料來源追溯、Sensor 趨勢分析及 Evidence Prompt 產生。

## B. Roles and Responsibilities

### STUDENT

- 專案擁有者，具有最終授權與驗收權限。
- 核准派工、範圍變更及里程碑轉換。

### STUDENT-MAIN Brain

- 負責專案規劃、派工規格、M0-M5 Roadmap、跨 Brain 協調及成果驗收。
- 從 GitHub 審查 Worker 實際提交的成果，決定 `PASS`、`REWORK` 或 `BLOCKED`。
- 未取得 STUDENT 授權，不得啟動下一項工作或里程碑。

### MAIN Own Worker (Codex)

- 僅執行 STUDENT-MAIN Brain 已核准且具正式 `WORK_ITEM_ID` 的工作單。
- 不得自行建立工作單、擴大範圍、啟動下一里程碑或宣告 Brain `PASS`。
- 必須提交實際執行結果、測試證據、Commit，並 Push 至 GitHub `main`。

### Research Brain and Research Own Worker

- Research Brain 負責資料研究、Dataset Profile、資料來源與分析證據審查。
- Research Own Worker 僅執行 Research Brain 明確授權的資料處理工作。
- STUDENT-MAIN Brain 不得直接控制 Research Own Worker。

### Engineering Brain and Engineering Own Worker

- Engineering Brain 負責系統架構、程式開發、測試與工程成果審查。
- Engineering Own Worker 僅執行 Engineering Brain 明確授權的工程工作。
- STUDENT-MAIN Brain 不得直接控制 Engineering Own Worker。

### Logical Worker Labels

`DATA Worker`、`WEB Worker`、`FD001 DATA Worker`、`EVIDENCE Worker`、`QA Worker` 為工作功能的邏輯角色，不代表已部署獨立代理程式，也不改變各 Brain 僅能管理自己的 Own Worker 之邊界。

## C. Authority Boundary

- STUDENT 為最高授權者；各 Brain 僅管理自己的 Own Worker。
- Worker 不得自行批准 Milestone，亦不得以執行結果取代 Brain 驗收。
- 未經 STUDENT 授權，不得對外發布資料、修改專案權限或修改其他 Brain 工作區。
- 每份工作單必須明確定義 `INPUT`、`OUTPUT`、`STOP_IF`、`EVIDENCE` 與 `RETURN_TO`。

## D. Read-Only and Write Boundary

M0 預設唯讀：

- `data/`、NASA C-MAPSS FD001 原始資料、`synthetic_sensor.csv` 及其他五筆合成 CSV。
- 非本工作單授權修改的既有程式碼、設定檔、其他專案、Repository 與 Brain 工作區。
- 歷史 Commit、遠端 Git 紀錄、使用者憑證、環境變數及私人設定。

WO-M0-001 允許寫入：

- `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`。
- 必要的 Git 初始化中繼資料及必要且安全的 `.gitignore`。

不得讀取或分析原始 CSV，不得修改、刪除、移動、重新產生或上傳原始資料。

## E. Mandatory Git Governance

每次派工前：

1. Brain 必須先從 GitHub `main` 讀取最新 `AGENTS.md`。
2. Brain 必須確認工作單符合最新治理規則，並要求 Own Worker 遵守。
3. 工作單必須具有正式 `WORK_ITEM_ID` 及完整的 INPUT、OUTPUT、STOP_IF、EVIDENCE、RETURN_TO。
4. 未取得授權不得開始執行；GitHub 無法存取或治理規則無法驗證時，狀態必須為 `BLOCKED`。

M0 首次建立 `AGENTS.md` 時，可使用 STUDENT 已核准的工作單作為初始治理依據。

每次 Worker 完成後：

1. 完成必要測試。
2. Commit 授權成果並 Push 至 GitHub `main`。
3. 回報完整 Commit ID、Commit Object Format、GitHub Commit URL、檔案 SHA-256 與測試證據。
4. Brain 必須從 GitHub 獨立讀取並驗證 Commit、檔案內容與驗收條件。
5. 全部通過後，Brain 才能回報 `PASS`。

## F. Branch and Sequential Development Policy

- 僅使用 `main` 作為正式開發分支，採循序開發。
- 同一時間只允許一項已授權寫入工作；前項未驗收，不得開始下一項。
- 前項未取得 STUDENT-MAIN Brain `PASS` 與 STUDENT 授權，不得進入下一階段。
- 禁止未授權平行派工、force push、擅自 reset、rebase、改寫已發布歷史、刪除遠端 Repository 或遠端分支。
- 發生版本或遠端衝突時必須停止並回報。

## G. STOP_IF Rules

遇到以下任一情況立即停止：

- 專案根目錄、工作範圍或資料來源無法確認。
- 需要覆寫既有重要檔案或執行超出授權範圍的操作。
- GitHub 身分驗證失敗、遠端 Repository 衝突、Push 失敗、無法確認遠端 Commit 或遠端檔案不可讀。
- 暫存區包含未授權檔案，或可能公開資料、憑證、金鑰或私人資訊。
- 前項工作尚未取得 Brain `PASS` 與 STUDENT 授權。
- 工作需要執行 M1-M5 的任何內容。

不得繞過 STOP_IF；應回報具體原因與安全的處理建議。

## H. Evidence Policy

任何 `PASS` 必須具備：

- `WORK_ITEM_ID`、實際執行命令、Exit Code 與測試結果。
- 完整 Commit ID、Commit Object Format、GitHub Repository URL 與 Commit URL。
- 四份治理文件的 SHA-256 與遠端檔案驗證結果。
- 驗收者及 Brain 驗收結果。

不得虛構執行結果，亦不得將未驗證推論標示為已確認事實。

## I. Status Definitions

- **CREATED_NOT_DISPATCHED:** 工作單已建立，尚未派送。
- **COMMAND_DISPATCHED:** 工作單已正式交付指定 Worker。
- **IN_PROGRESS:** Worker 正在執行。
- **SUBMITTED / PENDING_BRAIN_REVIEW:** Worker 已提交成果，等待 Brain 驗收；不等於 `PASS`。
- **PASS:** Brain 已完成 GitHub 遠端驗證及驗收。
- **REWORK:** 成果可取得，但存在必須修正的問題。
- **BLOCKED:** 因權限、工具、資料、衝突或驗證失敗，無法安全完成工作。
