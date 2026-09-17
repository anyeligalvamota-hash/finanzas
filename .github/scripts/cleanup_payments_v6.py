from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def remove_between(start_marker, end_marker):
    global s
    start = s.find(start_marker)
    if start < 0:
        return False
    end = s.find(end_marker, start)
    if end < 0:
        return False
    s = s[:start] + s[end:]
    return True

# V2 duplicate payment manager.
remove_between('function finanzaDeletePaymentV2(id)', 'function finanzaToastV2(')

# V5 duplicate payment manager and its edit/delete wrappers.
remove_between('function editPayment(id){const p=paymentData().find', 'function classifyDebt(d)')

# Remove the V5 invocation left in enhance().
s = s.replace('paymentsOnlyOnPage();', '')

# Remove V2 invocation left in finanzaPostV2().
s = s.replace("if(window.__finanzaV2Page==='Pagos')finanzaPaymentManagerV2();", '')

# Remove the V4 payment override, preserving the native editPayment() implementation.
remove_between('function editPayment(id){const p=(db.payments||[]).find', 'function drawHistory(')

# Remove references exported only for the duplicate V5 manager if any remain.
s = s.replace('window.finanzaEditPaymentV5=editPayment;window.finanzaDeletePaymentV5=deletePayment;\n', '')

# Remove the temporary V6 DOM cleanup script if an earlier run inserted it.
start = s.find('<script id="finanza-v6-payments-cleanup">')
if start >= 0:
    end = s.find('</script>', start)
    if end >= 0:
        s = s[:start] + s[end+9:]

p.write_text(s, encoding='utf-8')
