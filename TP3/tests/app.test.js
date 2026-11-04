const request = require('supertest');
jest.mock('child_process', () => ({ execFile: jest.fn() }));
const { execFile } = require('child_process');
const app = require('../src/app');

beforeEach(() => execFile.mockReset());

test('should return ok when calling /health', async () => {
  const res = await request(app).get('/health');
  expect(res.status).toBe(200);
  expect(res.body.status).toBe('ok');
});

test('should greet the user when name is given', async () => {
  const res = await request(app).get('/hello?name=Lina');
  expect(res.text).toContain('Lina');
});

test('utilise un nom par défaut et désactive la signature Express', async () => {
  const res = await request(app).get('/hello');
  expect(res.text).toBe('<h1>Bonjour inconnu</h1>');
  expect(res.headers['x-powered-by']).toBeUndefined();
});

test('renvoie les préférences par défaut ou les valeurs autorisées', async () => {
  expect((await request(app).get('/prefs')).body).toEqual({ theme: 'light', lang: 'fr' });
  const res = await request(app).get('/prefs?theme=dark&lang=en');
  expect(res.status).toBe(200);
  expect(res.body).toEqual({ theme: 'dark', lang: 'en' });
});

test.each(['example.com', '127.0.0.1', '::1'])('ping %s sans shell avec un timeout', async (host) => {
  execFile.mockImplementation((file, args, options, callback) => callback(null, 'pong'));
  const res = await request(app).get('/ping').query({ host });
  expect(res.status).toBe(200);
  expect(res.text).toBe('pong');
  const [file, args, options] = execFile.mock.calls[0];
  expect(file).toBe('ping');
  expect(args.at(-1)).toBe(host);
  expect(options).toEqual({ shell: false, timeout: 3000, maxBuffer: 65536 });
});

test('une erreur réseau renvoie 502 sans exposer de détails internes', async () => {
  execFile.mockImplementation((file, args, options, callback) => callback(new Error('private')));
  const res = await request(app).get('/ping?host=localhost');
  expect(res.status).toBe(502);
  expect(res.body).toEqual({ error: 'Hôte injoignable' });
});
