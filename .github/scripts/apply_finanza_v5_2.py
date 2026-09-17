from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove legacy V5.1/V5.2 layers before rebuilding the lightweight cleanup.
s=re.sub(r'<style id="finanza-v5-1-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-1-js">.*?</script>\s*','',s,flags=re.S)
s=re.sub(r'<style id="finanza-v5-2-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-2-js">.*?</script>\s*','',s,flags=re.S)

# Remove every known global observer from the injected V4/V5 layers.
s=re.sub(r'let busy=false;new MutationObserver\(\(\)=>\{if\(busy\)return;busy=true;setTimeout\(\(\)=>\{busy=false;enhance\(\)\},100\)\}\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',s,count=1)
s=re.sub(r'new MutationObserver\(\(\)=>\{clearTimeout\(window\.__finanzaV5Timer\);window\.__finanzaV5Timer=setTimeout\(enhance,90\)\}\)\.observe\(document\.body,\{childList:true,subtree:true\}\);','',s,count=1)

css='''<style id="finanza-v5-2-css">
/* Performance-safe navigation cleanup: no global DOM observers. */
@media(max-width:650px){
  .top .brand-inline,.top .logo,.top .brandmark{display:none!important}
  .top .hello{display:none!important}
  .floating{display:grid!important;place-items:center;font-size:0!important}
  .floating::before{content:'+';font-size:32px;line-height:1;font-weight:400}
}
.finanza-top-user-hidden{display:none!important}
.finanza-side-user{display:flex;align-items:center;gap:9px;margin:2px 8px 16px;padding:10px;border-radius:14px;background:var(--blush);border:1px solid var(--line)}
.finanza-side-user .avatar{width:34px;height:34px;flex:none}
.finanza-side-user strong{display:block;font-size:12px}
.finanza-side-user small{display:block;color:var(--muted);font-size:9px;margin-top:2px}
</style>'''

js='''<script id="finanza-v5-2-js">
(function(){
  function text(el){return (el.textContent||'').replace(/\\s+/g,' ').trim().toLowerCase()}
  function f(){
    try{
      const top=document.querySelector('.top');
      const side=document.querySelector('.side');
      if(top){
        const h=top.querySelector('.hello');
        if(h){
          h.classList.add('finanza-top-user-hidden');
          if(side&&!document.getElementById('finanzaSideUser')){
            const u=document.createElement('div');
            u.id='finanzaSideUser';u.className='finanza-side-user';
            const av=h.querySelector('.avatar');
            const name=(h.querySelector('#userName')?.textContent||h.innerText||'Mi espacio').trim().split(/\\n/)[0]||'Mi espacio';
            u.innerHTML=(av?av.outerHTML:'<div class="avatar">A</div>')+'<div><strong>'+name.replace(/[<>]/g,'')+'</strong><small>Mi espacio</small></div>';
            const nav=side.querySelector('.nav');if(nav)side.insertBefore(u,nav);else side.appendChild(u);
          }
        }
      }
      document.querySelectorAll('.primary-bottom button,.bottom-nav button,.mobile-nav button').forEach(e=>{
        const t=text(e);
        if(t==='deudas'||t.includes('deudas presupuesto')){
          e.innerHTML='<i aria-hidden="true">▥</i><span>Presupuesto</span>';
          e.setAttribute('aria-label','Presupuesto');
        }
      });
      document.querySelectorAll('.side .nav button,.side .nav a').forEach(e=>{
        if(text(e).includes('deudas'))e.innerHTML='<i aria-hidden="true">▣</i><span>Deudas</span>';
      });
    }catch(e){console.warn('Finanza V5.2',e)}
  }
  // Run after initial DOM creation. Navigation is already covered by the render wrappers in V4/V5.
  setTimeout(f,250);
  setTimeout(f,900);
})();
</script>'''

s=s.replace('</head>',css+'</head>',1).replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
