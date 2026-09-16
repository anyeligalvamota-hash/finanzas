from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<style id="finanza-v2-css">.*?</style>\s*','',s,count=1,flags=re.S)
s=re.sub(r'<script id="finanza-v2-js">.*?</script>\s*','',s,count=1,flags=re.S)

css=r'''<style id="finanza-v2-css">
.budget-overview{display:grid!important;grid-template-columns:1fr!important;gap:0!important;margin-bottom:14px!important}
.budget-stat{min-height:72px!important;padding:13px 12px!important;border:1px solid var(--line)!important;border-radius:18px!important;background:var(--paper)!important;box-shadow:none!important}
.budget-stat b{font-size:18px!important;color:var(--ink)!important}.budget-stat span{font-size:9px;color:var(--muted);font-weight:900}
.budget-stat .muted{font-size:9px;margin-top:3px}.budget-category-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.budget-category-card{padding:13px!important}.finanza-chart-legend,.debt-percent-legend{display:grid;gap:7px;max-height:130px;overflow:auto}
.debt-percent-row{display:grid;grid-template-columns:10px 1fr auto;align-items:center;gap:7px;font-size:10px;color:var(--muted)}
.debt-percent-row i{width:9px;height:9px;border-radius:50%;display:block}
#finanzaDebtChart{height:190px!important;max-height:190px!important}
.finanza-payment-manager{margin-top:14px}.finanza-payment-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}
.finanza-payment-row:last-child{border-bottom:0}.finanza-payment-main strong{display:block;font-size:12px}.finanza-payment-main small{display:block;color:var(--muted);font-size:10px;margin-top:3px}
.finanza-payment-actions{display:flex;gap:7px;align-items:center}.finanza-delete{background:#f7e2e2!important;color:#a25b5e!important}
.finanza-notify-toast{position:fixed;right:18px;bottom:18px;z-index:9999;width:min(380px,calc(100vw - 36px));padding:13px 15px;border:1px solid var(--line);border-radius:16px;background:var(--paper);box-shadow:0 18px 45px rgba(60,40,35,.18)}
.finanza-notify-banner{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 14px;border:1px solid var(--line);border-radius:16px;background:var(--paper);margin-bottom:12px}
.nav-mobile-label{display:none}
@media(max-width:1000px){.budget-category-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){
 .budget-stat{min-height:68px!important;padding:11px 10px!important}.budget-stat b{font-size:17px!important}.budget-category-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
 .grid .metric .value,.grid .metric .amount,.grid .metric b{color:var(--ink)!important}
 .nav-desktop-label{display:none}.nav-mobile-label{display:inline}.finanza-payment-row{align-items:flex-start}.finanza-payment-actions{flex-direction:column}.finanza-notify-banner{align-items:flex-start;flex-direction:column}
}
</style>'''

