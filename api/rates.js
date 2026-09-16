module.exports = async function handler(req, res) {
  try {
    const url = new URL(req.url, 'https://finanza.local');
    if (url.searchParams.get('catalog') === '1') {
      const r = await fetch('https://api.frankfurter.dev/v2/currencies');
      const data = await r.json();
      return res.status(r.ok ? 200 : 502).json(data);
    }
    const r = await fetch('https://api.frankfurter.dev/v2/rates?base=EUR');
    const data = await r.json();
    return res.status(r.ok ? 200 : 502).json(data);
  } catch (e) {
    return res.status(500).json({ error: e.message || 'Rate service error' });
  }
};
