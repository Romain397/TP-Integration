const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8').replace(/^\uFEFF/, ''));
const before = read('.artifacts/regression-before.raw.json');
const after = read('.artifacts/regression-after.raw.json');
const initial = read('.artifacts/baseline-initial.raw.json');
const coverage = read('coverage/coverage-summary.json').total;
function regressions(result) {
  return result.testResults.flatMap((suite) => suite.assertionResults)
    .filter((test) => test.fullName.startsWith('régression'))
    .map(({ fullName, status }) => ({ name: fullName, status }));
}
const report = {
  measuredAt: new Date().toISOString(),
  node: process.version,
  initialTests: { passed: initial.numPassedTests, failed: initial.numFailedTests },
  beforeFix: { regressions: regressions(before), expectedFailure: before.numFailedTests === 3 },
  afterFix: { passed: after.numPassedTests, failed: after.numFailedTests, regressions: regressions(after) },
  coveragePercent: Object.fromEntries(Object.entries(coverage)
    .filter(([key]) => key !== 'branchesTrue')
    .map(([key, value]) => [key, value.pct])),
  audit: Object.fromEntries(['before', 'after', 'production'].map((state) =>
    [state, read(`reports/npm-audit-${state}.json`).metadata.vulnerabilities])),
};
if (report.initialTests.passed !== 2 || report.initialTests.failed !== 0 ||
    !report.beforeFix.expectedFailure || report.afterFix.failed !== 0 ||
    report.afterFix.regressions.length !== 3 || report.afterFix.regressions.some((test) => test.status !== 'passed')) {
  throw new Error('Les résultats ne correspondent pas aux régressions attendues.');
}
fs.writeFileSync(path.join(root, 'reports', 'verification.json'), JSON.stringify(report, null, 2) + '\n');
console.log('Preuves synthétiques enregistrées dans reports/verification.json');
