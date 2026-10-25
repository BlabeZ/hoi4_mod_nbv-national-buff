/* Read-only HTML logic verification using Node VM and a minimal DOM mock.
 * Writes only ../vanilla-modifier-catalog/html-verification.json.
 * This does not perform browser layout, accessibility or visual verification.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const root = path.resolve(__dirname, '../vanilla-modifier-catalog');
const source = path.join(root, 'catalog.html');
const output = path.join(root, 'html-verification.json');
const html = fs.readFileSync(source, 'utf8');
const payloadMatch = html.match(/<script id="catalog-data" type="application\/json">([\s\S]*?)<\/script>/);
assert.ok(payloadMatch, 'Embedded catalog JSON must exist');
const payload = payloadMatch[1];
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(x => x[1]);
const js = scripts.at(-1);
assert.ok(js, 'Executable JavaScript must exist');
new vm.Script(js);

const elements = {};
for (const id of ['catalog-data', 'q', 'cat', 'tier', 'coverage', 'sort', 'used', 'prev', 'next', 'count', 'page', 'body']) {
  elements[id] = {
    value: id === 'sort' ? 'priority' : '',
    textContent: id === 'catalog-data' ? payload : '',
    checked: false,
    disabled: false,
    innerHTML: '',
    listeners: {},
    addEventListener(event, fn) { this.listeners[event] = fn; },
  };
}
const context = vm.createContext({ document: { getElementById: id => elements[id] }, console });
vm.runInContext(js, context, { timeout: 10000 });
const read = expression => vm.runInContext(expression, context);
const checks = [];
function check(name, fn) {
  fn();
  checks.push({ name, status: 'passed' });
}
function set(id, value) {
  elements[id][id === 'used' ? 'checked' : 'value'] = value;
  elements[id].listeners[id === 'q' ? 'input' : 'change']();
}
const rowCount = () => [...elements.body.innerHTML.matchAll(/<tr>/g)].length;

check('JavaScript syntax and initial render', () => {
  assert.equal(read('DATA.length'), 4484);
  assert.equal(read('filtered.length'), 4484);
  assert.equal(rowCount(), 60);
  assert.equal(elements.page.textContent, '1 / 75');
  assert.equal(elements.prev.disabled, true);
  assert.equal(elements.next.disabled, false);
});
const categoryCounts = {};
for (const category of ['政治', '工业', '陆军', '海军', '空军', '情报']) {
  set('cat', category);
  check('Category filter: ' + category, () => {
    assert.equal(read('filtered.every(r=>r.category===document.getElementById("cat").value)'), true);
    assert.equal(read('filtered.length'), read('DATA.filter(r=>r.category===document.getElementById("cat").value).length'));
    assert.ok(read('filtered.length') > 0);
  });
  categoryCounts[category] = read('filtered.length');
}
assert.equal(Object.values(categoryCounts).reduce((a, b) => a + b, 0), 4484);
set('cat', '');

for (const priority of ['P0', 'P1', 'P2', 'P3']) {
  set('tier', priority);
  check('Priority filter: ' + priority, () => {
    assert.equal(read('filtered.every(r=>r.priority===document.getElementById("tier").value)'), true);
    assert.ok(read('filtered.length') > 0);
  });
}
set('tier', '');
for (const coverage of ['yes', 'no']) {
  set('coverage', coverage);
  check('BUFF coverage filter: ' + coverage, () => {
    assert.equal(read('filtered.every(r=>document.getElementById("coverage").value==="yes"?r.buff_mods.length>0:r.buff_mods.length===0)'), true);
  });
}
set('coverage', '');
set('used', true);
const usedCount = read('filtered.length');
check('Only modifiers with definition assignments', () => assert.equal(read('filtered.every(r=>r.definition_count>0)'), true));
set('used', false);

for (const sort of ['definition_count', 'file_count']) {
  set('sort', sort);
  check('Numeric descending order: ' + sort, () => {
    assert.equal(read('filtered.every((r,i,a)=>!i||a[i-1][document.getElementById("sort").value]>=r[document.getElementById("sort").value])'), true);
  });
}
set('sort', 'key');
check('Key ascending order', () => assert.equal(read('filtered.every((r,i,a)=>!i||a[i-1].key.localeCompare(r.key)<=0)'), true));
set('sort', 'priority');
check('Priority then score order', () => {
  assert.equal(read('filtered.every((r,i,a)=>!i||a[i-1].priority<r.priority||(a[i-1].priority===r.priority&&a[i-1].evidence_score>=r.evidence_score))'), true);
});

for (const query of ['army_attack_factor', '政治', ' ARMY_ATTACK_FACTOR ', 'army attack']) {
  set('q', query);
  check('Text search: ' + query, () => assert.ok(read('filtered.length') > 0));
}
set('q', '');
set('cat', '陆军');
set('tier', 'P0');
set('coverage', 'yes');
set('used', true);
check('Combined category/priority/coverage/used filters', () => {
  assert.ok(read('filtered.length') > 0);
  assert.equal(read('filtered.every(r=>r.category==="陆军"&&r.priority==="P0"&&r.buff_mods.length&&r.definition_count>0)'), true);
});
for (const id of ['cat', 'tier', 'coverage']) set(id, '');
set('used', false);

check('All 75 pages render without duplicate or missing keys', () => {
  const visited = [];
  for (let index = 0; index < 75; index++) {
    assert.equal(read('page'), index);
    const keys = Array.from(read('filtered.slice(page*size,(page+1)*size).map(r=>r.key)'));
    assert.equal(rowCount(), keys.length);
    visited.push(...keys);
    if (index < 74) elements.next.onclick();
  }
  assert.equal(visited.length, 4484);
  assert.equal(new Set(visited).size, 4484);
  assert.equal(elements.next.disabled, true);
  assert.equal(rowCount(), 44);
  assert.equal(elements.page.textContent, '75 / 75');
  elements.prev.onclick();
  assert.equal(read('page'), 73);
});
set('q', 'no_such_modifier_qa_5b61f');
check('Empty result state and disabled pagination', () => {
  assert.equal(read('filtered.length'), 0);
  assert.equal(read('page'), 0);
  assert.equal(elements.page.textContent, '1 / 1');
  assert.equal(elements.prev.disabled, true);
  assert.equal(elements.next.disabled, true);
  assert.ok(elements.body.innerHTML.includes('没有匹配词条'));
});
set('q', '');
check('Filter reset restores first page', () => assert.equal(elements.page.textContent, '1 / 75'));
context.escapeInput = '<script>&"\'';
check('HTML special-character escaping', () => assert.equal(read('esc(escapeInput)'), '&lt;script&gt;&amp;&quot;&#39;'));

const localLinks = ['README.md', 'important-modifiers.md', 'data/catalog.json', 'data/occurrences.jsonl'];
for (const relative of localLinks) assert.ok(fs.existsSync(path.join(root, relative)), 'Missing local link: ' + relative);
assert.equal(fs.readFileSync(source, 'utf8'), html, 'Source changed while verification was running');
const result = {
  status: 'passed',
  method: 'Node.js vm execution with a minimal DOM mock',
  limitation: 'DOM 模拟功能测试；未进行真实浏览器视觉布局、无障碍或导航行为测试。',
  source,
  source_sha256: crypto.createHash('sha256').update(html).digest('hex'),
  source_bytes: Buffer.byteLength(html),
  node_version: process.version,
  verified_at_utc: new Date().toISOString(),
  catalog_snapshot_date: '2026-10-24',
  passed_checks: checks.length,
  failed_checks: 0,
  checks,
  total_keys: read('DATA.length'),
  categories: categoryCounts,
  used_count: usedCount,
  pagination: { rows_per_page: 60, pages: 75, last_page_rows: 44 },
  first_three_keys: Array.from(read('filtered.slice(0,3).map(r=>r.key)')),
  local_link_targets: localLinks.map(relative => ({ path: relative, exists: true })),
};
fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ status: result.status, passed_checks: result.passed_checks, total_keys: result.total_keys, categories: categoryCounts, used_count: usedCount, source_sha256: result.source_sha256, report: output }, null, 2));
