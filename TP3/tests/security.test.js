const request = require('supertest');
jest.mock('child_process', () => ({ execFile: jest.fn(), exec: jest.fn() }));
const { execFile, exec } = require('child_process');
const app = require('../src/app');

beforeEach(() => {
  jest.clearAllMocks();
  // L'ancien code reste testable sans exécuter réellement la commande d'attaque.
  exec.mockImplementation((command, callback) => callback(null, 'commande exécutée'));
});

test('régression XSS : échappe le HTML fourni dans name', async () => {
  const res = await request(app).get('/hello').query({ name: '<script>alert(1)</script>' });
  expect(res.status).toBe(200);
  expect(res.text).not.toContain('<script>');
  expect(res.text).toContain('&lt;script&gt;alert(1)&lt;/script&gt;');
});

test('régression injection de commande : rejette les métacaractères avant tout processus', async () => {
  const res = await request(app).get('/ping').query({ host: '127.0.0.1;id' });
  expect(res.status).toBe(400);
  expect(execFile).not.toHaveBeenCalled();
  expect(exec).not.toHaveBeenCalled();
});

test('régression merge non maîtrisé : rejette les propriétés de prototype', async () => {
  const res = await request(app).get('/prefs?constructor[prototype][isAdmin]=true');
  expect(res.status).toBe(400);
  expect(Object.prototype.isAdmin).toBeUndefined();
});

test('échappe aussi les guillemets, apostrophes et esperluettes', async () => {
  const res = await request(app).get('/hello').query({ name: '"\'&<>' });
  expect(res.text).toContain('&quot;&#39;&amp;&lt;&gt;');
});

test.each(['/hello?name[x]=a', '/hello?name=a&name=b', `/hello?name=${'a'.repeat(201)}`])(
  'rejette un nom invalide : %s', async (url) => {
    expect((await request(app).get(url)).status).toBe(400);
  });

test.each([undefined, '', '-help', 'a;id', 'a\nwhoami', 'a b', '$(id)', 'a|id', 'a&whoami', 'a/b', 'a'.repeat(254), 'a'.repeat(64) + '.com'])('rejette un hôte invalide : %s', async (host) => {
  const res = await request(app).get('/ping').query(host === undefined ? {} : { host });
  expect(res.status).toBe(400);
  expect(execFile).not.toHaveBeenCalled();
});

test.each([
  'host[x]=localhost', 'host=localhost&host=example.com',
])('rejette un hôte non scalaire : %s', async (query) => {
  expect((await request(app).get(`/ping?${query}`)).status).toBe(400);
  expect(execFile).not.toHaveBeenCalled();
});

test.each(['admin=true', 'theme[x]=dark', 'theme=neon', 'lang=xx', 'lang=fr&lang=en', 'prototype[x]=1'])('rejette des préférences hors schéma : %s', async (query) => {
  expect((await request(app).get(`/prefs?${query}`)).status).toBe(400);
  expect(Object.prototype.isAdmin).toBeUndefined();
});
