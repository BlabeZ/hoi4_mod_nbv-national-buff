/* Offline logic QA for global-buff-review/catalog.html.
 * Expected counts come from data/display-catalog.json. No A/B totals are hardcoded.
 * This script writes only global-buff-review/html-verification.json.
 * A DOM mock is not a real browser visual, accessibility or file-navigation test.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const root = path.resolve(__dirname, '../vanilla-modifier-catalog/global-buff-review');
const htmlPath = path.join(root, 'catalog.html');
const dataPath = path.join(root, 'data/display-catalog.json');
const outputPath = path.join(root, 'html-verification.json');
const result = {
  status: 'running',
  method: 'Node.js vm with a minimal DOM mock; expected values read from display-catalog.json',
  limitation: 'DOM 模拟功能测试，未进行真实浏览器视觉布局、无障碍或文件导航行为测试。',
  node_version: process.version,
  source: htmlPath,
  expected_data: dataPath,
  checks: [],
};
function check(name, action) {
  try {
    action();
    result.checks.push({ name, status: 'passed' });
  } catch (error) {
    result.checks.push({ name, status: 'failed', error: error.message });
  }
}
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const counts = (rows, field) => rows.reduce((acc, row) => ((acc[row[field]] = (acc[row[field]] || 0) + 1), acc), {});

try {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const expectedText = fs.readFileSync(dataPath, 'utf8');
  const expectedDocument = JSON.parse(expectedText);
  const expected = expectedDocument.records;
  assert.ok(Array.isArray(expected), 'display-catalog.json.records must be an array');
  const expectedByKey = new Map(expected.map(row => [row.key, row]));
  result.source_sha256 = sha256(html);
  result.expected_data_sha256 = sha256(expectedText);
  result.source_bytes = Buffer.byteLength(html);
  result.catalog_date = expectedDocument.date;
  result.expected_group_counts = counts(expected, 'group');
  result.expected_category_counts = counts(expected, 'category');

  const match = html.match(/<script id="catalog-data" type="application\/json">([\s\S]*?)<\/script>/);
  assert.ok(match, 'Embedded catalog JSON must exist');
  const payload = match[1];
  const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(item => item[1]);
  const js = scripts.at(-1);
  assert.ok(js, 'Executable script must exist');
  new vm.Script(js);
  const elements = {};
  for (const id of ['catalog-data', 'q', 'group', 'cat', 'coverage', 'sort', 'prev', 'next', 'count', 'page', 'body']) {
    elements[id] = {
      value: id === 'sort' ? 'source' : id === 'group' ? 'AB' : '',
      textContent: id === 'catalog-data' ? payload : '',
      disabled: false,
      innerHTML: '',
      listeners: {},
      addEventListener(event, fn) { this.listeners[event] = fn; },
    };
  }
  const context = vm.createContext({ document: { getElementById: id => elements[id] }, console });
  vm.runInContext(js, context, { timeout: 10000 });
  const read = expression => vm.runInContext(expression, context);
  const embedded = JSON.parse(payload);
  const rowCount = () => [...elements.body.innerHTML.matchAll(/<tr>/g)].length;
  const visibleKeys = () => [...elements.body.innerHTML.matchAll(/<summary>[\s\S]*?<code>([^<]+)<\/code><\/summary>/g)].map(item => item[1]);
  const set = (id, value) => {
    elements[id].value = value;
    elements[id].listeners[id === 'q' ? 'input' : 'change']();
  };
  const filteredKeys = () => Array.from(read('filtered.map(r=>r.key)'));
  const reset = () => { for (const id of ['q', 'group', 'cat', 'coverage']) set(id, ''); set('sort', 'source'); };

  check('Registry has 4484 unique keys and embedded data matches source JSON', () => {
    assert.equal(expected.length, 4484);
    assert.equal(expectedByKey.size, 4484);
    assert.equal(embedded.length, expected.length);
    assert.equal(new Set(embedded.map(row => row.key)).size, expected.length);
    for (const row of embedded) {
      const source = expectedByKey.get(row.key);
      assert.ok(source, 'Unknown embedded key: ' + row.key);
      for (const field of ['name_zh', 'name_en', 'category', 'group', 'country_spirit_direct_count', 'focus_unique_count', 'buff_mods', 'decision_reason']) {
        assert.deepEqual(row[field], source[field], 'Embedded mismatch: ' + row.key + '.' + field);
      }
      assert.equal(typeof source.focus_unique_count, 'number', 'Missing focus_unique_count: ' + row.key);
    }
    assert.deepEqual(counts(expected, 'group'), expectedDocument.statistics.groups);
  });
  check('Initial render defaults to named AB selection, 60 rows and first-page controls', () => {
    assert.ok(html.includes('<option value="AB" selected>'));
    const selected = expected.filter(row => row.group !== 'C');
    assert.equal(read('size'), 60);
    assert.equal(read('filtered.length'), selected.length);
    assert.ok(selected.every(row => row.has_confirmed_display_name));
    assert.equal(rowCount(), 60);
    assert.equal(visibleKeys().length, 60);
    assert.equal(elements.page.textContent, '1 / ' + Math.ceil(selected.length / 60));
    assert.equal(elements.prev.disabled, true);
    assert.equal(elements.next.disabled, false);
  });

  for (const group of ['A', 'B', 'C', 'AB']) {
    set('group', group);
    check('Group filter ' + group + ' equals JSON-defined selection', () => {
      const wanted = expected.filter(row => group === 'AB' ? row.group === 'A' || row.group === 'B' : row.group === group);
      assert.deepEqual(filteredKeys().sort(), wanted.map(row => row.key).sort());
      assert.equal(read('page'), 0);
    });
  }
  set('group', '');
  for (const category of ['政治', '工业', '陆军', '海军', '空军', '情报']) {
    set('cat', category);
    check('Category filter ' + category, () => {
      assert.deepEqual(filteredKeys().sort(), expected.filter(row => row.category === category).map(row => row.key).sort());
    });
  }
  set('cat', '');
  for (const coverage of ['yes', 'no']) {
    set('coverage', coverage);
    check('Old BUFF mod coverage filter ' + coverage, () => {
      assert.deepEqual(filteredKeys().sort(), expected.filter(row => coverage === 'yes' ? row.buff_mods.length > 0 : !row.buff_mods.length).map(row => row.key).sort());
    });
  }
  set('coverage', '');
  for (const query of ['army_attack_factor', '陆军', ' ARMY_ATTACK_FACTOR ', 'army attack']) {
    set('q', query);
    check('Case/whitespace/multi-term search: ' + query, () => {
      const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
      const wanted = expected.filter(row => terms.every(term => [row.key, row.name_zh, row.name_en, row.decision_reason].join(' ').toLowerCase().includes(term)));
      assert.ok(wanted.length > 0);
      assert.deepEqual(filteredKeys().sort(), wanted.map(row => row.key).sort());
    });
  }
  set('q', '');
  set('group', 'AB'); set('cat', '陆军'); set('coverage', 'yes');
  check('Combined AB/category/coverage filters', () => {
    const wanted = expected.filter(row => row.group !== 'C' && row.category === '陆军' && row.buff_mods.length);
    assert.ok(wanted.length > 0);
    assert.deepEqual(filteredKeys().sort(), wanted.map(row => row.key).sort());
  });
  reset();

  const orders = {
    source: (a, b) => b.country_spirit_direct_count - a.country_spirit_direct_count || a.key.localeCompare(b.key),
    focus: (a, b) => b.focus_unique_count - a.focus_unique_count || a.key.localeCompare(b.key),
    key: (a, b) => a.key.localeCompare(b.key),
  };
  for (const [sort, compare] of Object.entries(orders)) {
    set('sort', sort);
    check('Sort mode ' + sort + (sort === 'focus' ? ' uses unique focus count' : ''), () => {
      assert.deepEqual(filteredKeys(), [...expected].sort(compare).map(row => row.key));
    });
  }
  set('sort', 'focus');
  check('Rendered focus column uses focus_unique_count', () => {
    const visible = Array.from(read('filtered.slice(0,60).map(r=>({key:r.key,count:r.focus_unique_count}))'));
    const rows = [...elements.body.innerHTML.matchAll(/<tr>([\s\S]*?)<\/tr>/g)].map(item => item[1]);
    assert.equal(rows.length, visible.length);
    rows.forEach((row, index) => {
      const cells = [...row.matchAll(/<td(?:\s[^>]*)?>([\s\S]*?)<\/td>/g)].map(item => item[1]);
      assert.equal(cells[4], String(visible[index].count), 'Focus column mismatch: ' + visible[index].key);
    });
  });
  set('sort', 'key');
  check('Every 60-item page renders each key exactly once', () => {
    const visited = [];
    const pages = Math.ceil(expected.length / 60);
    for (let index = 0; index < pages; index++) {
      assert.equal(read('page'), index);
      const keys = visibleKeys();
      const wanted = Array.from(read('filtered.slice(page*size,(page+1)*size).map(r=>r.key)'));
      assert.deepEqual(keys, wanted);
      assert.equal(rowCount(), keys.length);
      visited.push(...keys);
      if (index < pages - 1) elements.next.onclick();
    }
    assert.equal(visited.length, expected.length);
    assert.equal(new Set(visited).size, expected.length);
    assert.deepEqual([...visited].sort(), [...expectedByKey.keys()].sort());
    assert.equal(visibleKeys().length, expected.length % 60 || 60);
    assert.equal(elements.next.disabled, true);
    elements.prev.onclick();
    assert.equal(read('page'), pages - 2);
    result.pagination = { rows_per_page: 60, pages, last_page_rows: expected.length % 60 || 60, unique_rendered_keys: new Set(visited).size };
  });
  set('q', '__no_global_buff_modifier_matches_qa_4287__');
  check('No-result state and disabled pagination', () => {
    assert.equal(read('filtered.length'), 0);
    assert.equal(elements.page.textContent, '1 / 1');
    assert.equal(elements.prev.disabled, true);
    assert.equal(elements.next.disabled, true);
    assert.equal(visibleKeys().length, 0);
    assert.ok(elements.body.innerHTML.includes('没有匹配词条'));
  });
  set('q', '');
  check('Changing filters resets to first page', () => {
    assert.equal(read('page'), 0);
    assert.equal(elements.page.textContent, '1 / ' + Math.ceil(expected.length / 60));
  });
  context.escapeInput = '<script>&"\'';
  check('HTML text escaping', () => assert.equal(read('esc(escapeInput)'), '&lt;script&gt;&amp;&quot;&#39;'));
  check('Relative navigation targets exist', () => {
    const markup = html.replace(/<script(?:\s[^>]*)?>[\s\S]*?<\/script>/g, '');
    const hrefs = [...markup.matchAll(/href="([^"]+)"/g)].map(item => item[1]).filter(href => !/^[a-z]+:|^#/i.test(href));
    for (const href of hrefs) assert.ok(fs.existsSync(path.resolve(root, href)), 'Missing relative target: ' + href);
    result.local_navigation_targets = hrefs;
  });
  check('HTML and source JSON remained unchanged during verification', () => {
    assert.equal(fs.readFileSync(htmlPath, 'utf8'), html);
    assert.equal(fs.readFileSync(dataPath, 'utf8'), expectedText);
  });
} catch (error) {
  result.fatal_error = error.message;
}
result.passed_checks = result.checks.filter(check => check.status === 'passed').length;
result.failed_checks = result.checks.filter(check => check.status === 'failed').length;
result.status = result.failed_checks || result.fatal_error ? 'failed' : 'passed';
result.verified_at_utc = new Date().toISOString();
fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ status: result.status, passed_checks: result.passed_checks, failed_checks: result.failed_checks, fatal_error: result.fatal_error, expected_groups: result.expected_group_counts, report: outputPath }, null, 2));
if (result.status !== 'passed') process.exitCode = 1;
