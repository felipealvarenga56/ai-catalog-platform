# Requirements Document

## Introduction

The Executive Report Dashboard is a redesign of the existing executive report feature in the Nexus Governance Platform. The current implementation is a simple modal triggered from the Catálogo page, displaying basic counts. The new feature replaces this with a dedicated navigation tab ("Relatório Executivo") providing a rich, interactive dashboard with KPI cards, dynamic filters, cross-tabulations, and charts — targeting the executive board (C-level) as the primary audience.

## Glossary

- **Dashboard**: The dedicated page/tab within Nexus that displays the executive report with KPIs, charts, filters, and tables.
- **KPI_Card**: A prominent visual card at the top of the Dashboard displaying a single key performance indicator (e.g., total contracts, active count, compliance rate).
- **Filter_Panel**: A UI component containing dropdown selectors and date inputs that allow users to narrow the data displayed on the Dashboard.
- **Cross_Table**: A two-dimensional table that shows contract counts at the intersection of two dimensions (e.g., Area × Initiative).
- **Chart_Component**: A visual chart (bar, pie, or line) rendered using Chart.js that displays aggregated contract data.
- **Report_API**: The FastAPI backend endpoint(s) that serve aggregated, filterable contract data for the Dashboard.
- **Contract**: A record in the `contracts` SQLite table representing a registered project/initiative in the Nexus platform.

## Requirements

### Requirement 1: Dashboard Navigation

**User Story:** As an executive, I want to access the report dashboard from a dedicated tab in the navigation bar, so that I can reach it directly without navigating through the Catálogo page. I want to understand the state of AI across my company.

#### Acceptance Criteria

1. WHEN the Nexus application loads, THE Dashboard SHALL be accessible as a navigation tab labeled "Relatório Executivo" in the main navigation bar.
2. WHEN a user clicks the "Relatório Executivo" tab, THE Dashboard SHALL display the full executive report page and hide other page sections.
3. WHEN the Dashboard tab is active, THE Dashboard SHALL visually indicate the active state using the same styling convention as other navigation tabs.

### Requirement 2: KPI Summary Cards

**User Story:** As an executive, I want to see key performance indicators at a glance at the top of the dashboard, so that I can quickly assess the portfolio health.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE KPI_Card components SHALL display the following metrics: total number of contracts, number of active contracts, number of contracts in development, and governance compliance rate.
2. WHEN filters are applied, THE KPI_Card components SHALL update to reflect only the filtered subset of contracts.
3. THE KPI_Card for governance compliance rate SHALL calculate the percentage as the number of contracts with a non-null `sec_approval` value divided by the total number of contracts in the current filtered set.

### Requirement 3: Dynamic Filters

**User Story:** As an executive, I want to filter the dashboard data by multiple dimensions, so that I can drill down into specific segments of the portfolio.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide filter controls for the following dimensions: area, initiative, status, and owner.
2. WHEN a user selects one or more filter values, THE Dashboard SHALL update all KPI_Cards, Charts, and Cross_Tables to reflect only the contracts matching the selected filters.
3. WHEN a user clears all filters, THE Dashboard SHALL revert to displaying data for the entire contract portfolio.
4. WHEN filters are applied, THE Report_API SHALL accept query parameters for area, initiative, status, and owner, and return only matching contracts in the aggregated response.

### Requirement 4: Distribution Charts

**User Story:** As an executive, I want to see visual charts showing how contracts are distributed across key dimensions, so that I can identify patterns and imbalances.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Chart_Component SHALL render a bar chart showing the count of contracts grouped by initiative.
2. WHEN the Dashboard loads, THE Chart_Component SHALL render a pie chart showing the count of contracts grouped by status.
3. WHEN the Dashboard loads, THE Chart_Component SHALL render a bar chart showing the count of contracts grouped by business area.
4. WHEN the Dashboard loads, THE Chart_Component SHALL render a horizontal bar chart showing the count of contracts grouped by owner.
5. WHEN filters are applied, THE Chart_Component instances SHALL re-render using only the filtered data.

### Requirement 5: Cross-Tabulation Tables

**User Story:** As an executive, I want to see cross-tabulation tables that show contract counts at the intersection of two dimensions, so that I can understand relationships between areas, initiatives, and statuses.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Cross_Table SHALL display a table of contract counts with Area as rows and Initiative as columns.
2. WHEN the Dashboard loads, THE Cross_Table SHALL display a table of contract counts with Area as rows and Status as columns.
3. WHEN the Cross_Table renders, THE Cross_Table SHALL include a totals row and a totals column summing each dimension.
4. WHEN filters are applied, THE Cross_Table instances SHALL update to reflect only the filtered contracts.

### Requirement 6: Enriched Report API

**User Story:** As a developer, I want the report API to return rich, structured data supporting all dashboard visualizations, so that the frontend can render KPIs, charts, and tables from a single endpoint.

#### Acceptance Criteria

1. THE Report_API SHALL return a JSON response containing: total contract count, count by status, count by initiative, count by area, count by owner, governance compliance metrics, and cross-tabulation data for Area × Initiative and Area × Status.
2. WHEN query parameters for area, initiative, status, or owner are provided, THE Report_API SHALL filter the underlying contract data before computing all aggregations.
3. IF no contracts match the provided filters, THEN THE Report_API SHALL return zero counts for all aggregations and empty cross-tabulation tables.
4. THE Report_API response SHALL be serialized using a Pydantic model that validates the structure of all nested aggregation fields.
5. THE Report_API SHALL compute aggregations using SQL queries against the `contracts` table in the SQLite database.

### Requirement 7: Governance Compliance Indicators

**User Story:** As an executive, I want to see governance compliance metrics, so that I can assess how well the portfolio adheres to security and documentation standards.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Dashboard SHALL display the percentage of contracts that have a non-null `sec_approval` value (security approval compliance).
2. WHEN the Dashboard loads, THE Dashboard SHALL display the percentage of contracts that have a non-null `docs_link` value (documentation compliance).
3. WHEN filters are applied, THE Dashboard SHALL recalculate compliance percentages based on the filtered contract set.

### Requirement 8: Responsive Layout and Executive Presentation

**User Story:** As an executive, I want the dashboard to be visually polished and readable on different screen sizes, so that I can present it in meetings or view it on various devices. 

#### Acceptance Criteria

1. THE Dashboard SHALL use a responsive grid layout that adapts from a single-column layout on small screens to a multi-column layout on larger screens.
2. THE Dashboard SHALL use consistent color coding for contract statuses across all charts and tables (e.g., active = green, development = blue, inactive = gray, staging = yellow).
3. THE Dashboard SHALL render all text labels, titles, and descriptions in Portuguese (Brazilian).
4. THE Dashboard SHALL not ressemble AI commom pallettes such as purple hue. Use a combination of dark green pallette
