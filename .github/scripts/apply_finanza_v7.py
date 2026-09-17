from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Replace previous V7 patch if the workflow is re-run.
s = re.sub(r'<style id="finanza-v7-css">.*?</style>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="finanza-v7-js">.*?</script>\s*', '', s, flags=re.S)

css = r'''<style id="finanza-v7-css">
/* V7: deuda, navegación, usuario único y tipografía */
body,body *{font-size:14px!important}
body .nav i{font-size:20px!important}.floating{font-size:28px!important}.avatar{font-size:14px!important}
.nav button.finanza-debt-nav{gap:10px}
.finanza-delete-debt{background:#ead8d2!important;color:var(--espresso,#4A342A)!important;border:0!important;border-radius:10px!important;padding:8px 12px!important;cursor:pointer!important;font-weight:800!important;margin-left:7px!important}
.finanza-modal-delete{background:#ead8d2!important;color:#4A342A!important}
.finanza-debt-actions{display:flex!important;align-items:center!important;gap:7px!important;flex-wrap:wrap!important}
.top .hello.finanza-hide-duplicate-user{display:none!important}
@media(max-width:650px){.nav button.finanza-debt-nav{font-size:14px!important}.nav button.finanza-debt-nav span{font-size:14px!important}.finanza-delete-debt{padding:7px 10px!important}}
</style>'''

js = r'''<script id="finanza-v7-js">
(function(){
  const getDB=()=>window.db||null;
  const saveRender=()=>{try{if(typeof window.save==='function')window.save()}catch(e){}try{if(typeof window.render==='function')window.render()}catch(e){}};
  function debtIdFromButton(btn){
    const oc=btn.getAttribute('onclick')||'';
    let m=oc.match(/(?:editDebt|openDebtEdit|showEditDebt)\s*\(\s*['\"]?([^'\")]+)['\"]?/i);
    if(m)return m[1];
    const own=btn.closest('[data-id],[data-debt-id]');
    if(own)return own.getAttribute('data-debt-id')||own.getAttribute('data-id');
    return btn.dataset.debtId||null;
  }
  function deleteDebt(id){
    const d=getDB();if(!d||!Array.isArray(d.debts))return;
    const debt=d.debts.find(x=>String(x.id)===String(id));if(!debt)return;
    if(!confirm('¿Eliminar la deuda "'+(debt.name||debt.nombre||'esta deuda')+'"? Esta acción no elimina los movimientos históricos.'))return;
    d.debts=d.debts.filter(x=>String(x.id)!==String(id));
    saveRender();
    setTimeout(enhance,100);
  }
  window.finanzaDeleteDebtV7=deleteDebt;
  function addModalDelete(id){
    const modal=document.querySelector('.modal-back.show .modal,.modal-back.show .modal-content,.modal');
    if(!modal||modal.querySelector('.finanza-modal-delete'))return;
    const foot=modal.querySelector('.modal-foot');if(!foot)return;
    const b=document.createElement('button');b.type='button';b.className='btn finanza-modal-delete';b.textContent='Eliminar deuda';
    b.onclick=()=>{deleteDebt(id);const back=modal.closest('.modal-back');if(back)back.classList.remove('show')};
    foot.insertBefore(b,foot.firstChild);
  }
  function wrapDebtEditor(){
    ['editDebt','openDebtEdit','showEditDebt'].forEach(name=>{
      const fn=window[name];
      if(typeof fn!=='function'||fn.__finanzaV7)return;
      const orig=fn;
      const wrapped=function(id){const r=orig.apply(this,arguments);setTimeout(()=>addModalDelete(id),50);return r};
      wrapped.__finanzaV7=true;wrapped.__finanzaV7Original=orig;window[name]=wrapped;
    });
  }
  function nav(){
    document.querySelectorAll('.nav button').forEach(b=>{
      const t=(b.innerText||'').replace(/\s+/g,' ').trim().toLowerCase();
      if(t.includes('deudas')&&t.includes('presupuesto')){b.classList.add('finanza-debt-nav');b.innerHTML='<i>💳</i><span>Deudas</span>'}
      else if(t==='deudas'||t.startsWith('deudas ')){b.classList.add('finanza-debt-nav');const span=b.querySelector('span');if(span)span.textContent='Deudas'}
      if(t.includes('presupuesto')&&!t.includes('deudas')){const span=b.querySelector('span');if(span)span.textContent='Presupuesto'}
    });
  }
  function uniqueUser(){
    const top=document.querySelector('.top .hello');
    const side=document.querySelector('#finanzaSideUser,.side .finanza-side-user');
    if(top&&side)top.classList.add('finanza-hide-duplicate-user');
  }
  function debtRows(){
    const root=document.getElementById('content')||document.body;
    root.querySelectorAll('button').forEach(btn=>{
      if((btn.innerText||'').trim().toLowerCase()!=='editar')return;
      const id=debtIdFromButton(btn);if(!id)return;
      if(btn.dataset.finanzaV7Edit)return;
      btn.dataset.finanzaV7Edit='1';
      btn.addEventListener('click',()=>setTimeout(()=>addModalDelete(id),60));
      const parent=btn.closest('.row,.card,tr,li')||btn.parentElement;if(!parent)return;
      if(parent.querySelector('.finanza-delete-debt'))return;
      const del=document.createElement('button');del.type='button';del.className='finanza-delete-debt';del.textContent='Eliminar';del.onclick=()=>deleteDebt(id);
      (btn.parentElement||parent).appendChild(del);
    });
  }
  function enhance(){nav();uniqueUser();wrapDebtEditor();debtRows()}
  setTimeout(enhance,450);setTimeout(enhance,1200);setTimeout(enhance,2200);
})();
</script>'''

s = s.replace('</body>', css + '\n' + js + '\n</body>') if '</body>' in s else s + '\n' + css + '\n' + js
p.write_text(s, encoding='utf-8')
