# Architecture and Governance Decision Log

本文件記錄所有經 STUDENT 核准的專案治理與架構決策；未經驗證的技術選擇不得寫成既定事實。

## DEC-001: Bounded Brain-Worker Governance

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 專案需要明確區分授權、執行與驗收責任。
- **Decision:** 採用 STUDENT-MAIN Brain 與 Bounded Worker 治理架構；各 Brain 僅管理自己的 Own Worker。
- **Consequences:** Worker 只能執行正式授權工作，且不得自行宣告 Brain PASS。

## DEC-002: Mandatory Work Item ID

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 工作必須可追溯至明確範圍與授權者。
- **Decision:** 所有開發工作必須具有正式 `WORK_ITEM_ID`，並定義 INPUT、OUTPUT、STOP_IF、EVIDENCE 與 RETURN_TO。
- **Consequences:** 沒有合格工作單的工作不得開始。

## DEC-003: GitHub Main as Formal Result Source

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 本地成果不足以支持獨立驗收。
- **Decision:** GitHub `main` 為正式成果的版本管理來源。
- **Consequences:** 驗收以遠端可讀的 Commit 與檔案為依據。

## DEC-004: Read Latest AGENTS.md Before Dispatch

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 治理規則可能隨已核准 Commit 更新。
- **Decision:** 每次派工前，Brain 必須先讀取 GitHub `main` 最新 `AGENTS.md` 並確認工作單相容。
- **Consequences:** GitHub 或治理文件無法驗證時不得派工，狀態為 BLOCKED。

## DEC-005: Commit, Push and Independent Review

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** Worker 自述不能取代可查核證據。
- **Decision:** Worker 完成後必須 Commit、Push，由 Brain 從 GitHub 獨立讀取並審查成果。
- **Consequences:** Worker 完成僅能進入 PENDING_BRAIN_REVIEW，不能自行宣告 PASS。

## DEC-006: Single Main Branch and Sequential Development

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 專案採嚴格里程碑閘門並避免平行寫入衝突。
- **Decision:** 採單一 `main` 正式分支與循序開發，禁止 force push 或改寫已發布歷史。
- **Consequences:** 同一時間只允許一項已授權寫入工作。

## DEC-007: Previous Work Must Pass Before Next Work

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 後續工作依賴前一項成果及其驗收證據。
- **Decision:** 前一工作未取得 Brain PASS 與 STUDENT 授權，不得開始下一工作或里程碑。
- **Consequences:** 任何提前執行都必須停止並回報。

## DEC-008: Synthetic Data Does Not Equal FD001 Integration

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** M1 使用六筆合成 CSV 練習治理與資料檢查閉環。
- **Decision:** M1 合成資料成果不得被描述為已完成 NASA C-MAPSS FD001 真實資料整合。
- **Consequences:** 合成與真實資料的來源、標示及驗收必須明確分離。

## DEC-009: Local Raw Data Is Read-Only

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 原始資料可能受授權、完整性與公開風險限制。
- **Decision:** 本地原始資料預設唯讀，不得未經授權讀取、分析、修改、刪除、移動、重新產生或公開。
- **Consequences:** Git 與 `.gitignore` 必須排除原始資料；任何例外需要正式工作單。

## DEC-010: GitHub Verification Failure Means Blocked

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 遠端驗證是 PASS 的必要證據。
- **Decision:** GitHub 無法存取、遠端 SHA 不一致或檔案無法讀取時，狀態必須為 BLOCKED。
- **Consequences:** 不得以本地結果、push 訊息或 Worker 自述代替遠端驗證。

## DEC-011: M1 Synthetic Dataset Contract Clarification

- **Date:** 2026-11-23
- **Status:** ACCEPTED
- **Context:** 既有文件將六筆合成資料誤解為六份 CSV，造成資料數量及路徑歧義。
- **Decision:** M1 使用一份 `synthetic_sensor.csv`，位於 `data/synthetic_sensor.csv`，預期包含六筆資料列且不含標題列；`ACTUAL_DATA_ROWS` 為 `NOT_VERIFIED`。
- **Consequences:**
  1. 不再要求六份獨立 CSV。
  2. 不得補造額外五份 CSV。
  3. 實際資料列數須於正式授權的 M1 驗證。
  4. 原始 CSV 維持唯讀。
  5. 合成資料不得冒充 NASA C-MAPSS FD001。
  6. M1 須另行取得 STUDENT 正式執行授權。

