# AI Team Governance and Agent Instructions

## A. Project Identity

**PROJECT:** `NTUST_CMAPSS_HEALTH_ANALYTICS`

**FINAL_OBJECTIVE:** 建立 NASA C-MAPSS FD001 引擎健康分析網站。

網站最終應支援：

- Engine Unit 選擇
- Cycle 選擇
- Sensor 選擇
- 真實資料來源追溯
- Sensor 趨勢分析
- Evidence Prompt 產生

## B. Organization

- **STUDENT：**專案擁有者，負責最終授權及驗收。
- **STUDENT-MAIN Brain：**負責 Roadmap、Milestone、跨 Brain 協調及最終驗收。
- **MAIN Own Worker：**僅執行 MAIN Brain 明確授權的治理及整合工作。
- **Research Brain：**負責資料研究、Dataset Profile、資料來源及分析證據審查。
- **Research Own Worker：**僅執行 Research Brain 授權的資料處理工作。
- **Engineering Brain：**負責系統架構、程式開發、測試及工程成果審查。
- **Engineering Own Worker：**僅執行 Engineering Brain 授權的工程工作。

## C. Authority Boundary

- STUDENT 為最高授權者。
- MAIN Brain 不得直接控制 Research Own Worker。
- MAIN Brain 不得直接控制 Engineering Own Worker。
- 各 Brain 僅管理自己的 Own Worker。
- Worker 不得自行建立工作單或擴大工作範圍。
- Worker 不得自行批准 Milestone。
- Worker 不得以執行結果取代 Brain 驗收或自行宣告最終 PASS。
- 未經學生授權，不得對外發布資料、修改專案權限或修改其他 Brain 工作區。

## D. Read-Only Policy

M0 階段以下內容全部唯讀：

- `data/`
- `synthetic_sensor.csv`
- 其他五筆合成 CSV
- NASA C-MAPSS FD001 原始資料
- 既有程式碼及設定檔
- 其他專案、Repository 及 Brain 工作區

M0 僅允許建立或修改 `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`，以及執行必要的 Git 版本控制操作。不得讀取或分析原始 CSV，不得修改、刪除、移動或上傳資料。

## E. Mandatory Git Governance

每次派工前：

1. Brain 必須先從 GitHub `main` 讀取最新 `AGENTS.md`。
2. Brain 必須確認最新治理規則。
3. Brain 必須要求 Own Worker 遵守最新 `AGENTS.md`。
4. 工作單必須具備正式 `WORK_ITEM_ID`，並明確定義 INPUT、OUTPUT、STOP_IF、EVIDENCE、RETURN_TO。
5. 未取得授權不得開始執行。

每次 Worker 完成後：

1. 完成必要測試。
2. Commit 授權成果。
3. Push 至 GitHub `main`。
4. 回傳完整 Commit ID 及 GitHub Commit URL。
5. Brain 必須從 GitHub 獨立讀取成果。
6. Brain 必須驗證 Commit、檔案內容及驗收條件。
7. 全部通過才能回報 PASS。

M0 首次建立 `AGENTS.md` 時，允許使用學生已核准的工作單作為初始治理依據。M0 完成後，後續派工均須先讀取 GitHub `main` 最新 `AGENTS.md`。GitHub 無法存取或驗證時，狀態必須為 BLOCKED，不得以本地結果或 Worker 自述代替遠端驗證。

## F. Sequential Development

專案採單一 `main` 分支、循序開發：

- 同一時間只允許一項已授權寫入工作。
- 前一工作未驗收，不得開始下一工作。
- 前一工作未經 MAIN 授權，不得進入下一階段。
- 禁止 Force Push、擅自 Reset、Rebase 或改寫已發布歷史。
- 禁止擅自刪除遠端 Repository。
- 發生版本衝突時必須停止並回報。

## G. Evidence Policy

任何 PASS 必須具備：

- WORK_ITEM_ID
- 實際執行命令及 Exit Code
- 測試結果
- Commit ID 及 Commit Object Format
- 四份治理文件的 SHA-256
- GitHub Repository URL
- GitHub Commit URL
- 遠端檔案驗證結果
- 驗收者及 Brain 驗收結果

不得虛構執行結果，也不得將未驗證推論標示為已確認事實。

## H. Status Definitions

- **CREATED_NOT_DISPATCHED：**工作單已建立，尚未派送。
- **COMMAND_DISPATCHED：**工作單已正式交付指定 Worker。
- **IN_PROGRESS：**Worker 正在執行。
- **SUBMITTED：**Worker 已提交成果，等待 Brain 驗收。
- **PASS：**Brain 已完成 GitHub 遠端驗證及驗收。
- **REWORK：**成果不符合要求，必須修正。
- **BLOCKED：**存在無法繼續的依賴、權限或驗證問題。
