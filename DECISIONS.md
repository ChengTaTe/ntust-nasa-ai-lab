# Architecture and Governance Decision Log

本文件僅記錄 WO-M0-001 已核准的治理決策；未經驗證的技術選擇不得寫成既定事實。

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
