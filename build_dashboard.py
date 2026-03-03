#!/usr/bin/env python3
"""
Janchor Auto Tracker - Dashboard Generator v2
Fixes: bar-chart axes, adds period picker, annual toggle, YoY growth charts, total rows.
"""
import json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'data.json')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'dashboard.html')

with open(DATA_FILE, 'r') as f:
    data_json = f.read()

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Janchor Auto Tracker</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#1f2937;font-size:14px}
.header{background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.header h1{font-size:18px;font-weight:700;letter-spacing:0.5px;white-space:nowrap}
.seg-tabs{display:flex;gap:4px}
.seg-tab{padding:6px 16px;border-radius:20px;cursor:pointer;font-weight:600;font-size:13px;border:2px solid rgba(255,255,255,0.3);background:transparent;color:rgba(255,255,255,0.8);transition:all 0.2s}
.seg-tab:hover{background:rgba(255,255,255,0.15)}
.seg-tab.active{background:#fff;color:#1e3a5f;border-color:#fff}
.nav{background:#fff;border-bottom:1px solid #e5e7eb;padding:0 24px;display:flex;align-items:center;gap:24px}
.nav-tab{padding:12px 4px;cursor:pointer;font-weight:500;color:#6b7280;border-bottom:2px solid transparent;transition:all 0.2s;font-size:14px}
.nav-tab:hover{color:#1e3a5f}
.nav-tab.active{color:#2563eb;border-bottom-color:#2563eb;font-weight:600}
.main{max-width:1440px;margin:0 auto;padding:16px 24px}
.filter-bar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:16px;padding:12px 16px;background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.08)}
.filter-bar label{font-weight:600;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px}
.filter-bar select{padding:6px 28px 6px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:13px;background:#fff;cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%236b7280' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center}
.filter-bar select:focus{outline:none;border-color:#2563eb;box-shadow:0 0 0 2px rgba(37,99,235,0.2)}
.sep{width:1px;height:24px;background:#e5e7eb;margin:0 4px}
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px}
.kpi{background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08)}
.kpi-label{font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
.kpi-value{font-size:24px;font-weight:700;color:#1f2937}
.kpi-sub{font-size:12px;margin-top:2px}
.kpi-sub.positive{color:#059669}
.kpi-sub.negative{color:#dc2626}
.chart-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.chart-card{background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);min-height:340px}
.chart-card.full{grid-column:1/-1}
.chart-title{font-size:13px;font-weight:600;color:#374151;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.3px}
.table-wrap{background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow-x:auto;margin-bottom:16px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:8px 12px;border-bottom:2px solid #e5e7eb;font-weight:600;color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;cursor:pointer;white-space:nowrap;user-select:none}
th:hover{color:#2563eb}
td{padding:8px 12px;border-bottom:1px solid #f3f4f6;white-space:nowrap}
tr:hover td{background:#f8fafc}
tr.clickable{cursor:pointer}
tr.clickable:hover td{background:#eff6ff}
tr.total-row td{font-weight:700;background:#f8fafc;border-top:2px solid #d1d5db}
.positive{color:#059669}
.negative{color:#dc2626}
.neutral{color:#6b7280}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.badge-green{background:#d1fae5;color:#065f46}
.badge-red{background:#fee2e2;color:#991b1b}
.hidden{display:none!important}
.panel{display:none}
.panel.active{display:block}
@media(max-width:900px){.chart-row{grid-template-columns:1fr}.header{flex-direction:column;text-align:center}}
.subseg-chips{display:flex;gap:6px;flex-wrap:wrap}
.subseg-chip,.view-chip{padding:4px 12px;border-radius:14px;font-size:12px;cursor:pointer;border:1px solid #d1d5db;background:#fff;color:#374151;font-weight:500;transition:all 0.15s}
.subseg-chip:hover,.view-chip:hover{border-color:#2563eb;color:#2563eb}
.subseg-chip.active{background:#2563eb;color:#fff;border-color:#2563eb}
.view-chip.active{background:#1e3a5f;color:#fff;border-color:#1e3a5f}
.align-right{text-align:right}
.upload-zone{border:2px dashed #d1d5db;border-radius:12px;padding:48px 24px;text-align:center;cursor:pointer;transition:all 0.2s;background:#fafbfc;margin-bottom:16px}
.upload-zone:hover,.upload-zone.dragover{border-color:#2563eb;background:#eff6ff}
.upload-zone h3{font-size:16px;color:#374151;margin-bottom:8px}
.upload-zone p{font-size:13px;color:#6b7280;margin:0}
.upload-zone input[type=file]{display:none}
.data-info{background:#fff;border-radius:8px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08);margin-bottom:16px}
.data-info h3{font-size:14px;font-weight:600;color:#374151;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.3px}
.data-info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.data-info-item{padding:12px;background:#f8fafc;border-radius:6px;border:1px solid #e5e7eb}
.data-info-item .di-label{font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
.data-info-item .di-value{font-size:16px;font-weight:700;color:#1f2937}
.status-msg{padding:12px 16px;border-radius:8px;font-size:13px;margin-bottom:12px;display:none}
.status-msg.show{display:block}
.status-msg.success{background:#d1fae5;color:#065f46}
.status-msg.error{background:#fee2e2;color:#991b1b}
.status-msg.info{background:#dbeafe;color:#1e40af}
#table-co-share-ts{font-size:11px;white-space:nowrap}
#table-co-share-ts th,#table-co-share-ts td{padding:4px 8px;min-width:60px}
#table-co-share-ts thead th:first-child{position:sticky;left:0;z-index:2;background:#f8fafc}
#table-co-share-ts tbody td:first-child{position:sticky;left:0;z-index:1;background:#fff}
.table-wrap{overflow-x:auto}
.btn{padding:8px 20px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all 0.15s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:#2563eb;color:#fff}.btn-primary:hover{background:#1d4ed8}
.btn-outline{background:#fff;color:#6b7280;border:1px solid #d1d5db}.btn-outline:hover{border-color:#2563eb;color:#2563eb}
.btn-danger{background:#fff;color:#dc2626;border:1px solid #fecaca}.btn-danger:hover{background:#fef2f2;border-color:#dc2626}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="header">
  <h1>JANCHOR AUTO TRACKER</h1>
  <div class="seg-tabs" id="segTabs">
    <div class="seg-tab active" data-seg="2W">2W</div>
    <div class="seg-tab" data-seg="PV">PV</div>
    <div class="seg-tab" data-seg="3W">3W</div>
    <div class="seg-tab" data-seg="MHCV">MHCV</div>
    <div class="seg-tab" data-seg="LCV">LCV</div>
  </div>
</div>
<div class="nav" id="navTabs">
  <div class="nav-tab active" data-tab="overview">Industry Overview</div>
  <div class="nav-tab" data-tab="company">Company Deep-Dive</div>
  <div class="nav-tab" data-tab="state">State Deep-Dive</div>
  <div class="nav-tab" data-tab="data" style="margin-left:auto;color:#9ca3af">&#9881; Data</div>
</div>
<div class="main">

<!-- OVERVIEW PANEL -->
<div class="panel active" id="panel-overview">
  <div class="filter-bar">
    <label>View:</label>
    <div class="subseg-chips" id="viewChips-overview">
      <div class="view-chip active" data-view="quarterly">Quarterly</div>
      <div class="view-chip" data-view="annual">Annual</div>
    </div>
    <div class="sep"></div>
    <label>Period:</label>
    <select id="sel-period-overview"></select>
    <div class="sep"></div>
    <label>Subsegment:</label>
    <div class="subseg-chips" id="subsegChips-overview"></div>
  </div>
  <div class="kpi-row" id="kpi-overview"></div>
  <div class="chart-row">
    <div class="chart-card"><div class="chart-title" id="title-ov-vol">Industry Volume Trend</div><div id="chart-ov-vol" style="height:300px"></div></div>
    <div class="chart-card"><div class="chart-title">Market Share Trend - Top Companies</div><div id="chart-ov-share" style="height:300px"></div></div>
  </div>
  <div class="table-wrap">
    <div class="chart-title">Company Rankings (<span id="ov-latest-qtr"></span>)</div>
    <table id="table-ov-companies"><thead></thead><tbody></tbody></table>
  </div>
</div>

<!-- COMPANY PANEL -->
<div class="panel" id="panel-company">
  <div class="filter-bar">
    <label>Company:</label>
    <select id="sel-company"></select>
    <div class="sep"></div>
    <label>View:</label>
    <div class="subseg-chips" id="viewChips-company">
      <div class="view-chip active" data-view="quarterly">Quarterly</div>
      <div class="view-chip" data-view="annual">Annual</div>
    </div>
    <div class="sep"></div>
    <label>Period:</label>
    <select id="sel-period-company"></select>
    <div class="sep"></div>
    <label>Subsegment:</label>
    <div class="subseg-chips" id="subsegChips-company"></div>
    <div class="sep"></div>
    <label>Geo:</label>
    <div class="subseg-chips" id="geoChips-company">
      <div class="view-chip active" data-geo="state">State</div>
      <div class="view-chip" data-geo="zone">Zone</div>
    </div>
  </div>
  <div class="kpi-row" id="kpi-company"></div>
  <div class="chart-row">
    <div class="chart-card"><div class="chart-title" id="title-co-vol">Volume Trend</div><div id="chart-co-vol" style="height:300px"></div></div>
    <div class="chart-card"><div class="chart-title">Market Share Trend</div><div id="chart-co-share" style="height:300px"></div></div>
  </div>
  <div class="chart-row">
    <div class="chart-card full"><div class="chart-title">YoY Volume Growth Trend (%)</div><div id="chart-co-yoy" style="height:280px"></div></div>
  </div>
  <div class="chart-row">
    <div class="chart-card"><div class="chart-title" id="title-co-states">Top States by Volume</div><div id="chart-co-states" style="height:400px"></div></div>
    <div class="chart-card"><div class="chart-title" id="title-co-share-chg">Market Share Change by State (YoY, pp)</div><div id="chart-co-share-chg" style="height:400px"></div></div>
  </div>
  <div class="chart-row">
    <div class="chart-card full"><div class="chart-title" id="title-co-contrib">Sales Contribution Trend by State (%)</div><div id="chart-co-contrib" style="height:340px"></div></div>
  </div>
  <div class="table-wrap">
    <div class="chart-title" id="title-co-share-ts">Market Share Time-Series by State (%)</div>
    <table id="table-co-share-ts"><thead></thead><tbody></tbody></table>
  </div>
  <div class="table-wrap">
    <div class="chart-title" id="title-co-geo-details">State-wise Details</div>
    <table id="table-co-states"><thead></thead><tbody></tbody></table>
  </div>
</div>

<!-- STATE PANEL -->
<div class="panel" id="panel-state">
  <div class="filter-bar">
    <label>Zone:</label>
    <select id="sel-zone"><option value="All">All Zones</option></select>
    <label style="margin-left:8px">State:</label>
    <select id="sel-state"></select>
    <div class="sep"></div>
    <label>View:</label>
    <div class="subseg-chips" id="viewChips-state">
      <div class="view-chip active" data-view="quarterly">Quarterly</div>
      <div class="view-chip" data-view="annual">Annual</div>
    </div>
    <div class="sep"></div>
    <label>Period:</label>
    <select id="sel-period-state"></select>
    <div class="sep"></div>
    <label>Subsegment:</label>
    <div class="subseg-chips" id="subsegChips-state"></div>
  </div>
  <div class="kpi-row" id="kpi-state"></div>
  <div class="chart-row">
    <div class="chart-card"><div class="chart-title" id="title-st-vol">Industry Volume Trend in State</div><div id="chart-st-vol" style="height:300px"></div></div>
    <div class="chart-card"><div class="chart-title" id="title-st-pie">Market Share Breakdown</div><div id="chart-st-pie" style="height:300px"></div></div>
  </div>
  <div class="chart-row">
    <div class="chart-card"><div class="chart-title">Market Share Trends - Top Companies</div><div id="chart-st-share" style="height:300px"></div></div>
    <div class="chart-card"><div class="chart-title">YoY Volume Growth Trend (%)</div><div id="chart-st-yoy" style="height:300px"></div></div>
  </div>
  <div class="table-wrap">
    <div class="chart-title">Company Rankings in State</div>
    <table id="table-st-companies"><thead></thead><tbody></tbody></table>
  </div>
</div>

<!-- DATA MANAGEMENT PANEL -->
<div class="panel" id="panel-data">
  <div style="max-width:800px;margin:0 auto">
    <div class="status-msg" id="data-status"></div>
    <div class="data-info" id="data-info-box">
      <h3>Current Data</h3>
      <div class="data-info-grid" id="data-info-grid"></div>
    </div>
    <div class="upload-zone" id="upload-zone">
      <input type="file" id="file-input" accept=".xlsx,.xls">
      <h3>&#128193; Upload New Data File</h3>
      <p>Drag &amp; drop your Excel file here, or click to browse</p>
      <p style="margin-top:8px;font-size:11px;color:#9ca3af">Accepts .xlsx files with raw data sheets (PVs, 2Ws, 3Ws, M&amp;HCVs, LCVs)</p>
    </div>
    <div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap">
      <button class="btn btn-danger" id="btn-reset-data" style="display:none">Reset to Embedded Data</button>
    </div>
  </div>
</div>

</div>

<script>
// ============================================
// DATA
// ============================================
const EMBEDDED_DATA = ''' + data_json + ''';
const RAW = (function(){try{const s=localStorage.getItem("janchor_auto_data");if(s)return JSON.parse(s);}catch(e){}return EMBEDDED_DATA;})();
const DATA_IS_CUSTOM = (RAW !== EMBEDDED_DATA);
const Q = RAW.quarters;
const NQ = Q.length;
const ROWS = RAW.rows;

// ============================================
// FISCAL YEAR / ANNUAL HELPERS
// ============================================
const FYS = []; // ['FY17','FY18',...] derived dynamically from Q
const FY_Q_IDXS = {}; // {'FY17':[0,1,2,3], ...}
(function() {
  for (let i = 0; i < Q.length; i++) {
    const fy = 'FY' + Q[i].slice(4); // "Q1FY17" -> "FY17"
    if (!FY_Q_IDXS[fy]) { FYS.push(fy); FY_Q_IDXS[fy] = []; }
    FY_Q_IDXS[fy].push(i);
  }
})();
const NFY = FYS.length;

function annualVols(qVols) {
  return FYS.map(fy => FY_Q_IDXS[fy].reduce((s, qi) => s + qVols[qi], 0));
}

function fyDates() {
  return FYS.map(fy => {
    const yr = 2000 + parseInt(fy.slice(2)) - 1;
    return new Date(yr, 3, 1); // April of start year
  });
}
const FYDATES = fyDates();
const FYLABELS = [...FYS]; // "FY17", "FY18", ...

// ============================================
// CONSTANTS & CONFIG
// ============================================
const COMPANY_COLORS = {
  'Maruti':'#FF6B35','Hyundai':'#004B87','Tata Motors':'#1B1464','M&M':'#C62828','Kia':'#BB162B',
  'Toyota':'#EB0A1E','Honda':'#CC0000','Renault':'#F4B400','Skoda':'#4CAF50','MG Motor':'#FF5722',
  'Volkswagen':'#1565C0','Nissan':'#C0392B','Ford':'#1A237E','Force Motors':'#795548',
  'Hero':'#00A651','Bajaj':'#0055A5','Royal Enfield':'#212121','TVS Motors':'#E30613',
  'Yamaha':'#005AAC','Suzuki':'#003DA5','Ather':'#00BCD4','Okinawa':'#FF9800',
  'Piaggio':'#4CAF50','Ashok Leyland':'#C41230','VECV':'#FFB800','SML Isuzu':'#607D8B',
  'Atul Auto':'#8BC34A','TI Clean Mobility':'#00ACC1','Continental Engines':'#9C27B0',
  'Scooters India':'#CDDC39','Isuzu':'#455A64',
  'AMW Motors':'#3F51B5','Pinnacle Mobility':'#009688','PMI Electro Mobility':'#E91E63',
  'Volvo Group':'#1B5E20','VECV-Volvo':'#33691E','Maruti Suzuki':'#FF6B35','Isuzu Motors':'#455A64'
};
const PALETTE = ['#2563eb','#dc2626','#059669','#d97706','#7c3aed','#db2777','#0891b2','#65a30d','#ea580c','#4f46e5','#be123c','#0d9488','#ca8a04','#9333ea','#e11d48'];
function getColor(company, idx) { return COMPANY_COLORS[company] || PALETTE[idx % PALETTE.length]; }

// ============================================
// STATE
// ============================================
let currentSegment = '2W';
let currentTab = 'overview';
let currentSubseg = 'All';
let currentCompany = '';
let currentZone = 'All';
let currentState = '';
let currentGeo = 'state'; // 'state' or 'zone' — for company deep-dive geo breakdown
let viewMode = 'quarterly'; // per-tab
const viewModes = {overview:'quarterly', company:'quarterly', state:'quarterly'};
const selectedPeriods = {overview: NQ-1, company: NQ-1, state: NQ-1}; // quarter index or fy index

function getViewMode() { return viewModes[currentTab]; }
function getSelectedPeriod() { return selectedPeriods[currentTab]; }

// ============================================
// INDEXES
// ============================================
let segRows = [], segCompanies = [], segStates = [], segZones = [], segSubsegs = [];
let zoneStateMap = {};

function buildIndexes() {
  segRows = [];
  const compSet = new Set(), stateSet = new Set(), zoneSet = new Set(), subsegSet = new Set();
  zoneStateMap = {};
  for (let i = 0; i < ROWS.length; i++) {
    if (ROWS[i][0] === currentSegment) {
      segRows.push(i);
      compSet.add(ROWS[i][4]); stateSet.add(ROWS[i][3]); zoneSet.add(ROWS[i][2]); subsegSet.add(ROWS[i][1]);
      const z = ROWS[i][2], s = ROWS[i][3];
      if (!zoneStateMap[z]) zoneStateMap[z] = new Set();
      zoneStateMap[z].add(s);
    }
  }
  segCompanies = [...compSet].sort();
  segStates = [...stateSet].sort();
  segZones = [...zoneSet].sort();
  segSubsegs = [...subsegSet].sort();
  for (const z in zoneStateMap) zoneStateMap[z] = [...zoneStateMap[z]].sort();
}

// ============================================
// DATA HELPERS
// ============================================
function filterRows(company, state, subseg, zone) {
  let rows = segRows;
  if (subseg && subseg !== 'All') rows = rows.filter(i => ROWS[i][1] === subseg);
  if (company) rows = rows.filter(i => ROWS[i][4] === company);
  if (state) rows = rows.filter(i => ROWS[i][3] === state);
  if (zone) rows = rows.filter(i => ROWS[i][2] === zone);
  return rows;
}

function sumVolumes(rowIdxs) {
  const vols = new Array(NQ).fill(0);
  for (const i of rowIdxs) { for (let q = 0; q < NQ; q++) vols[q] += (ROWS[i][5+q]||0); }
  return vols;
}

function getIndustryVols(sub) { return sumVolumes(filterRows(null,null,sub)); }
function getCompanyVols(co,sub) { return sumVolumes(filterRows(co,null,sub)); }
function getStateIndustryVols(st,sub) { return sumVolumes(filterRows(null,st,sub)); }
function getStateCompanyVols(st,co,sub) { return sumVolumes(filterRows(co,st,sub)); }
function getZoneIndustryVols(zone,sub) { return sumVolumes(filterRows(null,null,sub,zone)); }
function getZoneCompanyVols(zone,co,sub) { return sumVolumes(filterRows(co,null,sub,zone)); }
function computeShare(cv,iv) { return cv.map((v,i) => iv[i]>0 ? v/iv[i]*100 : 0); }

// Get volumes for current view mode
function tsVols(qVols) { return getViewMode()==='annual' ? annualVols(qVols) : qVols; }
function tsDates() { return getViewMode()==='annual' ? FYLABELS : QLABELS; }
function tsLabels() { return getViewMode()==='annual' ? FYLABELS : QLABELS; }
function tsLen() { return getViewMode()==='annual' ? NFY : NQ; }

// Period helpers: convert selected period index to quarter indices for data lookup
function periodQIdxs() {
  const vm = getViewMode(), pi = getSelectedPeriod();
  if (vm === 'annual') return FY_Q_IDXS[FYS[pi]] || [];
  return [pi];
}
function periodVol(qVols) { return periodQIdxs().reduce((s,qi) => s + qVols[qi], 0); }
function periodLabel() {
  const vm = getViewMode(), pi = getSelectedPeriod();
  if (vm === 'annual') return FYS[pi] + (FY_Q_IDXS[FYS[pi]].length < 4 ? ' YTD' : '');
  return QLABELS[pi];
}
// YoY comparison period
function yoyPeriodQIdxs() {
  const vm = getViewMode(), pi = getSelectedPeriod();
  if (vm === 'annual') {
    const prevFY = pi > 0 ? FYS[pi-1] : null;
    if (!prevFY) return [];
    // For partial year, compare same quarters
    const curQs = FY_Q_IDXS[FYS[pi]];
    const prevQs = FY_Q_IDXS[prevFY];
    return prevQs.slice(0, curQs.length);
  }
  return pi >= 4 ? [pi - 4] : [];
}
function yoyPeriodVol(qVols) { return yoyPeriodQIdxs().reduce((s,qi) => s + qVols[qi], 0); }
function yoyPeriodLabel() {
  const vm = getViewMode(), pi = getSelectedPeriod();
  if (vm === 'annual') {
    if (pi > 0) {
      const curQs = FY_Q_IDXS[FYS[pi]];
      return FYS[pi-1] + (curQs.length < 4 ? ' (comparable)' : '');
    }
    return '-';
  }
  return pi >= 4 ? QLABELS[pi-4] : '-';
}

function fmt(n) {
  if (n === 0) return '0';
  if (Math.abs(n) >= 1e7) return (n/1e7).toFixed(1)+'Cr';
  if (Math.abs(n) >= 1e5) return (n/1e5).toFixed(1)+'L';
  if (Math.abs(n) >= 1e3) return (n/1e3).toFixed(1)+'K';
  return Math.round(n).toLocaleString('en-IN');
}
function fmtPct(n) { return n.toFixed(1)+'%'; }
function fmtPP(n) { return (n>=0?'+':'')+n.toFixed(1)+' pp'; }

function quarterDates() {
  return Q.map(q => {
    const qn=parseInt(q[1]), fy=parseInt(q.slice(4));
    const months={1:3,2:6,3:9,4:0};
    const yr=2000+fy-1+(qn===4?1:0);
    return new Date(yr,months[qn],1);
  });
}
const QDATES = quarterDates();
const QLABELS = Q.map(q => q[1]+'Q'+q.slice(2)); // "1QFY17","2QFY17",...

// Top N companies by volume in selected period
function topCompanies(n, sub, state) {
  const volMap = {};
  const rows = state ? filterRows(null,state,sub) : filterRows(null,null,sub);
  for (const i of rows) {
    const c = ROWS[i][4];
    volMap[c] = (volMap[c]||0) + periodQIdxs().reduce((s,qi) => s+(ROWS[i][5+qi]||0), 0);
  }
  return Object.entries(volMap).sort((a,b)=>b[1]-a[1]).slice(0,n).map(e=>e[0]);
}

// YoY growth time-series
function yoyGrowthSeries(qVols) {
  const vm = getViewMode();
  if (vm === 'annual') {
    const av = annualVols(qVols);
    return av.map((v,i) => {
      if (i === 0) return null;
      const prev = av[i-1];
      return prev > 0 ? ((v/prev-1)*100) : null;
    });
  }
  return qVols.map((v,i) => {
    if (i < 4) return null;
    const prev = qVols[i-4];
    return prev > 0 ? ((v/prev-1)*100) : null;
  });
}

// ============================================
// CHART RENDERING
// ============================================
const PLOTLY_LAYOUT = {
  margin:{l:50,r:20,t:10,b:40},
  font:{family:'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif',size:11},
  hovermode:'x unified',
  legend:{orientation:'h',y:-0.18,font:{size:10}},
  xaxis:{showgrid:false,tickangle:-45},
  yaxis:{showgrid:true,gridcolor:'#f0f0f0'},
  plot_bgcolor:'white',paper_bgcolor:'white'
};
const PLOTLY_CONFIG = {responsive:true,displayModeBar:false};

function plotLines(id, traces, yTitle, pctFmt) {
  const layout = {...PLOTLY_LAYOUT,
    yaxis:{...PLOTLY_LAYOUT.yaxis, title:yTitle, tickformat:pctFmt?'.1f':',', ticksuffix:pctFmt?'%':''}
  };
  Plotly.newPlot(id, traces, layout, PLOTLY_CONFIG);
}

function plotHBar(id, labels, values, colors) {
  const trace = {
    type:'bar', orientation:'h',
    y:labels, x:values,
    marker:{color:colors||'#2563eb'},
    text:values.map(v => typeof v==='number'?(Math.abs(v)<10?v.toFixed(1):fmt(v)):v),
    textposition:'outside', textfont:{size:10},
    hovertemplate:'%{y}: %{x:,.0f}<extra></extra>'
  };
  const layout = {
    ...PLOTLY_LAYOUT, hovermode:'closest',
    margin:{l:130,r:70,t:10,b:30},
    yaxis:{autorange:'reversed',showgrid:false,type:'category'},
    xaxis:{showgrid:true,gridcolor:'#f0f0f0',type:'linear'}
  };
  Plotly.newPlot(id,[trace],layout,PLOTLY_CONFIG);
}

function plotHBarDiverging(id, labels, values, colors) {
  const trace = {
    type:'bar', orientation:'h',
    y:labels, x:values,
    marker:{color:colors},
    text:values.map(v => (v>=0?'+':'')+v.toFixed(1)),
    textposition:'outside', textfont:{size:10},
    hovertemplate:'%{y}: %{x:.1f} pp<extra></extra>'
  };
  const layout = {
    ...PLOTLY_LAYOUT, hovermode:'closest',
    margin:{l:130,r:60,t:10,b:30},
    yaxis:{autorange:'reversed',showgrid:false,type:'category'},
    xaxis:{showgrid:true,gridcolor:'#f0f0f0',type:'linear',zeroline:true,zerolinecolor:'#94a3b8'}
  };
  Plotly.newPlot(id,[trace],layout,PLOTLY_CONFIG);
}

function plotDonut(id, labels, values, colors) {
  const trace = {
    type:'pie',labels,values,hole:0.45,marker:{colors},
    textinfo:'label+percent',textposition:'outside',textfont:{size:10},
    hovertemplate:'%{label}: %{value:,.0f} (%{percent})<extra></extra>',sort:false
  };
  Plotly.newPlot(id,[trace],{...PLOTLY_LAYOUT,showlegend:false,margin:{l:10,r:10,t:10,b:10}},PLOTLY_CONFIG);
}

function plotYoYGrowth(id, traces, title) {
  const layout = {
    ...PLOTLY_LAYOUT,
    yaxis:{...PLOTLY_LAYOUT.yaxis, title:'YoY Growth (%)', ticksuffix:'%', zeroline:true, zerolinecolor:'#94a3b8', zerolinewidth:1.5},
    shapes:[{type:'line',x0:0,x1:1,xref:'paper',y0:0,y1:0,line:{color:'#94a3b8',width:1.5,dash:'dot'}}]
  };
  Plotly.newPlot(id, traces, layout, PLOTLY_CONFIG);
}

// ============================================
// PERIOD SELECTOR
// ============================================
function populatePeriodSelector(tabName) {
  const sel = document.getElementById('sel-period-' + tabName);
  if (!sel) return;
  const vm = viewModes[tabName];
  sel.innerHTML = '';
  if (vm === 'annual') {
    FYS.forEach((fy,i) => {
      const lbl = fy + (FY_Q_IDXS[fy].length < 4 ? ' (YTD)' : '');
      sel.innerHTML += '<option value="'+i+'"'+(i===selectedPeriods[tabName]?' selected':'')+'>'+lbl+'</option>';
    });
  } else {
    Q.forEach((q,i) => {
      sel.innerHTML += '<option value="'+i+'"'+(i===selectedPeriods[tabName]?' selected':'')+'>'+QLABELS[i]+'</option>';
    });
  }
  sel.value = selectedPeriods[tabName];
}

// ============================================
// OVERVIEW
// ============================================
function renderOverview() {
  const sub = currentSubseg;
  const indQ = getIndustryVols(sub);

  // KPIs use selected period
  const curVol = periodVol(indQ);
  const yoyV = yoyPeriodVol(indQ);
  const yoyG = yoyV > 0 ? ((curVol/yoyV-1)*100) : 0;

  const comps = topCompanies(50,sub,null);
  let bestGainer='',bestGain=-999,bestLoser='',bestLoss=999;
  for (const c of comps) {
    const cv = getCompanyVols(c,sub);
    const curC = periodVol(cv), yoyC = yoyPeriodVol(cv);
    const sCur = curVol>0?curC/curVol*100:0;
    const sYoy = yoyV>0?yoyC/yoyV*100:0;
    const chg = sCur-sYoy;
    if (chg>bestGain && sCur>0.5){bestGain=chg;bestGainer=c;}
    if (chg<bestLoss && sYoy>0.5){bestLoss=chg;bestLoser=c;}
  }

  document.getElementById('kpi-overview').innerHTML = `
    <div class="kpi"><div class="kpi-label">Industry Volume (${periodLabel()})</div><div class="kpi-value">${fmt(curVol)}</div></div>
    <div class="kpi"><div class="kpi-label">YoY Growth vs ${yoyPeriodLabel()}</div><div class="kpi-value ${yoyG>=0?'positive':'negative'}">${yoyG>=0?'+':''}${yoyG.toFixed(1)}%</div></div>
    <div class="kpi"><div class="kpi-label">Top Share Gainer</div><div class="kpi-value" style="font-size:18px">${bestGainer}</div><div class="kpi-sub positive">${fmtPP(bestGain)}</div></div>
    <div class="kpi"><div class="kpi-label">Top Share Loser</div><div class="kpi-value" style="font-size:18px">${bestLoser}</div><div class="kpi-sub negative">${fmtPP(bestLoss)}</div></div>
  `;

  document.getElementById('ov-latest-qtr').textContent = periodLabel();
  document.getElementById('title-ov-vol').textContent = 'Industry Volume Trend (' + (getViewMode()==='annual'?'Annual':'Quarterly') + ')';

  // Volume trend
  const tsV = tsVols(indQ);
  plotLines('chart-ov-vol',[{
    x:tsDates(),y:tsV,type:'scatter',mode:'lines+markers',
    name:'Industry Volume',line:{color:'#2563eb',width:2.5},marker:{size:4},
    fill:'tozeroy',fillcolor:'rgba(37,99,235,0.08)',
    hovertemplate:'%{x}: %{y:,.0f}<extra></extra>'
  }],'Volume (units)',false);

  // Market share trend
  const top8 = topCompanies(8,sub,null);
  const shareTraces = top8.map((c,ci) => {
    const cv = getCompanyVols(c,sub);
    const share = computeShare(tsVols(cv), tsV);
    return {x:tsDates(),y:share,type:'scatter',mode:'lines',name:c,line:{color:getColor(c,ci),width:2},
      hovertemplate:c+': %{y:.1f}%<extra></extra>'};
  });
  plotLines('chart-ov-share',shareTraces,'Market Share (%)',true);

  // Company table
  renderOverviewTable(sub);
}

function renderOverviewTable(sub) {
  const indQ = getIndustryVols(sub);
  const curIndVol = periodVol(indQ);
  const yoyIndVol = yoyPeriodVol(indQ);
  const comps = topCompanies(50,sub,null);

  const tableData = comps.map(c => {
    const cv = getCompanyVols(c,sub);
    const vol = periodVol(cv);
    const yv = yoyPeriodVol(cv);
    const growth = yv>0?((vol/yv-1)*100):0;
    const share = curIndVol>0?(vol/curIndVol*100):0;
    const shareY = yoyIndVol>0?(yv/yoyIndVol*100):0;
    return {company:c,vol,yoyVol:yv,growth,share,shareChg:share-shareY};
  }).filter(d=>d.vol>0);
  tableData.sort((a,b)=>b.vol-a.vol);

  // Total
  const totVol = tableData.reduce((s,d)=>s+d.vol,0);
  const totYoy = tableData.reduce((s,d)=>s+d.yoyVol,0);
  const totGrowth = totYoy>0?((totVol/totYoy-1)*100):0;

  const thead = document.querySelector('#table-ov-companies thead');
  thead.innerHTML = '<tr><th>#</th><th>Company</th><th class="align-right">Volume</th><th class="align-right">YoY Volume</th><th class="align-right">YoY Growth</th><th class="align-right">Mkt Share</th><th class="align-right">Share Chg</th></tr>';

  const tbody = document.querySelector('#table-ov-companies tbody');
  tbody.innerHTML = tableData.map((d,i) => `
    <tr class="clickable" onclick="drillToCompany('${esc(d.company)}')">
      <td>${i+1}</td><td><b>${d.company}</b></td>
      <td class="align-right">${fmt(d.vol)}</td><td class="align-right">${fmt(d.yoyVol)}</td>
      <td class="align-right ${d.growth>=0?'positive':'negative'}">${d.growth>=0?'+':''}${d.growth.toFixed(1)}%</td>
      <td class="align-right">${d.share.toFixed(1)}%</td>
      <td class="align-right"><span class="badge ${d.shareChg>=0?'badge-green':'badge-red'}">${fmtPP(d.shareChg)}</span></td>
    </tr>
  `).join('') + `
    <tr class="total-row"><td></td><td><b>TOTAL</b></td>
      <td class="align-right"><b>${fmt(totVol)}</b></td><td class="align-right"><b>${fmt(totYoy)}</b></td>
      <td class="align-right ${totGrowth>=0?'positive':'negative'}"><b>${totGrowth>=0?'+':''}${totGrowth.toFixed(1)}%</b></td>
      <td class="align-right"><b>100.0%</b></td><td class="align-right"></td>
    </tr>`;
}

// ============================================
// COMPANY DEEP-DIVE
// ============================================
function renderCompanyView() {
  const c = currentCompany, sub = currentSubseg;
  if (!c) return;

  const indQ = getIndustryVols(sub);
  const cvQ = getCompanyVols(c,sub);
  const curVol = periodVol(cvQ), yoyV = yoyPeriodVol(cvQ);
  const curInd = periodVol(indQ), yoyInd = yoyPeriodVol(indQ);
  const growth = yoyV>0?((curVol/yoyV-1)*100):0;
  const shareCur = curInd>0?(curVol/curInd*100):0;
  const shareYoy = yoyInd>0?(yoyV/yoyInd*100):0;
  const shareChg = shareCur-shareYoy;

  document.getElementById('kpi-company').innerHTML = `
    <div class="kpi"><div class="kpi-label">Volume (${periodLabel()})</div><div class="kpi-value">${fmt(curVol)}</div></div>
    <div class="kpi"><div class="kpi-label">Market Share</div><div class="kpi-value">${shareCur.toFixed(1)}%</div><div class="kpi-sub ${shareChg>=0?'positive':'negative'}">${fmtPP(shareChg)} YoY</div></div>
    <div class="kpi"><div class="kpi-label">YoY Volume Growth</div><div class="kpi-value ${growth>=0?'positive':'negative'}">${growth>=0?'+':''}${growth.toFixed(1)}%</div></div>
    <div class="kpi"><div class="kpi-label">Industry Rank</div><div class="kpi-value">#${topCompanies(50,sub,null).indexOf(c)+1}</div></div>
  `;

  const vm = getViewMode();
  document.getElementById('title-co-vol').textContent = 'Volume Trend (' + (vm==='annual'?'Annual':'Quarterly') + ')';
  const geoLabel = currentGeo === 'zone' ? 'Zone' : 'State';
  document.getElementById('title-co-states').textContent = 'Top ' + geoLabel + 's by Volume (' + periodLabel() + ')';
  document.getElementById('title-co-share-chg').textContent = 'Mkt Share Change by ' + geoLabel + ' (YoY, pp) - ' + periodLabel();
  document.getElementById('title-co-contrib').textContent = 'Sales Contribution Trend by ' + geoLabel + ' (%)';
  document.getElementById('title-co-share-ts').textContent = 'Market Share Time-Series by ' + geoLabel + ' (%)';
  document.getElementById('title-co-geo-details').textContent = geoLabel + '-wise Details';

  // Volume trend
  const tsC = tsVols(cvQ), tsI = tsVols(indQ);
  Plotly.newPlot('chart-co-vol',[
    {x:tsDates(),y:tsC,type:'scatter',mode:'lines+markers',name:c+' Volume',line:{color:getColor(c,0),width:2.5},marker:{size:4},hovertemplate:c+': %{y:,.0f}<extra></extra>'},
    {x:tsDates(),y:tsI,type:'scatter',mode:'lines',name:'Industry',yaxis:'y2',line:{color:'#94a3b8',width:1.5,dash:'dot'},hovertemplate:'Industry: %{y:,.0f}<extra></extra>'}
  ],{...PLOTLY_LAYOUT,yaxis:{title:c,showgrid:true,gridcolor:'#f0f0f0'},yaxis2:{title:'Industry',overlaying:'y',side:'right',showgrid:false},legend:{orientation:'h',y:-0.18,font:{size:10}}},PLOTLY_CONFIG);

  // Market share trend
  const shareTS = computeShare(tsC, tsI);
  plotLines('chart-co-share',[{
    x:tsDates(),y:shareTS,type:'scatter',mode:'lines+markers',name:'Market Share',
    line:{color:getColor(c,0),width:2.5},marker:{size:4},
    fill:'tozeroy',fillcolor:getColor(c,0)+'15',
    hovertemplate:'Share: %{y:.1f}%<extra></extra>'
  }],'Market Share (%)',true);

  // YoY growth trend
  const coYoY = yoyGrowthSeries(cvQ);
  const indYoY = yoyGrowthSeries(indQ);
  const dates = tsDates();
  plotYoYGrowth('chart-co-yoy',[
    {x:dates,y:vm==='annual'?coYoY:coYoY,type:'scatter',mode:'lines+markers',name:c,line:{color:getColor(c,0),width:2.5},marker:{size:4},connectgaps:false,hovertemplate:c+': %{y:.1f}%<extra></extra>'},
    {x:dates,y:vm==='annual'?indYoY:indYoY,type:'scatter',mode:'lines',name:'Industry',line:{color:'#94a3b8',width:1.5,dash:'dot'},connectgaps:false,hovertemplate:'Industry: %{y:.1f}%<extra></extra>'}
  ]);

  // Geo-level volume (selected period) — works for both state and zone
  const geoList = currentGeo === 'zone' ? segZones : segStates;
  const getGeoIndVols = currentGeo === 'zone'
    ? (g,sub2) => getZoneIndustryVols(g,sub2)
    : (g,sub2) => getStateIndustryVols(g,sub2);
  const getGeoCoVols = currentGeo === 'zone'
    ? (g,co2,sub2) => getZoneCompanyVols(g,co2,sub2)
    : (g,co2,sub2) => getStateCompanyVols(g,co2,sub2);

  const geoVols = {};
  const pQs = periodQIdxs();
  for (const g of geoList) {
    const cv = getGeoCoVols(g,c,sub);
    const vol = pQs.reduce((s,qi)=>s+(cv[qi]||0),0);
    if (vol > 0) geoVols[g] = vol;
  }
  const sortedGeos = Object.entries(geoVols).sort((a,b)=>b[1]-a[1]);
  const topN = sortedGeos.slice(0,15);
  plotHBar('chart-co-states',
    topN.map(e=>e[0]).reverse(), topN.map(e=>e[1]).reverse(),
    topN.map(()=>getColor(c,0)).reverse()
  );

  // Share change by geo
  const yoyQs = yoyPeriodQIdxs();
  const shareChgByGeo = [];
  for (const [g] of sortedGeos) {
    const gIndQ = getGeoIndVols(g,sub);
    const gCoQ = getGeoCoVols(g,c,sub);
    const curG = pQs.reduce((s,qi)=>s+gCoQ[qi],0);
    const curGInd = pQs.reduce((s,qi)=>s+gIndQ[qi],0);
    const yoyG = yoyQs.reduce((s,qi)=>s+(gCoQ[qi]||0),0);
    const yoyGInd = yoyQs.reduce((s,qi)=>s+(gIndQ[qi]||0),0);
    const sCur = curGInd>0?curG/curGInd*100:0;
    const sYoy = yoyGInd>0?yoyG/yoyGInd*100:0;
    if (sCur>0||sYoy>0) shareChgByGeo.push({geo:g,chg:sCur-sYoy,curShare:sCur});
  }
  shareChgByGeo.sort((a,b)=>b.chg-a.chg);
  const displayChg = shareChgByGeo.slice(0,18);
  plotHBarDiverging('chart-co-share-chg',
    displayChg.map(e=>e.geo).reverse(),
    displayChg.map(e=>parseFloat(e.chg.toFixed(1))).reverse(),
    displayChg.map(e=>e.chg>=0?'#059669':'#dc2626').reverse()
  );

  // --- Contribution Time-Series Chart ---
  const top10Geos = sortedGeos.slice(0,10).map(e=>e[0]);
  const tsLen2 = tsLen();
  const contribTraces = [];
  const coTotalTS = tsVols(cvQ); // company total volumes time-series
  top10Geos.forEach((g,gi) => {
    const gCoQ = getGeoCoVols(g,c,sub);
    const gTS = tsVols(gCoQ);
    const contribTS = gTS.map((v,t) => coTotalTS[t]>0 ? v/coTotalTS[t]*100 : 0);
    contribTraces.push({
      x:tsDates(), y:contribTS, type:'scatter', mode:'lines+markers',
      name:g, line:{color:PALETTE[gi%PALETTE.length],width:2}, marker:{size:3},
      hovertemplate:g+': %{y:.1f}%<extra></extra>'
    });
  });
  // Others contribution line
  if (sortedGeos.length > 10) {
    const othersContrib = tsDates().map((_,t) => {
      const topSum = top10Geos.reduce((s,g) => {
        const gCoQ = getGeoCoVols(g,c,sub);
        return s + tsVols(gCoQ)[t];
      }, 0);
      return coTotalTS[t]>0 ? (coTotalTS[t]-topSum)/coTotalTS[t]*100 : 0;
    });
    contribTraces.push({
      x:tsDates(), y:othersContrib, type:'scatter', mode:'lines',
      name:'Others', line:{color:'#d1d5db',width:1.5,dash:'dot'},
      hovertemplate:'Others: %{y:.1f}%<extra></extra>'
    });
  }
  plotLines('chart-co-contrib', contribTraces, 'Contribution (%)', true);

  // --- Market Share Time-Series Table ---
  const tsLabels2 = tsDates();
  const shareTSHead = document.querySelector('#table-co-share-ts thead');
  const shareTSBody = document.querySelector('#table-co-share-ts tbody');
  let shareHdr = '<tr><th>' + geoLabel + '</th>';
  for (let t = 0; t < tsLen2; t++) shareHdr += '<th class="align-right">' + tsLabels2[t] + '</th>';
  shareHdr += '</tr>';
  shareTSHead.innerHTML = shareHdr;

  let shareRows = '';
  for (let gi = 0; gi < Math.min(sortedGeos.length, 10); gi++) {
    const g = sortedGeos[gi][0];
    const gCoQ = getGeoCoVols(g,c,sub);
    const gIndQ = getGeoIndVols(g,sub);
    const gCoTS = tsVols(gCoQ);
    const gIndTS = tsVols(gIndQ);
    shareRows += '<tr><td><b>' + g + '</b></td>';
    for (let t = 0; t < tsLen2; t++) {
      const sh = gIndTS[t]>0 ? gCoTS[t]/gIndTS[t]*100 : 0;
      const bg = sh > 20 ? 'rgba(5,150,105,0.15)' : sh > 10 ? 'rgba(5,150,105,0.07)' : '';
      shareRows += '<td class="align-right" style="background:' + bg + '">' + sh.toFixed(1) + '%</td>';
    }
    shareRows += '</tr>';
  }
  // Others row
  if (sortedGeos.length > 10) {
    const othersGeos = sortedGeos.slice(10).map(e=>e[0]);
    shareRows += '<tr><td><b>Others</b></td>';
    for (let t = 0; t < tsLen2; t++) {
      let oCo = 0, oInd = 0;
      for (const g of othersGeos) {
        oCo += tsVols(getGeoCoVols(g,c,sub))[t];
        oInd += tsVols(getGeoIndVols(g,sub))[t];
      }
      const sh = oInd>0 ? oCo/oInd*100 : 0;
      shareRows += '<td class="align-right">' + sh.toFixed(1) + '%</td>';
    }
    shareRows += '</tr>';
  }
  shareTSBody.innerHTML = shareRows;

  // Geo details table
  const totalCoVol = curVol;
  const geoDetails = sortedGeos.map(([g,vol]) => {
    const gIndQ = getGeoIndVols(g,sub);
    const gCoQ = getGeoCoVols(g,c,sub);
    const sVol = pQs.reduce((s,qi)=>s+(gCoQ[qi]||0),0);
    const sYoyVol = yoyQs.reduce((s,qi)=>s+(gCoQ[qi]||0),0);
    const sGrowth = sYoyVol>0?((sVol/sYoyVol-1)*100):0;
    const sIndCur = pQs.reduce((s,qi)=>s+(gIndQ[qi]||0),0);
    const sIndYoy = yoyQs.reduce((s,qi)=>s+(gIndQ[qi]||0),0);
    const sShare = sIndCur>0?sVol/sIndCur*100:0;
    const sShareYoy = sIndYoy>0?sYoyVol/sIndYoy*100:0;
    let zone = '';
    if (currentGeo === 'state') {
      const r = filterRows(c,g,sub);
      zone = r.length>0 ? ROWS[r[0]][2] : '';
    }
    return {geo:g,zone,vol:sVol,yoyVol:sYoyVol,growth:sGrowth,share:sShare,shareChg:sShare-sShareYoy,contrib:totalCoVol>0?sVol/totalCoVol*100:0};
  }).filter(d=>d.vol>0);

  // Totals
  const totVol2=geoDetails.reduce((s,d)=>s+d.vol,0);
  const totYoy2=geoDetails.reduce((s,d)=>s+d.yoyVol,0);
  const totGrowth2=totYoy2>0?((totVol2/totYoy2-1)*100):0;

  const thead = document.querySelector('#table-co-states thead');
  const zoneCol = currentGeo === 'state' ? '<th>Zone</th>' : '';
  thead.innerHTML = '<tr><th>#</th><th>' + geoLabel + '</th>' + zoneCol + '<th class="align-right">Volume</th><th class="align-right">YoY Vol</th><th class="align-right">YoY Growth</th><th class="align-right">Mkt Share</th><th class="align-right">Share Chg</th><th class="align-right">Contribution</th></tr>';
  const tbody2 = document.querySelector('#table-co-states tbody');
  tbody2.innerHTML = geoDetails.map((d,i) => {
    const zoneTd = currentGeo === 'state' ? '<td>' + d.zone + '</td>' : '';
    const onclick = currentGeo === 'state' ? `onclick="drillToState('${esc(d.geo)}','${esc(d.zone)}')"` : '';
    return `<tr class="${currentGeo==='state'?'clickable':''}" ${onclick}>
      <td>${i+1}</td><td><b>${d.geo}</b></td>${zoneTd}
      <td class="align-right">${fmt(d.vol)}</td><td class="align-right">${fmt(d.yoyVol)}</td>
      <td class="align-right ${d.growth>=0?'positive':'negative'}">${d.growth>=0?'+':''}${d.growth.toFixed(1)}%</td>
      <td class="align-right">${d.share.toFixed(1)}%</td>
      <td class="align-right"><span class="badge ${d.shareChg>=0?'badge-green':'badge-red'}">${fmtPP(d.shareChg)}</span></td>
      <td class="align-right">${d.contrib.toFixed(1)}%</td>
    </tr>`;
  }).join('') + `
    <tr class="total-row"><td></td><td><b>TOTAL</b></td>${currentGeo==='state'?'<td></td>':''}
      <td class="align-right"><b>${fmt(totVol2)}</b></td><td class="align-right"><b>${fmt(totYoy2)}</b></td>
      <td class="align-right ${totGrowth2>=0?'positive':'negative'}"><b>${totGrowth2>=0?'+':''}${totGrowth2.toFixed(1)}%</b></td>
      <td class="align-right"><b>${shareCur.toFixed(1)}%</b></td><td class="align-right"><span class="badge ${shareChg>=0?'badge-green':'badge-red'}">${fmtPP(shareChg)}</span></td>
      <td class="align-right"><b>100.0%</b></td>
    </tr>`;
}

// ============================================
// STATE DEEP-DIVE
// ============================================
function renderStateView() {
  const st = currentState, sub = currentSubseg;
  if (!st) return;

  const stIndQ = getStateIndustryVols(st,sub);
  const curVol = periodVol(stIndQ);
  const yoyV = yoyPeriodVol(stIndQ);
  const growth = yoyV>0?((curVol/yoyV-1)*100):0;
  const natVol = periodVol(getIndustryVols(sub));

  const top = topCompanies(8,sub,st);
  const topShares = top.map(c => {
    const cv = getStateCompanyVols(st,c,sub);
    const v = periodVol(cv);
    return {company:c, share:curVol>0?v/curVol*100:0};
  });

  const vm = getViewMode();
  document.getElementById('title-st-vol').textContent = 'Industry Volume Trend (' + (vm==='annual'?'Annual':'Quarterly') + ')';
  document.getElementById('title-st-pie').textContent = 'Market Share Breakdown (' + periodLabel() + ')';

  document.getElementById('kpi-state').innerHTML = `
    <div class="kpi"><div class="kpi-label">State Volume (${periodLabel()})</div><div class="kpi-value">${fmt(curVol)}</div><div class="kpi-sub ${growth>=0?'positive':'negative'}">YoY: ${growth>=0?'+':''}${growth.toFixed(1)}%</div></div>
    <div class="kpi"><div class="kpi-label">% of National Volume</div><div class="kpi-value">${(natVol>0?(curVol/natVol*100):0).toFixed(1)}%</div></div>
    <div class="kpi"><div class="kpi-label">#1 Company</div><div class="kpi-value" style="font-size:18px">${topShares[0]?.company||'-'}</div><div class="kpi-sub neutral">${topShares[0]?.share.toFixed(1)||0}% share</div></div>
    <div class="kpi"><div class="kpi-label">#2 Company</div><div class="kpi-value" style="font-size:18px">${topShares[1]?.company||'-'}</div><div class="kpi-sub neutral">${topShares[1]?.share.toFixed(1)||0}% share</div></div>
  `;

  // Volume trend
  const tsV = tsVols(stIndQ);
  plotLines('chart-st-vol',[{
    x:tsDates(),y:tsV,type:'scatter',mode:'lines+markers',name:'Volume',
    line:{color:'#2563eb',width:2.5},marker:{size:4},
    fill:'tozeroy',fillcolor:'rgba(37,99,235,0.08)',
    hovertemplate:'%{x}: %{y:,.0f}<extra></extra>'
  }],'Volume (units)',false);

  // Market share donut (selected period)
  const pQs = periodQIdxs();
  const allComps = topCompanies(20,sub,st);
  const pieLabels=[],pieValues=[],pieColors=[];
  let othersVol=0;
  allComps.forEach((c,ci) => {
    const cv = getStateCompanyVols(st,c,sub);
    const v = pQs.reduce((s,qi)=>s+(cv[qi]||0),0);
    if (ci<8 && v>0){pieLabels.push(c);pieValues.push(v);pieColors.push(getColor(c,ci));}
    else othersVol+=v;
  });
  if (othersVol>0){pieLabels.push('Others');pieValues.push(othersVol);pieColors.push('#d1d5db');}
  plotDonut('chart-st-pie',pieLabels,pieValues,pieColors);

  // Market share trend
  const top10 = topCompanies(10,sub,st);
  const shareTraces = top10.map((c,ci) => {
    const cv = getStateCompanyVols(st,c,sub);
    const share = computeShare(tsVols(cv), tsV);
    return {x:tsDates(),y:share,type:'scatter',mode:'lines',name:c,line:{color:getColor(c,ci),width:2},
      hovertemplate:c+': %{y:.1f}%<extra></extra>'};
  });
  plotLines('chart-st-share',shareTraces,'Market Share (%)',true);

  // YoY growth trend
  const stYoY = yoyGrowthSeries(stIndQ);
  const natYoY = yoyGrowthSeries(getIndustryVols(sub));
  const top3 = topCompanies(3,sub,st);
  const yoyTraces = [
    {x:tsDates(),y:stYoY,type:'scatter',mode:'lines+markers',name:st+' Industry',line:{color:'#2563eb',width:2.5},marker:{size:4},connectgaps:false,hovertemplate:st+': %{y:.1f}%<extra></extra>'},
    {x:tsDates(),y:natYoY,type:'scatter',mode:'lines',name:'National Industry',line:{color:'#94a3b8',width:1.5,dash:'dot'},connectgaps:false,hovertemplate:'National: %{y:.1f}%<extra></extra>'}
  ];
  top3.forEach((c,ci) => {
    const yoy = yoyGrowthSeries(getStateCompanyVols(st,c,sub));
    yoyTraces.push({x:tsDates(),y:yoy,type:'scatter',mode:'lines',name:c,line:{color:getColor(c,ci+2),width:1.5},connectgaps:false,hovertemplate:c+': %{y:.1f}%<extra></extra>'});
  });
  plotYoYGrowth('chart-st-yoy',yoyTraces);

  // Company table
  const yoyQs = yoyPeriodQIdxs();
  const comps = topCompanies(50,sub,st);
  const tableData = comps.map(c => {
    const cv = getStateCompanyVols(st,c,sub);
    const v = pQs.reduce((s,qi)=>s+(cv[qi]||0),0);
    const yv = yoyQs.reduce((s,qi)=>s+(cv[qi]||0),0);
    const g = yv>0?((v/yv-1)*100):0;
    const s = curVol>0?v/curVol*100:0;
    const stIndYoy = yoyQs.reduce((sum,qi)=>sum+(stIndQ[qi]||0),0);
    const sy = stIndYoy>0?yv/stIndYoy*100:0;
    return {company:c,vol:v,yoyVol:yv,growth:g,share:s,shareChg:s-sy};
  }).filter(d=>d.vol>0);
  tableData.sort((a,b)=>b.vol-a.vol);

  const totVol=tableData.reduce((s,d)=>s+d.vol,0);
  const totYoy=tableData.reduce((s,d)=>s+d.yoyVol,0);
  const totG=totYoy>0?((totVol/totYoy-1)*100):0;

  const thead = document.querySelector('#table-st-companies thead');
  thead.innerHTML = '<tr><th>#</th><th>Company</th><th class="align-right">Volume</th><th class="align-right">YoY Vol</th><th class="align-right">YoY Growth</th><th class="align-right">Mkt Share</th><th class="align-right">Share Chg</th></tr>';
  const tbody = document.querySelector('#table-st-companies tbody');
  tbody.innerHTML = tableData.map((d,i) => `
    <tr class="clickable" onclick="drillToCompany('${esc(d.company)}')">
      <td>${i+1}</td><td><b>${d.company}</b></td>
      <td class="align-right">${fmt(d.vol)}</td><td class="align-right">${fmt(d.yoyVol)}</td>
      <td class="align-right ${d.growth>=0?'positive':'negative'}">${d.growth>=0?'+':''}${d.growth.toFixed(1)}%</td>
      <td class="align-right">${d.share.toFixed(1)}%</td>
      <td class="align-right"><span class="badge ${d.shareChg>=0?'badge-green':'badge-red'}">${fmtPP(d.shareChg)}</span></td>
    </tr>`).join('') + `
    <tr class="total-row"><td></td><td><b>TOTAL</b></td>
      <td class="align-right"><b>${fmt(totVol)}</b></td><td class="align-right"><b>${fmt(totYoy)}</b></td>
      <td class="align-right ${totG>=0?'positive':'negative'}"><b>${totG>=0?'+':''}${totG.toFixed(1)}%</b></td>
      <td class="align-right"><b>100.0%</b></td><td class="align-right"></td>
    </tr>`;
}

// ============================================
// UI HELPERS
// ============================================
function esc(s) { return s.replace(/'/g,"\\\\'"); }

function switchSegment(seg) {
  currentSegment = seg;
  currentSubseg = 'All';
  document.querySelectorAll('.seg-tab').forEach(t => t.classList.toggle('active',t.dataset.seg===seg));
  buildIndexes();
  updateDropdowns();
  renderSubsegChips();
  populatePeriodSelector(currentTab);
  renderCurrentTab();
}

function switchTab(tab) {
  currentTab = tab;
  currentSubseg = 'All';
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active',t.dataset.tab===tab));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-'+tab).classList.add('active');
  renderSubsegChips();
  syncViewChips();
  populatePeriodSelector(tab);
  renderCurrentTab();
}

function renderSubsegChips() {
  const el = document.getElementById('subsegChips-'+currentTab);
  if (!el) return;
  el.innerHTML = '<div class="subseg-chip active" data-sub="All">All</div>' +
    segSubsegs.map(s=>`<div class="subseg-chip" data-sub="${s}">${s}</div>`).join('');
  el.querySelectorAll('.subseg-chip').forEach(chip => {
    chip.onclick = () => {
      currentSubseg = chip.dataset.sub;
      el.querySelectorAll('.subseg-chip').forEach(c=>c.classList.toggle('active',c.dataset.sub===currentSubseg));
      renderCurrentTab();
    };
  });
}

function syncViewChips() {
  const el = document.getElementById('viewChips-'+currentTab);
  if (!el) return;
  el.querySelectorAll('.view-chip').forEach(c => c.classList.toggle('active',c.dataset.view===viewModes[currentTab]));
}

function updateDropdowns() {
  const selCo = document.getElementById('sel-company');
  const topC = topCompanies(50,'All',null);
  selCo.innerHTML = topC.map(c=>`<option value="${c}" ${c===currentCompany?'selected':''}>${c}</option>`).join('');
  if (!currentCompany||!topC.includes(currentCompany)) currentCompany=topC[0]||'';
  selCo.value = currentCompany;
  const selZone = document.getElementById('sel-zone');
  selZone.innerHTML = '<option value="All">All Zones</option>'+segZones.map(z=>`<option value="${z}">${z}</option>`).join('');
  selZone.value = currentZone;
  updateStateDropdown();
}

function updateStateDropdown() {
  const selState = document.getElementById('sel-state');
  const states = currentZone==='All'?segStates:(zoneStateMap[currentZone]||[]);
  selState.innerHTML = states.map(s=>`<option value="${s}" ${s===currentState?'selected':''}>${s}</option>`).join('');
  if (!currentState||!states.includes(currentState)) currentState=states[0]||'';
  selState.value = currentState;
}

function renderCurrentTab() {
  if (currentTab==='overview') renderOverview();
  else if (currentTab==='company') renderCompanyView();
  else if (currentTab==='state') renderStateView();
  else if (currentTab==='data') renderDataTab();
}

function drillToCompany(company) {
  currentCompany = company;
  document.getElementById('sel-company').value = company;
  switchTab('company');
}
function drillToState(state, zone) {
  if (zone && zone!=='All'){currentZone=zone;document.getElementById('sel-zone').value=zone;updateStateDropdown();}
  currentState = state;
  document.getElementById('sel-state').value = state;
  switchTab('state');
}

// ============================================
// DATA MANAGEMENT
// ============================================
function renderDataTab() {
  const infoGrid = document.getElementById('data-info-grid');
  const resetBtn = document.getElementById('btn-reset-data');
  const statusEl = document.getElementById('data-status');
  const segments = [...new Set(ROWS.map(r => r[0]))];
  const companies = [...new Set(ROWS.map(r => r[4]))];
  const states = [...new Set(ROWS.map(r => r[3]))];
  const meta = JSON.parse(localStorage.getItem("janchor_auto_meta") || "null");
  infoGrid.innerHTML =
    '<div class="data-info-item"><div class="di-label">Quarters</div><div class="di-value">'+NQ+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">Period Range</div><div class="di-value">'+QLABELS[0]+' \u2013 '+QLABELS[NQ-1]+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">Segments</div><div class="di-value">'+segments.length+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">Companies</div><div class="di-value">'+companies.length+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">States</div><div class="di-value">'+states.length+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">Total Rows</div><div class="di-value">'+ROWS.length.toLocaleString()+'</div></div>'+
    '<div class="data-info-item"><div class="di-label">Data Source</div><div class="di-value">'+(DATA_IS_CUSTOM ? 'Uploaded File' : 'Embedded (Default)')+'</div></div>'+
    (meta ? '<div class="data-info-item"><div class="di-label">Uploaded</div><div class="di-value">'+new Date(meta.uploadedAt).toLocaleDateString()+'</div></div>' : '')+
    (meta && meta.fileName ? '<div class="data-info-item"><div class="di-label">File Name</div><div class="di-value">'+meta.fileName+'</div></div>' : '');
  resetBtn.style.display = DATA_IS_CUSTOM ? 'inline-flex' : 'none';
  if (DATA_IS_CUSTOM) {
    showStatus('info', 'Using uploaded data. Click "Reset to Embedded Data" to revert to the original dataset.');
  } else {
    statusEl.className = 'status-msg';
  }
}

function showStatus(type, msg) {
  var el = document.getElementById('data-status');
  el.className = 'status-msg show ' + type;
  el.textContent = msg;
}

function parseExcel(arrayBuffer, fileName) {
  try {
    showStatus('info', 'Parsing Excel file...');
    var wb = XLSX.read(arrayBuffer, {type: 'array'});
    var SHEET_MAP = {
      'PVs - Raw data': 'PV',
      '2Ws - Raw data': '2W',
      '3Ws - Raw data': '3W',
      'M&HCVs - Raw data': 'MHCV',
      'LCVs - Raw data': 'LCV'
    };
    var allQuarters = null;
    var allRows = [];
    var sheetsFound = 0;
    var sheetNames = Object.keys(SHEET_MAP);
    for (var si = 0; si < sheetNames.length; si++) {
      var sheetName = sheetNames[si];
      var segment = SHEET_MAP[sheetName];
      if (wb.SheetNames.indexOf(sheetName) < 0) {
        showStatus('error', 'Missing sheet: "' + sheetName + '". Please check your Excel file has all 5 raw data sheets.');
        return null;
      }
      sheetsFound++;
      var ws = wb.Sheets[sheetName];
      var jsonData = XLSX.utils.sheet_to_json(ws, {header:1, defval:0});
      if (jsonData.length < 3) {
        showStatus('error', 'Sheet "' + sheetName + '" has insufficient data.');
        return null;
      }
      var headerRowIdx = -1;
      for (var r = 0; r < Math.min(5, jsonData.length); r++) {
        var row = jsonData[r];
        for (var c = 0; c < row.length; c++) {
          var val = String(row[c] || '');
          if (/^Q\\dFY\\d{2}$/.test(val)) { headerRowIdx = r; break; }
        }
        if (headerRowIdx >= 0) break;
      }
      if (headerRowIdx < 0) {
        showStatus('error', 'Cannot find quarter headers (like Q1FY17) in sheet "' + sheetName + '".');
        return null;
      }
      var headers = jsonData[headerRowIdx];
      var colZone=-1, colState=-1, colMfr=-1, colSubseg=-1;
      var qStartCol = -1;
      var quarters = [];
      for (var c2 = 0; c2 < headers.length; c2++) {
        var h = String(headers[c2] || '').trim();
        var hLow = h.toLowerCase();
        if (hLow === 'zone') colZone = c2;
        else if (hLow === 'state') colState = c2;
        else if (hLow === 'manufacturer' || hLow === 'oem') colMfr = c2;
        else if (hLow === 'sub-segment' || hLow === 'subsegment' || hLow === 'sub_segment' || hLow === 'sub segment') colSubseg = c2;
        else if (/^Q\\dFY\\d{2}$/.test(h)) {
          if (qStartCol < 0) qStartCol = c2;
          quarters.push(h);
        }
      }
      if (colZone < 0 || colState < 0 || colMfr < 0 || qStartCol < 0) {
        showStatus('error', 'Cannot find required columns (Zone, State, Manufacturer, Quarters) in sheet "' + sheetName + '".');
        return null;
      }
      if (allQuarters === null) {
        allQuarters = quarters;
      } else if (quarters.length > allQuarters.length) {
        allQuarters = quarters;
      }
      for (var r2 = headerRowIdx + 1; r2 < jsonData.length; r2++) {
        var drow = jsonData[r2];
        var zone = String(drow[colZone] || '').trim();
        var state = String(drow[colState] || '').trim();
        var mfr = String(drow[colMfr] || '').trim();
        var subseg = colSubseg >= 0 ? String(drow[colSubseg] || '').trim() : 'All';
        if (!zone || !state || !mfr) continue;
        if (zone.toLowerCase() === 'zone' || state.toLowerCase() === 'state') continue;
        var volumes = [];
        var hasNonZero = false;
        for (var q = 0; q < quarters.length; q++) {
          var v = drow[qStartCol + q];
          var num = typeof v === 'number' ? v : (parseFloat(v) || 0);
          volumes.push(num);
          if (num > 0) hasNonZero = true;
        }
        if (hasNonZero) {
          allRows.push([segment, subseg, zone, state, mfr].concat(volumes));
        }
      }
    }
    if (allRows.length === 0) {
      showStatus('error', 'No valid data rows found in the Excel file.');
      return null;
    }
    var result = {
      quarters: allQuarters,
      columns: ['segment','subsegment','zone','state','manufacturer'].concat(allQuarters.map(function(q){return 'vol_'+q.toLowerCase();})),
      rows: allRows
    };
    showStatus('success', 'Parsed ' + allRows.length.toLocaleString() + ' rows across ' + sheetsFound + ' segments, ' + allQuarters.length + ' quarters (' + allQuarters[0] + ' to ' + allQuarters[allQuarters.length-1] + '). Saving...');
    return result;
  } catch(e) {
    showStatus('error', 'Error parsing Excel: ' + e.message);
    return null;
  }
}

function handleFileUpload(file) {
  if (!file) return;
  var ext = file.name.split('.').pop().toLowerCase();
  if (ext !== 'xlsx' && ext !== 'xls') {
    showStatus('error', 'Please upload an Excel file (.xlsx or .xls)');
    return;
  }
  showStatus('info', 'Reading file: ' + file.name + '...');
  var reader = new FileReader();
  reader.onload = function(e) {
    var data = parseExcel(e.target.result, file.name);
    if (data) {
      try {
        var jsonStr = JSON.stringify(data);
        localStorage.setItem("janchor_auto_data", jsonStr);
        localStorage.setItem("janchor_auto_meta", JSON.stringify({
          fileName: file.name,
          uploadedAt: new Date().toISOString(),
          rows: data.rows.length,
          quarters: data.quarters.length
        }));
        showStatus('success', 'Data saved! Reloading dashboard with new data...');
        setTimeout(function(){ location.reload(); }, 1500);
      } catch(err) {
        if (err.name === 'QuotaExceededError') {
          showStatus('error', 'Data too large for browser storage. The file exceeds the 5MB browser storage limit.');
        } else {
          showStatus('error', 'Error saving data: ' + err.message);
        }
      }
    }
  };
  reader.onerror = function() {
    showStatus('error', 'Error reading file. Please try again.');
  };
  reader.readAsArrayBuffer(file);
}

function resetData() {
  localStorage.removeItem("janchor_auto_data");
  localStorage.removeItem("janchor_auto_meta");
  showStatus('success', 'Data reset! Reloading with embedded data...');
  setTimeout(function(){ location.reload(); }, 1000);
}

// ============================================
// TABLE SORTING
// ============================================
document.addEventListener('click', function(e) {
  if (e.target.tagName==='TH') {
    const table=e.target.closest('table'), tbody=table.querySelector('tbody');
    const idx=Array.from(e.target.parentNode.children).indexOf(e.target);
    const rows=Array.from(tbody.querySelectorAll('tr:not(.total-row)'));
    const isAsc=e.target.dataset.sort==='asc';
    rows.sort((a,b) => {
      let va=a.children[idx]?.textContent.trim()||'';
      let vb=b.children[idx]?.textContent.trim()||'';
      const na=parseFloat(va.replace(/[^\\d.\\-]/g,''));
      const nb=parseFloat(vb.replace(/[^\\d.\\-]/g,''));
      if (!isNaN(na)&&!isNaN(nb)) return isAsc?na-nb:nb-na;
      return isAsc?va.localeCompare(vb):vb.localeCompare(va);
    });
    e.target.dataset.sort = isAsc?'desc':'asc';
    const totalRow = tbody.querySelector('.total-row');
    rows.forEach(r=>tbody.appendChild(r));
    if (totalRow) tbody.appendChild(totalRow);
  }
});

// ============================================
// EVENT LISTENERS
// ============================================
document.querySelectorAll('.seg-tab').forEach(t=>t.onclick=()=>switchSegment(t.dataset.seg));
document.querySelectorAll('.nav-tab').forEach(t=>t.onclick=()=>switchTab(t.dataset.tab));
document.getElementById('sel-company').onchange=function(){currentCompany=this.value;renderCurrentTab();};
document.getElementById('sel-zone').onchange=function(){currentZone=this.value;updateStateDropdown();renderCurrentTab();};
document.getElementById('sel-state').onchange=function(){currentState=this.value;renderCurrentTab();};

// View mode toggles
document.querySelectorAll('[id^="viewChips-"]').forEach(container => {
  container.querySelectorAll('.view-chip').forEach(chip => {
    chip.onclick = () => {
      const tab = container.id.replace('viewChips-','');
      viewModes[tab] = chip.dataset.view;
      // Reset period to latest
      selectedPeriods[tab] = chip.dataset.view==='annual' ? NFY-1 : NQ-1;
      container.querySelectorAll('.view-chip').forEach(c=>c.classList.toggle('active',c.dataset.view===chip.dataset.view));
      populatePeriodSelector(tab);
      if (tab===currentTab) renderCurrentTab();
    };
  });
});

// Period selectors
['overview','company','state'].forEach(tab => {
  const sel = document.getElementById('sel-period-'+tab);
  if (sel) sel.onchange = function() {
    selectedPeriods[tab] = parseInt(this.value);
    if (tab===currentTab) renderCurrentTab();
  };
});

// Data management event listeners
(function() {
  var uploadZone = document.getElementById('upload-zone');
  var fileInput = document.getElementById('file-input');
  var resetBtn = document.getElementById('btn-reset-data');
  if (uploadZone && fileInput) {
    uploadZone.onclick = function() { fileInput.click(); };
    fileInput.onchange = function() { if (this.files[0]) handleFileUpload(this.files[0]); };
    uploadZone.ondragover = function(e) { e.preventDefault(); e.stopPropagation(); this.classList.add('dragover'); };
    uploadZone.ondragleave = function(e) { e.preventDefault(); e.stopPropagation(); this.classList.remove('dragover'); };
    uploadZone.ondrop = function(e) {
      e.preventDefault(); e.stopPropagation(); this.classList.remove('dragover');
      if (e.dataTransfer.files[0]) handleFileUpload(e.dataTransfer.files[0]);
    };
  }
  if (resetBtn) {
    resetBtn.onclick = function() {
      if (confirm('Reset to the original embedded data? Your uploaded data will be removed.')) resetData();
    };
  }
})();

// Geo toggle (State / Zone) for Company Deep-Dive
document.getElementById('geoChips-company').querySelectorAll('.view-chip').forEach(chip => {
  chip.onclick = () => {
    currentGeo = chip.dataset.geo;
    document.getElementById('geoChips-company').querySelectorAll('.view-chip').forEach(c => c.classList.toggle('active', c.dataset.geo === currentGeo));
    if (currentTab === 'company') renderCurrentTab();
  };
});

// ============================================
// INITIALIZE
// ============================================
buildIndexes();
updateDropdowns();
['overview','company','state'].forEach(tab => populatePeriodSelector(tab));
renderSubsegChips();
syncViewChips();
renderCurrentTab();
</script>
</body>
</html>'''

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard generated: {OUTPUT_FILE}")
print(f"File size: {os.path.getsize(OUTPUT_FILE)/1024:.0f} KB")
