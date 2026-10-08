import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
for (const path of ['src/games/shheep', 'scripts/shheep', 'tests/shheep']) {
  if (existsSync(resolve(root, path))) throw Error(`Private game source must not be published: ${path}`);
}
const wrapper = readFileSync(resolve(root, 'src/components/ShheepGame.astro'), 'utf8');
if (!wrapper.startsWith('---\n// Generated game artifact.')) throw Error('Use an exported game wrapper');
for (const base of ['public/shheep/game', 'dist/shheep/game']) {
  const files = readdirSync(resolve(root, base));
  if (files.length !== 2 || !files.some(f => f.endsWith('.js')) || !files.some(f => f.endsWith('.css'))) throw Error(`Unexpected game files in ${base}`);
  for (const file of files) {
    const match = /^game\.([a-f0-9]{16})\.(js|css)$/.exec(file);
    if (!match) throw Error(`Unexpected artifact: ${file}`);
    const bytes = readFileSync(resolve(root, base, file));
    if (createHash('sha256').update(bytes).digest('hex').slice(0, 16) !== match[1]) throw Error(`Artifact hash mismatch: ${file}`);
    if (!wrapper.includes(`/shheep/game/${file}`)) throw Error(`Unreferenced artifact: ${file}`);
    if (/sourceMappingURL|root\.shheep\s*=/.test(bytes.toString())) throw Error(`Source/debug data in ${file}`);
  }
}
console.log('Shheep artifacts verified: hashed JS/CSS, no private source directories or maps.');
