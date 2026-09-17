from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'<style id="finanza-v5-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-js">.*?</script>\s*','',s,flags=re.S)

css=r'''<style id="finanza-v5-css">
/* V5: navegación, encabezado, pagos, cuentas y gráficos */
#finanzaUserSpace{margin:0 8px 16px;padding:11px 10px;border:1px solid var(--line);border-radius:15px;background:var(--paper)}
#finanzaUserSpace strong{display:block;font-size:13px}#finanzaUserSpace small{display:block;font-size:9px;color:var(--muted);margin-top:2px}
.top .hello{display:none!important}.top .brand-inline{display:none!important}
#finanzaTopActions{display:flex;gap:8px;align-items:center;margin-left:auto}.finanza-action-hidden{display:none!important}
.finanza-page-cuentas .card,.finanza-page-cuentas .panel{padding:11px!important;border-radius:15px!important}.finanza-page-cuentas .card h2,.finanza-page-cuentas .panel h2{font-size:15px!important}.finanza-page-cuentas .amount,.finanza-page-cuentas .account-balance{font-size:19px!important}.finanza-page-cuentas .muted,.finanza-page-cuentas small{font-size:9px!important}.finanza-page-cuentas .row{padding:8px 0!important}
.finanza-payment-manager{margin-top:14px!important}.finanza-payment-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}.finanza-payment-row:last-child{border-bottom:0}.finanza-payment-main strong{display:block;font-size:12px}.finanza-payment-main small{display:block;color:var(--muted)!important;font-size:10px;margin-top:3px}.finanza-payment-actions{display:flex;gap:7px}.finanza-payment-actions .btn{font-size:10px!important;padding:7px 10px!important}.finanza-delete{background:#EAD8D2!important}.finanza-edit{background:var(--rose2)!important}
.finanza-legacy-payments{display:none!important}.finanza-hide-copy{display:none!important}
.floating{font-size:0!important;width:54px!important;height:54px!important;background:var(--cocoa)!important;color:#fff!important}.floating::after{content:'+';font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:31px;font-weight:400;line-height:54px;display:block;text-align:center}
.finanza-history-shell{height:310px!important;min-height:310px!important}.finanza-history-shell canvas{height:280px!important;max-height:280px!important}.finanza-debt-shell{height:300px!important;min-height:300px!important}.finanza-debt-shell canvas{height:230px!important;max-height:230px!important}
@media(max-width:650px){.top .brand-inline{display:none!important}.top{min-height:34px!important}.finanza-page-cuentas .card,.finanza-page-cuentas .panel{padding:10px!important}.finanza-payment-row{align-items:flex-start}.finanza-payment-actions{flex-wrap:wrap;justify-content:flex-end}.finanza-history-shell{height:290px!important;min-height:290px!important}.finanza-history-shell canvas{height:255px!important;max-height:255px!important}.finanza-debt-shell{height:285px!important;min-height:285px!important}}
</style>'''