js=r'''<script id="finanza-v2-js">
function finanzaV2Money(n){try{return new Intl.NumberFormat(db?.language||'es',{minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(n)||0)}catch(e){return (Number(n)||0).toFixed(2)}}
function finanzaV2Color(v,f){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()||f}
function finanzaV2Donut(c,labels,vals,legendId){
 if(!c)return;const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2),w=Math.max(300,r.width||300),h=Math.max(180,r.height||180);c.width=w*d;c.height=h*d;
 const x=c.getContext('2d');x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,w,h);const total=vals.reduce((a,v)=>a+v,0),cs=[finanzaV2Color('--rose','#dba8a1'),finanzaV2Color('--gold','#b99460'),finanzaV2Color('--green','#789b83'),'#9b8fb1','#8aa6a3','#c58d76','#7e91ad','#aa9b78'];let lg=document.getElementById(legendId);
 if(!total){x.fillStyle=finanzaV2Color('--muted','#8a7e79');x.textAlign='center';x.font='12px sans-serif';x.fillText('Sin datos registrados',w/2,h/2);if(lg)lg.innerHTML='<div class="notice">No hay datos registrados.</div>';return}
 const cx=Math.min(88,w*.23),cy=h/2,rad=Math.min(64,h/2-12),inn=rad*.57;let a=-Math.PI/2;
 vals.forEach((v,i)=>{if(v<=0)return;const z=v/total*Math.PI*2;x.beginPath();x.arc(cx,cy,rad,a,a+z);x.lineWidth=24;x.strokeStyle=cs[i%cs.length];x.stroke();a+=z});
 x.beginPath();x.arc(cx,cy,inn,0,Math.PI*2);x.fillStyle=finanzaV2Color('--paper','#fffdfc');x.fill();x.fillStyle=finanzaV2Color('--ink','#302b2a');x.textAlign='center';x.font='900 12px sans-serif';x.fillText('100%',cx,cy+4);
 if(lg)lg.innerHTML=labels.map((q,i)=>vals[i]>0?`<div class="debt-percent-row"><i style="background:${cs[i%cs.length]}"></i><span>${q}</span><b>${(vals[i]/total*100).toFixed(1)}%</b></div>`:'').join('')
}
function renderDebtChart(){const c=document.getElementById('finanzaDebtChart');if(!c||!db)return;const gs=['Préstamos','Tarjetas','Otros'],vs=gs.map(g=>(db.debts||[]).filter(d=>String(d.group||'Otros')===g).reduce((a,d)=>a+Math.max(0,eqBase(debtBalance(d),d.currency)),0));finanzaV2Donut(c,gs,vs,'debtPercentLegend')}
function renderExpenseCategoryChartV2(){
 const c=['finanzaCategoryChart','expenseCategoryChart','finanzaExpenseCategoryChart'].map(id=>document.getElementById(id)).find(Boolean)||[...document.querySelectorAll('canvas')].find(q=>((q.closest('.card,.dash-panel,.panel,.section')||q.parentElement)?.innerText||'').toLowerCase().includes('gastos por categor'));
 if(!c||!db)return;const cur=db.expenseSummaryCurrency||db.baseCurrency,m=today().slice(0,7),map={};(db.transactions||[]).filter(t=>t.type==='Gasto'&&String(t.date||'').startsWith(m)).forEach(t=>{const k=t.category||'Otros';map[k]=(map[k]||0)+convert(t.amount,t.currency,cur)});const e=Object.entries(map).sort((a,b)=>b[1]-a[1]).slice(0,8);finanzaV2Donut(c,e.map(x=>x[0]),e.map(x=>x[1]),'finanzaExpenseLegend')
}
function budgetMonthlyTotalV2(cur,m){const h=db.budgetHistory?.[m];if(h&&Number.isFinite(Number(h.total)))return h.currency&&h.currency!==cur?convert(h.total,h.currency,cur):Number(h.total)||0;return m===today().slice(0,7)?Object.values(db.budgets||{}).reduce((a,v)=>a+(Number(v)||0),0):0}
function budgetMonthlySpentV2(cur,m){return(db.transactions||[]).filter(t=>(t.type==='Gasto'||t.type==='Pago de deuda')&&String(t.date||'').startsWith(m)).reduce((a,t)=>a+convert(t.amount,t.currency,cur),0)}
function renderBudgetVsSpentChart(cur){
 const c=document.getElementById('finanzaBudgetChart');if(!c||!db)return;cur=cur||db.budgetCurrency||db.baseCurrency;const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2),w=Math.max(360,r.width||360),h=Math.max(220,r.height||220);c.width=w*d;c.height=h*d;const x=c.getContext('2d');x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,w,h);
 const ms=[];for(let i=-5;i<=0;i++){let z=new Date();z.setDate(1);z.setMonth(z.getMonth()+i);ms.push({k:z.toISOString().slice(0,7),l:z.toLocaleDateString(db?.language||'es',{month:'short'}).replace('.','')})}
 const v=ms.map(m=>({b:budgetMonthlyTotalV2(cur,m.k),s:budgetMonthlySpentV2(cur,m.k)})),mx=Math.max(1,...v.flatMap(q=>[q.b,q.s])),L=36,R=12,T=30,B=38,cw=w-L-R,ch=h-T-B,gw=cw/ms.length,bw=Math.max(9,Math.min(18,gw*.25));x.font='700 9px sans-serif';x.textAlign='center';
 v.forEach((q,i)=>{const xx=L+gw*i+gw/2,bh=q.b/mx*ch,sh=q.s/mx*ch;x.fillStyle=finanzaV2Color('--rose2','#f0e2df');if(bh){x.beginPath();x.roundRect(xx-bw-2,T+ch-bh,bw,bh,4);x.fill()}x.fillStyle=finanzaV2Color('--rose','#dba8a1');if(sh){x.beginPath();x.roundRect(xx+2,T+ch-sh,bw,sh,4);x.fill()}x.fillStyle=finanzaV2Color('--muted','#8a7e79');x.fillText(ms[i].l,xx,T+ch+17)});
 x.textAlign='left';x.font='800 9px sans-serif';x.fillStyle=finanzaV2Color('--rose2','#f0e2df');x.fillRect(L,8,9,9);x.fillStyle=finanzaV2Color('--ink','#302b2a');x.fillText('Presupuesto',L+14,16);x.fillStyle=finanzaV2Color('--rose','#dba8a1');x.fillRect(L+92,8,9,9);x.fillStyle=finanzaV2Color('--ink','#302b2a');x.fillText('Gastado',L+106,16)
}
function budget(){
 const m=today().slice(0,7),cur=db.budgetCurrency||db.baseCurrency,total=Object.values(db.budgets||{}).reduce((a,v)=>a+(Number(v)||0),0),spent=budgetMonthlySpentV2(cur,m),pct=total?spent/total*100:0;
 const cards=Object.entries(db.budgets||{}).map(([n,lim])=>{const used=(db.transactions||[]).filter(t=>(t.type==='Gasto'||t.type==='Pago de deuda')&&String(t.date||'').startsWith(m)&&t.category===n).reduce((a,t)=>a+convert(t.amount,t.currency,cur),0),p=Number(lim)?used/Number(lim)*100:0;return `<div class="budget-category-card"><div class="budget-name">${n}</div><div class="budget-number">${finanzaV2Money(lim)}</div><div class="budget-meta">Gastado: ${finanzaV2Money(used)} · ${p.toFixed(0)}%</div><div class="budget-bar"><i class="${p>100?'over':''}" style="width:${Math.min(100,p)}%"></i></div></div>`}).join('');
 $('content').innerHTML=`<div class="budget-overview"><div class="budget-stat"><span>Presupuesto total del mes</span><b>${finanzaV2Money(total)}</b><div class="muted">Categorías</div></div><div class="budget-stat"><span>Gastado este mes</span><b>${finanzaV2Money(spent)}</b><div class="muted">Gastos + pagos registrados</div></div><div class="budget-stat"><span>Ejecución</span><b>${pct.toFixed(0)}%</b><div class="muted">${pct>100?'Exceso '+(pct-100).toFixed(0)+'%':(100-pct).toFixed(0)+'% disponible'}</div></div><div class="budget-stat"><span>Disponible del presupuesto</span><b>${finanzaV2Money(Math.max(0,total-spent))}</b><div class="budget-bar"><i class="${pct>100?'over':''}" style="width:${Math.min(100,pct)}%"></i></div></div></div><div class="card"><div class="section-head"><div><h2>Presupuesto mensual</h2><div class="muted">Moneda: ${cur}. Las cuotas y responsabilidades se gestionan desde Pagos.</div></div><div style="display:flex;gap:7px;flex-wrap:wrap"><select class="btn" onchange="setBudgetCurrency(this.value)">${currencyCodes().map(c=>`<option value="${c}" ${c===cur?'selected':''}>${c} · ${currencyName(c)}</option>`).join('')}</select><button class="btn" onclick="addBudgetCategory()">＋ Categoría</button><button class="btn rose" onclick="editBudget()">Editar</button></div></div><div class="budget-category-grid">${cards||'<div class="success">No tienes categorías de presupuesto.</div>'}</div></div>`
}
function finanzaDeletePaymentV2(id){const p=(db.payments||[]).find(q=>q.id===id);if(!p)return;if(!confirm(`¿Eliminar la responsabilidad de pago “${p.name}”?`))return;db.payments=(db.payments||[]).filter(q=>q.id!==id);save();finanzaToastV2('Responsabilidad eliminada',p.name);render()}
function finanzaPaymentManagerV2(){if(!db||!Array.isArray(db.payments))return;const c=document.getElementById('content');if(!c)return;document.getElementById('finanzaPaymentManagerV2')?.remove();const w=document.createElement('div');w.id='finanzaPaymentManagerV2';w.className='card finanza-payment-manager';const rows=db.payments.map(p=>`<div class="finanza-payment-row"><div class="finanza-payment-main"><strong>${p.name||'Responsabilidad'}</strong><small>${p.dueDate?'Vence: '+p.dueDate+' · ':''}${p.frequency||''} · ${money(p.amount,p.currency)}</small></div><div class="finanza-payment-actions"><span class="badge ${p.active===false?'bad':'good'}">${p.active===false?'Inactiva':'Activa'}</span><button class="btn small finanza-delete" onclick="finanzaDeletePaymentV2(${JSON.stringify(p.id)})">Eliminar</button></div></div>`).join('');w.innerHTML=`<div class="section-head"><div><h2>Responsabilidades de pago</h2><div class="muted">Puedes eliminar una responsabilidad sin borrar la deuda ni los movimientos históricos.</div></div></div>${rows||'<div class="notice">No hay responsabilidades de pago registradas.</div>'}`;c.appendChild(w)}
function finanzaToastV2(t,b){document.querySelector('.finanza-notify-toast')?.remove();const e=document.createElement('div');e.className='finanza-notify-toast';e.innerHTML=`<strong>${t}</strong><div class="muted" style="margin-top:4px">${b||''}</div>`;document.body.appendChild(e);setTimeout(()=>e.remove(),6500)}
function finanzaBrowserNotifyV2(t,b){try{if('Notification' in window&&Notification.permission==='granted')new Notification(t,{body:b,icon:'/icon.svg'})}catch(e){}}
async function finanzaRequestNotificationsV2(){if(!('Notification' in window))return false;if(Notification.permission==='granted')return true;if(Notification.permission==='denied')return false;try{return(await Notification.requestPermission())==='granted'}catch(e){return false}}
function finanzaCheckNotificationsV2(){
 if(!db)return;const now=Date.now(),sig=(db.transactions||[]).map(t=>t.id+':'+t.date+':'+t.amount).sort().join('|'),st=JSON.parse(localStorage.getItem('finanzaActivityV2')||'{}');
 if(st.sig!==sig){st.sig=sig;st.last=now;st.sent8=false;st.sent24=false;localStorage.setItem('finanzaActivityV2',JSON.stringify(st))}
 const h=(now-Number(st.last||now))/3600000;if(h>=8&&!st.sent8){st.sent8=true;localStorage.setItem('finanzaActivityV2',JSON.stringify(st));finanzaToastV2('Más de 8 horas sin movimientos','Registra tus gastos, ingresos o pagos.');finanzaBrowserNotifyV2('Más de 8 horas sin movimientos','Registra tus gastos, ingresos o pagos.')}
 if(h>=24&&!st.sent24){st.sent24=true;localStorage.setItem('finanzaActivityV2',JSON.stringify(st));finanzaToastV2('1 día sin movimientos','Revisa y actualiza tus finanzas.');finanzaBrowserNotifyV2('1 día sin movimientos','Revisa y actualiza tus finanzas.')}
 const d=today().slice(0,10);(db.payments||[]).filter(p=>p.active!==false&&p.dueDate===d).forEach(p=>{const k='finanzaPayV2-'+p.id+'-'+d;if(!localStorage.getItem(k)){localStorage.setItem(k,'1');finanzaToastV2('Fecha de pago','Hoy vence '+p.name);finanzaBrowserNotifyV2('Fecha de pago','Hoy vence '+p.name)}})
}
function finanzaPostV2(){
 try{renderBudgetVsSpentChart(db?.budgetCurrency||db?.baseCurrency);renderDebtChart();renderExpenseCategoryChartV2();if(window.__finanzaV2Page==='Pagos')finanzaPaymentManagerV2();if(window.__finanzaV2Page==='Configuración'&&!document.getElementById('finanzaV2NotifyBanner')){const c=document.getElementById('content'),b=document.createElement('div');if(c){b.id='finanzaV2NotifyBanner';b.className='finanza-notify-banner';b.innerHTML='<div><strong>Notificaciones</strong><div class="muted">Fechas de pago, actividad y recordatorios de movimientos.</div></div><button class="btn rose" id="finanzaV2NotifyBtn">Activar</button>';c.prepend(b);b.querySelector('button').onclick=async()=>finanzaToastV2((await finanzaRequestNotificationsV2())?'Notificaciones activadas':'Permiso no activado','Puedes cambiar el permiso desde el navegador.')}}
  [...document.querySelectorAll('.nav button')].forEach(b=>{const s=[...b.querySelectorAll('span')].find(x=>(x.textContent||'').trim()==='Deudas');if(s&&!b.dataset.v2){const o=b.getAttribute('onclick')||'go("Deudas")';b.dataset.v2='1';s.innerHTML='<span class="nav-desktop-label">Deudas</span><span class="nav-mobile-label">Presupuesto</span>';b.setAttribute('onclick',`if(innerWidth<=650){go('Presupuesto')}else{${o}}`)}})
 }catch(e){console.warn('Finanza V2',e)}
}
if(!window.__finanzaV2Installed){window.__finanzaV2Installed=true;const g=go;window.go=function(p,push=true){window.__finanzaV2Page=p;const r=g(p,push);setTimeout(finanzaPostV2,80);setTimeout(finanzaPostV2,350);return r};setTimeout(finanzaPostV2,600);setInterval(finanzaCheckNotificationsV2,60000);setTimeout(finanzaCheckNotificationsV2,2000);window.addEventListener('resize',()=>setTimeout(finanzaPostV2,100))}
window.finanzaRequestNotifications=finanzaRequestNotificationsV2;
</script>'''

s=s.replace('</head>',css+'</head>',1)
s=s.replace('</body></html>',js+'</body></html>',1)
p.write_text(s,encoding='utf-8')
print('patched',p.stat().st_size)
