# M0-M5 Project Roadmap

所有里程碑必須循序驗收。M0 不得執行 M1，M1 不得提前執行 M2；不得以合成資料冒充真實 FD001 資料，亦不得宣稱已完成尚未執行的測試。RUL 預測模型不屬於本 Roadmap 的必要交付範圍。

## M0: Governance Initialization

- **STATUS:** `PASS / CLOSED`

- **目標：** 建立 AI Team Governance、正式工作單規範與 GitHub 同步及遠端驗證流程。
- **輸入：** STUDENT 核准的 `WO-M0-001`。
- **交付物：** `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`、安全的 Git 設定、GitHub `main` 成果與驗證證據。
- **責任 Brain：** STUDENT-MAIN Brain。
- **執行 Worker：** MAIN Own Worker (Codex)。
- **驗收條件：** 四份文件完整一致；Commit 與 Push 成功；本地與遠端 SHA 一致；遠端文件可讀；STUDENT-MAIN Brain 完成獨立審查。
- **STOP_IF：** 根目錄、授權帳號或範圍無法確認；敏感資料風險；Git/GitHub 衝突或遠端不可驗證。
- **下一角色：** STUDENT-MAIN Brain；僅在 Brain PASS 且 STUDENT 另行授權後派送 M1。

## M1: Synthetic Dataset Governance Exercise

- **STATUS:** `PASS / CLOSED`

- **目標：** 使用一份 `synthetic_sensor.csv`（預期含六筆合成資料列，不含標題列）學習資料檢查、派工、Worker 回報與 Brain 驗收閉環。
- **資料契約：** `DATASET_PATH: data/synthetic_sensor.csv`；`DATASET_TYPE: Synthetic Sensor Data`；`EXPECTED_CSV_COUNT: 1`；`EXPECTED_DATA_ROWS: 6`；`HEADER_INCLUDED_IN_ROW_COUNT: NO`；`ACTUAL_DATA_ROWS: NOT_VERIFIED`。
- **輸入：** 已獲正式 M1 執行授權且身分待驗證的一份本地合成 CSV，以及 M0 已通過的治理規則。
- **交付物：** 實際資料列數驗證、欄位與格式驗證、合成資料來源與身分確認、可重現的 Dataset Profile、Worker 證據與 Brain 驗收結果。
- **責任 Brain：** Research Brain。
- **執行 Worker：** Research Own Worker（DATA Worker 為功能標籤）。
- **驗收條件：** 驗證實際資料列數、欄位與資料格式，確認合成資料來源與身分，建立可重現的 Dataset Profile，且由 Research Brain 獨立審查；不得將合成資料誤稱為 FD001。
- **STOP_IF：** M0 未 PASS 或未獲 STUDENT 正式 M1 執行授權；資料來源、身分、數量或權限不明；需修改原始資料。
- **下一角色：** STUDENT-MAIN Brain，進行里程碑閘門審查。

### M1 Current Acceptance Record

- **ACTUAL_DATA_ROWS:** `6`
- **M1_GATE:** `PASS`
- **M1_ACCEPTED_COMMIT:** `0ba0a16c1e6904a389fef87b66389662cf0737b3`
- **Research Domain Acceptance:** `PASS`
- **MAIN Brain Acceptance:** `PASS`
- **Dataset Profile:** `COMPLETED` — `outputs/INTRO_PROFILE.md`
- **Reproducible Profiler:** `COMPLETED` — `tools/profile_intro.py`
- 原始 CSV 維持本地唯讀且未提交 GitHub。
- 本資料為合成 Sensor 資料，不等於 NASA C-MAPSS FD001。
- 合成資料的生成來源限制已於 Dataset Profile 揭露並由 Research Brain 與 STUDENT-MAIN Brain 接受。

## M2: FD001 Data Validation and Local Website MVP

M2 採 Data First 順序：`M2-G → M2-A → M2-B`。M2-A PASS 不等於整體 M2 PASS。

### M2-G: Governance Alignment

- **OWNER:** STUDENT-MAIN Brain
- **EXECUTOR:** MAIN Own Worker (Codex)
- **WORK_ITEM:** `WO-M2-001-GOV-ALIGN`
- **OBJECTIVE:** 完成 M2 Data First 治理對齊。
- **DELIVERABLES:** 四份一致、可查核且已 Push 至 GitHub `main` 的治理文件。
- **GATE:** STUDENT-MAIN Brain GitHub Independent Review。
- **NEXT:** STUDENT-MAIN Brain 正式放行 M2-A。

### M2-A: FD001 Local Data Validation and Contract

- **OWNER:** STUDENT-RESEARCH Brain
- **EXECUTOR:** Research Own Worker
- **WORK_ITEM:** `WO-M2-001`
- **CHILD_WORK_ITEM:** `WO-M2-001-RW-001`
- **INPUT:** STUDENT 已信任的本地 FD001 三份文字檔。
- **EXPECTED_FILES:** `train_FD001.txt`、`test_FD001.txt`、`RUL_FD001.txt`
- **SOURCE_TRUST_POLICY:** `STUDENT_TRUSTED_LOCAL_FILES`
- **EXTERNAL_SOURCE_VERIFICATION:** `NOT_REQUIRED`
- **INTERNET_DATA_DOWNLOAD:** `PROHIBITED`
- **EXTERNAL_DATA_REPLACEMENT:** `PROHIBITED`
- **RAW_DATA_ACCESS:** `AUTHORIZED_READ_ONLY_AFTER_RELEASE`
- **RAW_DATA_UPLOAD:** `PROHIBITED`

