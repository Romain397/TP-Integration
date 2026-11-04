const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const target = path.join(root, '.artifacts', 'baseline');
fs.mkdirSync(path.join(target, 'src'), { recursive: true });
fs.mkdirSync(path.join(target, 'tests'), { recursive: true });
for (const name of ['package.json', 'Dockerfile']) {
  fs.copyFileSync(path.join(root, 'baseline', name), path.join(target, name));
}
const lockfile = path.join(root, 'baseline', 'package-lock.json');
if (fs.existsSync(lockfile)) fs.copyFileSync(lockfile, path.join(target, 'package-lock.json'));
fs.copyFileSync(path.join(root, 'baseline', 'app.js.txt'), path.join(target, 'src', 'app.js'));
fs.copyFileSync(path.join(root, 'src', 'index.js'), path.join(target, 'src', 'index.js'));
fs.copyFileSync(path.join(root, 'tests', 'security.test.js'), path.join(target, 'tests', 'security.test.js'));
fs.writeFileSync(path.join(target, 'tests', 'app.test.js'), `const request = require('supertest');
const app = require('../src/app');
test('health', async () => { expect((await request(app).get('/health')).body.status).toBe('ok'); });
test('hello', async () => { expect((await request(app).get('/hello?name=Lina')).text).toContain('Lina'); });
`);
const pkg = JSON.parse(fs.readFileSync(path.join(target, 'package.json'), 'utf8'));
pkg.scripts.start = 'node src/index.js';
fs.writeFileSync(path.join(target, 'package.json'), JSON.stringify(pkg, null, 2) + '\n');
console.log('Baseline créée dans .artifacts/baseline ; ne pas exposer cette application sur le réseau.');
