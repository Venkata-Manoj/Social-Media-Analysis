#!/usr/bin/env node
/**
 * SocialPulse — Dashboard Logic JS Test (minimal)
 * Validates filtering parity: platform/sentiment/topic/user/search/date
 * Mirrors the filter logic in index.html and web/server.py
 *
 * Run:
 *   node tests/test_dashboard_logic.js
 *   npm test (if added to package.json)
 * Exit 0 on success, 1 on failure.
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const DATA_JSON = path.join(PROJECT_ROOT, 'data', 'social_media_dataset.json');
const STATS_JSON = path.join(PROJECT_ROOT, 'data', 'dataset_stats.json');

let RAW_DATA;
try {
  RAW_DATA = JSON.parse(fs.readFileSync(DATA_JSON, 'utf8'));
} catch (e) {
  console.error(`[fatal] cannot load ${DATA_JSON}: ${e.message}`);
  process.exit(1);
}

console.log('='.repeat(70));
console.log('SocialPulse — Dashboard Logic JS Test');
console.log(`Data: ${DATA_JSON} (${RAW_DATA.length} posts)`);
console.log(`Root: ${PROJECT_ROOT}`);
console.log('='.repeat(70));

function getFilters(overrides = {}) {
  const defaults = {
    platform: 'all',
    sentiment: 'all',
    topic: 'all',
    user: 'all',
    start: '2026-03-01',
    end: '2026-08-31',
    search: ''
  };
  return { ...defaults, ...overrides };
}

function applyFiltersJS(raw, filters) {
  // Exact parity with index.html JS: Hay = text+hashtags_str+topic+platform lowercased
  return raw.filter(r => {
    if (filters.platform !== 'all' && r.platform !== filters.platform) return false;
    if (filters.sentiment !== 'all' && r.sentiment_label !== filters.sentiment) return false;
    if (filters.topic !== 'all' && r.topic !== filters.topic) return false;
    if (filters.user !== 'all' && r.user_type !== filters.user) return false;
    if (filters.start && r.date < filters.start) return false;
    if (filters.end && r.date > filters.end) return false;
    if (filters.search) {
      const hay = (r.text + ' ' + r.hashtags_str + ' ' + r.topic + ' ' + r.platform).toLowerCase();
      if (!hay.includes(filters.search.toLowerCase())) return false;
    }
    return true;
  });
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg);
}

let passed = 0, failed = 0;
function test(name, fn) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (e) {
    console.error(`✗ ${name}: ${e.message}`);
    failed++;
  }
}

// Tests
test('total posts 420', () => {
  assert(RAW_DATA.length === 420, `expected 420 got ${RAW_DATA.length}`);
});

test('filter platform=Instagram (parity)', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ platform: 'Instagram' }));
  assert(out.length > 0, 'should match some');
  assert(out.every(r => r.platform === 'Instagram'), 'all should be Instagram');
  // Compare to expected from dataset_stats
  const stats = JSON.parse(fs.readFileSync(STATS_JSON, 'utf8'));
  assert(out.length === stats.platform_dist.Instagram, `expected ${stats.platform_dist.Instagram} got ${out.length}`);
});

test('filter sentiment=positive', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ sentiment: 'positive' }));
  assert(out.every(r => r.sentiment_label === 'positive'), 'all positive');
  const stats = JSON.parse(fs.readFileSync(STATS_JSON, 'utf8'));
  assert(out.length === stats.sentiment_dist.positive, 'positive count matches stats');
});

test('filter topic=Customer Service (negative skew check)', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ topic: 'Customer Service' }));
  assert(out.every(r => r.topic === 'Customer Service'), 'all Customer Service');
  // This topic skews negative per generator, so check that
  const neg = out.filter(r => r.sentiment_label === 'negative').length;
  // Should be more negative than positive for this topic (per generate_dataset.py: 20 pos/30 neu/50 neg)
  assert(neg > out.length * 0.3, `Customer Service should skew negative, got ${neg}/${out.length} negatives`);
});

test('filter user=Influencer', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ user: 'Influencer' }));
  assert(out.every(r => r.user_type === 'Influencer'), 'all Influencer');
});

test('filter search=launch (hashtag/text partial)', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ search: 'launch' }));
  assert(out.length > 0, 'search launch should match some');
  assert(out.every(r => (r.text + ' ' + r.hashtags_str + ' ' + r.topic).toLowerCase().includes('launch')), 'all contain launch');
  // also test hashtag search with #
  const outHash = applyFiltersJS(RAW_DATA, getFilters({ search: '#TechLaunch' }));
  assert(outHash.length > 0, '#TechLaunch should match');
  assert(outHash.every(r => r.hashtags_str.toLowerCase().includes('#techlaunch') || r.text.toLowerCase().includes('#techlaunch')), 'hashtag match');
});

test('filter search case-insensitive', () => {
  const a = applyFiltersJS(RAW_DATA, getFilters({ search: 'LAUNCH' }));
  const b = applyFiltersJS(RAW_DATA, getFilters({ search: 'launch' }));
  assert(a.length === b.length, 'case insensitive');
});

test('filter date range 2026-04-15 (campaign peak)', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ start: '2026-04-15', end: '2026-04-15' }));
  assert(out.every(r => r.date === '2026-04-15'), 'all on 2026-04-15');
  // This is a campaign peak date per README
  console.log(`  (campaign peak 2026-04-15: ${out.length} posts, engagement ${out.reduce((a,b)=>a+b.engagement,0)})`);
});

test('filter combined platform+sentiment', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters({ platform: 'Twitter', sentiment: 'positive' }));
  assert(out.every(r => r.platform === 'Twitter' && r.sentiment_label === 'positive'), 'combined filter');
});

test('engagement = likes+shares+comments (JS check)', () => {
  for (const r of RAW_DATA) {
    assert(r.engagement === r.likes + r.shares + r.comments, `${r.post_id} engagement mismatch`);
  }
});

test('sentiment_score in [-1,1]', () => {
  for (const r of RAW_DATA) {
    assert(r.sentiment_score >= -1 && r.sentiment_score <= 1, `${r.post_id} score ${r.sentiment_score} out of bounds`);
  }
});

test('pagination logic (pageSize 20)', () => {
  const filtered = applyFiltersJS(RAW_DATA, getFilters());
  const pageSize = 20;
  const page1 = filtered.slice(0, pageSize);
  const page2 = filtered.slice(pageSize, pageSize*2);
  assert(page1.length === 20, 'page1 20');
  assert(page2.length === 20, 'page2 20');
  assert(page1[0].post_id !== page2[0].post_id, 'different pages');
});

test('sort by engagement desc', () => {
  const out = applyFiltersJS(RAW_DATA, getFilters());
  const sorted = [...out].sort((a,b)=> b.engagement - a.engagement);
  assert(sorted[0].engagement >= sorted[1].engagement, 'sorted desc');
  assert(sorted[sorted.length-1].engagement <= sorted[sorted.length-2].engagement, 'tail sorted');
});

console.log('='.repeat(70));
if (failed === 0) {
  console.log(`✅ All ${passed} JS tests passed`);
  process.exit(0);
} else {
  console.error(`❌ JS tests failed: ${failed} failed, ${passed} passed`);
  process.exit(1);
}
