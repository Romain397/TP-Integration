const request = require('supertest');
jest.mock('child_process', () => ({
  execFile: jest.fn((file, args, options, callback) => callback(null, 'pong')),
}));
const { execFile } = require('child_process');
const app = require('../src/app');

test('bloque le onzième ping par IP sans démarrer de nouveau processus', async () => {
  for (let index = 0; index < 10; index++) {
    expect((await request(app).get('/ping?host=localhost')).status).toBe(200);
  }
  const response = await request(app).get('/ping?host=localhost');
  expect(response.status).toBe(429);
  expect(response.body.error).toContain('Trop de requêtes');
  expect(execFile).toHaveBeenCalledTimes(10);
  expect((await request(app).get('/health')).status).toBe(200);
});
