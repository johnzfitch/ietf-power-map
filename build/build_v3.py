import json

with open('/home/claude/graph_final.json') as f:
    data_json = f.read()

# Build the HTML in parts to manage size
with open('/home/claude/ietf_v3.html', 'w') as out:
    out.write('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,maximum-scale=1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<title>IETF Governance Power Map</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;500;700&display=swap');
:root{--nav:44px;--tab:49px;--touch:44px;--linen:#e5e0d8;--cell:#fff;--brd:#c8c7cc;--t1:#1a1a1a;--t2:#6d6d72;--blue:#007aff;--iab:#c0392b;--iesg:#2980b9;--area:#8e44ad;--irtf:#27ae60;--wg:#7f8c8d;--co:#e67e22}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{width:100%;height:100%;overflow:hidden;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:16px;color:var(--t1);background:var(--linen);-webkit-font-smoothing:antialiased}
body::before{content:'';position:fixed;inset:0;z-index:-1;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.02) 2px,rgba(0,0,0,.02) 4px),repeating-linear-gradient(90deg,transparent,transparent 2px,rgba(0,0,0,.015) 2px,rgba(0,0,0,.015) 4px),linear-gradient(180deg,#e8e3db,#d5d0c8)}
.nav{position:fixed;top:0;left:0;right:0;height:var(--nav);z-index:100;background:linear-gradient(180deg,#b8c5d6 0%,#8e9faf 2%,#7d8fa1 50%,#6a7d90 51%,#5d7085 100%);border-bottom:1px solid rgba(0,0,0,.4);box-shadow:0 1px 0 rgba(255,255,255,.15) inset,0 1px 3px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center}
.nav h1{font-size:18px;font-weight:700;color:#fff;text-shadow:0 -1px 1px rgba(0,0,0,.5);letter-spacing:-.3px}
.nav .sub{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-size:11px;color:rgba(255,255,255,.7);text-shadow:0 -1px 1px rgba(0,0,0,.3)}
.tabs{position:fixed;bottom:0;left:0;right:0;height:var(--tab);z-index:100;background:linear-gradient(180deg,#434343 0%,#2a2a2a 2%,#1a1a1a 50%,#111 51%,#0a0a0a 100%);border-top:1px solid rgba(255,255,255,.08);box-shadow:0 -1px 4px rgba(0,0,0,.6);display:flex}
.ti{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:var(--touch);cursor:pointer;border:none;background:none;color:#8e8e93;font-size:10px;font-weight:500;-webkit-user-select:none;user-select:none}
.ti.on{color:#fff}.ti svg{width:22px;height:22px;margin-bottom:2px;fill:currentColor}.ti.on svg{filter:drop-shadow(0 0 4px rgba(100,160,255,.4))}
.content{position:fixed;top:var(--nav);bottom:var(--tab);left:0;right:0;overflow:hidden}
.pnl{display:none;width:100%;height:100%;overflow-y:auto;overflow-x:hidden}.pnl.on{display:block}
#gp{overflow:hidden;background:#1a1c2e}#gp svg{width:100%;height:100%}
.gc{position:absolute;top:8px;left:8px;right:8px;display:flex;gap:6px;flex-wrap:wrap;z-index:50}
.seg{display:inline-flex;background:rgba(0,0,0,.5);border-radius:7px;border:1px solid rgba(255,255,255,.12);overflow:hidden;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.sb{padding:5px 10px;font-size:11px;font-weight:600;color:rgba(255,255,255,.6);border:none;background:none;cursor:pointer;border-right:1px solid rgba(255,255,255,.1);min-height:30px}
.sb:last-child{border-right:none}.sb.on{background:rgba(255,255,255,.18);color:#fff;text-shadow:0 0 6px rgba(100,160,255,.5)}
.gl{position:absolute;bottom:12px;left:12px;background:rgba(0,0,0,.7);border:1px solid rgba(255,255,255,.15);border-radius:8px;padding:8px 10px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:11px;color:rgba(255,255,255,.8)}
.gl .lr{display:flex;align-items:center;margin:2px 0}.gl .ld{width:10px;height:10px;border-radius:50%;margin-right:6px}
.tw{position:absolute;bottom:55px;left:12px;right:12px;background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:8px 12px 12px;backdrop-filter:blur(8px);display:none;z-index:50}
.tw.vis{display:block}
.tval{font-size:20px;font-weight:300;color:#fff;text-align:center;margin:2px 0 4px}
.tbc{display:flex;align-items:flex-end;gap:2px;height:28px;margin:4px 0}.tb{flex:1;background:rgba(100,160,255,.35);border-radius:2px 2px 0 0;min-height:2px;transition:background .2s}.tb.act{background:rgba(100,160,255,.9)}
input[type=range]{-webkit-appearance:none;width:100%;height:6px;border-radius:3px;background:linear-gradient(90deg,#2c3e50,#3498db,#2ecc71,#e67e22,#e74c3c);outline:none;opacity:.9}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:26px;height:26px;border-radius:50%;background:linear-gradient(180deg,#fff,#e0e0e0);box-shadow:0 2px 6px rgba(0,0,0,.4);cursor:pointer}
.gtt{position:absolute;pointer-events:none;background:rgba(0,0,0,.85);color:#fff;padding:6px 10px;border-radius:6px;font-size:12px;font-weight:500;white-space:nowrap;display:none;z-index:50;max-width:280px}
#lp{-webkit-overflow-scrolling:touch;padding:10px 0}
.sbw{padding:8px 10px;position:sticky;top:0;z-index:10;background:var(--linen)}
.si{width:100%;height:36px;border-radius:8px;border:1px solid #b0b0b5;background:#fff;padding:0 12px 0 32px;font-size:15px;color:var(--t1);box-shadow:0 1px 2px rgba(0,0,0,.1) inset;outline:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%238e8e93'%3E%3Ccircle cx='7' cy='7' r='5.5' stroke='%238e8e93' stroke-width='1.5' fill='none'/%3E%3Cline x1='11' y1='11' x2='14' y2='14' stroke='%238e8e93' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:10px center}
.lc{padding:4px 10px;display:flex;gap:5px;flex-wrap:wrap}
.sseg{display:inline-flex;background:#d1d1d6;border-radius:7px;overflow:hidden;border:1px solid #b0b0b5}
.ss{padding:4px 8px;font-size:11px;font-weight:600;color:var(--t2);border:none;background:none;cursor:pointer;border-right:1px solid #b0b0b5}
.ss:last-child{border-right:none}.ss.on{background:#fff;color:var(--t1);box-shadow:0 1px 2px rgba(0,0,0,.1)}
.gh{padding:6px 16px 4px;font-size:13px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:.5px;text-shadow:0 1px 0 rgba(255,255,255,.8)}
.tg{margin:0 10px 12px;background:var(--cell);border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.12),0 0 0 1px rgba(0,0,0,.04);overflow:hidden}
.cl{display:flex;align-items:center;min-height:var(--touch);padding:7px 14px 7px 10px;border-bottom:1px solid var(--brd);cursor:pointer;transition:background .1s}
.cl:last-child{border-bottom:none}.cl:active{background:#d0d0d5}
.cl::after{content:'';width:7px;height:7px;border-right:2px solid #c7c7cc;border-bottom:2px solid #c7c7cc;transform:rotate(-45deg);flex-shrink:0;margin-left:6px}
.cr{width:24px;font-size:15px;font-weight:700;color:var(--t2);text-align:center;flex-shrink:0}
.cb{flex:1;min-width:0;margin-left:8px}.cn{font-size:16px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cd{font-size:11px;color:var(--t2);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cbs{flex-shrink:0;margin-left:6px;display:flex;gap:3px;align-items:center}
.wb{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:22px;border-radius:11px;font-size:12px;font-weight:700;color:#fff;padding:0 6px;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.wb.gov{background:linear-gradient(180deg,#5ac8fa,#007aff)}.wb.rfc{background:linear-gradient(180deg,#f39c12,#e67e22)}
.op{display:flex;gap:2px;margin-top:2px;flex-wrap:wrap}
.pill{font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;color:#fff;text-transform:uppercase;letter-spacing:.3px}
.pill.IAB{background:var(--iab)}.pill.IESG{background:var(--iesg)}.pill.AREA{background:var(--area)}.pill.IRTF-RG{background:var(--irtf)}.pill.IETF-WG{background:var(--wg)}
.gnd{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:4px;flex-shrink:0}
.gnd.male{background:#3498db}.gnd.female{background:#e91e63}.gnd.unknown{background:#999}
/* Corp panel */
#cp{-webkit-overflow-scrolling:touch;padding:10px 0;background:var(--linen)}
.corp-card{margin:6px 10px;background:var(--cell);border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.12);padding:12px 14px;cursor:pointer}
.corp-card:active{background:#e8e8ed}
.corp-name{font-size:18px;font-weight:600}.corp-stats{font-size:12px;color:var(--t2);margin-top:2px}
.corp-bar{height:6px;border-radius:3px;margin-top:6px;background:#e8e8ed;overflow:hidden}
.corp-fill{height:100%;border-radius:3px}
.corp-members{margin-top:8px;display:flex;flex-wrap:wrap;gap:4px}
.corp-member{font-size:10px;background:#f0f0f5;padding:2px 6px;border-radius:4px;color:var(--t2)}
/* Stats */
#sp{-webkit-overflow-scrolling:touch;padding:10px 0 20px}
.sc{margin:6px 10px;background:var(--cell);border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.12);padding:14px 16px}
.sc h3{font-size:13px;font-weight:700;color:var(--t2);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.sn{font-size:42px;font-weight:300;line-height:1}.sl{font-size:13px;color:var(--t2);margin-top:2px}
.sbr{display:flex;align-items:center;margin:5px 0}.sbl{width:72px;font-size:12px;color:var(--t2);flex-shrink:0}
.sbt{flex:1;height:16px;background:#e8e8ed;border-radius:8px;overflow:hidden}.sbf{height:100%;border-radius:8px;transition:width .4s}
.sbv{width:32px;text-align:right;font-size:12px;font-weight:600;margin-left:5px}
/* Detail */
.dov{position:fixed;inset:0;z-index:200;display:none;flex-direction:column}.dov.open{display:flex}
.dbk{position:absolute;inset:0;background:rgba(0,0,0,.4)}
.dsh{position:absolute;bottom:0;left:0;right:0;max-height:80vh;background:var(--linen);border-radius:12px 12px 0 0;box-shadow:0 -4px 20px rgba(0,0,0,.3);overflow-y:auto;-webkit-overflow-scrolling:touch;animation:su .25s ease-out}
@keyframes su{from{transform:translateY(100%)}to{transform:translateY(0)}}
.dhd{width:36px;height:5px;border-radius:2.5px;background:rgba(0,0,0,.15);margin:8px auto}
.dcl{position:absolute;top:8px;right:12px;width:var(--touch);height:var(--touch);display:flex;align-items:center;justify-content:center;background:none;border:none;font-size:28px;color:var(--blue);cursor:pointer}
.dhdr{padding:4px 16px 8px;text-align:center}
.dname{font-size:22px;font-weight:700}.dbio{font-size:13px;color:var(--t2);margin-top:4px;line-height:1.4}
.dsec{margin:0 10px 12px;background:var(--cell);border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.12);overflow:hidden}
.dr{display:flex;align-items:center;min-height:36px;padding:6px 14px;border-bottom:1px solid var(--brd);font-size:14px}.dr:last-child{border-bottom:none}
.drl{color:var(--t2);width:72px;flex-shrink:0;font-size:13px}.drv{flex:1;font-weight:500}
.career-tl{padding:8px 14px}
.career-seg{display:flex;align-items:center;margin:4px 0}
.career-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-right:8px}
.career-line{position:relative}
.career-line::before{content:'';position:absolute;left:4px;top:14px;bottom:-8px;width:2px;background:var(--brd)}
.career-seg:last-child .career-line::before{display:none}
.career-info{flex:1}.career-co{font-size:14px;font-weight:500}.career-yr{font-size:11px;color:var(--t2)}
.dspk{display:flex;align-items:flex-end;gap:2px;height:36px;padding:8px 14px}
.dspk-b{flex:1;background:var(--co);border-radius:2px 2px 0 0;min-height:2px;opacity:.7}
::-webkit-scrollbar{width:0}
</style>
</head>
<body>
<nav class="nav"><h1>IETF Power Map</h1><span class="sub">263 People · 25 Corps</span></nav>
<div class="tabs">
  <button class="ti on" data-t="gp"><svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="12" cy="18" r="3"/><line x1="8.5" y1="7.5" x2="10.5" y2="16" stroke="currentColor" stroke-width="1.5" fill="none"/><line x1="15.5" y1="7.5" x2="13.5" y2="16" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>Graph</button>
  <button class="ti" data-t="lp"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="3" rx="1"/><rect x="3" y="10.5" width="18" height="3" rx="1"/><rect x="3" y="17" width="18" height="3" rx="1"/></svg>People</button>
  <button class="ti" data-t="cp"><svg viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2" fill="none"/><path d="M8 7V5a4 4 0 018 0v2" stroke="currentColor" stroke-width="2" fill="none"/></svg>Corps</button>
  <button class="ti" data-t="sp"><svg viewBox="0 0 24 24"><rect x="3" y="14" width="4" height="7" rx="1"/><rect x="10" y="8" width="4" height="13" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>Stats</button>
</div>
<div class="content">
  <div id="gp" class="pnl on">
    <svg id="gsv"></svg>
    <div class="gc">
      <div class="seg" id="lctl"><button class="sb on" data-l="gov">Governance</button><button class="sb" data-l="rfc">RFC</button><button class="sb" data-l="time">Temporal</button><button class="sb" data-l="corp">Corporate</button><button class="sb" data-l="gender">Gender</button></div>
    </div>
    <div class="gl" id="leg"></div>
    <div class="tw" id="tscrub">
      <div style="font-size:10px;color:rgba(255,255,255,.5);font-weight:600;text-transform:uppercase;letter-spacing:.5px">Era Filter</div>
      <div class="tval" id="elbl">All Eras</div>
      <div class="tbc" id="ebars"></div>
      <input type="range" id="eslider" min="0" max="10" value="0" step="1">
    </div>
    <div class="gtt" id="tip"></div>
  </div>
  <div id="lp" class="pnl">
    <div class="sbw"><input type="search" class="si" placeholder="Search..." id="sinp" autocomplete="off" autocorrect="off"></div>
    <div class="lc">
      <div class="sseg" id="sctl"><button class="ss on" data-s="weight">Gov</button><button class="ss" data-s="rfc">RFCs</button><button class="ss" data-s="span">Span</button><button class="ss" data-s="combined">Power</button></div>
    </div>
    <div id="lcon"></div>
  </div>
  <div id="cp" class="pnl"><div id="ccon"></div></div>
  <div id="sp" class="pnl"><div id="scon"></div></div>
</div>
<div class="dov" id="dov"><div class="dbk" id="dbk"></div><div class="dsh"><div class="dhd"></div><button class="dcl" id="dcl">&times;</button><div class="dhdr"><div class="dname" id="dn"></div><div class="dbio" id="db"></div></div><div id="dd"></div></div></div>
<script>
''')

    out.write(f'const D={data_json};\n')

    out.write(r'''
const N=D.n.map(d=>({id:d.i,name:d.n,weight:d.w,orgs:d.o,groups:d.g,numOrgs:d.c,bio:d.b||'',
  rfcCount:d.rc||0,firstYear:d.fy,lastYear:d.ly,span:d.sp||0,decades:d.dc||{},
  career:d.cr||[],companies:d.co||[],sectors:d.sc||[],gender:d.gd||'unknown'}));
const L=D.l.map(d=>({source:d.s,target:d.t,weight:d.w,coauth:d.c||0}));
const YH=D.yh||{};
const CS=D.cs||{};
const GT=D.gt||{};
const NM=new Map(N.map(n=>[n.id,n]));

// Company color palette
const CORP_COLORS={Cisco:'#049fd9',Huawei:'#e2231a',Ericsson:'#2164aa',Juniper:'#84b135',Google:'#4285f4',Apple:'#555',Microsoft:'#00a4ef',Nokia:'#124191',Qualcomm:'#3253dc',Fastly:'#ff282d',Akamai:'#009bde','Amazon/AWS':'#ff9900',Meta:'#0668e1',Mozilla:'#e66000',Samsung:'#034ea2'};
function corpColor(companies){
  for(const c of companies){if(CORP_COLORS[c])return CORP_COLORS[c]}
  return '#666';
}

function orgColor(o){
  if(o.includes('IAB')&&o.includes('IESG'))return '#e74c3c';
  if(o.includes('IAB'))return'#c0392b';if(o.includes('IESG')||o.includes('AREA'))return'#2980b9';
  if(o.includes('IRTF-RG'))return'#27ae60';return'#7f8c8d';
}
function genderColor(g){return g==='female'?'#e91e63':g==='male'?'#3498db':'#888'}

function nR(n,layer){
  if(layer==='rfc')return Math.max(3,Math.sqrt(n.rfcCount)*1.8);
  if(layer==='time')return n.span>0?Math.max(4,n.span*.4):3;
  if(layer==='corp')return Math.max(3,Math.sqrt(n.rfcCount)*1.5);
  if(layer==='gender')return n.weight>=5?10:n.weight>=3?7:4;
  const w=n.weight;return w>=10?14:w>=8?11:w>=5?9:w>=3?7:4;
}
function nC(n,layer){
  if(layer==='rfc'){if(!n.rfcCount)return'#333';const t=Math.min(n.rfcCount/80,1);return`rgb(${44+t*187|0},${62+(1-t)*64|0},${80-t*40|0})`}
  if(layer==='time'){if(!n.firstYear)return'#333';const t=Math.min((2025-n.firstYear)/40,1);return`rgb(${46+t*185|0},${204-t*74|0},${250-t*210|0})`}
  if(layer==='corp')return n.companies.length?corpColor(n.companies):'#444';
  if(layer==='gender')return genderColor(n.gender);
  return orgColor(n.orgs);
}

// Tabs
document.querySelectorAll('.ti').forEach(t=>{t.addEventListener('click',()=>{
  document.querySelectorAll('.ti').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.pnl').forEach(p=>p.classList.remove('on'));
  t.classList.add('on');document.getElementById(t.dataset.t).classList.add('on');
  if(t.dataset.t==='gp'&&!GR)initGraph();
})});

// Detail
function showDetail(n){
  document.getElementById('dn').textContent=n.name;
  document.getElementById('db').textContent=n.bio;
  let h='<div class="dsec">';
  h+=`<div class="dr"><span class="drl">Gender</span><span class="drv"><span class="gnd ${n.gender}"></span>${n.gender}</span></div>`;
  h+=`<div class="dr"><span class="drl">Weight</span><span class="drv">${n.weight}</span></div>`;
  h+=`<div class="dr"><span class="drl">RFCs</span><span class="drv">${n.rfcCount}</span></div>`;
  if(n.firstYear)h+=`<div class="dr"><span class="drl">Active</span><span class="drv">${n.firstYear}–${n.lastYear} (${n.span}yr)</span></div>`;
  h+=`<div class="dr"><span class="drl">Bodies</span><span class="drv">${n.orgs.join(', ')}</span></div>`;
  h+=`<div class="dr"><span class="drl">Sectors</span><span class="drv">${n.sectors.join(', ')||'—'}</span></div>`;
  h+='</div>';

  // Career timeline
  if(n.career.length){
    h+='<div class="gh">Career Timeline</div><div class="dsec"><div class="career-tl">';
    n.career.forEach((seg,i)=>{
      const c=CORP_COLORS[seg.company]||'#888';
      h+=`<div class="career-seg"><div class="career-line"><div class="career-dot" style="background:${c}"></div></div><div class="career-info"><div class="career-co">${seg.company}</div><div class="career-yr">${seg.from}–${seg.to} · ${seg.rfcs} RFCs</div></div></div>`;
    });
    h+='</div></div>';
  }

  // Decade sparkline
  const dk=Object.keys(n.decades).sort();
  if(dk.length){
    const eras=['1980','1985','1990','1995','2000','2005','2010','2015','2020','2025'];
    const mx=Math.max(...Object.values(n.decades));
    h+='<div class="gh">RFC Output by Era</div><div class="dsec"><div class="dspk">';
    eras.forEach(e=>{const v=n.decades[e]||0;h+=`<div class="dspk-b" style="height:${Math.max(v/mx*100,3)}%"></div>`});
    h+='</div><div style="display:flex;justify-content:space-between;padding:0 14px 6px;font-size:9px;color:var(--t2)"><span>1980</span><span>1995</span><span>2010</span><span>2025</span></div></div>';
  }

  h+='<div class="gh">Groups</div><div class="dsec">';
  n.groups.forEach(g=>{const[org,nm]=g.split(':');h+=`<div class="dr"><span class="drl" style="width:60px"><span class="pill ${org}">${org}</span></span><span class="drv">${nm}</span></div>`});
  h+='</div>';

  document.getElementById('dd').innerHTML=h;
  document.getElementById('dov').classList.add('open');
}
document.getElementById('dbk').addEventListener('click',()=>document.getElementById('dov').classList.remove('open'));
document.getElementById('dcl').addEventListener('click',()=>document.getElementById('dov').classList.remove('open'));

// ═══════════════════════════════════════
// GRAPH
// ═══════════════════════════════════════
let GR=false,CL='gov',sim,nodeE,linkE,labE;

function updateLeg(l){
  const el=document.getElementById('leg');
  const legends={
    gov:`<div class="lr"><div class="ld" style="background:var(--iab)"></div>IAB</div><div class="lr"><div class="ld" style="background:var(--iesg)"></div>IESG/Area</div><div class="lr"><div class="ld" style="background:var(--irtf)"></div>IRTF</div><div class="lr"><div class="ld" style="background:var(--wg)"></div>WG</div>`,
    rfc:`<div class="lr"><div class="ld" style="background:#e74c3c"></div>100+ RFCs</div><div class="lr"><div class="ld" style="background:#6a5d80"></div>10+ RFCs</div><div class="lr" style="font-size:10px;opacity:.6">Size = √count</div>`,
    time:`<div class="lr"><div class="ld" style="background:rgb(231,186,40)"></div>Since 1980s</div><div class="lr"><div class="ld" style="background:rgb(46,204,250)"></div>Recent</div><div class="lr" style="font-size:10px;opacity:.6">Size = years</div>`,
    corp:`<div class="lr"><div class="ld" style="background:#049fd9"></div>Cisco</div><div class="lr"><div class="ld" style="background:#e2231a"></div>Huawei</div><div class="lr"><div class="ld" style="background:#2164aa"></div>Ericsson</div><div class="lr"><div class="ld" style="background:#4285f4"></div>Google</div><div class="lr"><div class="ld" style="background:#666"></div>Other</div>`,
    gender:`<div class="lr"><div class="ld" style="background:#3498db"></div>Male (${GT.male||0})</div><div class="lr"><div class="ld" style="background:#e91e63"></div>Female (${GT.female||0})</div><div class="lr"><div class="ld" style="background:#888"></div>Unknown (${GT.unknown||0})</div>`
  };
  el.innerHTML=legends[l]||'';
}

function setLayer(l){
  CL=l;
  document.querySelectorAll('#lctl .sb').forEach(b=>b.classList.toggle('on',b.dataset.l===l));
  document.getElementById('tscrub').classList.toggle('vis',l==='time');
  updateLeg(l);
  if(!nodeE)return;
  nodeE.select('circle').transition().duration(350)
    .attr('r',d=>nR(d,l)).attr('fill',d=>nC(d,l))
    .attr('stroke',d=>{
      if(l==='corp'&&d.companies.length)return'rgba(255,255,255,.25)';
      if(l==='gender')return'rgba(255,255,255,.2)';
      return d.weight>=8?'rgba(255,255,255,.4)':'rgba(255,255,255,.1)';
    });
  linkE.transition().duration(350)
    .attr('stroke',d=>{
      if(l==='corp'&&d.coauth)return'rgba(230,126,34,.3)';
      return d.coauth?'rgba(230,126,34,.2)':'rgba(100,130,180,.1)';
    })
    .attr('stroke-dasharray',d=>d.coauth?'4,3':'none')
    .attr('opacity',d=>{if(l==='rfc')return d.coauth?.7:.1;return d.coauth?.35:.25});
  labE.text(d=>{
    if(l==='rfc'&&d.rfcCount>=30)return d.name.split(' ').pop();
    if(l==='time'&&d.span>=20)return d.name.split(' ').pop();
    if(l==='corp'&&d.rfcCount>=20)return d.name.split(' ').pop();
    if(l==='gender'&&d.weight>=5)return d.name.split(' ').pop();
    if(l==='gov'&&d.weight>=5)return d.name.split(' ').pop();
    return'';
  });
  sim.force('collision',d3.forceCollide(d=>nR(d,l)+3));
  sim.alpha(.12).restart();
}

function initGraph(){
  GR=true;const ct=document.getElementById('gp');
  const svg=d3.select('#gsv');const W=ct.clientWidth,H=ct.clientHeight;
  svg.attr('viewBox',[0,0,W,H]);
  const defs=svg.append('defs');
  const gr=defs.append('radialGradient').attr('id','bg');
  gr.append('stop').attr('offset','0%').attr('stop-color','#252840');
  gr.append('stop').attr('offset','100%').attr('stop-color','#0f1019');
  svg.append('rect').attr('width',W).attr('height',H).attr('fill','url(#bg)');
  const glow=defs.append('filter').attr('id','gl');
  glow.append('feGaussianBlur').attr('stdDeviation','3').attr('result','b');
  const mg=glow.append('feMerge');mg.append('feMergeNode').attr('in','b');mg.append('feMergeNode').attr('in','SourceGraphic');

  const vis=N.filter(n=>n.weight>=1||n.rfcCount>=3);
  const vids=new Set(vis.map(n=>n.id));
  const vlinks=L.filter(l=>vids.has(l.source)&&vids.has(l.target));

  sim=d3.forceSimulation(vis)
    .force('link',d3.forceLink(vlinks).id(d=>d.id).distance(80).strength(d=>Math.min(d.weight*.1,.6)))
    .force('charge',d3.forceManyBody().strength(d=>-35-d.weight*10-d.rfcCount*.4))
    .force('center',d3.forceCenter(W/2,H/2))
    .force('collision',d3.forceCollide(d=>nR(d,'gov')+3))
    .force('x',d3.forceX(W/2).strength(.02))
    .force('y',d3.forceY(H/2).strength(.02));

  const g=svg.append('g');
  linkE=g.append('g').selectAll('line').data(vlinks).join('line')
    .attr('stroke',d=>d.coauth?'rgba(230,126,34,.2)':'rgba(100,130,180,.12)')
    .attr('stroke-width',d=>Math.min(d.weight*.7,3))
    .attr('stroke-dasharray',d=>d.coauth?'4,3':'none');

  nodeE=g.append('g').selectAll('g').data(vis).join('g').style('cursor','pointer')
    .call(d3.drag()
      .on('start',(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y})
      .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y})
      .on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}));

  nodeE.append('circle')
    .attr('r',d=>nR(d,'gov')).attr('fill',d=>orgColor(d.orgs))
    .attr('stroke',d=>d.weight>=8?'rgba(255,255,255,.4)':'rgba(255,255,255,.1)')
    .attr('stroke-width',d=>d.weight>=8?2:1)
    .attr('filter',d=>d.weight>=8?'url(#gl)':null);

  labE=nodeE.append('text').text(d=>d.weight>=5?d.name.split(' ').pop():'')
    .attr('dy',d=>nR(d,'gov')+11).attr('text-anchor','middle')
    .attr('fill','rgba(255,255,255,.65)').attr('font-size','9px').attr('font-weight','500').attr('pointer-events','none');

  const tip=document.getElementById('tip');
  nodeE.on('mouseover',(e,d)=>{
    let txt=`${d.name}`;
    if(CL==='corp'&&d.companies.length)txt+=` · ${d.companies[0]}`;
    else if(CL==='rfc')txt+=` · ${d.rfcCount} RFCs`;
    else if(CL==='gender')txt+=` · ${d.gender}`;
    else txt+=` · ${d.orgs.join('/')}`;
    tip.style.display='block';tip.textContent=txt;
  }).on('mousemove',e=>{
    const r=ct.getBoundingClientRect();
    tip.style.left=(e.clientX-r.left+10)+'px';tip.style.top=(e.clientY-r.top-28)+'px';
  }).on('mouseout',()=>tip.style.display='none')
    .on('click',(e,d)=>{tip.style.display='none';showDetail(d)});

  svg.call(d3.zoom().scaleExtent([.3,5]).on('zoom',e=>g.attr('transform',e.transform)));
  sim.on('tick',()=>{
    linkE.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
    nodeE.attr('transform',d=>`translate(${d.x},${d.y})`);
  });

  updateLeg('gov');
  document.querySelectorAll('#lctl .sb').forEach(b=>b.addEventListener('click',()=>setLayer(b.dataset.l)));

  // Era slider
  const eras=['All','1980–84','1985–89','1990–94','1995–99','2000–04','2005–09','2010–14','2015–19','2020–24','2025+'];
  const eStarts=[0,1980,1985,1990,1995,2000,2005,2010,2015,2020,2025];
  const yk=['1980','1985','1990','1995','2000','2005','2010','2015','2020','2025'];
  const mxY=Math.max(...yk.map(k=>YH[k]||0));
  const bel=document.getElementById('ebars');
  yk.forEach((k,i)=>{const b=document.createElement('div');b.className='tb';b.style.height=Math.max((YH[k]||0)/mxY*100,5)+'%';b.dataset.idx=i+1;bel.appendChild(b)});

  document.getElementById('eslider').addEventListener('input',function(){
    const i=+this.value;document.getElementById('elbl').textContent=eras[i];
    bel.querySelectorAll('.tb').forEach(b=>b.classList.toggle('act',i===0||+b.dataset.idx===i));
    if(i===0){nodeE.select('circle').transition().duration(250).attr('opacity',1);linkE.transition().duration(250).attr('opacity',d=>d.coauth?.3:.2)}
    else{const s=eStarts[i];nodeE.select('circle').transition().duration(250).attr('opacity',d=>{if(!d.firstYear)return.06;return(d.decades[String(s)]||0)>0?1:.06});linkE.transition().duration(250).attr('opacity',.03)}
  });
}

// ═══════════════════════════════════════
// LIST
// ═══════════════════════════════════════
let CS_='weight';
function sortN(m){const s=[...N];
  if(m==='rfc')s.sort((a,b)=>b.rfcCount-a.rfcCount||b.weight-a.weight);
  else if(m==='span')s.sort((a,b)=>b.span-a.span||b.rfcCount-a.rfcCount);
  else if(m==='combined')s.sort((a,b)=>(b.weight*3+b.rfcCount+b.span*.5)-(a.weight*3+a.rfcCount+a.span*.5));
  else s.sort((a,b)=>b.weight-a.weight||b.numOrgs-a.numOrgs);return s}

function renderList(f=''){
  const lc=f.toLowerCase(),so=sortN(CS_),fl=lc?so.filter(n=>n.name.toLowerCase().includes(lc)||n.companies.some(c=>c.toLowerCase().includes(lc))):so;
  const td=CS_==='rfc'?[{l:'50+ RFCs',f:n=>n.rfcCount>=50},{l:'20+ RFCs',f:n=>n.rfcCount>=20&&n.rfcCount<50},{l:'5+ RFCs',f:n=>n.rfcCount>=5&&n.rfcCount<20},{l:'< 5 RFCs',f:n=>n.rfcCount<5}]
    :CS_==='span'?[{l:'25yr+',f:n=>n.span>=25},{l:'15yr+',f:n=>n.span>=15&&n.span<25},{l:'5yr+',f:n=>n.span>=5&&n.span<15},{l:'Recent',f:n=>n.span<5}]
    :CS_==='combined'?[{l:'Apex',f:n=>(n.weight*3+n.rfcCount+n.span*.5)>=60},{l:'Major',f:n=>{const s=n.weight*3+n.rfcCount+n.span*.5;return s>=20&&s<60}},{l:'Active',f:n=>{const s=n.weight*3+n.rfcCount+n.span*.5;return s>=5&&s<20}},{l:'Peripheral',f:n=>(n.weight*3+n.rfcCount+n.span*.5)<5}]
    :[{l:'Cross-Body',f:n=>n.weight>=10},{l:'Core',f:n=>n.weight>=5&&n.weight<10},{l:'Research/WG',f:n=>n.weight>=3&&n.weight<5},{l:'WG Chair',f:n=>n.weight<3}];
  let h='',rk=1;
  td.forEach(t=>{const tn=fl.filter(t.f);if(!tn.length)return;
    h+=`<div class="gh">${t.l} (${tn.length})</div><div class="tg">`;
    tn.forEach(n=>{
      const pills=n.orgs.map(o=>`<span class="pill ${o}">${o}</span>`).join('');
      const co=n.companies.length?n.companies[0]:'';
      const sp=n.span>0?`${n.firstYear}–${n.lastYear}`:'';
      h+=`<div class="cl" data-id="${n.id}"><div class="cr">${rk}</div><div class="cb"><div class="cn"><span class="gnd ${n.gender}"></span>${n.name}</div><div class="cd">${co}${co&&sp?' · ':''}${sp}</div><div class="op">${pills}</div></div><div class="cbs">${n.rfcCount?`<span class="wb rfc">${n.rfcCount}</span>`:''}<span class="wb gov">${n.weight}</span></div></div>`;
      rk++});h+='</div>'});
  document.getElementById('lcon').innerHTML=h;
  document.querySelectorAll('.cl[data-id]').forEach(c=>c.addEventListener('click',()=>{const n=NM.get(c.dataset.id);if(n)showDetail(n)}));
}
document.getElementById('sinp').addEventListener('input',e=>renderList(e.target.value));
document.querySelectorAll('#sctl .ss').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('#sctl .ss').forEach(x=>x.classList.remove('on'));
  b.classList.add('on');CS_=b.dataset.s;renderList(document.getElementById('sinp').value)}));
renderList();

// ═══════════════════════════════════════
// CORPORATE PANEL
// ═══════════════════════════════════════
function renderCorps(){
  const sorted=Object.entries(CS).sort((a,b)=>(b[1].people*3+b[1].rfcs+b[1].gov_weight*2)-(a[1].people*3+a[1].rfcs+a[1].gov_weight*2));
  const mxR=Math.max(...sorted.map(([,s])=>s.rfcs));
  let h='<div class="gh">Corporate Influence Index</div>';
  sorted.forEach(([name,s])=>{
    const c=CORP_COLORS[name]||'#888';
    const pct=(s.rfcs/mxR*100).toFixed(0);
    const members=s.members.map(id=>NM.get(id)).filter(Boolean).sort((a,b)=>b.rfcCount-a.rfcCount);
    h+=`<div class="corp-card" data-corp="${name}">`;
    h+=`<div class="corp-name" style="color:${c}">${name}</div>`;
    h+=`<div class="corp-stats">${s.people} people · ${s.rfcs} RFCs authored · ${s.gov_weight} governance weight</div>`;
    h+=`<div class="corp-bar"><div class="corp-fill" style="width:${pct}%;background:${c}"></div></div>`;
    h+=`<div class="corp-members">`;
    members.slice(0,8).forEach(m=>{h+=`<span class="corp-member" data-id="${m.id}">${m.name.split(' ').pop()} (${m.rfcCount})</span>`});
    if(members.length>8)h+=`<span class="corp-member">+${members.length-8}</span>`;
    h+='</div></div>';
  });
  h+=`<div style="padding:12px 16px;font-size:11px;color:var(--t2);text-align:center">Affiliations extracted from RFC author metadata<br>Reflects declared employer at time of publication</div>`;
  document.getElementById('ccon').innerHTML=h;
  document.querySelectorAll('.corp-member[data-id]').forEach(el=>el.addEventListener('click',e=>{
    e.stopPropagation();const n=NM.get(el.dataset.id);if(n)showDetail(n)}));
}
renderCorps();

// ═══════════════════════════════════════
// STATS
// ═══════════════════════════════════════
function renderStats(){
  const wR=N.filter(n=>n.rfcCount>0);const tR=N.reduce((s,n)=>s+n.rfcCount,0);
  const multi=N.filter(n=>n.numOrgs>=2);
  const oc={};N.forEach(n=>n.orgs.forEach(o=>oc[o]=(oc[o]||0)+1));const mO=Math.max(...Object.values(oc));
  let h='<div style="display:flex;gap:5px;padding:0 10px;flex-wrap:wrap">';
  h+=`<div class="sc" style="flex:1;min-width:80px;text-align:center"><div class="sn">${N.length}</div><div class="sl">People</div></div>`;
  h+=`<div class="sc" style="flex:1;min-width:80px;text-align:center"><div class="sn">${tR}</div><div class="sl">RFC authorships</div></div>`;
  h+=`<div class="sc" style="flex:1;min-width:80px;text-align:center"><div class="sn">${Object.keys(CS).length}</div><div class="sl">Companies</div></div>`;
  h+='</div>';

  // Gender
  h+=`<div class="sc"><h3>Gender (name-inferred)</h3>`;
  const gd=[['Male',GT.male||0,'#3498db'],['Female',GT.female||0,'#e91e63'],['Unresolved',GT.unknown||0,'#999']];
  const mG=Math.max(...gd.map(g=>g[1]));
  gd.forEach(([l,c,cl])=>h+=`<div class="sbr"><span class="sbl">${l}</span><div class="sbt"><div class="sbf" style="width:${c/mG*100}%;background:${cl}"></div></div><span class="sbv">${c}</span></div>`);
  h+=`<p style="font-size:11px;color:var(--t2);margin-top:6px">⚠ Inferred from first names. ~51% unresolved (non-Western names, initials). Of resolved: ${((GT.female||0)/((GT.male||0)+(GT.female||0))*100).toFixed(1)}% female.</p></div>`;

  // Governance bodies
  h+='<div class="sc"><h3>By Body</h3>';
  ['IETF-WG','IRTF-RG','AREA','IESG','IAB'].forEach(o=>{
    const c=oc[o]||0;const colors={'IAB':'var(--iab)','IESG':'var(--iesg)','AREA':'var(--area)','IRTF-RG':'var(--irtf)','IETF-WG':'var(--wg)'};
    const labels={'IAB':'IAB','IESG':'IESG','AREA':'Area Dir','IRTF-RG':'IRTF RG','IETF-WG':'WG Chair'};
    h+=`<div class="sbr"><span class="sbl">${labels[o]}</span><div class="sbt"><div class="sbf" style="width:${c/mO*100}%;background:${colors[o]}"></div></div><span class="sbv">${c}</span></div>`;
  });h+='</div>';

  // Sector
  const sectors={industry:0,academic:0,independent:0,'standards-body':0};
  N.forEach(n=>n.sectors.forEach(s=>sectors[s]=(sectors[s]||0)+1));
  const mS=Math.max(...Object.values(sectors));
  h+='<div class="sc"><h3>Sectors (from affiliations)</h3>';
  [['Industry',sectors.industry,'#2980b9'],['Academic',sectors.academic,'#27ae60'],['Independent',sectors.independent,'#95a5a6'],['Standards Body',sectors['standards-body'],'#8e44ad']].forEach(([l,c,cl])=>{
    if(c)h+=`<div class="sbr"><span class="sbl">${l}</span><div class="sbt"><div class="sbf" style="width:${c/mS*100}%;background:${cl}"></div></div><span class="sbv">${c}</span></div>`;
  });
  h+=`<p style="font-size:11px;color:var(--t2);margin-top:6px">Based on top 100 RFC authors with 5+ RFCs. Many individuals span multiple sectors across their careers.</p></div>`;

  h+=`<div class="sc" style="text-align:center"><p style="font-size:11px;color:var(--t2)">Data: IETF Datatracker API (live fetch)<br>RFC dates: number→year interpolation<br>Gender: first-name inference (high uncertainty)<br>Affiliations: declared in RFC metadata</p></div>`;

  document.getElementById('scon').innerHTML=h;
}
renderStats();
initGraph();
</script></body></html>
''')

import os
print(f"Final: {os.path.getsize('/home/claude/ietf_v3.html')/1024:.1f}KB")
