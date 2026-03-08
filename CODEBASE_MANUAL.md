# Janchor Auto Tracker - Codebase Manual

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [File Structure](#3-file-structure)
4. [Build System](#4-build-system)
5. [Data Pipeline](#5-data-pipeline)
6. [JavaScript Application Structure](#6-javascript-application-structure)
7. [Tab Panels and Rendering](#7-tab-panels-and-rendering)
8. [Data Access Layer](#8-data-access-layer)
9. [Chart System](#9-chart-system)
10. [UI Navigation and State](#10-ui-navigation-and-state)
11. [Data Management](#11-data-management)
12. [AI Chat Feature](#12-ai-chat-feature)
13. [Styling and CSS](#13-styling-and-css)
14. [Extending the Dashboard](#14-extending-the-dashboard)

---

## 1. Project Overview

Janchor Auto Tracker is a single-page web application for analyzing Indian automobile industry state-wise primary sales data. It provides interactive charts, tables, KPIs, and an AI-powered chat interface for querying the data.

Key characteristics:
- Self-contained: The entire application (HTML + CSS + JS + data) is generated as a single HTML file
- No backend server: Runs entirely in the browser; data is embedded in the HTML
- Build tool: A single Python script (build_dashboard.py) generates everything
- Deployment: Hosted as a static page on GitHub Pages

Live URL: https://vaidyaritesh88.github.io/Auto-state-database/
Repository: https://github.com/vaidyaritesh88/Auto-state-database

---

## 2. Architecture

```
                    build_dashboard.py (~3100 lines)
                    ================================
                    |                              |
              [Python Section]              [HTML Template]
              Lines 1-222                   Lines 225-3070
                    |                              |
           Excel-to-JSON Converter         Inline CSS + HTML + JS
           OEM name mapping                All embedded in one string
                    |                              |
                    v                              v
               data.json  ──────────────>  dashboard.html (634 KB)
               (raw data)                  (complete SPA)
                                                   |
                                                   v
                                           index.html (copy)
                                           (for GitHub Pages)
```

Why a single file?
- Zero dependencies at runtime (except CDN libs: Plotly.js, SheetJS)
- Easy to share, email, or host anywhere
- No CORS issues, no API servers to maintain
- Data travels with the application

---

## 3. File Structure

```
State-wise analysis/
  build_dashboard.py     # THE source file (~3100 lines) - generates everything
  data.json              # Raw data (2118 rows x 43 quarters) - in .gitignore
  dashboard.html         # Generated output (~634 KB)
  index.html             # Copy of dashboard.html (for GitHub Pages)
  .gitignore             # Excludes data.json
```

Important: build_dashboard.py is the ONLY file you edit. dashboard.html and index.html are generated outputs.

---

## 4. Build System

### How to Build

```bash
# Just build (uses existing data.json)
python build_dashboard.py

# Convert Excel and build
python build_dashboard.py path/to/data.xlsx
```

### Python Section (Lines 1-222)

The Python section handles two jobs:

Job 1: Excel-to-JSON Conversion (lines 16-216)
- convert_excel_to_json(excel_path) - Entry point
- Supports two Excel formats:
  - Old format: Explicit columns (Zone, State, Manufacturer, volumes)
  - Kotak format: Hierarchical layout (Zone > State > OEM rows)
- OEM_NAME_MAP (lines 17-46): Maps 45+ legal manufacturer names to display names
- clean_oem(name): Normalizes OEM names
- Output: data.json with structure {quarters, columns, rows}

Job 2: HTML Generation (lines 218-end)
- Reads data.json into a string
- Embeds it into a large HTML template string
- Writes the complete HTML to dashboard.html

### Data Format (data.json)

```json
{
  "quarters": ["Q1FY16", "Q2FY16", ..., "Q3FY26"],
  "columns": ["segment", "subsegment", "zone", "state", "manufacturer", ...],
  "rows": [
    ["PV", "Cars", "North", "Delhi", "Maruti Suzuki", 5000, 5200, ...],
    ...
  ]
}
```

Row structure (each row is an array):

| Index | Field | Example Values |
|-------|-------|---------------|
| 0 | Segment | PV, 2W, 3W, MHCV, LCV |
| 1 | Subsegment | Cars, UVs, Motorcycle, Scooters, All |
| 2 | Zone | North, South, East, West |
| 3 | State | Delhi, Maharashtra, Tamil Nadu, ... |
| 4 | Manufacturer | Maruti Suzuki, Hyundai, Hero, ... |
| 5+ | Quarterly volumes | Numeric values (0, 1000, 5200, ...) |

Each row represents one unique (Segment, Subsegment, Zone, State, Manufacturer) combination.
There are 2118 rows across 5 segments and 43 quarterly columns (Q1FY16 to Q3FY26).

---

## 5. Data Pipeline

```
data.json --> EMBEDDED_DATA (JS const) --> RAW --> Q, ROWS
                                            |
                                  localStorage override?
                                  (user uploaded data)
```

Lines 626-631:
```javascript
const EMBEDDED_DATA = <data_json>;  // Injected by Python at build time
const RAW = (function(){
  try {
    const s = localStorage.getItem("janchor_auto_data");
    if (s) return JSON.parse(s);
  } catch(e) {}
  return EMBEDDED_DATA;
})();
const DATA_IS_CUSTOM = (RAW !== EMBEDDED_DATA);
const Q = RAW.quarters;   // ["Q1FY16", "Q2FY16", ...]
const NQ = Q.length;      // 43
const ROWS = RAW.rows;    // 2118 rows
```

Fiscal Year derivation (lines 635-648):
```javascript
const FYS = [];           // ["FY16", "FY17", ..., "FY26"]
const FY_Q_IDXS = {};     // {"FY16": [0,1,2,3], "FY17": [4,5,6,7], ...}
// Derived by parsing quarter labels: "Q1FY17" -> "FY17"
```

Key principle: Data flows one way. Raw quarters + rows are the single source of truth. Everything else (FYs, indexes, aggregations) is computed from them.

---

## 6. JavaScript Application Structure

### Global State Variables (lines 681-697)

```javascript
var currentSegment = '2W';       // Active segment
var currentTab = 'overview';     // Active tab panel
var currentSubseg = 'All';       // Subsegment filter
var currentCompany = '';         // Selected company (Company tab)
var currentZone = 'All';         // Zone filter
var currentState = '';           // State filter
var currentGeo = 'state';       // Geo breakdown: 'state' or 'zone'
var viewModes = { overview:'quarterly', company:'quarterly', ... };
var selectedPeriods = { overview: NQ-1, company: NQ-1, ... };
```

### Segment Indexes (lines 705-726)

When a segment changes, buildIndexes() rebuilds:
```javascript
var segRows = [];        // Row indices for current segment
var segCompanies = [];   // Company names in segment (sorted)
var segStates = [];      // State names (sorted)
var segZones = [];       // Zone names (sorted)
var segSubsegs = [];     // Subsegment names (sorted, includes "All")
var zoneStateMap = {};   // {"North": ["Delhi", "UP", ...], ...}
```

### Function Organization

| Section | Lines | Purpose |
|---------|-------|---------|
| Data constants | 626-658 | ROWS, quarters, FY computation |
| Colors and state | 661-726 | COMPANY_COLORS, global state, indexes |
| Data retrieval | 731-856 | filterRows, getXxxVols, computeShare |
| View mode helpers | 755-802 | tsVols, periodVol, yoyPeriodVol |
| Formatting | 804-823 | fmt, fmtPct, fmtPP |
| Analysis | 826-856 | topCompanies, yoyGrowthSeries |
| Chart rendering | 861-960 | plotLines, plotHBar, plotDonut |
| Period selector | 965-981 | populatePeriodSelector |
| Tab renderers | 986-1954 | renderOverview, renderCompanyView, etc. |
| Navigation | 1959-2056 | switchSegment, switchTab, drill functions |
| Data management | 2061-2406 | Upload, parse, reset |
| Table sorting | 2410-2429 | Click-to-sort table headers |
| Event listeners | 2434-2495 | All UI event bindings |
| Chat feature | 2499-3050 | AI chat system |
| Initialization | 3055-3061 | App startup |

---

## 7. Tab Panels and Rendering

### Panel Structure

Each tab has a div with class "panel" and id "panel-{name}" that is shown/hidden.

| Tab | Panel ID | Render Function | Lines |
|-----|----------|----------------|-------|
| Industry Overview | panel-overview | renderOverview() | 986-1192 |
| Company Deep-Dive | panel-company | renderCompanyView() | 1197-1498 |
| State Deep-Dive | panel-state | renderStateView() | 1503-1688 |
| Zone Deep-Dive | panel-zone | renderZoneView() | 1693-1954 |
| Chat | panel-chat | renderChatTab() | 2499-2512 |
| Data Management | panel-data | renderDataTab() | 2061-2085 |

### Render Pattern (every tab follows this)

```javascript
function renderXxxView() {
  // 1. Get data for current filters
  var indQ = getIndustryVols(currentSubseg);
  var compQ = getCompanyVols(currentCompany, currentSubseg);

  // 2. Compute KPIs
  var vol = periodVol(compQ);
  var growth = ...;

  // 3. Update KPI cards in DOM

  // 4. Render charts (Plotly)
  plotLines('chart-xxx', traces, 'Volume');
  plotDonut('chart-yyy', labels, values, colors);

  // 5. Render tables (build HTML string, set on tbody)
}
```

### Subsegment Mix (conditional section)

For segments with 2+ subsegments (PV: Cars/UVs, 2W: Motorcycle/Scooters), an additional section renders:
- 100% stacked bar chart showing subsegment mix over time
- Volumes table per subsegment
- YoY growth table per subsegment

This section is in a hidden div and shown only when applicable:
```javascript
var actualSubsegs = segSubsegs.filter(function(s){return s!=='All';});
if (actualSubsegs.length >= 2 && currentSubseg === 'All') {
  document.getElementById('subseg-mix-xxx').style.display = '';
  // ... render charts and tables
}
```

---

## 8. Data Access Layer

### Core Functions (lines 731-753)

All data access goes through a consistent pattern:

```javascript
// Filter: returns array of row indices matching criteria
filterRows(company, state, subseg, zone)
// null = skip filter. E.g., filterRows('Maruti', null, 'Cars', null)

// Aggregate: sums quarterly volumes for given row indices
sumVolumes(rowIdxs) // Returns: [q1_total, q2_total, ..., qN_total]

// Convenience wrappers:
getIndustryVols(sub)              // All companies, all states
getCompanyVols(co, sub)           // Specific company, all states
getStateIndustryVols(st, sub)     // All companies, specific state
getStateCompanyVols(st, co, sub)  // Specific company + state
getZoneIndustryVols(zone, sub)    // All companies, specific zone
getZoneCompanyVols(zone, co, sub) // Specific company + zone
```

Each returns a quarterly array of length NQ (43).

### Derived Computations

```javascript
annualVols(qVols)              // Quarterly -> annual FY array (length NFY)
computeShare(coVols, indVols)  // Percentage array: co/ind * 100
yoyGrowthSeries(qVols)        // YoY growth % array
topCompanies(n, sub, st, zone) // Top N by volume in selected period
```

---

## 9. Chart System

### Plotly.js Integration (lines 861-960)

All charts use Plotly.js with consistent defaults defined in PLOTLY_LAYOUT.

| Function | Type | Use Case |
|----------|------|----------|
| plotLines(id, traces, yTitle, pctFmt) | Line chart | Volume/share trends |
| plotHBar(id, labels, values, colors) | Horizontal bar | Top states/companies |
| plotHBarDiverging(id, labels, values, colors) | Diverging bar | Share change |
| plotDonut(id, labels, values, colors) | Pie/donut | Zone split, share breakdown |
| plotYoYGrowth(id, traces, title) | Bar chart | YoY growth with zero line |

### Copy-to-Clipboard

Every chart card gets a copy button via addChartCopyBtn(chartId). Uses Plotly.toImage() to capture PNG and navigator.clipboard.write() to copy.

---

## 10. UI Navigation and State

### Segment Switching

```javascript
function switchSegment(seg) {
  currentSegment = seg;
  buildIndexes();           // Rebuild segRows, segCompanies, etc.
  currentSubseg = 'All';   // Reset subsegment
  updateDropdowns();        // Repopulate selectors
  renderSubsegChips();      // Update subsegment buttons
  renderCurrentTab();       // Re-render active tab
}
```

### Drill-Down Navigation

Tables have clickable names that navigate to detail tabs:
```javascript
drillToCompany('Maruti Suzuki')      // -> Company tab
drillToState('Maharashtra', 'West')  // -> State tab
drillToZone('South')                 // -> Zone tab
```

---

## 11. Data Management

### Upload Flow (lines 2362-2398)

```
User drops .xlsx file
  -> FileReader.readAsArrayBuffer()
  -> XLSX.read() (SheetJS library)
  -> parseExcel(workbook)
     -> Detect format (old vs. Kotak)
     -> parseOldFormat() or parseNewFormat()
  -> Validate (quarters, rows)
  -> Store in localStorage("janchor_auto_data")
  -> Store metadata in localStorage("janchor_auto_meta")
  -> Page reload (data reloaded from localStorage)
```

### Reset Flow

```javascript
function resetData() {
  localStorage.removeItem('janchor_auto_data');
  localStorage.removeItem('janchor_auto_meta');
  location.reload();  // Falls back to EMBEDDED_DATA
}
```

---

## 12. AI Chat Feature

See the separate document CHAT_FEATURE_GUIDE.md for a comprehensive guide to the chat architecture, implementation details, and how to replicate it in other applications.

Quick summary:
- Direct browser-to-Anthropic API calls (no backend needed)
- Full raw data for the active segment sent in system prompt
- Prompt caching enabled (90% cost reduction on repeat queries)
- Response parsing supports: text, JS code execution, Plotly charts, tables
- Export saved insights as HTML report
- Download Data CSV button for use with external AI tools

---

## 13. Styling and CSS

### Design System (lines 233-360)

Color Palette:
- Primary blue: #2563eb
- Dark blue (header gradient): #1e3a5f
- Positive (green): #059669
- Negative (red): #dc2626
- Background: #f0f2f5
- Card background: #fff
- Border: #e5e7eb
- Text: #1f2937 (dark), #6b7280 (muted)

Layout:
- Max container width: 1440px
- Chart cards: min-height 340px
- Responsive: single column below 900px

Key CSS Classes:
- .header - Top gradient bar
- .nav-tab / .seg-tab - Navigation buttons
- .panel / .panel.active - Tab content visibility
- .kpi - KPI metric cards
- .chart-card - Chart containers
- .chart-row - Flex row for charts (2 per row default)
- .table-wrap - Scrollable table container
- .view-chip / .subseg-chip - Toggle buttons
- .badge-green / .badge-red - Inline status badges
- .positive / .negative / .neutral - Color utility classes

---

## 14. Extending the Dashboard

### Adding a New Chart to an Existing Tab

1. Add HTML placeholder in the panel section:
```html
<div class="chart-row">
  <div class="chart-card" style="flex:1">
    <div class="chart-title">My New Chart</div>
    <div id="chart-my-new" style="height:340px"></div>
  </div>
</div>
```

2. Add rendering code in the tab render function:
```javascript
var traces = [{
  x: tsLabels(), y: tsVols(someData),
  type: 'scatter', mode: 'lines', name: 'Series'
}];
plotLines('chart-my-new', traces, 'Y-Axis Title');
```

### Adding a New Tab

1. Add nav tab button in HTML
2. Add panel div with content
3. Add render function
4. Register in renderCurrentTab()
5. Add view mode and period selector if needed

### Indian Fiscal Year Conventions

- FY17 = April 2016 to March 2017
- Q1 = Apr-Jun, Q2 = Jul-Sep, Q3 = Oct-Dec, Q4 = Jan-Mar
- Latest FY is usually partial (e.g., FY26 has only Q1-Q3)
- FYTD comparisons must compare same quarters only

---

*Document generated: March 2026*
*Codebase version: build_dashboard.py (~3100 lines)*
