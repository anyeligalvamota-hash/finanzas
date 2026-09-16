const json = (status, body, extraHeaders = {}) => Response.json(body, { status, headers: { 'Cache-Control': 'public, max-age=900, stale-while-revalidate=3600', ...extraHeaders } });
export default async function handler(request) {
  try {
    const url = new URL(request.url);
    const base = String(url.searchParams.get('base') || 'EUR').toUpperCase();
    const catalog = url.searchParams.get('catalog') === '1';
    if (catalog) {
      const response = await fetch('https://api.frankfurter.dev/v2/currencies', { headers: { accept: 'application/json' } });
      if (!response.ok) return json(502, { error: 'currency_provider_unavailable' });
      const data = await response.json();
      return json(200, { source: 'Frankfurter', currencies: Object.entries(data || {}).map(([code, name]) => ({ code, name })) });
    }
    if (!/^[A-Z]{3}$/.test(base)) return json(400, { error: 'invalid_base_currency' });
    const response = await fetch(`https://api.frankfurter.dev/v2/rates?base=${encodeURIComponent(base)}`, { headers: { accept: 'application/json' } });
    if (!response.ok) return json(502, { error: 'currency_provider_unavailable', providerStatus: response.status });
    const data = await response.json();
    return json(200, { source: 'Frankfurter', date: data?.[0]?.date || new Date().toISOString().slice(0, 10), rates: Array.isArray(data) ? data.map(item => ({ base: item.base, quote: item.quote, rate: Number(item.rate) })) : [] });
  } catch { return json(500, { error: 'rates_unavailable' }); }
}