## DEC-012: Data First Development Sequence

- **Date:** 2026-11-24
- **Status:** ACCEPTED
- **Authorized By:** STUDENT
- **Context:** FD001 網站開發必須先建立可查核的資料契約，避免網站自行推定資料語意。
- **Decision:** 採用 `M2-G Governance Alignment → M2-A FD001 Data Validation → Data Contract Acceptance → M2-B Local Website MVP → M3 System Integration → M4 Evidence Prompt → M5 Final Acceptance` 的 Data First 順序；M0、M1 已驗收成果維持不變。
- **Consequences:** 各階段必須依序取得必要驗收、授權與 Release，禁止提前執行網站或後續工作。

## DEC-013: Student-Trusted Local FD001 Files

- **Date:** 2026-11-24
- **Status:** ACCEPTED
- **Authorized By:** STUDENT
- **Context:** STUDENT 已指定並信任本地 `train_FD001.txt`、`test_FD001.txt`、`RUL_FD001.txt` 作為 M2-A 輸入。
- **Decision:** M2-A 不要求重新上網核對 NASA 來源，且禁止重新下載或替換資料；來源信任與本地檔案完整性驗證為不同事項。STUDENT 信任政策不取代檔案存在性、SHA-256、行列數、欄位、Unit/Cycle、RUL 對應及資料品質驗證，亦不得宣稱已獨立驗證 NASA 官方來源。
- **Consequences:** 原始資料維持唯讀、不得上傳；本決議不撤銷 DEC-009。

## DEC-014: Data Contract Before Website Development

- **Date:** 2026-11-24
- **Status:** ACCEPTED
- **Authorized By:** STUDENT
- **Context:** 網站查詢、顯示與趨勢功能必須依賴穩定且已驗收的 FD001 資料語意。
- **Decision:** FD001 Data Contract 必須先取得 Research Brain 與 STUDENT-MAIN Brain 驗收；STUDENT-WEB Brain 僅能使用已接受契約進行正式網站開發。Data Contract 未驗收前不得啟動 M2-B，網站不得自行變更資料語意、索引、欄位或原始數值。
- **Consequences:** M2-A PASS 不等於整體 M2 PASS；M2-B 仍須 STUDENT 正式授權。

## DEC-015: Milestone-Aware Governance and Release

- **Date:** 2026-11-24
- **Status:** ACCEPTED
- **Authorized By:** STUDENT
- **Context:** M0 專用限制若被永久套用，會錯誤阻擋已正式授權的後續里程碑。
- **Decision:** 各里程碑依正式授權、前置驗收與必要 Execution Release 執行，並採條件式放行機制。治理工作單經獨立驗收後，STUDENT-MAIN Brain 的正式 PASS 與 Release 可解除已驗證的治理阻擋；不要求另開僅為同步 PASS 或 RELEASED 狀態的遞迴工作單。
- **Consequences:** 本決議不得削弱 GitHub 驗證、循序開發、資料保護、權限邊界或其他 STOP_IF。

## DEC-016: Web Brain Authority Boundary

- **Date:** 2026-11-24
- **Status:** ACCEPTED
- **Authorized By:** STUDENT
- **Context:** API、網站、Evidence Prompt 與 Browser UAT 需要獨立且清楚的責任邊界。
- **Decision:** 正式建立 STUDENT-WEB Brain 與 Web Own Worker。Web Brain 負責 API、網站、Evidence Prompt 及 Browser UAT；Research Brain 負責資料研究與資料證據正確性；Engineering Brain 負責系統架構與跨元件整合驗證；STUDENT-MAIN Brain 負責治理與跨 Brain 驗收。所有 Brain 僅管理自己的 Own Worker。
- **Consequences:** MAIN Brain 不得直接派工給 Web Own Worker；功能標籤 `WEB Worker` 不代表正式權責角色。
