import json

with open('/home/claude/graph_temporal.json') as f:
    graph_data = f.read()

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<title>IETF Power Map</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
/* ═══════════════════════════════════════════════════════
   PRE-iOS 7 SKEUOMORPHIC + TEMPORAL LAYERS
   iPhone HIG 2008-2012: embossed surfaces, 44pt targets,
   visual depth, linen textures, steel nav bars
   ═══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;500;700&display=swap');

:root {
  --nav-h: 44px;
  --tab-h: 49px;
  --touch: 44px;
  --linen: #e5e0d8;
  --cell-bg: #fff;
  --cell-border: #c8c7cc;
  --txt1: #1a1a1a;
  --txt2: #6d6d72;
  --blue: #007aff;
  --iab: #c0392b;
  --iesg: #2980b9;
  --area: #8e44ad;
  --irtf: #27ae60;
  --wg: #7f8c8d;
  --coauth: #e67e22;
}

* { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }

html, body {
  width:100%; height:100%;
  overflow:hidden;
  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
  font-size:16px;
  color:var(--txt1);
  background:var(--linen);
  -webkit-font-smoothing:antialiased;
}

body::before {
  content:'';
  position:fixed; inset:0; z-index:-1;
  background:
    repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.02) 2px,rgba(0,0,0,.02) 4px),
    repeating-linear-gradient(90deg,transparent,transparent 2px,rgba(0,0,0,.015) 2px,rgba(0,0,0,.015) 4px),
    linear-gradient(180deg,#e8e3db,#d5d0c8);
}

/* ─── Nav Bar ─── */
.nav-bar {
  position:fixed; top:0; left:0; right:0;
  height:var(--nav-h); z-index:100;
  background:linear-gradient(180deg,#b8c5d6 0%,#8e9faf 2%,#7d8fa1 50%,#6a7d90 51%,#5d7085 100%);
  border-bottom:1px solid rgba(0,0,0,.4);
  box-shadow:0 1px 0 rgba(255,255,255,.15) inset,0 1px 3px rgba(0,0,0,.45);
  display:flex; align-items:center; justify-content:center;
}
.nav-bar h1 { font-size:20px; font-weight:700; color:#fff; text-shadow:0 -1px 1px rgba(0,0,0,.5); letter-spacing:-.3px; }
.nav-bar .sub { position:absolute; right:10px; top:50%; transform:translateY(-50%); font-size:11px; color:rgba(255,255,255,.7); text-shadow:0 -1px 1px rgba(0,0,0,.3); }

/* ─── Tab Bar ─── */
.tab-bar {
  position:fixed; bottom:0; left:0; right:0;
  height:var(--tab-h); z-index:100;
  background:linear-gradient(180deg,#434343 0%,#2a2a2a 2%,#1a1a1a 50%,#111 51%,#0a0a0a 100%);
  border-top:1px solid rgba(255,255,255,.08);
  box-shadow:0 -1px 4px rgba(0,0,0,.6);
  display:flex;
}
.tab-item {
  flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center;
  min-height:var(--touch); cursor:pointer; border:none; background:none;
  color:#8e8e93; font-size:10px; font-weight:500;
  -webkit-user-select:none; user-select:none;
}
.tab-item.active { color:#fff; }
.tab-item svg { width:24px; height:24px; margin-bottom:2px; fill:currentColor; }
.tab-item.active svg { filter:drop-shadow(0 0 4px rgba(100,160,255,.4)); }

/* ─── Content ─── */
.content { position:fixed; top:var(--nav-h); bottom:var(--tab-h); left:0; right:0; overflow:hidden; }
.panel { display:none; width:100%; height:100%; overflow-y:auto; overflow-x:hidden; }
.panel.active { display:block; }

/* ─── Graph ─── */
#graph-panel { overflow:hidden; background:#1a1c2e; }
#graph-panel svg { width:100%; height:100%; }

.graph-controls {
  position:absolute; top:8px; left:8px; right:8px;
  display:flex; gap:6px; flex-wrap:wrap; z-index:50;
}

/* iOS segmented control */
.seg-control {
  display:inline-flex;
  background:rgba(0,0,0,.5);
  border-radius:7px;
  border:1px solid rgba(255,255,255,.12);
  overflow:hidden;
  backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
}
.seg-btn {
  padding:6px 12px;
  font-size:12px; font-weight:600;
  color:rgba(255,255,255,.65);
  border:none; background:none; cursor:pointer;
  border-right:1px solid rgba(255,255,255,.1);
  min-height:32px;
}
.seg-btn:last-child { border-right:none; }
.seg-btn.active {
  background:rgba(255,255,255,.18);
  color:#fff;
  text-shadow:0 0 6px rgba(100,160,255,.5);
}

.graph-legend {
  position:absolute; bottom:12px; left:12px;
  background:rgba(0,0,0,.7);
  border:1px solid rgba(255,255,255,.15);
  border-radius:8px;
  padding:10px 12px;
  backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
}
.legend-row { display:flex; align-items:center; margin:3px 0; font-size:11px; color:rgba(255,255,255,.85); }
.legend-dot { width:10px; height:10px; border-radius:50%; margin-right:7px; }
.legend-line { width:14px; height:0; margin-right:7px; }

/* ─── Timeline Scrubber ─── */
.timeline-wrap {
  position:absolute; bottom:60px; left:12px; right:12px;
  background:rgba(0,0,0,.65);
  border:1px solid rgba(255,255,255,.12);
  border-radius:10px;
  padding:8px 12px 12px;
  backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);
  display:none;
  z-index:50;
}
.timeline-wrap.visible { display:block; }
.timeline-label { font-size:11px; color:rgba(255,255,255,.6); margin-bottom:4px; font-weight:600; text-transform:uppercase; letter-spacing:.5px; }
.timeline-value { font-size:22px; font-weight:300; color:#fff; text-align:center; margin:2px 0 6px; }

/* iOS-style slider track */
.timeline-slider {
  -webkit-appearance:none; appearance:none;
  width:100%; height:6px;
  border-radius:3px;
  background:linear-gradient(90deg,#2c3e50,#3498db,#2ecc71,#e67e22,#e74c3c);
  outline:none;
  opacity:0.9;
}
.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance:none; appearance:none;
  width:28px; height:28px;
  border-radius:50%;
  background:linear-gradient(180deg,#fff 0%,#e0e0e0 100%);
  box-shadow:0 2px 6px rgba(0,0,0,.4),0 0 0 1px rgba(0,0,0,.1);
  cursor:pointer;
}

.timeline-bar-chart {
  display:flex; align-items:flex-end; gap:2px; height:30px; margin:4px 0;
}
.timeline-bar {
  flex:1; background:rgba(100,160,255,.4);
  border-radius:2px 2px 0 0;
  min-height:2px;
  transition:background .2s;
}
.timeline-bar.active { background:rgba(100,160,255,.9); }

.graph-tooltip {
  position:absolute; pointer-events:none;
  background:rgba(0,0,0,.85); color:#fff;
  padding:6px 10px; border-radius:6px;
  font-size:13px; font-weight:500;
  white-space:nowrap; display:none; z-index:50;
  box-shadow:0 2px 8px rgba(0,0,0,.4);
}

/* ─── List Panel ─── */
#list-panel { -webkit-overflow-scrolling:touch; padding:10px 0; }

.search-bar-wrap { padding:8px 10px; position:sticky; top:0; z-index:10; background:var(--linen); }
.search-bar {
  width:100%; height:36px; border-radius:8px;
  border:1px solid #b0b0b5;
  background:#fff;
  padding:0 12px 0 32px; font-size:15px; color:var(--txt1);
  box-shadow:0 1px 2px rgba(0,0,0,.1) inset,0 1px 0 rgba(255,255,255,.6);
  outline:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%238e8e93'%3E%3Ccircle cx='7' cy='7' r='5.5' stroke='%238e8e93' stroke-width='1.5' fill='none'/%3E%3Cline x1='11' y1='11' x2='14' y2='14' stroke='%238e8e93' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat:no-repeat; background-position:10px center;
}

/* Sort segmented control for list */
.list-controls { padding:6px 10px; display:flex; gap:6px; }
.sort-seg {
  display:inline-flex;
  background:#d1d1d6;
  border-radius:7px;
  overflow:hidden;
  border:1px solid #b0b0b5;
}
.sort-btn {
  padding:5px 10px; font-size:12px; font-weight:600;
  color:var(--txt2); border:none; background:none; cursor:pointer;
  border-right:1px solid #b0b0b5;
}
.sort-btn:last-child { border-right:none; }
.sort-btn.active { background:#fff; color:var(--txt1); box-shadow:0 1px 2px rgba(0,0,0,.1); }

.group-header {
  padding:6px 16px 4px; font-size:13px; font-weight:700;
  color:var(--txt2); text-transform:uppercase; letter-spacing:.5px;
  text-shadow:0 1px 0 rgba(255,255,255,.8);
}
.table-group {
  margin:0 10px 12px; background:var(--cell-bg);
  border-radius:10px;
  box-shadow:0 1px 3px rgba(0,0,0,.12),0 0 0 1px rgba(0,0,0,.04);
  overflow:hidden;
}
.cell {
  display:flex; align-items:center;
  min-height:var(--touch); padding:8px 16px 8px 12px;
  border-bottom:1px solid var(--cell-border);
  cursor:pointer; transition:background .1s;
}
.cell:last-child { border-bottom:none; }
.cell:active { background:#d0d0d5; }

.cell-rank { width:28px; font-size:17px; font-weight:700; color:var(--txt2); text-align:center; flex-shrink:0; }
.cell-body { flex:1; min-width:0; margin-left:10px; }
.cell-name { font-size:17px; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cell-detail { font-size:12px; color:var(--txt2); margin-top:1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cell-badges { flex-shrink:0; margin-left:8px; display:flex; gap:4px; align-items:center; }

.weight-badge {
  display:inline-flex; align-items:center; justify-content:center;
  min-width:28px; height:24px; border-radius:12px;
  font-size:13px; font-weight:700; color:#fff; padding:0 8px;
  background:linear-gradient(180deg,#5ac8fa,#007aff);
  box-shadow:0 1px 2px rgba(0,0,0,.2),0 1px 0 rgba(255,255,255,.3) inset;
}
.rfc-badge {
  display:inline-flex; align-items:center; justify-content:center;
  min-width:28px; height:24px; border-radius:12px;
  font-size:13px; font-weight:700; color:#fff; padding:0 8px;
  background:linear-gradient(180deg,#f39c12,#e67e22);
  box-shadow:0 1px 2px rgba(0,0,0,.2),0 1px 0 rgba(255,255,255,.3) inset;
}

.org-pills { display:flex; gap:3px; margin-top:3px; flex-wrap:wrap; }
.org-pill {
  font-size:9px; font-weight:700; padding:1px 5px;
  border-radius:3px; color:#fff; text-transform:uppercase; letter-spacing:.3px;
}
.org-pill.IAB { background:var(--iab); }
.org-pill.IESG { background:var(--iesg); }
.org-pill.AREA { background:var(--area); }
.org-pill.IRTF-RG { background:var(--irtf); }
.org-pill.IETF-WG { background:var(--wg); }

.cell::after {
  content:''; width:8px; height:8px;
  border-right:2px solid #c7c7cc; border-bottom:2px solid #c7c7cc;
  transform:rotate(-45deg); flex-shrink:0; margin-left:8px;
}

/* ─── Timeline Panel ─── */
#timeline-panel { -webkit-overflow-scrolling:touch; padding:10px 0 20px; background:#1a1c2e; }
#timeline-panel .era-section { margin:0 10px 16px; }
#timeline-panel .era-header {
  font-size:13px; font-weight:700; color:rgba(255,255,255,.5);
  text-transform:uppercase; letter-spacing:.5px;
  padding:6px 6px 4px;
}
.era-card {
  background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.08);
  border-radius:10px; padding:12px 14px;
  margin-bottom:8px;
}
.era-card-name { font-size:17px; font-weight:500; color:#fff; }
.era-card-sub { font-size:12px; color:rgba(255,255,255,.5); margin-top:2px; }
.era-sparkline { margin-top:8px; height:24px; display:flex; align-items:flex-end; gap:1px; }
.era-spark-bar {
  flex:1; background:rgba(100,160,255,.35); border-radius:1px 1px 0 0; min-height:1px;
}
.era-spark-bar.peak { background:rgba(100,160,255,.85); }
.era-year-range {
  display:flex; justify-content:space-between; font-size:9px; color:rgba(255,255,255,.35); margin-top:2px;
}

/* ─── Stats Panel ─── */
#stats-panel { -webkit-overflow-scrolling:touch; padding:10px 0 20px; }

.stat-card {
  margin:6px 10px; background:var(--cell-bg);
  border-radius:10px;
  box-shadow:0 1px 3px rgba(0,0,0,.12),0 0 0 1px rgba(0,0,0,.04);
  padding:14px 16px;
}
.stat-card h3 { font-size:13px; font-weight:700; color:var(--txt2); text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px; }
.stat-number { font-size:44px; font-weight:300; color:var(--txt1); line-height:1; }
.stat-label { font-size:13px; color:var(--txt2); margin-top:2px; }

.stat-bar-row { display:flex; align-items:center; margin:6px 0; }
.stat-bar-label { width:80px; font-size:13px; color:var(--txt2); flex-shrink:0; }
.stat-bar-track { flex:1; height:18px; background:#e8e8ed; border-radius:9px; overflow:hidden; box-shadow:0 1px 2px rgba(0,0,0,.08) inset; }
.stat-bar-fill { height:100%; border-radius:9px; transition:width .4s ease; }
.stat-bar-val { width:36px; text-align:right; font-size:13px; font-weight:600; margin-left:6px; }

/* ─── Detail Overlay ─── */
.detail-overlay { position:fixed; inset:0; z-index:200; display:none; flex-direction:column; }
.detail-overlay.open { display:flex; }
.detail-backdrop { position:absolute; inset:0; background:rgba(0,0,0,.4); }
.detail-sheet {
  position:absolute; bottom:0; left:0; right:0;
  max-height:75vh; background:var(--linen);
  border-radius:12px 12px 0 0;
  box-shadow:0 -4px 20px rgba(0,0,0,.3);
  overflow-y:auto; -webkit-overflow-scrolling:touch;
  animation:sheetUp .25s ease-out;
}
@keyframes sheetUp { from{transform:translateY(100%)} to{transform:translateY(0)} }
.detail-handle { width:36px; height:5px; border-radius:2.5px; background:rgba(0,0,0,.15); margin:8px auto; }
.detail-close {
  position:absolute; top:8px; right:12px;
  width:var(--touch); height:var(--touch);
  display:flex; align-items:center; justify-content:center;
  background:none; border:none; font-size:28px; color:var(--blue); cursor:pointer;
}
.detail-header { padding:4px 16px 12px; text-align:center; }
.detail-name { font-size:22px; font-weight:700; }
.detail-bio { font-size:14px; color:var(--txt2); margin-top:4px; line-height:1.4; }
.detail-section { margin:0 10px 12px; background:var(--cell-bg); border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.12); overflow:hidden; }
.detail-row { display:flex; align-items:center; min-height:38px; padding:6px 16px; border-bottom:1px solid var(--cell-border); font-size:15px; }
.detail-row:last-child { border-bottom:none; }
.detail-row-label { color:var(--txt2); width:80px; flex-shrink:0; }
.detail-row-value { flex:1; font-weight:500; }

/* ─── Detail sparkline ─── */
.detail-sparkline { display:flex; align-items:flex-end; gap:2px; height:40px; padding:8px 16px; }
.detail-spark-bar { flex:1; background:var(--coauth); border-radius:2px 2px 0 0; min-height:2px; opacity:.7; }

::-webkit-scrollbar { width:0; }
</style>
</head>
<body>

<nav class="nav-bar">
  <h1>IETF Power Map</h1>
  <span class="sub">Live Datatracker</span>
</nav>

<div class="tab-bar">
  <button class="tab-item active" data-tab="graph-panel">
    <svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="12" cy="18" r="3"/><line x1="8.5" y1="7.5" x2="10.5" y2="16" stroke="currentColor" stroke-width="1.5" fill="none"/><line x1="15.5" y1="7.5" x2="13.5" y2="16" stroke="currentColor" stroke-width="1.5" fill="none"/><line x1="9" y1="6" x2="15" y2="6" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>
    Graph
  </button>
  <button class="tab-item" data-tab="list-panel">
    <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="3" rx="1"/><rect x="3" y="10.5" width="18" height="3" rx="1"/><rect x="3" y="17" width="18" height="3" rx="1"/></svg>
    Power List
  </button>
  <button class="tab-item" data-tab="timeline-panel">
    <svg viewBox="0 0 24 24"><path d="M3 21V3m0 18h18M7 14l4-5 4 3 5-7" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
    Timeline
  </button>
  <button class="tab-item" data-tab="stats-panel">
    <svg viewBox="0 0 24 24"><rect x="3" y="14" width="4" height="7" rx="1"/><rect x="10" y="8" width="4" height="13" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>
    Stats
  </button>
</div>

<div class="content">
  <div id="graph-panel" class="panel active">
    <svg id="graph-svg"></svg>
    <div class="graph-controls">
      <div class="seg-control" id="layer-control">
        <button class="seg-btn active" data-layer="governance">Governance</button>
        <button class="seg-btn" data-layer="rfc">RFC Weight</button>
        <button class="seg-btn" data-layer="temporal">Temporal</button>
      </div>
    </div>
    <div class="graph-legend" id="graph-legend"></div>
    <div class="timeline-wrap" id="timeline-scrubber">
      <div class="timeline-label">Era Filter</div>
      <div class="timeline-value" id="era-label">All Eras</div>
      <div class="timeline-bar-chart" id="era-bars"></div>
      <input type="range" class="timeline-slider" id="era-slider" min="0" max="10" value="0" step="1">
    </div>
    <div class="graph-tooltip" id="tooltip"></div>
  </div>

  <div id="list-panel" class="panel">
    <div class="search-bar-wrap">
      <input type="search" class="search-bar" placeholder="Search people..." id="search-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
    </div>
    <div class="list-controls">
      <div class="sort-seg" id="sort-control">
        <button class="sort-btn active" data-sort="weight">Governance</button>
        <button class="sort-btn" data-sort="rfc">RFCs</button>
        <button class="sort-btn" data-sort="span">Longevity</button>
        <button class="sort-btn" data-sort="combined">Combined</button>
      </div>
    </div>
    <div id="list-content"></div>
  </div>

  <div id="timeline-panel" class="panel">
    <div id="timeline-content"></div>
  </div>

  <div id="stats-panel" class="panel">
    <div id="stats-content"></div>
  </div>
</div>

<div class="detail-overlay" id="detail-overlay">
  <div class="detail-backdrop" id="detail-backdrop"></div>
  <div class="detail-sheet">
    <div class="detail-handle"></div>
    <button class="detail-close" id="detail-close">&times;</button>
    <div class="detail-header">
      <div class="detail-name" id="detail-name"></div>
      <div class="detail-bio" id="detail-bio"></div>
    </div>
    <div id="detail-body"></div>
  </div>
</div>

<script>
'''

html += f'const D = {graph_data};\n'

html += r'''
// ═══════════════════════════════════════════
// DATA
// ═══════════════════════════════════════════
const nodes = D.n.map(d => ({
  id:d.i, name:d.n, weight:d.w, orgs:d.o, groups:d.g, numOrgs:d.c, bio:d.b||'',
  rfcCount:d.rc||0, firstYear:d.fy, lastYear:d.ly, span:d.sp||0, decades:d.dc||{}
}));
const links = D.l.map(d => ({source:d.s, target:d.t, weight:d.w, coauth:d.c||0}));
const yearHist = D.yh || {};
const nodeMap = new Map(nodes.map(n => [n.id, n]));

function orgColor(orgs) {
  if (orgs.includes('IAB') && orgs.includes('IESG')) return '#e74c3c';
  if (orgs.includes('IAB')) return '#c0392b';
  if (orgs.includes('IESG') || orgs.includes('AREA')) return '#2980b9';
  if (orgs.includes('IRTF-RG')) return '#27ae60';
  return '#7f8c8d';
}

// ═══════════════════════════════════════════
// TABS
// ═══════════════════════════════════════════
document.querySelectorAll('.tab-item').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
    if (tab.dataset.tab === 'graph-panel' && !graphReady) initGraph();
  });
});

// ═══════════════════════════════════════════
// DETAIL
// ═══════════════════════════════════════════
function showDetail(n) {
  document.getElementById('detail-name').textContent = n.name;
  document.getElementById('detail-bio').textContent = n.bio;
  let h = '<div class="detail-section">';
  h += `<div class="detail-row"><span class="detail-row-label">Weight</span><span class="detail-row-value">${n.weight}</span></div>`;
  h += `<div class="detail-row"><span class="detail-row-label">RFCs</span><span class="detail-row-value">${n.rfcCount}</span></div>`;
  if (n.firstYear) h += `<div class="detail-row"><span class="detail-row-label">Active</span><span class="detail-row-value">${n.firstYear} – ${n.lastYear} (${n.span}yr)</span></div>`;
  h += `<div class="detail-row"><span class="detail-row-label">Bodies</span><span class="detail-row-value">${n.orgs.join(', ')}</span></div>`;
  h += '</div>';

  // Sparkline for decade histogram
  const dkeys = Object.keys(n.decades).sort();
  if (dkeys.length > 0) {
    const allEras = ['1980','1985','1990','1995','2000','2005','2010','2015','2020','2025'];
    const maxD = Math.max(...Object.values(n.decades));
    h += '<div class="group-header">RFC Output by Era</div><div class="detail-section">';
    h += '<div class="detail-sparkline">';
    allEras.forEach(e => {
      const v = n.decades[e] || 0;
      const pct = maxD > 0 ? (v / maxD * 100) : 0;
      h += `<div class="detail-spark-bar" style="height:${Math.max(pct, 3)}%" title="${e}: ${v} RFCs"></div>`;
    });
    h += '</div>';
    h += '<div style="display:flex;justify-content:space-between;padding:0 16px 8px;font-size:9px;color:var(--txt2)">';
    h += '<span>1980</span><span>1995</span><span>2010</span><span>2025</span></div>';
    h += '</div>';
  }

  h += '<div class="group-header">Groups</div><div class="detail-section">';
  n.groups.forEach(g => {
    const [org, name] = g.split(':');
    h += `<div class="detail-row"><span class="detail-row-label" style="width:70px"><span class="org-pill ${org}">${org}</span></span><span class="detail-row-value">${name}</span></div>`;
  });
  h += '</div>';

  // Connections
  const conns = [];
  links.forEach(l => {
    const sid = typeof l.source === 'object' ? l.source.id : l.source;
    const tid = typeof l.target === 'object' ? l.target.id : l.target;
    if (sid === n.id || tid === n.id) {
      const oid = sid === n.id ? tid : sid;
      const o = nodeMap.get(oid);
      if (o && (o.weight > 1 || o.rfcCount > 5)) conns.push({...o, linkCoauth: l.coauth, linkW: l.weight});
    }
  });
  conns.sort((a, b) => b.weight - a.weight);
  if (conns.length) {
    h += '<div class="group-header">Connections</div><div class="detail-section">';
    conns.slice(0, 12).forEach(c => {
      const tag = c.linkCoauth ? `<span style="font-size:10px;color:var(--coauth)"> ${c.linkW} shared RFCs</span>` : '';
      h += `<div class="detail-row"><span class="detail-row-value">${c.name}${tag}</span><span style="margin-left:auto"><span class="weight-badge">${c.weight}</span></span></div>`;
    });
    h += '</div>';
  }

  document.getElementById('detail-body').innerHTML = h;
  document.getElementById('detail-overlay').classList.add('open');
}
document.getElementById('detail-backdrop').addEventListener('click', () => document.getElementById('detail-overlay').classList.remove('open'));
document.getElementById('detail-close').addEventListener('click', () => document.getElementById('detail-overlay').classList.remove('open'));

// ═══════════════════════════════════════════
// GRAPH
// ═══════════════════════════════════════════
let graphReady = false;
let currentLayer = 'governance';
let simulation, nodeEls, linkEls, labelEls;

function nodeRadius(n, layer) {
  if (layer === 'rfc') return Math.max(3, Math.sqrt(n.rfcCount) * 1.8);
  if (layer === 'temporal') return n.span > 0 ? Math.max(4, n.span * 0.4) : 3;
  // governance
  const w = n.weight;
  if (w >= 10) return 14; if (w >= 8) return 11; if (w >= 5) return 9; if (w >= 3) return 7;
  return 4;
}

function nodeColor(n, layer) {
  if (layer === 'rfc') {
    if (n.rfcCount === 0) return '#444';
    const t = Math.min(n.rfcCount / 80, 1);
    const r = Math.round(44 + t * 187);
    const g = Math.round(62 + (1 - t) * 64);
    const b = Math.round(80 - t * 40);
    return `rgb(${r},${g},${b})`;
  }
  if (layer === 'temporal') {
    if (!n.firstYear) return '#333';
    const t = Math.min((2025 - n.firstYear) / 40, 1);
    // old = gold, new = cyan
    const r = Math.round(46 + t * 185);
    const g = Math.round(204 - t * 74);
    const b = Math.round(250 - t * 210);
    return `rgb(${r},${g},${b})`;
  }
  return orgColor(n.orgs);
}

function updateLegend(layer) {
  const el = document.getElementById('graph-legend');
  if (layer === 'governance') {
    el.innerHTML = `
      <div class="legend-row"><div class="legend-dot" style="background:var(--iab)"></div>IAB</div>
      <div class="legend-row"><div class="legend-dot" style="background:var(--iesg)"></div>IESG / Area</div>
      <div class="legend-row"><div class="legend-dot" style="background:var(--irtf)"></div>IRTF Research</div>
      <div class="legend-row"><div class="legend-dot" style="background:var(--wg)"></div>WG Chair</div>
      <div class="legend-row"><div class="legend-line" style="border-top:2px solid rgba(100,130,180,.4)"></div>Same group</div>
      <div class="legend-row"><div class="legend-line" style="border-top:2px dashed var(--coauth)"></div>Co-authors</div>`;
  } else if (layer === 'rfc') {
    el.innerHTML = `
      <div class="legend-row"><div class="legend-dot" style="background:#e74c3c"></div>100+ RFCs</div>
      <div class="legend-row"><div class="legend-dot" style="background:#c0392b"></div>50+ RFCs</div>
      <div class="legend-row"><div class="legend-dot" style="background:#6a5d80"></div>10+ RFCs</div>
      <div class="legend-row"><div class="legend-dot" style="background:#444"></div>0 RFCs</div>
      <div class="legend-row" style="font-size:10px;color:rgba(255,255,255,.5)">Size = √(RFC count)</div>`;
  } else {
    el.innerHTML = `
      <div class="legend-row"><div class="legend-dot" style="background:rgb(231,186,40)"></div>Active since 1980s</div>
      <div class="legend-row"><div class="legend-dot" style="background:rgb(140,160,130)"></div>Active since 2000s</div>
      <div class="legend-row"><div class="legend-dot" style="background:rgb(46,204,250)"></div>Recent (2020s)</div>
      <div class="legend-row" style="font-size:10px;color:rgba(255,255,255,.5)">Size = years active</div>`;
  }
}

function setLayer(layer) {
  currentLayer = layer;
  document.querySelectorAll('#layer-control .seg-btn').forEach(b => b.classList.toggle('active', b.dataset.layer === layer));
  document.getElementById('timeline-scrubber').classList.toggle('visible', layer === 'temporal');
  updateLegend(layer);
  if (!nodeEls) return;

  nodeEls.select('circle')
    .transition().duration(400)
    .attr('r', d => nodeRadius(d, layer))
    .attr('fill', d => nodeColor(d, layer))
    .attr('stroke', d => {
      if (layer === 'rfc' && d.rfcCount > 50) return 'rgba(255,255,255,.4)';
      if (layer === 'temporal' && d.span > 25) return 'rgba(255,200,50,.5)';
      if (layer === 'governance' && d.weight >= 8) return 'rgba(255,255,255,.4)';
      return 'rgba(255,255,255,.12)';
    });

  linkEls
    .transition().duration(400)
    .attr('stroke', d => d.coauth ? 'rgba(230,126,34,.25)' : 'rgba(100,130,180,.12)')
    .attr('stroke-dasharray', d => d.coauth ? '4,3' : 'none')
    .attr('stroke-width', d => {
      if (layer === 'rfc' && d.coauth) return Math.min(d.weight * 0.5, 4);
      return Math.min(d.weight * 0.8, 3);
    })
    .attr('opacity', d => {
      if (layer === 'rfc') return d.coauth ? 0.8 : 0.15;
      if (layer === 'temporal') return 0.2;
      return d.coauth ? 0.4 : 0.6;
    });

  labelEls
    .text(d => {
      if (layer === 'rfc' && d.rfcCount >= 30) return d.name.split(' ').pop();
      if (layer === 'temporal' && d.span >= 20) return d.name.split(' ').pop();
      if (layer === 'governance' && d.weight >= 5) return d.name.split(' ').pop();
      return '';
    });

  simulation.force('collision', d3.forceCollide(d => nodeRadius(d, layer) + 3));
  simulation.alpha(0.15).restart();
}

function initGraph() {
  graphReady = true;
  const container = document.getElementById('graph-panel');
  const svg = d3.select('#graph-svg');
  const W = container.clientWidth, H = container.clientHeight;
  svg.attr('viewBox', [0, 0, W, H]);

  const defs = svg.append('defs');
  const grad = defs.append('radialGradient').attr('id', 'bg');
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#252840');
  grad.append('stop').attr('offset', '100%').attr('stop-color', '#0f1019');
  svg.append('rect').attr('width', W).attr('height', H).attr('fill', 'url(#bg)');

  const glow = defs.append('filter').attr('id', 'glow');
  glow.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'b');
  const m = glow.append('feMerge'); m.append('feMergeNode').attr('in', 'b'); m.append('feMergeNode').attr('in', 'SourceGraphic');

  const vis = nodes.filter(n => n.weight >= 1 || n.rfcCount >= 3);
  const visIds = new Set(vis.map(n => n.id));
  const visLinks = links.filter(l => visIds.has(l.source) && visIds.has(l.target));

  simulation = d3.forceSimulation(vis)
    .force('link', d3.forceLink(visLinks).id(d => d.id)
      .distance(d => 90 - Math.min((nodeMap.get(typeof d.source === 'object' ? d.source.id : d.source)?.weight || 1), 8) * 4)
      .strength(d => Math.min(d.weight * 0.12, 0.7)))
    .force('charge', d3.forceManyBody().strength(d => -40 - d.weight * 12 - d.rfcCount * 0.5))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collision', d3.forceCollide(d => nodeRadius(d, currentLayer) + 3))
    .force('x', d3.forceX(W / 2).strength(0.025))
    .force('y', d3.forceY(H / 2).strength(0.025));

  const g = svg.append('g');

  linkEls = g.append('g').selectAll('line').data(visLinks).join('line')
    .attr('stroke', d => d.coauth ? 'rgba(230,126,34,.25)' : 'rgba(100,130,180,.15)')
    .attr('stroke-width', d => Math.min(d.weight * 0.8, 3))
    .attr('stroke-dasharray', d => d.coauth ? '4,3' : 'none');

  nodeEls = g.append('g').selectAll('g').data(vis).join('g')
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
    );

  nodeEls.append('circle')
    .attr('r', d => nodeRadius(d, 'governance'))
    .attr('fill', d => orgColor(d.orgs))
    .attr('stroke', d => d.weight >= 8 ? 'rgba(255,255,255,.4)' : 'rgba(255,255,255,.12)')
    .attr('stroke-width', d => d.weight >= 8 ? 2 : 1)
    .attr('filter', d => d.weight >= 8 ? 'url(#glow)' : null);

  labelEls = nodeEls.append('text')
    .text(d => d.weight >= 5 ? d.name.split(' ').pop() : '')
    .attr('dy', d => nodeRadius(d, 'governance') + 12)
    .attr('text-anchor', 'middle')
    .attr('fill', 'rgba(255,255,255,.7)')
    .attr('font-size', '10px').attr('font-weight', '500')
    .attr('pointer-events', 'none');

  const tip = document.getElementById('tooltip');
  nodeEls.on('mouseover', (e, d) => {
    tip.style.display = 'block';
    tip.textContent = `${d.name} — ${d.orgs.join('/')}${d.rfcCount ? ' · ' + d.rfcCount + ' RFCs' : ''}`;
  }).on('mousemove', e => {
    const r = container.getBoundingClientRect();
    tip.style.left = (e.clientX - r.left + 12) + 'px';
    tip.style.top = (e.clientY - r.top - 30) + 'px';
  }).on('mouseout', () => tip.style.display = 'none')
    .on('click', (e, d) => { tip.style.display = 'none'; showDetail(d); });

  svg.call(d3.zoom().scaleExtent([0.3, 5]).on('zoom', e => g.attr('transform', e.transform)));

  simulation.on('tick', () => {
    linkEls.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    nodeEls.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  updateLegend('governance');

  // Layer control
  document.querySelectorAll('#layer-control .seg-btn').forEach(b => {
    b.addEventListener('click', () => setLayer(b.dataset.layer));
  });

  // Era slider for temporal mode
  const eras = ['All','1980–84','1985–89','1990–94','1995–99','2000–04','2005–09','2010–14','2015–19','2020–24','2025+'];
  const eraStarts = [0, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025];
  const slider = document.getElementById('era-slider');
  const eraLabel = document.getElementById('era-label');

  // Build mini bar chart
  const yearKeys = ['1980','1985','1990','1995','2000','2005','2010','2015','2020','2025'];
  const maxYH = Math.max(...yearKeys.map(k => yearHist[k] || 0));
  const barsEl = document.getElementById('era-bars');
  yearKeys.forEach((k, i) => {
    const v = yearHist[k] || 0;
    const pct = maxYH > 0 ? (v / maxYH * 100) : 0;
    const bar = document.createElement('div');
    bar.className = 'timeline-bar';
    bar.style.height = Math.max(pct, 5) + '%';
    bar.dataset.idx = i + 1;
    barsEl.appendChild(bar);
  });

  slider.addEventListener('input', () => {
    const idx = parseInt(slider.value);
    eraLabel.textContent = eras[idx];
    barsEl.querySelectorAll('.timeline-bar').forEach(b => {
      b.classList.toggle('active', idx === 0 || parseInt(b.dataset.idx) === idx);
    });

    if (idx === 0) {
      // Show all
      nodeEls.select('circle').transition().duration(300).attr('opacity', 1);
      linkEls.transition().duration(300).attr('opacity', d => d.coauth ? 0.3 : 0.2);
    } else {
      const eraStart = eraStarts[idx];
      const eraEnd = eraStart + 5;
      nodeEls.select('circle').transition().duration(300).attr('opacity', d => {
        if (!d.firstYear) return 0.08;
        // Check if active during this era (via decades)
        const eraKey = String(eraStart);
        const hasRFCs = (d.decades[eraKey] || 0) > 0;
        return hasRFCs ? 1 : 0.08;
      });
      linkEls.transition().duration(300).attr('opacity', 0.05);
    }
  });
}

// ═══════════════════════════════════════════
// LIST
// ═══════════════════════════════════════════
let currentSort = 'weight';

function sortNodes(method) {
  const s = [...nodes];
  if (method === 'rfc') s.sort((a, b) => b.rfcCount - a.rfcCount || b.weight - a.weight);
  else if (method === 'span') s.sort((a, b) => b.span - a.span || b.rfcCount - a.rfcCount);
  else if (method === 'combined') s.sort((a, b) => (b.weight * 3 + b.rfcCount + b.span * 0.5) - (a.weight * 3 + a.rfcCount + a.span * 0.5));
  else s.sort((a, b) => b.weight - a.weight || b.numOrgs - a.numOrgs);
  return s;
}

function renderList(filter = '') {
  const lc = filter.toLowerCase();
  const sorted = sortNodes(currentSort);
  const filtered = lc ? sorted.filter(n => n.name.toLowerCase().includes(lc)) : sorted;

  let h = '', rank = 1;
  const tierDefs = currentSort === 'rfc'
    ? [{l:'Prolific Authors (50+)', f:n=>n.rfcCount>=50}, {l:'Major Contributors (20+)', f:n=>n.rfcCount>=20&&n.rfcCount<50}, {l:'Active Authors (5+)', f:n=>n.rfcCount>=5&&n.rfcCount<20}, {l:'Occasional / None', f:n=>n.rfcCount<5}]
    : currentSort === 'span'
    ? [{l:'Decades-long (25yr+)', f:n=>n.span>=25}, {l:'Established (15yr+)', f:n=>n.span>=15&&n.span<25}, {l:'Mid-career (5yr+)', f:n=>n.span>=5&&n.span<15}, {l:'Recent / No RFCs', f:n=>n.span<5}]
    : currentSort === 'combined'
    ? [{l:'Apex Influence', f:n=>(n.weight*3+n.rfcCount+n.span*.5)>=60}, {l:'Major Players', f:n=>{const s=n.weight*3+n.rfcCount+n.span*.5;return s>=20&&s<60}}, {l:'Contributors', f:n=>{const s=n.weight*3+n.rfcCount+n.span*.5;return s>=5&&s<20}}, {l:'Participants', f:n=>(n.weight*3+n.rfcCount+n.span*.5)<5}]
    : [{l:'Cross-Body Leadership', f:n=>n.weight>=10}, {l:'Governance Core', f:n=>n.weight>=5&&n.weight<10}, {l:'Research & WG Leaders', f:n=>n.weight>=3&&n.weight<5}, {l:'Working Group Chairs', f:n=>n.weight<3}];

  tierDefs.forEach(tier => {
    const tn = filtered.filter(tier.f);
    if (!tn.length) return;
    h += `<div class="group-header">${tier.l} (${tn.length})</div><div class="table-group">`;
    tn.forEach(n => {
      const pills = n.orgs.map(o => `<span class="org-pill ${o}">${o}</span>`).join('');
      const spanTxt = n.span > 0 ? ` · ${n.firstYear}–${n.lastYear}` : '';
      h += `<div class="cell" data-id="${n.id}">
        <div class="cell-rank">${rank}</div>
        <div class="cell-body">
          <div class="cell-name">${n.name}</div>
          <div class="cell-detail">${n.rfcCount} RFCs${spanTxt}</div>
          <div class="org-pills">${pills}</div>
        </div>
        <div class="cell-badges">
          ${n.rfcCount > 0 ? `<span class="rfc-badge">${n.rfcCount}</span>` : ''}
          <span class="weight-badge">${n.weight}</span>
        </div>
      </div>`;
      rank++;
    });
    h += '</div>';
  });

  document.getElementById('list-content').innerHTML = h;
  document.querySelectorAll('.cell[data-id]').forEach(c => c.addEventListener('click', () => {
    const n = nodeMap.get(c.dataset.id);
    if (n) showDetail(n);
  }));
}

document.getElementById('search-input').addEventListener('input', e => renderList(e.target.value));
document.querySelectorAll('#sort-control .sort-btn').forEach(b => {
  b.addEventListener('click', () => {
    document.querySelectorAll('#sort-control .sort-btn').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    currentSort = b.dataset.sort;
    renderList(document.getElementById('search-input').value);
  });
});
renderList();

// ═══════════════════════════════════════════
// TIMELINE PANEL
// ═══════════════════════════════════════════
function renderTimeline() {
  const withSpan = nodes.filter(n => n.span > 0).sort((a, b) => a.firstYear - b.firstYear || b.span - a.span);
  const allEras = ['1980','1985','1990','1995','2000','2005','2010','2015','2020','2025'];
  const eraNames = {'1980':'Early Internet','1985':'Pre-Web','1990':'Web Dawn','1995':'Dot-Com','2000':'Post-Bubble','2005':'Web 2.0','2010':'Cloud Era','2015':'Encryption Push','2020':'Pandemic Shift','2025':'Post-Quantum'};

  let h = '';

  // Global production chart
  h += '<div class="era-section"><div class="era-header">RFC Production by Era</div>';
  h += '<div class="era-card"><div class="era-sparkline">';
  const maxG = Math.max(...allEras.map(e => yearHist[e] || 0));
  allEras.forEach(e => {
    const v = yearHist[e] || 0;
    h += `<div class="era-spark-bar${v === maxG ? ' peak' : ''}" style="height:${Math.max(v / maxG * 100, 3)}%" title="${eraNames[e]}: ${v} RFCs"></div>`;
  });
  h += '</div><div class="era-year-range"><span>1980</span><span>1995</span><span>2010</span><span>2025</span></div></div></div>';

  // Longest-serving authors
  const legends = withSpan.filter(n => n.span >= 15).sort((a, b) => b.span - a.span);
  h += '<div class="era-section"><div class="era-header">Internet Elders (15yr+ span)</div>';
  legends.forEach(n => {
    const maxD = Math.max(...Object.values(n.decades), 1);
    h += `<div class="era-card" style="cursor:pointer" data-id="${n.id}">`;
    h += `<div class="era-card-name">${n.name}</div>`;
    h += `<div class="era-card-sub">${n.rfcCount} RFCs · ${n.firstYear}–${n.lastYear} · ${n.span} years</div>`;
    h += '<div class="era-sparkline">';
    allEras.forEach(e => {
      const v = n.decades[e] || 0;
      h += `<div class="era-spark-bar${v === maxD ? ' peak' : ''}" style="height:${Math.max(v / maxD * 100, 3)}%"></div>`;
    });
    h += '</div><div class="era-year-range"><span>1980</span><span>1995</span><span>2010</span><span>2025</span></div>';
    h += '</div>';
  });
  h += '</div>';

  // Rising stars (recent, high output)
  const rising = nodes.filter(n => n.firstYear && n.firstYear >= 2012 && n.rfcCount >= 5).sort((a, b) => b.rfcCount - a.rfcCount);
  if (rising.length) {
    h += '<div class="era-section"><div class="era-header">Rising Stars (post-2012, 5+ RFCs)</div>';
    rising.forEach(n => {
      h += `<div class="era-card" style="cursor:pointer" data-id="${n.id}">`;
      h += `<div class="era-card-name">${n.name}</div>`;
      h += `<div class="era-card-sub">${n.rfcCount} RFCs since ${n.firstYear}</div>`;
      h += '</div>';
    });
    h += '</div>';
  }

  document.getElementById('timeline-content').innerHTML = h;
  document.querySelectorAll('#timeline-content [data-id]').forEach(c => c.addEventListener('click', () => {
    const n = nodeMap.get(c.dataset.id);
    if (n) showDetail(n);
  }));
}
renderTimeline();

// ═══════════════════════════════════════════
// STATS
// ═══════════════════════════════════════════
function renderStats() {
  const multiOrg = nodes.filter(n => n.numOrgs >= 2);
  const withRFCs = nodes.filter(n => n.rfcCount > 0);
  const totalRFCs = nodes.reduce((s, n) => s + n.rfcCount, 0);
  const orgCounts = {};
  nodes.forEach(n => n.orgs.forEach(o => orgCounts[o] = (orgCounts[o] || 0) + 1));
  const maxOrg = Math.max(...Object.values(orgCounts));

  let h = '<div style="display:flex;gap:6px;padding:0 10px;flex-wrap:wrap">';
  h += `<div class="stat-card" style="flex:1;min-width:90px;text-align:center"><div class="stat-number">${nodes.length}</div><div class="stat-label">People</div></div>`;
  h += `<div class="stat-card" style="flex:1;min-width:90px;text-align:center"><div class="stat-number">${multiOrg.length}</div><div class="stat-label">Multi-body</div></div>`;
  h += `<div class="stat-card" style="flex:1;min-width:90px;text-align:center"><div class="stat-number">${totalRFCs}</div><div class="stat-label">RFC authorships</div></div>`;
  h += '</div>';

  h += '<div class="stat-card"><h3>By Governance Body</h3>';
  ['IETF-WG','IRTF-RG','AREA','IESG','IAB'].forEach(o => {
    const c = orgCounts[o] || 0;
    const colors = {'IAB':'var(--iab)','IESG':'var(--iesg)','AREA':'var(--area)','IRTF-RG':'var(--irtf)','IETF-WG':'var(--wg)'};
    const labels = {'IAB':'IAB','IESG':'IESG','AREA':'Area Dir','IRTF-RG':'IRTF RG','IETF-WG':'WG Chair'};
    h += `<div class="stat-bar-row"><span class="stat-bar-label">${labels[o]}</span><div class="stat-bar-track"><div class="stat-bar-fill" style="width:${c/maxOrg*100}%;background:${colors[o]}"></div></div><span class="stat-bar-val">${c}</span></div>`;
  });
  h += '</div>';

  const avgRFC = withRFCs.length ? (withRFCs.reduce((s,n) => s + n.rfcCount, 0) / withRFCs.length).toFixed(1) : 0;
  const avgSpan = withRFCs.filter(n=>n.span>0).length ? (withRFCs.filter(n=>n.span>0).reduce((s,n) => s+n.span, 0) / withRFCs.filter(n=>n.span>0).length).toFixed(1) : 0;
  h += `<div class="stat-card"><h3>Temporal Profile</h3>`;
  h += `<p style="font-size:14px;color:var(--txt2);line-height:1.6">Of ${nodes.length} governance participants, <strong>${withRFCs.length}</strong> have authored at least one RFC (avg <strong>${avgRFC}</strong> RFCs each). The average active span is <strong>${avgSpan} years</strong>. The oldest continuously active contributor dates to <strong>1982</strong>.</p>`;
  h += '</div>';

  h += '<div class="stat-card" style="text-align:center"><p style="font-size:11px;color:var(--txt2)">Data: IETF Datatracker API · RFC number→year interpolation<br>Temporal resolution: 5-year buckets · Coauthorship: ≥2 shared RFCs</p></div>';

  document.getElementById('stats-content').innerHTML = h;
}
renderStats();

initGraph();
</script>
</body>
</html>
'''

with open('/home/claude/ietf_power_map_v2.html', 'w') as f:
    f.write(html)

import os
print(f"Output: {os.path.getsize('/home/claude/ietf_power_map_v2.html') / 1024:.1f} KB")
