#!/usr/bin/env node
/**
 * sync.mjs — SocialPulse web layer sync
 * Copies canonical ../index.html + ../data/* + ../assets/* into web/dist (and optionally web/public)
 * so that `web/` can be deployed as an isolated static host (Vercel/Netlify web root = web/dist)
 * while keeping the canonical single-file ../index.html untouched (fallback for file://).
 *
 * Zero dependencies — Node stdlib only.
 * Usage:
 *   node scripts/sync.mjs
 *   node scripts/sync.mjs --public   # also sync to public/ (for Netlify publish = public)
 *   npm run sync
 */

import { cpSync, mkdirSync, existsSync, statSync, readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WEB = resolve(__dirname, '..');
const ROOT = resolve(WEB, '..');
const DIST = join(WEB, 'dist');
const PUBLIC = join(WEB, 'public');

const args = process.argv.slice(2);
const alsoPublic = args.includes('--public') || args.includes('-p');

function ensureDir(p) { mkdirSync(p, { recursive: true }); }
function copyFile(src, dst) {
  ensureDir(dirname(dst));
  cpSync(src, dst, { force: true });
  const s = statSync(src).size;
  console.log(`  copied ${src.replace(ROOT+'/', '')} -> ${dst.replace(WEB+'/', '')} (${s.toLocaleString()} bytes)`);
}
function copyDir(srcDir, dstDir) {
  if (!existsSync(srcDir)) { console.log(`  skip missing ${srcDir}`); return; }
  ensureDir(dstDir);
  // Node >=16: cpSync dir
  cpSync(srcDir, dstDir, { recursive: true, force: true });
  const count = readdirSync(dstDir).length;
  console.log(`  copied dir ${srcDir.replace(ROOT+'/', '')}/ -> ${dstDir.replace(WEB+'/', '')}/ (${count} entries)`);
}

console.log('SocialPulse sync — root:', ROOT);
console.log('             web:', WEB);
console.log('            dist:', DIST);

ensureDir(DIST);

// 1. index.html (canonical)
const idxSrc = join(ROOT, 'index.html');
if (!existsSync(idxSrc)) { console.error('ERROR: ../index.html not found'); process.exit(1); }
copyFile(idxSrc, join(DIST, 'index.html'));
// also keep a readable copy name
copyFile(idxSrc, join(DIST, 'index.canonical.html'));

// 2. data
copyDir(join(ROOT, 'data'), join(DIST, 'data'));

// 3. assets
copyDir(join(ROOT, 'assets'), join(DIST, 'assets'));

// 4. report — optional (can be large .docx — include but note size)
if (existsSync(join(ROOT, 'report'))) {
  copyDir(join(ROOT, 'report'), join(DIST, 'report'));
}

// 5. web configs into dist
for (const f of ['vercel.json','netlify.toml','.htaccess','seo.json','SEO_HEAD.html']) {
  const src = join(WEB, f);
  if (existsSync(src)) copyFile(src, join(DIST, f));
}
// also public scaffolding
if (existsSync(join(WEB, 'public'))) {
  // copy public/* into dist/public (so site.webmanifest etc are reachable at /public/* and at root via rewrite)
  const pubSrc = join(WEB, 'public');
  const entries = readdirSync(pubSrc, { withFileTypes: true });
  for (const e of entries) {
    if (e.name.startsWith('.')) continue;
    // don't copy nested data copy again — dist already has data/assets
    if (e.name === 'data' || e.name === 'assets') continue;
    const src = join(pubSrc, e.name);
    const dst = join(DIST, 'public', e.name);
    if (e.isDirectory()) copyDir(src, dst);
    else copyFile(src, dst);
  }
}

// 6. write dist/README.txt
writeFileSync(join(DIST, 'README.txt'), `SocialPulse dist — generated ${new Date().toISOString()}
Canonical source: ../index.html (single-file, double-click)
This dist/ is a deploy-ready copy for hosts whose publish dir must be web/dist.
It is NOT canonical — do not edit. Regenerate via: npm run sync  (or node scripts/sync.mjs)
`);

if (alsoPublic) {
  console.log('\n--public: also syncing to public/');
  copyFile(idxSrc, join(PUBLIC, 'index.html'));
  copyDir(join(ROOT, 'data'), join(PUBLIC, 'data'));
  copyDir(join(ROOT, 'assets'), join(PUBLIC, 'assets'));
}

// quick validation
const distIdx = join(DIST, 'index.html');
const sz = statSync(distIdx).size;
console.log(`\n✓ dist ready: ${distIdx} (${sz.toLocaleString()} bytes, ${readFileSync(distIdx,'utf-8').slice(0,60).replace(/\n/g,' ')}...)`);
console.log('  deploy: vercel --cwd dist | netlify deploy --dir=dist | npx serve dist');
console.log('  local static test: npx serve dist --listen 4173 --single');
console.log('  local API test:    python3 ../web/server.py --port 8000');
