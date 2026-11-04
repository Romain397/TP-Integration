const express = require('express');
const { execFile } = require('child_process');
const { isIP } = require('node:net');
const _ = require('lodash');
const { rateLimit } = require('express-rate-limit');

const app = express();
app.disable('x-powered-by');
app.set('query parser', 'extended');

function isValidHost(host) {
  if (typeof host !== 'string' || host.length === 0 || host.length > 253) return false;
  if (isIP(host)) return true;
  return host.split('.').every((label) =>
    /^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/.test(label));
}

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.get('/hello', (req, res) => {
  const name = req.query.name === undefined ? 'inconnu' : req.query.name;
  if (typeof name !== 'string' || name.length > 200) {
    return res.status(400).json({ error: 'Nom invalide' });
  }
  res.type('html').send(`<h1>Bonjour ${_.escape(name)}</h1>`);
});

const pingLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 10,
  standardHeaders: 'draft-8',
  legacyHeaders: false,
  skipFailedRequests: true,
  message: { error: 'Trop de requêtes ping. Réessayer dans une minute.' },
});

app.get('/ping', pingLimiter, (req, res) => {
  const host = req.query.host;
  if (!isValidHost(host)) return res.status(400).json({ error: 'Hôte invalide' });

  const args = process.platform === 'win32'
    ? ['-n', '1', '-w', '2000', host]
    : ['-c', '1', '-W', '2', host];

  execFile('ping', args, { shell: false, timeout: 3000, maxBuffer: 64 * 1024 }, (error, stdout) => {
    if (error) return res.status(502).json({ error: 'Hôte injoignable' });
    res.type('text').send(stdout);
  });
});

app.get('/prefs', (req, res) => {
  const query = req.query;
  const allowedKeys = ['theme', 'lang'];
  if (Object.keys(query).some((key) => !allowedKeys.includes(key)) ||
      (query.theme !== undefined && !['light', 'dark'].includes(query.theme)) ||
      (query.lang !== undefined && !['fr', 'en'].includes(query.lang))) {
    return res.status(400).json({ error: 'Préférences invalides' });
  }

  // Construction explicite : aucun merge profond de propriétés contrôlées par le client.
  res.json({ theme: query.theme ?? 'light', lang: query.lang ?? 'fr' });
});

module.exports = app;
