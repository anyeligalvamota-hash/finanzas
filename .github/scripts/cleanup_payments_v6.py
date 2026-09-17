from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove only the injected duplicate payment managers. The original/native Pagos
# section remains the single source of truth.
patterns = [
    r'function finanzaDeletePaymentV2\(id\)\{.*?\}\nfunction finanzaPaymentManagerV2\(\)\{.*?\}\n',
    r'function editPayment\(id\)\{const p=paymentData\(\)\.find\(x=>String\(x\.id\)===String\(id\)\);.*?window\.finanzaDeletePaymentV5=deletePayment;\n',
    r'function paymentsOnlyOnPage\(\)\{.*?\n\}\nfunction classifyDebt\(d\)',
]
for pat in patterns:
    s, count = re.subn(pat, (lambda m: 'function classifyDebt(d)' if 'function classifyDebt' in pat else ''), s, count=1, flags=re.S)

# The previous replacement for the V5 block above intentionally leaves the
# classifyDebt declaration; normalize accidental duplicate prefix if present.
s = s.replace('function classifyDebt(d)function classifyDebt(d)', 'function classifyDebt(d)')

# Remove V2's call to its duplicate payment manager, without touching other V2 features.
s = re.sub(r'if\(window\.__finanzaV2Page===\'Pagos\'\)finanzaPaymentManagerV2\(\);', '', s, count=1)

# Remove V5's call to the duplicate payment manager from enhance().
s = re.sub(r'paymentsOnlyOnPage\(\);', '', s, count=1)

# Remove V4's payment edit override if it is still present. This restores the
# application's native editPayment implementation.
s = re.sub(r'function editPayment\(id\)\{const p=\(db\.payments\|\|\[\]\)\.find\(q=>String\(q\.id\)===String\(id\)\);.*?window\.finanzaDeletePaymentV4=.*?;\n', '', s, count=1, flags=re.S)

# Remove any leftover injected payment-manager DOM created by older layers.
cleanup_js = '''<script id="finanza-v6-payments-cleanup">\n(function(){\n  function clean(){\n    try{\n      document.querySelectorAll('#finanzaPaymentManagerV2,#finanzaUnifiedPayments,.finanza-legacy-payments').forEach(function(e){e.remove()});\n    }catch(e){}\n  }\n  setTimeout(clean,120);\n  setTimeout(clean,500);\n})();\n</script>'''
s = re.sub(r'<script id="finanza-v6-payments-cleanup">.*?</script>\s*', '', s, flags=re.S)
s = s.replace('</body>', cleanup_js + '</body>', 1)

p.write_text(s, encoding='utf-8')