交付物：

- 本地檔案身分及 SHA-256 驗證。
- Train／Test／RUL 語意與限制。
- 實際行列數及 Unit／Cycle 驗證。
- Raw Data Index Specification。
- Operational Settings 欄位字典。
- Sensor 1-21 欄位字典。
- Dataset Profile、Data Quality Report 及可追溯 Sensor Trend Analysis。
- FD001 Data Contract v1.0.0、可重現程式與測試證據。

驗收條件：

- 三份資料檔案結構與完整性通過。
- Unit／Cycle 索引可重現，RUL 與 Test Unit 對應可查核。
- 資料品質、趨勢分析及 Data Contract 完整、一致且可追溯。
- 原始資料未修改或上傳。
- Research Brain 完成獨立審查，STUDENT-MAIN Brain 完成 Domain Acceptance。

STOP_IF：

- M2-G 尚未取得 STUDENT-MAIN Brain PASS，或尚未收到正式 M2-A Execution Release。
- 資料身分、結構或完整性無法確認。
- 原始資料需要修改或替換。
- 必須重新下載或上網核對來源。
- GitHub 驗證失敗。

**NEXT:** STUDENT-MAIN Brain 審查 Data Contract；取得 STUDENT 授權後才能啟動 M2-B。

### M2-B: Local FD001 Website MVP

- **OWNER:** STUDENT-WEB Brain
- **EXECUTOR:** Web Own Worker
- **AUTHORIZATION:** `NOT_GRANTED`
- **INPUT:** M2-A 已驗收的 FD001 Data Contract、資料解析與索引規格、資料品質與趨勢證據，以及 STUDENT 核准的網站規格。

交付物：

- 本地 FD001 查詢 API。
- Dataset Split、Engine Unit、Cycle 與 Sensor 選擇器。
- 資料明細、Sensor 趨勢視圖及原始資料定位資訊。
- 網站功能與 Browser UAT 證據。

驗收條件：

- 網站資料符合已驗收 Data Contract，且顯示值可追溯至本地 FD001。
- 不得使用 M1 合成資料冒充 FD001，不得自行生成或補造 Sensor 數值。
- 查詢邊界與必要功能測試通過。
- STUDENT-WEB Brain 完成 GitHub 獨立審查，STUDENT-MAIN Brain 完成 M2 里程碑驗收。

STOP_IF：

- M2-A 尚未取得 STUDENT-MAIN Brain PASS，Data Contract 尚未正式接受，或 STUDENT 尚未授權 M2-B。
- 網站與 Data Contract 不一致，或關鍵功能／測試失敗。

## M3: FD001 System Integration and Verification

- **OBJECTIVE:** 整合並驗證 M2-A 與 M2-B 的資料解析、API、網站及來源追溯。
- **RESPONSIBLE_BRAINS:** Engineering Brain 負責系統整合與工程驗證；Research Brain 負責資料證據正確性；STUDENT-WEB Brain 負責 API 與網站整合驗證。各 Brain 僅管理自己的 Own Worker。
- **DELIVERABLES:** 跨元件整合測試、Raw Data 至 API 與 API 至網站的一致性證據、Unit／Cycle／Sensor 查詢追溯測試、Data Contract 相容性驗證及整合驗收報告。
- 不得無理由重新執行 M2-A 已驗收的資料分析；保留必要的資料解析及一致性測試。
- **GATE:** STUDENT-MAIN Brain Integration Acceptance。

## M4: Evidence Prompt Generator

- **OBJECTIVE:** 依網站實際選取狀態與已驗收 FD001 證據產生可查核提示詞。
- **RESPONSIBLE_BRAINS:** STUDENT-WEB Brain 負責功能實作與網站測試；Research Brain 負責資料證據審查；Engineering Brain 負責必要系統整合驗證。
- 保留原有 Evidence Prompt 驗收要求；不得將未驗證推論寫成資料事實。

## M5: Integration, Documentation and Final Acceptance

- **OBJECTIVE:** 完成端對端測試、文件、本地部署及 STUDENT 最終驗收。
- STUDENT-MAIN Brain 彙整 Research Brain、Engineering Brain 與 STUDENT-WEB Brain 的驗收結果。
- 保留原有 M5 最終驗收要求。

## Global Roadmap Constraints

- M0、M1 已正式結案。
- `M2-G → M2-A → M2-B` 必須循序執行。
- M2-A PASS 不等於整體 M2 PASS；M2-B 未驗收不得進入 M3。
- M3-M5 仍須逐階段取得 STUDENT 授權。
- RUL 預測模型不屬於必要交付範圍。
- 不得將參考資料規格寫成實測結果，亦不得虛構已完成的研究或測試。
