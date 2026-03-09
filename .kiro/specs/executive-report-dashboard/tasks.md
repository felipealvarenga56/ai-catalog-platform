# Implementation Plan: Executive Report Dashboard

## Overview

Transform the existing executive report modal into a dedicated dashboard tab with KPI cards, dynamic filters, distribution charts (Chart.js), and cross-tabulation tables. Backend delivers all data via a single enriched FastAPI endpoint with filter support. Frontend renders everything with vanilla JS + Tailwind CSS + Chart.js (CDN).

## Tasks

- [x] 1. Add Pydantic response models for the dashboard API
  - [x] 1.1 Create `FilterOptions`, `ComplianceMetrics`, `CrossTabEntry`, and `ExecutiveDashboardReport` models in `api/models.py`
    - `FilterOptions`: lists of distinct areas, initiatives, statuses, owners
    - `ComplianceMetrics`: sec_approval_count, sec_approval_percentage, docs_link_count, docs_link_percentage
    - `CrossTabEntry`: row, col, count
    - `ExecutiveDashboardReport`: total_contracts, by_status, by_initiative, by_area, by_owner, compliance, cross_area_initiative, cross_area_status, filter_options
    - _Requirements: 6.1, 6.4_

- [x] 2. Implement the enriched Report API endpoint
  - [x] 2.1 Add `build_where_clause()` helper function in `api/routes/reports.py`
    - Accepts optional area, initiative, status, owner parameters
    - Returns a tuple of (where_sql, params) for parameterized SQL
    - _Requirements: 3.4, 6.2_
  - [x] 2.2 Add `GET /api/reports/executive-dashboard` endpoint in `api/routes/reports.py`
    - Accept query parameters: area, initiative, status, owner (all optional)
    - Execute SQL aggregation queries for: total, by_status, by_initiative, by_area, by_owner
    - Compute compliance metrics (sec_approval, docs_link counts and percentages)
    - Compute cross-tabulations: area × initiative, area × status
    - Fetch distinct filter option values (unfiltered)
    - Return `ExecutiveDashboardReport` response
    - _Requirements: 2.1, 2.2, 2.3, 3.4, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 6.1, 6.2, 6.3, 6.5, 7.1, 7.2, 7.3_
  - [ ]* 2.3 Write property test: Filtering correctness (Property 1)
    - **Property 1: Filtering correctness**
    - Generate random contract datasets and random filter combinations using Hypothesis
    - Insert contracts into a test SQLite DB, call the endpoint, verify all aggregations reflect only matching contracts
    - **Validates: Requirements 2.2, 3.2, 3.4, 4.5, 5.4, 6.2, 7.3**
  - [ ]* 2.4 Write property test: Aggregation invariant (Property 2)
    - **Property 2: Aggregation invariant**
    - Generate random contracts, call the endpoint, verify sum of each grouped dict equals total_contracts
    - **Validates: Requirements 2.1, 4.1, 4.2, 4.3, 4.4**
  - [ ]* 2.5 Write property test: Compliance calculation correctness (Property 3)
    - **Property 3: Compliance calculation correctness**
    - Generate random contracts with random sec_approval/docs_link values (some null, some not)
    - Verify compliance percentages match: count(non-null) / total * 100
    - **Validates: Requirements 2.3, 7.1, 7.2**
  - [ ]* 2.6 Write property test: Cross-tabulation correctness (Property 4)
    - **Property 4: Cross-tabulation correctness**
    - Generate random contracts, call the endpoint, verify each cross-tab cell count matches contracts with both dimension values
    - **Validates: Requirements 5.1, 5.2**
  - [ ]* 2.7 Write property test: Cross-tabulation totals invariant (Property 5)
    - **Property 5: Cross-tabulation totals invariant**
    - Generate random cross-tab data, verify row totals = sum of row cells, column totals = sum of column cells, grand total consistent
    - **Validates: Requirements 5.3**
  - [ ]* 2.8 Write unit tests for edge cases
    - Test empty database returns zero counts and empty aggregations
    - Test filters that match no contracts return zero results
    - Test `build_where_clause` with no filters, single filter, and all filters
    - _Requirements: 6.3_

- [x] 3. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Add the Dashboard tab and page structure to the frontend
  - [x] 4.1 Update `frontend/index.html` with the new dashboard tab and page section
    - Add Chart.js CDN script tag
    - Add "Relatório Executivo" button in the nav bar with `data-page="relatorio"`
    - Add `<section id="page-relatorio">` with placeholder structure: filter panel area, KPI cards grid, charts grid, cross-table area
    - Remove or keep the old report modal button (keep for backward compat, or remove — user preference)
    - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.3_
  - [x] 4.2 Add dashboard data fetching and filter logic in `frontend/app.js`
    - Add `loadDashboard()` function that fetches `GET /api/reports/executive-dashboard` with current filter params
    - Populate filter dropdowns from `filter_options` in the API response on first load
    - Wire filter `<select>` change events to re-call `loadDashboard()` with selected values
    - Add a "Limpar Filtros" button that resets all filters and reloads
    - Wire the new nav tab into the existing navigation logic
    - _Requirements: 1.2, 3.1, 3.2, 3.3_

- [x] 5. Render KPI cards and compliance indicators
  - [x] 5.1 Add `renderKPICards(data)` function in `frontend/app.js`
    - Render four KPI cards: Total de Contratos, Contratos Ativos, Em Desenvolvimento, Conformidade de Governança (sec_approval %)
    - Add documentation compliance (docs_link %) as a fifth card
    - Use Tailwind styling with large numbers and labels
    - _Requirements: 2.1, 7.1, 7.2, 8.2, 8.3_

- [x] 6. Render distribution charts
  - [x] 6.1 Add `renderCharts(data)` function in `frontend/app.js`
    - Create/destroy Chart.js instances for: bar chart (by initiative), pie chart (by status), bar chart (by area), horizontal bar chart (by owner)
    - Use consistent status color mapping (active=green, development=blue, inactive=gray, staging=yellow)
    - Charts re-render on each `loadDashboard()` call
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.2, 8.3_

- [x] 7. Render cross-tabulation tables
  - [x] 7.1 Add `renderCrossTable(crossData, containerId, rowLabel, colLabel)` function in `frontend/app.js`
    - Build an HTML table from the cross-tab entries
    - Compute and display row totals, column totals, and grand total
    - Call for both Area × Initiative and Area × Status tables
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.3_

- [x] 8. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases using pytest
- The existing `/api/reports/executive` endpoint is preserved for backward compatibility
- All frontend text is in Portuguese (Brazilian)
