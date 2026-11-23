# Architecture and Governance Decision Log

## ADR-0001: Student Authority

- **DECISION:** 學生擁有最終授權及驗收權。
- **STATUS:** APPROVED

## ADR-0002: Brain and Worker Separation

- **DECISION:** 各 Brain 僅管理自己的 Own Worker，禁止跨 Brain 越級派工。
- **STATUS:** APPROVED

## ADR-0003: Single Main Branch

- **DECISION:** 專案採單一 `main` 分支及循序開發。
- **STATUS:** APPROVED

## ADR-0004: GitHub Verification

- **DECISION:** Worker 必須 Commit 並 Push；Brain 必須從 GitHub 讀取實際成果後才能判定 PASS。
- **STATUS:** APPROVED

## ADR-0005: Read-Only Dataset Policy

- **DECISION:** M0 不得讀取、修改、分析或上傳原始資料、合成 CSV 與 NASA FD001。
- **STATUS:** APPROVED

## ADR-0006: Milestone Gate

- **DECISION:** 前一工作未驗收及取得 MAIN 授權，下一 Worker 不得開始。
- **STATUS:** APPROVED

## ADR-0007: Public Repository Authorization

- **DECISION:** 學生授權建立公開 GitHub Repository `ntust-nasa-ai-lab`，僅發布本工作單授權且經檢查的治理文件。
- **STATUS:** APPROVED

## ADR-0008: Preserve Existing Data Directory

- **DECISION:** 保留 `data/` 並維持唯讀；不得刪除、修改、移動、重新命名、分析或納入 Git Commit。
- **STATUS:** APPROVED

## ADR-0009: GitHub CLI Setup

- **DECISION:** GitHub CLI 由學生自行安裝及登入；Worker 必須在執行前確認環境及帳號可用。
- **STATUS:** APPROVED
