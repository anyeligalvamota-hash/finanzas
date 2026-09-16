import { get, put } from '@vercel/blob';
import { randomBytes, createHash } from 'node:crypto';
import { PERSONAL_SEED } from './personal-seed.js';

const STORE_ACCESS = 'private';
const ANYELI = {
  username: 'Anyeli',
  email: '',
  birthdate: '',
  passwordHash: '3714ca5fbcbd68442b48ca3f1067ede956b906cdaf6887ae7a71039cf903f918',
  createdAt: '2026-09-15T00:00:00.000Z',
};

const json = (status, body) => Response.json(body, {
  status,
  headers: { 'Cache-Control': 'no-store' },
});

const clean = (value) => String(value || '').trim().toLowerCase();
const userPath = (username) => `users/${encodeURIComponent(username)}.json`;
const clone = (value) => JSON.parse(JSON.stringify(value));

function personalizedSeed() {
  const db = clone(PERSONAL_SEED);
  db.profile = { ...(db.profile || {}), name: 'Anyeli', username: 'Anyeli', email: '', birthdate: '', notifications: true };
  return db;
}

async function readUser(username) {
  const result = await get(userPath(username), { access: STORE_ACCESS, useCache: false });
  if (!result || result.statusCode !== 200 || !result.stream) return null;
  const chunks = [];
  for await (const chunk of result.stream) chunks.push(Buffer.from(chunk));
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { return null; }
}

async function writeUser(username, record) {
  await put(userPath(username), JSON.stringify(record), {
    access: STORE_ACCESS,
    contentType: 'application/json',
    allowOverwrite: true,
  });
}

async function ensureAnyeli() {
  const existing = await readUser(ANYELI.username);
  if (!existing) {
    const record = {
      user: { ...ANYELI },
      db: personalizedSeed(),
      updatedAt: new Date().toISOString(),
    };
    await writeUser(ANYELI.username, record);
    return record;
  }

  // Migrate an older/empty Anyeli record created during the Vercel transition.
  // Never overwrite a user-changed password or existing financial data.
  const existingDb = existing.db && typeof existing.db === 'object' ? existing.db : null;
  const looksEmpty = !existingDb || ((existingDb.accounts?.length || 0) === 0 && (existingDb.debts?.length || 0) === 0);
  const needsIdentityRepair = existing.user?.passwordHash === ANYELI.passwordHash;
  if (looksEmpty && needsIdentityRepair) {
    const record = {
      ...existing,
      user: { ...ANYELI, ...existing.user, username: 'Anyeli', passwordHash: ANYELI.passwordHash },
      db: personalizedSeed(),
      updatedAt: new Date().toISOString(),
    };
    await writeUser(ANYELI.username, record);
    return record;
  }
  return existing;
}

