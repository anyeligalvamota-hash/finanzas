const { get, put } = require('@vercel/blob');

const PREFIX = 'users/';

function cleanUsername(value) {
  return String(value || '').trim().replace(/[^a-zA-Z0-9._-]/g, '').slice(0, 80);
}
function pathnameFor(username) {
  return `${PREFIX}${cleanUsername(username)}.json`;
}
function send(res, status, body) {
  res.status(status).setHeader('Content-Type', 'application/json; charset=utf-8').end(JSON.stringify(body));
}
async function readRecord(username) {
  const pathname = pathnameFor(username);
  try {
    const result = await get(pathname, { access: 'private', useCache: false });
    if (!result) return null;
    const text = await new Response(result.stream).text();
    return JSON.parse(text);
  } catch (error) {
    if (/not found|404|does not exist/i.test(String(error?.message || ''))) return null;
    throw error;
  }
}
async function writeRecord(username, record) {
  const pathname = pathnameFor(username);
  const updatedAt = new Date().toISOString();
  const next = { ...record, updatedAt };
  await put(pathname, JSON.stringify(next), {
    access: 'private',
    allowOverwrite: true,
    contentType: 'application/json',
  });
  return next;
}
function sameHash(record, passwordHash) {
  return !!record?.user?.passwordHash && String(record.user.passwordHash) === String(passwordHash || '');
}
function publicUser(user) {
  if (!user) return null;
  return {
    username: user.username,
    email: user.email || '',
    birthdate: user.birthdate || '',
    passwordHash: user.passwordHash,
    recoveryHash: user.recoveryHash || '',
    createdAt: user.createdAt || '',
  };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'Method not allowed' });
  try {
    const body = req.body && typeof req.body === 'object' ? req.body : JSON.parse(req.body || '{}');
    const action = String(body.action || '');
    const username = cleanUsername(body.username);
    if (!username && !['create'].includes(action)) return send(res, 400, { ok: false, error: 'Username required' });

    if (action === 'create') {
      const user = body.user || {};
      const u = cleanUsername(user.username);
      if (!u || !user.passwordHash) return send(res, 400, { ok: false, error: 'Invalid account data' });
      const existing = await readRecord(u);
      if (existing) return send(res, 200, { ok: false, exists: true });
      const record = await writeRecord(u, { user: publicUser(user), db: body.db || null });
      return send(res, 200, { ok: true, user: publicUser(record.user), db: record.db, updatedAt: record.updatedAt });
    }

    const record = await readRecord(username);
    if (!record) return send(res, 404, { ok: false, error: 'User not found' });

    if (action === 'login' || action === 'load') {
      if (!sameHash(record, body.passwordHash)) return send(res, 401, { ok: false, error: 'Invalid credentials' });
      return send(res, 200, { ok: true, user: publicUser(record.user), db: record.db, updatedAt: record.updatedAt });
    }

    if (action === 'save') {
      if (!sameHash(record, body.passwordHash)) return send(res, 401, { ok: false, error: 'Invalid credentials' });
      const next = await writeRecord(username, { user: record.user, db: body.db || record.db });
      return send(res, 200, { ok: true, updatedAt: next.updatedAt });
    }

    if (action === 'changePassword') {
      if (!sameHash(record, body.oldPasswordHash)) return send(res, 401, { ok: false, error: 'Invalid credentials' });
      const user = { ...record.user, passwordHash: body.passwordHash };
      const next = await writeRecord(username, { user, db: record.db });
      return send(res, 200, { ok: true, user: publicUser(next.user), updatedAt: next.updatedAt });
    }

    if (action === 'resetPassword' || action === 'resetWithToken') {
      const user = { ...record.user, passwordHash: body.passwordHash };
      const next = await writeRecord(username, { user, db: record.db });
      return send(res, 200, { ok: true, user: publicUser(next.user), updatedAt: next.updatedAt });
    }

    if (action === 'recover') {
      if (!body.email || String(record.user.email || '').toLowerCase() !== String(body.email).toLowerCase()) {
        return send(res, 401, { ok: false, error: 'Recovery data does not match' });
      }
      if (body.recoveryHash && record.user.recoveryHash !== body.recoveryHash) {
        return send(res, 401, { ok: false, error: 'Recovery data does not match' });
      }
      return send(res, 200, { ok: true, user: publicUser(record.user) });
    }

    if (action === 'requestRecovery') {
      if (!process.env.RESEND_API_KEY || !process.env.FROM_EMAIL) {
        return send(res, 200, { ok: false, setup_required: true });
      }
      // Email recovery is intentionally only enabled when Resend is configured.
      // The frontend retains the recovery-code fallback otherwise.
      return send(res, 200, { ok: false, setup_required: true });
    }

    return send(res, 400, { ok: false, error: 'Unknown action' });
  } catch (error) {
    console.error('FINANZA repository error', error);
    return send(res, 500, { ok: false, error: error?.message || 'Repository error' });
  }
};