js=r'''<script id="finanza-v5-js">
(function(){
const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
const n=v=>Number(v)||0;
function activePage(){
 const a=document.querySelector('.nav button.active,.nav a.active,.bottom-nav button.active,.mobile-nav button.active');
 if(a)return (a.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();
 const h=(document.querySelector('.top h1')?.textContent||'').trim().toLowerCase();return h;
}
function setPageClass(){document.body.classList.toggle('finanza-page-cuentas',activePage().includes('cuenta'));}
function hideRequestedText(){
 document.querySelectorAll('body *').forEach(e=>{if(e.children.length===0){const t=(e.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();if(t.includes('pequeñas decisiones')||t.includes('grandes resultados')){e.classList.add('finanza-hide-copy');if(e.parentElement?.children.length<=2)e.parentElement.classList.add('finanza-hide-copy')}}});
}
function moveUserToSide(){
 const hello=document.querySelector('.top .hello');if(!hello)return;
 let side=document.querySelector('.side');if(!side)return;
 let box=document.getElementById('finanzaUserSpace');if(!box){box=document.createElement('div');box.id='finanzaUserSpace';side.insertBefore(box,side.querySelector('.nav')||null)}
 const name=hello.querySelector('strong')?.textContent||hello.querySelector('.name')?.textContent||'Anyeli';
 box.innerHTML='<strong>'+esc(name)+'</strong><small>Mi espacio</small>';
 hello.style.display='none';
}
function cleanTop(){
 const top=document.querySelector('.top');if(!top)return;
 top.querySelectorAll('.brand-inline').forEach(e=>e.classList.add('finanza-action-hidden'));
 const hello=top.querySelector('.hello');if(hello)hello.classList.add('finanza-action-hidden');
 const actions=top.querySelector('.actions');if(!actions)return;
 actions.id='finanzaTopActions';
 [...actions.children].forEach(el=>{const t=((el.textContent||'')+' '+(el.getAttribute('aria-label')||'')+' '+(el.getAttribute('title')||'')).toLowerCase();const keep=/notific|alert|campana|bell|notification|inbox/.test(t);if(!keep)el.classList.add('finanza-action-hidden')});
}
function fixMenus(){
 document.querySelectorAll('.side .nav button,.side .nav a').forEach(e=>{const t=(e.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();if(t.includes('deudas')){e.innerHTML='<i aria-hidden="true">▣</i><span>Deudas</span>';e.removeAttribute('data-page-label')}});
 document.querySelectorAll('.bottom-nav button,.mobile-nav button').forEach(e=>{const t=(e.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();if(t==='deudas'||t.includes('deudas presupuesto')){e.innerHTML='<i aria-hidden="true">▥</i><span>Presupuesto</span>'}});
}
function paymentData(){return Array.isArray(window.db?.payments)?db.payments:[]}
function editPayment(id){const p=paymentData().find(x=>String(x.id)===String(id));if(!p)return;const name=prompt('Responsabilidad de pago:',p.name||p.description||'');if(name===null)return;const amount=prompt('Importe mensual:',p.amount??p.monthlyAmount??'');if(amount===null)return;const due=prompt('Fecha de pago (YYYY-MM-DD):',p.dueDate||p.date||'');if(due===null)return;p.name=name.trim()||'Responsabilidad de pago';p.amount=n(amount);if('monthlyAmount' in p)p.monthlyAmount=n(amount);if('dueDate' in p||due)p.dueDate=due.trim();if(typeof save==='function')save();if(typeof render==='function')render();setTimeout(enhance,120)}
function deletePayment(id){const p=paymentData().find(x=>String(x.id)===String(id));if(!p)return;if(!confirm('¿Eliminar esta responsabilidad de pago?'))return;db.payments=paymentData().filter(x=>String(x.id)!==String(id));if(typeof save==='function')save();if(typeof render==='function')render();setTimeout(enhance,120)}
window.finanzaEditPaymentV5=editPayment;window.finanzaDeletePaymentV5=deletePayment;
function paymentsOnlyOnPage(){
 const isPagos=activePage().includes('pago');
 document.querySelectorAll('.finanza-legacy-payments').forEach(e=>e.classList.add('finanza-hide-copy'));
 let box=document.getElementById('finanzaUnifiedPayments');
 if(!isPagos){if(box)box.remove();return;}
 const c=document.getElementById('content');if(!c)return;
 if(!box){box=document.createElement('div');box.id='finanzaUnifiedPayments';box.className='card finanza-payment-manager';c.appendChild(box)}
 const rows=paymentData().map(p=>{const id=JSON.stringify(p.id);const amount=p.amount??p.monthlyAmount;const date=p.dueDate??p.date;return '<div class="finanza-payment-row"><div class="finanza-payment-main"><strong>'+esc(p.name||p.description||'Responsabilidad de pago')+'</strong><small>'+(date?'Fecha: '+esc(date)+' · ':'')+(amount!=null?esc(String(amount))+' '+esc(p.currency||db.baseCurrency||''):'')+'</small></div><div class="finanza-payment-actions"><button class="btn small finanza-edit" onclick="finanzaEditPaymentV5('+id+')">Editar</button><button class="btn small finanza-delete" onclick="finanzaDeletePaymentV5('+id+')">Eliminar</button></div></div>'}).join('');
 box.innerHTML='<div class="section-head"><div><h2>Responsabilidades de pago</h2><div class="muted">Cuotas y responsabilidades en un solo lugar.</div></div></div>'+(rows||'<div class="finanza-empty">No tienes responsabilidades de pago registradas.</div>');
}
function classifyDebt(d){const s=String(d.group||d.type||d.category||d.kind||d.name||d.nombre||'').toLowerCase();if(/tarjet|visa|mastercard|american express|amex|credito|credit card/.test(s))return 'Tarjetas';if(/prestam|préstam|loan|hipotec|financ/.test(s))return 'Préstamos';return 'Otros'}
function debtAmount(d){return Math.max(0,n(d.balance??d.saldo??d.remainingBalance??d.saldoPendiente??d.pending??d.debt??d.amount))}
function drawDebtV5(){const c=document.getElementById('finanzaDebtChart');if(!c||!window.db)return;const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2),w=Math.max(300,r.width||300),h=230;c.width=w*d;c.height=h*d;const x=c.getContext('2d');x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,w,h);const g=['Préstamos','Tarjetas','Otros'],v=g.map(q=>(db.debts||[]).filter(z=>classifyDebt(z)===q).reduce((a,z)=>a+debtAmount(z),0)),total=v.reduce((a,z)=>a+z,0),cs=['#B2967D','#7D5A44','#7F927F'];let a=-Math.PI/2,cx=Math.min(95,w*.25),cy=100,rad=68;if(!total){x.fillStyle='#806F63';x.textAlign='center';x.font='12px Baskerville,Georgia,serif';x.fillText('Sin deudas registradas',cx,cy);return}v.forEach((z,i)=>{if(!z)return;const q=z/total*Math.PI*2;x.beginPath();x.arc(cx,cy,rad,a,a+q);x.lineWidth=30;x.strokeStyle=cs[i];x.stroke();a+=q});x.beginPath();x.arc(cx,cy,rad*.56,0,Math.PI*2);x.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--paper').trim();x.fill();x.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--ink').trim();x.textAlign='center';x.font='900 11px Baskerville,Georgia,serif';x.fillText('100%',cx,cy+4);const lg=document.getElementById('debtPercentLegend');if(lg)lg.innerHTML=g.map((q,i)=>v[i]?'<div class="debt-percent-row"><i style="background:'+cs[i]+'"></i><span>'+q+'</span><b>'+((v[i]/total)*100).toFixed(1)+'%</b></div>':'').join('')}
function drawHistoryV5(){const c=document.getElementById('finanzaBudgetChart');if(!c||!window.db)return;const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,2),w=Math.max(500,r.width||500),h=280;c.width=w*d;c.height=h*d;const x=c.getContext('2d');x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,w,h);const now=new Date();now.setDate(1);const ms=[];for(let i=11;i>=0;i--){const q=new Date(now);q.setMonth(now.getMonth()-i);ms.push(q.toISOString().slice(0,7))}const budgets=db.budgetHistory||db.budget_history||{};const current=Object.values(db.budgets||{}).reduce((a,z)=>a+n(z),0);const spent=ms.map(k=>(db.transactions||[]).filter(t=>String(t.date||'').slice(0,7)===k&&(t.type==='Gasto'||t.type==='Pago de deuda')).reduce((a,t)=>a+n(t.amount),0));const bv=ms.map(k=>budgets[k]!=null?(typeof budgets[k]==='object'?n(budgets[k].total??budgets[k].budget):n(budgets[k])):current),max=Math.max(1,...bv,...spent),L=42,R=10,T=32,B=38,cw=w-L-R,ch=h-T-B,gw=cw/ms.length,bw=Math.max(7,Math.min(18,gw*.28));x.font='700 9px Baskerville,Georgia,serif';x.textAlign='center';ms.forEach((k,i)=>{const xx=L+gw*i+gw/2,bh=bv[i]/max*ch,sh=spent[i]/max*ch;x.fillStyle='#EADFD4';x.fillRect(xx-bw-2,T+ch-bh,bw,bh);x.fillStyle='#B2967D';x.fillRect(xx+2,T+ch-sh,bw,sh);const dt=new Date(k+'-01');x.fillStyle='#806F63';x.fillText(dt.toLocaleDateString('es',{month:'short'}).replace('.',''),xx,T+ch+16)});x.textAlign='left';x.font='800 9px Baskerville,Georgia,serif';x.fillStyle='#EADFD4';x.fillRect(L,8,9,9);x.fillStyle='#4A342A';x.fillText('Presupuestado',L+14,16);x.fillStyle='#B2967D';x.fillRect(L+105,8,9,9);x.fillStyle='#4A342A';x.fillText('Gastado',L+119,16)}
function floatingPlus(){const b=document.querySelector('.floating');if(b){b.textContent='';b.setAttribute('aria-label','Añadir');}}
function enhance(){try{setPageClass();hideRequestedText();moveUserToSide();cleanTop();fixMenus();paymentsOnlyOnPage();drawDebtV5();drawHistoryV5();floatingPlus()}catch(e){console.warn('Finanza V5',e)}}
const oldRender=window.render;if(typeof oldRender==='function'&&!oldRender.__finanzaV5){const r=oldRender;window.render=function(){const z=r.apply(this,arguments);setTimeout(enhance,70);return z};window.render.__finanzaV5=true}
new MutationObserver(()=>{clearTimeout(window.__finanzaV5Timer);window.__finanzaV5Timer=setTimeout(enhance,90)}).observe(document.body,{childList:true,subtree:true});window.addEventListener('resize',()=>{clearTimeout(window.__finanzaV5Resize);window.__finanzaV5Resize=setTimeout(()=>{drawHistoryV5();drawDebtV5()},120)});setTimeout(enhance,500);
})();
</script>'''

s=s.replace('</head>',css+'</head>',1)
s=s.replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
