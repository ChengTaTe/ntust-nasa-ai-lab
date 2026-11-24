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

### STUDENT-WEB Brain and Web Own Worker

- STUDENT-WEB Brain 負責 FD001 資料查詢 API、本地網站、Engine Unit／Cycle／Sensor 選擇器、資料明細、趨勢視圖、Evidence Prompt Generator、Browser User Acceptance Testing 與網站成果獨立驗收。
- Web Own Worker 僅執行 STUDENT-WEB Brain 正式授權的工作，並遵守已驗收的 FD001 Data Contract。
- Web Own Worker 不得自行變更資料契約、直接修改原始資料、擴大工作範圍或宣告 Brain `PASS`。
- Web Own Worker 必須完成工作單要求的測試、Commit、Push 與證據回報。
- STUDENT-MAIN Brain 不得直接控制 Web Own Worker。

### Cross-Brain Responsibility Boundaries

- Research Brain：資料研究、資料契約及資料證據正確性。
- Engineering Brain：系統架構、跨元件整合及工程驗證。
- STUDENT-WEB Brain：API、網站、Evidence Prompt 及 Browser UAT。
- STUDENT-MAIN Brain：治理、跨 Brain 協調及里程碑驗收。
- 所有 Brain 僅能管理自己的 Own Worker；STUDENT-MAIN Brain 不得直接派工給 Research、Engineering 或 Web Own Worker。

### Logical Worker Labels

`DATA Worker`、`WEB Worker`、`FD001 DATA Worker`、`EVIDENCE Worker`、`QA Worker` 為工作功能的邏輯標籤，不代表已部署獨立代理程式。`WEB Worker` 功能標籤不得與正式的 STUDENT-WEB Brain 或 Web Own Worker 混淆，亦不改變各 Brain 僅能管理自己的 Own Worker 之邊界。

## C. Authority Boundary

- STUDENT 為最高授權者；各 Brain 僅管理自己的 Own Worker。
- STUDENT-MAIN Brain 僅能向其他 Brain 交付 Brain-to-Brain 工作，不得越級直接派工給 Research、Engineering 或 Web Own Worker。
- Worker 不得自行批准 Milestone，亦不得以執行結果取代 Brain 驗收。
- 未經 STUDENT 授權，不得對外發布資料、修改專案權限或修改其他 Brain 工作區。
- 每份工作單必須明確定義 `INPUT`、`OUTPUT`、`STOP_IF`、`EVIDENCE` 與 `RETURN_TO`。

## D. Read-Only and Write Boundary

### Historical M0 Boundary

M0 執行期間，`data/`、NASA C-MAPSS FD001 原始資料、`synthetic_sensor.csv`、其他資料、非授權程式與設定、歷史 Git 紀錄及私人設定均為唯讀；WO-M0-001 僅允許寫入四份治理文件、必要 Git 中繼資料及安全的 `.gitignore`。此限制保留為 M0 歷史治理證據，不是對已正式授權之 M1-M5 工作的永久禁止。

M1 正式資料契約以 DEC-011 與 `ROADMAP.md` 的 M1 Current Acceptance Record 為準；舊有「其他五筆合成 CSV」敘述不得作為現行資料契約。歷史執行證據不得改寫。

### General M0-M5 Data Rules

1. 原始資料預設唯讀。
2. 只有取得 STUDENT 授權、正式工作單及該工作單要求的必要 Execution Release 後，指定 Worker 才能讀取與分析工作單明確指定的原始資料。
3. 未經授權不得讀取工作單範圍外的資料。
4. 禁止修改、刪除、移動、覆寫或重新產生原始資料。
5. 禁止 Commit、Push、上傳或對外發布原始資料。
6. 衍生資料、摘要、索引規格及原始資料必須明確區隔。
7. 公開 GitHub 僅保存已授權的程式、測試、契約、索引規格及必要摘要。
8. 完整逐列索引及完整時間序列預設保留於本地，除非 STUDENT 另以正式工作單核准。

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
- 工作超出目前正式授權的 Milestone、Substage 或 Work Item。
- 前置里程碑或工作尚未取得必要 `PASS`。
- 尚未取得 STUDENT 正式授權或工作單要求的 Execution Release。
- 未經授權提前執行後續工作。

已正式授權且符合前置閘門的當前工作，不得僅因屬於 M1-M5 而被歷史 M0 規則阻擋。不得繞過 STOP_IF；應回報具體原因與安全的處理建議。

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

## J. Bounded Governance Change Procedure

當已驗收治理規則與 STUDENT 新核准的專案範圍發生衝突時：

1. 責任 Brain 必須明確回報衝突及受影響工作。
2. STUDENT 核准必要的治理修改範圍。
3. STUDENT-MAIN Brain 建立並正式派送治理工作單。
4. MAIN Own Worker 僅修改工作單授權的治理文件。
5. Worker 完成 Commit、Push 與證據回報；STUDENT-MAIN Brain 從 GitHub 獨立驗收。
6. 驗收通過後，STUDENT-MAIN Brain 正式放行原工作。
7. 正式放行前不得執行原工作。

此程序不得用於繞過安全規則、資料保護、權限邊界、前置驗收或 GitHub 驗證。

## K. Acceptance and Release Policy

- **AUTHORIZATION:** STUDENT 已核准工作範圍。
- **EXECUTION_RELEASE:** 工作單要求的必要前置條件已由 STUDENT-MAIN Brain 驗收，允許指定工作進入執行。
- **WORKER_COMPLETED:** Worker 已完成工作並提交證據，不等於 Brain PASS。
- **BRAIN_PASS:** 責任 Brain 已從 GitHub 獨立查核並正式驗收。

當工作單具有條件式放行規則時，以 STUDENT-MAIN Brain 正式 Release、已驗收 Commit SHA 與 GitHub `main` 最新治理文件共同作為執行依據。不得要求另建立僅為同步治理工作單 `PASS` 或 `RELEASED` 狀態而產生的遞迴工作單；正式驗收及 Release 決議應於下一張已授權的實質工作提交中留存。

所有工作仍須遵守單一 `main` 分支、循序開發、強制 GitHub 驗證、同一時間僅一項已授權寫入工作，以及禁止未授權擴張範圍。