export default async function handler(request) {
  if (request.method !== 'POST') return json(405, { error: 'Method not allowed' });
  try {
    const body = await request.json().catch(() => ({}));
    const action = body.action;
    const usernameRaw = String(body.username || body.user?.username || '').trim();
    const username = clean(usernameRaw);
    if (!username) return json(400, { error: 'username_required' });

    let existing = await readUser(usernameRaw || username);
    if (username === 'anyeli' && (action === 'login' || action === 'load' || action === 'save')) {
      existing = await ensureAnyeli();
    }

    if (action === 'create') {
      if (username === 'anyeli') {
        await ensureAnyeli();
        return json(200, { exists: true });
      }
      if (existing) return json(200, { exists: true });
      const u = body.user || {};
      if (!u.passwordHash || !u.email) return json(400, { error: 'invalid_user' });
      await writeUser(usernameRaw, {
        user: {
          username: u.username,
          email: u.email,
          birthdate: u.birthdate || '',
          passwordHash: u.passwordHash,
          recoveryHash: u.recoveryHash || '',
          createdAt: u.createdAt || new Date().toISOString(),
        },
        db: body.db || null,
        updatedAt: new Date().toISOString(),
      });
      return json(200, { ok: true, created: true });
    }

    if (action === 'login') {
      if (!existing || existing.user?.passwordHash !== body.passwordHash) return json(200, { ok: false });
      return json(200, {
        ok: true,
        user: {
          username: existing.user.username,
          email: existing.user.email || '',
          birthdate: existing.user.birthdate || '',
          passwordHash: existing.user.passwordHash,
          recoveryHash: existing.user.recoveryHash || '',
        },
        db: existing.db || null,
        updatedAt: existing.updatedAt || null,
      });
    }

    if (action === 'load') {
      if (!existing || !body.passwordHash || body.passwordHash !== existing.user?.passwordHash) return json(401, { error: 'unauthorized' });
      return json(200, { ok: true, db: existing.db || null, updatedAt: existing.updatedAt || null });
    }

    if (action === 'save') {
      if (!existing) return json(404, { error: 'user_not_found' });
      if (!body.passwordHash || body.passwordHash !== existing.user?.passwordHash) return json(401, { error: 'unauthorized' });
      const incomingDb = body.db || existing.db || null;
      const incomingAt = Number(incomingDb?._localUpdatedAt || 0);
      const existingAt = Number(existing.db?._localUpdatedAt || 0);
      if (existingAt > incomingAt) {
        return json(200, { ok: true, conflict: true, db: existing.db || null, updatedAt: existing.updatedAt || null });
      }
      const updatedAt = new Date().toISOString();
      await writeUser(existing.user.username, { ...existing, db: incomingDb, updatedAt });
      return json(200, { ok: true, updatedAt });
    }

    if (action === 'requestRecovery') {
      const email = String(body.email || '').trim().toLowerCase();
      if (!existing || !email || existing.user?.email?.toLowerCase() !== email) return json(200, { ok: true });
      const apiKey = process.env.RESEND_API_KEY;
      const from = process.env.FROM_EMAIL;
      const appUrl = String(process.env.APP_URL || '').replace(/\/$/, '');
      if (!apiKey || !from || !appUrl) return json(200, { setup_required: true });
      const token = randomBytes(32).toString('base64url');
      const tokenHash = createHash('sha256').update(token).digest('hex');
      const expiresAt = Date.now() + 15 * 60 * 1000;
      await writeUser(existing.user.username, { ...existing, recoveryReset: { tokenHash, expiresAt, used: false }, updatedAt: new Date().toISOString() });
      const link = `${appUrl}/?reset=${encodeURIComponent(token)}&u=${encodeURIComponent(existing.user.username)}`;
      await fetch('https://api.resend.com/emails', {
        method: 'POST', headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ from, to: [existing.user.email], subject: 'FINANZA · Recuperar contraseña', html: `<h2>FINANZA</h2><p><a href="${link}">Crear nueva contraseña</a></p><p>El enlace caduca en 15 minutos.</p>` }),
      });
      return json(200, { ok: true });
    }

    if (action === 'resetWithToken') {
      const tokenHash = createHash('sha256').update(String(body.token || '')).digest('hex');
      if (!existing?.recoveryReset || existing.recoveryReset.used || existing.recoveryReset.expiresAt < Date.now() || existing.recoveryReset.tokenHash !== tokenHash || !body.passwordHash) return json(401, { error: 'invalid_or_expired_token' });
      await writeUser(existing.user.username, { ...existing, user: { ...existing.user, passwordHash: body.passwordHash }, recoveryReset: { ...existing.recoveryReset, used: true }, updatedAt: new Date().toISOString() });
      return json(200, { ok: true });
    }

    if (action === 'resetPassword') {
      if (!existing || existing.user?.email?.toLowerCase() !== String(body.email || '').trim().toLowerCase() || existing.user?.recoveryHash !== body.recoveryHash || !body.passwordHash) return json(401, { error: 'unauthorized' });
      await writeUser(existing.user.username, { ...existing, user: { ...existing.user, passwordHash: body.passwordHash }, updatedAt: new Date().toISOString() });
      return json(200, { ok: true });
    }

    if (action === 'changePassword') {
      if (!existing || existing.user?.passwordHash !== body.oldPasswordHash || !body.passwordHash) return json(401, { error: 'unauthorized' });
      await writeUser(existing.user.username, { ...existing, user: { ...existing.user, passwordHash: body.passwordHash }, updatedAt: new Date().toISOString() });
      return json(200, { ok: true });
    }

    if (action === 'recover') {
      if (!existing || existing.user?.email?.toLowerCase() !== String(body.email || '').trim().toLowerCase() || existing.user?.recoveryHash !== body.recoveryHash) return json(200, { ok: false });
      return json(200, { ok: true, user: existing.user });
    }

    if (action === 'health') {
      const anyeli = username === 'anyeli' ? await ensureAnyeli() : null;
      return json(200, { ok: true, storage: 'vercel-blob-private', anyeliReady: !!anyeli, hasDb: !!anyeli?.db, accountCount: anyeli?.db?.accounts?.length || 0, debtCount: anyeli?.db?.debts?.length || 0 });
    }

    return json(400, { error: 'unknown_action' });
  } catch (error) {
    console.error('FINANZA repository error', error);
    const message = error?.message === 'BLOB_READ_WRITE_TOKEN' ? 'storage_not_configured' : 'repository_unavailable';
    return json(500, { error: message });
  }
}
