# M0-M5 Project Roadmap

## M0: Governance Initialization

- **OBJECTIVE:** 建立 AI Team 治理文件及 GitHub Repository。
- **INPUT:** 學生核准的治理規劃。
- **DELIVERABLE:** 四份治理文件、Git Commit、GitHub Repository。
- **OWNER:** STUDENT-MAIN Brain / MAIN Own Worker。
- **ACCEPTANCE:** 四份文件完整，Commit 與 Push 成功，MAIN Brain 從 GitHub 獨立驗證。
- **STOP_IF:** 權限不足、檔案衝突、GitHub 無法驗證。
- **NEXT_ROLE:** Research Brain（須經 MAIN 授權）。

## M1: Synthetic Dataset Verification

- **OBJECTIVE:** 使用六筆合成 CSV 建立 Dataset Profile，先完成第一筆可驗證資料的派工閉環。
- **INPUT:** 本地端合成 CSV；已知 `synthetic_sensor.csv`，其餘五筆待確認。
- **DELIVERABLE:** File Identity、SHA-256、欄位資訊、資料品質報告及驗證證據。
- **OWNER:** Research Brain / Research Own Worker。
- **ACCEPTANCE:** 資料來源可追溯，結果可重現，Research Brain 完成審查。
- **STOP_IF:** 資料無法存取、來源不明、證據不足。
- **NEXT_ROLE:** STUDENT-MAIN Brain。

## M2: Synthetic Analytics Prototype

- **OBJECTIVE:** 建立 Unit、Cycle、Sensor 查詢與趨勢分析原型。
- **INPUT:** M1 驗證資料。
- **DELIVERABLE:** 查詢模組、趨勢分析、測試紀錄。
- **OWNER:** Research Brain / Engineering Brain。
- **ACCEPTANCE:** 查詢結果與原始資料一致且可重現。
- **STOP_IF:** 資料錯誤、測試失敗、來源不一致。
- **NEXT_ROLE:** STUDENT-MAIN Brain。

## M3: NASA FD001 Integration

- **OBJECTIVE:** 整合 NASA C-MAPSS FD001 真實資料。
- **INPUT:** 本地端 FD001 資料及 M2 原型。
- **DELIVERABLE:** FD001 Dataset Profile、欄位模型、資料來源與完整性驗證。
- **OWNER:** Research Brain / Engineering Brain。
- **ACCEPTANCE:** Unit、Cycle、Sensor 可追溯至原始資料。
- **STOP_IF:** 來源不明、資料錯誤、驗證失敗。
- **NEXT_ROLE:** STUDENT-MAIN Brain。

## M4: Health Analytics Website

- **OBJECTIVE:** 完成引擎健康分析網站。
- **INPUT:** M3 驗證資料與分析規格。
- **DELIVERABLE:** 網站、互動趨勢圖、來源檢視、Evidence Prompt Generator。
- **OWNER:** Engineering Brain / Engineering Own Worker。
- **ACCEPTANCE:** 網站功能正常、資料正確、Evidence Prompt 可追溯。
- **STOP_IF:** 功能失效、資料不一致、證據不足。
- **NEXT_ROLE:** STUDENT-MAIN Brain。

## M5: End-to-End Verification

- **OBJECTIVE:** 完成端對端驗證與專案交付。
- **INPUT:** M4 網站、FD001 資料、測試案例。
- **DELIVERABLE:** 完整網站、測試報告、操作文件、最終驗收報告。
- **OWNER:** STUDENT-MAIN Brain。
- **ACCEPTANCE:** 測試通過、結果可重現、GitHub 成果可驗證，學生完成最終驗收。
- **STOP_IF:** 關鍵測試失敗、資料不可追溯、GitHub 成果無法驗證。
- **NEXT_ROLE:** STUDENT。
