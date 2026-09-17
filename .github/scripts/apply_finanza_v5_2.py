from pathlib import Path
import re
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Remove the V5.1 observer, which can retrigger itself continuously.
s=re.sub(r'<style id="finanza-v5-1-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-1-js">.*?</script>\s*','',s,flags=re.S)
# Disable the V4 global MutationObserver; DOM changes should be handled by render/explicit actions.
old=r"let busy=false;new MutationObserver\(\(\)=>\{if\(busy\)return;busy=true;setTimeout\(\(\)=>\{busy=false;enhance\(\)\},100\)\}\)\.observe\(document\.body,\{childList:true,subtree:true\}\);"
s=re.sub(old,"",s,count=1)
# Add a lightweight, one-shot navigation/mobile cleanup layer.
s=re.sub(r'<style id="finanza-v5-2-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-2-js">.*?</script>\s*','',s,flags=re.S)
css='''<style id="finanza-v5-2-css">\n@media(max-width:650px){.top .brand-inline,.top .logo,.top .brandmark{display:none!important}.top .hello{display:none!important}.floating{display:grid!important;place-items:center;font-size:0!important}.floating::before{content:'+';font-size:32px;line-height:1;font-weight:400}}\n.finanza-top-user-hidden{display:none!important}.finanza-side-user{display:flex;align-items:center;gap:9px;margin:2px 8px 16px;padding:10px;border-radius:14px;background:var(--blush);border:1px solid var(--line)}.finanza-side-user .avatar{width:34px;height:34px;flex:none}.finanza-side-user strong{display:block;font-size:12px}.finanza-side-user small{display:block;color:var(--muted);font-size:9px;margin-top:2px}\n</style>'''
js='''<script id="finanza-v5-2-js">(function(){function f(){try{const top=document.querySelector('.top');if(top){const h=top.querySelector('.hello');if(h){h.classList.add('finanza-top-user-hidden');const side=document.querySelector('.side');if(side&&!document.getElementById('finanzaSideUser')){const u=document.createElement('div');u.id='finanzaSideUser';u.className='finanza-side-user';const av=h.querySelector('.avatar');const name=(h.innerText||'').trim().split(/\\n/)[0]||'Mi espacio';u.innerHTML=(av?av.outerHTML:'<div class="avatar">A</div>')+'<div><strong>'+name.replace(/[<>]/g,'')+'</strong><small>Mi espacio</small></div>';const nav=side.querySelector('.nav');if(nav)side.insertBefore(u,nav)}}}document.querySelectorAll('.bottom-nav button,.mobile-nav button').forEach(e=>{const t=(e.textContent||'').replace(/\\s+/g,' ').trim().toLowerCase();if(t==='deudas' || t.includes('deudas presupuesto'))e.innerHTML='<i aria-hidden="true">▥</i><span>Presupuesto</span>'});document.querySelectorAll('.side .nav button,.side .nav a').forEach(e=>{const t=(e.textContent||'').replace(/\\s+/g,' ').trim().toLowerCase();if(t.includes('deudas'))e.innerHTML='<i aria-hidden="true">▣</i><span>Deudas</span>'});}catch(e){console.warn('Finanza V5.2',e)}}setTimeout(f,250);})();</script>'''
s=s.replace('</head>',css+'</head>',1).replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
