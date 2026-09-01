#!/usr/bin/env node
/**
 * apply-seo.mjs — optionally inject SEO_HEAD.html snippet into ../index.html
 * By default DRY-RUN (prints diff). Use --write to actually patch.
 * Keeps canonical fallback: injection is idempotent and reversible (--revert).
 *
 * Usage:
 *   node scripts/apply-seo.mjs           # dry-run, show what would change
 *   node scripts/apply-seo.mjs --write   # inject
 *   node scripts/apply-seo.mjs --revert  # remove injected block
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WEB = resolve(__dirname, '..');
const ROOT = resolve(WEB, '..');
const IDX = join(ROOT, 'index.html');
const SNIPPET = join(WEB, 'SEO_HEAD.html');
const MARK_START = '<!-- SEO_HEAD injected by web/scripts/apply-seo.mjs — start -->';
const MARK_END = '<!-- SEO_HEAD injected — end -->';

const args = process.argv.slice(2);
const doWrite = args.includes('--write');
const doRevert = args.includes('--revert');

if (!existsSync(IDX)) { console.error('missing', IDX); process.exit(1); }
if (!existsSync(SNIPPET)) { console.error('missing', SNIPPET); process.exit(1); }

let html = readFileSync(IDX, 'utf-8');
let snippet = readFileSync(SNIPPET, 'utf-8').trim();

function hasInjected(h) { return h.includes(MARK_START); }
function inject(h) {
  if (hasInjected(h)) return h;
  // inject right after <title> line, before <link rel="preconnect"
  const wrapped = `${MARK_START}\n${snippet}\n${MARK_END}`;
  // find insertion point
  if (h.includes('<link rel="preconnect" href="https://cdn.jsdelivr.net">')) {
    return h.replace(
      '<link rel="preconnect" href="https://cdn.jsdelivr.net">',
      `${wrapped}\n<link rel="preconnect" href="https://cdn.jsdelivr.net">`
    );
  }
  // fallback: after </title>
  return h.replace('</title>', `</title>\n${wrapped}`);
}
function revert(h) {
  if (!hasInjected(h)) return h;
  const re = new RegExp(`${escapeReg(MARK_START)}[\\s\\S]*?${escapeReg(MARK_END)}\\n?`, 'g');
  return h.replace(re, '');
}
function escapeReg(s){ return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

if (doRevert) {
  if (!hasInjected(html)) { console.log('No injected block found — nothing to revert.'); process.exit(0); }
  const out = revert(html);
  if (doWrite) { writeFileSync(IDX, out, 'utf-8'); console.log('✓ reverted', IDX); }
  else { console.log('DRY-RUN revert would remove block (', (html.length - out.length), 'chars ) . Pass --write to confirm.'); }
  process.exit(0);
}

if (hasInjected(html)) {
  console.log('Already injected — no change. Use --revert to remove.');
  process.exit(0);
}

const out = inject(html);
console.log(`Dry-run: would inject ${snippet.length} chars into ${IDX}`);
console.log(`  original: ${html.length.toLocaleString()} bytes`);
console.log(`  patched : ${out.length.toLocaleString()} bytes (+${(out.length - html.length).toLocaleString()})`);
console.log('  location: after <title>, before cdn preconnect');
if (doWrite) {
  writeFileSync(IDX, out, 'utf-8');
  console.log('✓ wrote', IDX);
} else {
  console.log('  pass --write to apply');
}
