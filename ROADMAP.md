# M0-M5 Project Roadmap

所有里程碑必須循序驗收。M0 不得執行 M1，M1 不得提前執行 M2；不得以合成資料冒充真實 FD001 資料，亦不得宣稱已完成尚未執行的測試。RUL 預測模型不屬於本 Roadmap 的必要交付範圍。

## M0: Governance Initialization

- **目標：** 建立 AI Team Governance、正式工作單規範與 GitHub 同步及遠端驗證流程。
- **輸入：** STUDENT 核准的 `WO-M0-001`。
- **交付物：** `AGENTS.md`、`ROADMAP.md`、`WORK_ITEM.md`、`DECISIONS.md`、安全的 Git 設定、GitHub `main` 成果與驗證證據。
- **責任 Brain：** STUDENT-MAIN Brain。
- **執行 Worker：** MAIN Own Worker (Codex)。
- **驗收條件：** 四份文件完整一致；Commit 與 Push 成功；本地與遠端 SHA 一致；遠端文件可讀；STUDENT-MAIN Brain 完成獨立審查。
- **STOP_IF：** 根目錄、授權帳號或範圍無法確認；敏感資料風險；Git/GitHub 衝突或遠端不可驗證。
- **下一角色：** STUDENT-MAIN Brain；僅在 Brain PASS 且 STUDENT 另行授權後派送 M1。

## M1: Synthetic Dataset Governance Exercise

- **目標：** 使用本地 `synthetic_sensor.csv` 等六筆合成資料，學習資料檢查、派工、Worker 回報與 Brain 驗收閉環。
- **輸入：** 已授權且經辨識的六筆本地合成 CSV，以及 M0 已通過的治理規則。
- **交付物：** 可重現的資料檢查紀錄、Dataset Profile、來源標示、Worker 證據與 Brain 驗收結果。
- **責任 Brain：** Research Brain。
- **執行 Worker：** Research Own Worker（DATA Worker 為功能標籤）。
- **驗收條件：** 六筆合成資料身分清楚、未被誤稱為 FD001、檢查結果可重現且由 Research Brain 審查。
- **STOP_IF：** M0 未 PASS 或未獲 STUDENT 授權；資料來源、數量或權限不明；需修改原始資料。
- **下一角色：** STUDENT-MAIN Brain，進行里程碑閘門審查。

## M2: Local Health Analytics Website MVP

- **目標：** 建立本地健康分析網站 MVP，支援 Engine Unit、Cycle、Sensor 選擇，並顯示資料明細與 Sensor 趨勢。
- **輸入：** M1 已驗收的合成資料 Profile、查詢需求與網站規格。
- **交付物：** 本地網站 MVP、選擇器、資料明細、趨勢視圖及工程測試證據。
- **責任 Brain：** Engineering Brain。
- **執行 Worker：** Engineering Own Worker（WEB Worker 與 QA Worker 為功能標籤）。
- **驗收條件：** 選擇與顯示功能可重現，畫面資料與 M1 已驗證資料一致，測試通過並由 Engineering Brain 審查。
- **STOP_IF：** M1 未 PASS 或未獲 STUDENT 授權；資料契約不明；關鍵功能或測試失敗。
- **下一角色：** STUDENT-MAIN Brain，進行里程碑閘門審查。

## M3: NASA C-MAPSS FD001 Integration

- **目標：** 整合 NASA C-MAPSS FD001 真實資料，建立資料解析、欄位對照及來源追溯。
- **輸入：** 已授權且來源可確認的 FD001 原始資料、M2 MVP 與已核准的資料契約。
- **交付物：** FD001 解析流程、欄位對照、Dataset Profile、完整性檢查與來源追溯證據。
- **責任 Brain：** Research Brain 與 Engineering Brain，各自審查其權責成果。
- **執行 Worker：** 各 Brain 的 Own Worker（FD001 DATA Worker 為功能標籤）。
- **驗收條件：** Unit、Cycle 與 Sensor 可追溯至真實原始資料；合成與真實資料明確區隔；檢查與測試可重現。
- **STOP_IF：** M2 未 PASS 或未獲 STUDENT 授權；FD001 來源、授權、欄位或完整性無法確認。
- **下一角色：** STUDENT-MAIN Brain，整合跨 Brain 驗收結果。

## M4: Evidence Prompt Generator

- **目標：** 依網站實際選取的 Engine Unit、Cycle、Sensor 與資料證據產生可查核的 Evidence Prompt。
- **輸入：** M3 已驗收的 FD001 資料、來源追溯資訊及網站選取狀態。
- **交付物：** Evidence Prompt Generator、提示詞格式、來源引用與測試證據。
- **責任 Brain：** Engineering Brain；Research Brain 審查資料證據正確性。
- **執行 Worker：** 各 Brain 的 Own Worker（EVIDENCE Worker 與 QA Worker 為功能標籤）。
- **驗收條件：** Prompt 僅使用實際選取且可追溯的資料，內容可查核，邊界案例測試通過。
- **STOP_IF：** M3 未 PASS 或未獲 STUDENT 授權；資料來源、選取狀態或引用證據不完整。
- **下一角色：** STUDENT-MAIN Brain，進行里程碑閘門審查。

## M5: Integration, Documentation and Final Acceptance

- **目標：** 完成整合測試、文件、本地部署與最終驗收。
- **輸入：** M4 已驗收網站、FD001 整合、Evidence Prompt Generator 及全部測試規格。
- **交付物：** 完整本地網站、端對端測試報告、操作與部署文件、最終驗收證據。
- **責任 Brain：** STUDENT-MAIN Brain，彙整 Research Brain 與 Engineering Brain 審查結果。
- **執行 Worker：** 經正式工作單授權的各 Brain Own Worker（QA Worker 為功能標籤）。
- **驗收條件：** 功能、資料追溯、Evidence Prompt、文件及本地部署全部通過可重現測試，STUDENT 完成最終驗收。
- **STOP_IF：** M4 未 PASS 或未獲 STUDENT 授權；關鍵測試失敗；資料不可追溯；GitHub 成果無法驗證。
- **下一角色：** STUDENT，執行最終授權與驗收。
