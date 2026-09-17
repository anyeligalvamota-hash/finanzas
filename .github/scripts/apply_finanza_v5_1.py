from pathlib import Path
import re
p=Path('index.html');s=p.read_text(encoding='utf-8')
s=re.sub(r'<style id="finanza-v5-1-css">.*?</style>\s*','',s,flags=re.S)
s=re.sub(r'<script id="finanza-v5-1-js">.*?</script>\s*','',s,flags=re.S)
css='''<style id="finanza-v5-1-css">@media(max-width:650px){.top .brand-inline,.top .logo,.top .brandmark{display:none!important}}#finanzaUserSpace{display:block!important}</style>'''
js='''<script id="finanza-v5-1-js">(function(){function f(){const a=document.querySelector('.top .actions');if(a){a.id='finanzaTopActions';[...a.children].forEach((e,i)=>{e.classList.toggle('finanza-action-hidden',i>0)})}document.querySelectorAll('.side .nav button,.side .nav a').forEach(e=>{const t=(e.textContent||'').replace(/\\s+/g,' ').trim().toLowerCase();if(t.includes('deudas'))e.innerHTML='<i aria-hidden="true">▣</i><span>Deudas</span>'});document.querySelectorAll('.bottom-nav button,.mobile-nav button').forEach(e=>{const t=(e.textContent||'').replace(/\\s+/g,' ').trim().toLowerCase();if(t==='deudas'||t.includes('deudas presupuesto'))e.innerHTML='<i aria-hidden="true">▥</i><span>Presupuesto</span>'})}new MutationObserver(f).observe(document.body,{childList:true,subtree:true});setTimeout(f,100);})();</script>'''
s=s.replace('</head>',css+'</head>',1).replace('</body>',js+'</body>',1);p.write_text(s,encoding='utf-8')
