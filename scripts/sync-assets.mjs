/**
 * Mirror static/ into public/.
 *
 * The Hugo editor writes uploads and media into static/, so static/ stays the
 * source of truth. Astro only serves its own public/ directory, so we copy it
 * before every dev run and build.
 *
 * Deliberately non-destructive: copy over the existing public/ and prune only
 * entries whose source disappeared. Wiping the directory broke a running
 * `astro dev` (its public middleware began returning 404 for /js/*.js), which
 * silently disabled the atlas and the other client scripts.
 */
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const root = process.cwd();
const source = join(root, 'static');
const target = join(root, 'public');

if (!existsSync(source)) {
  console.warn('[sync-assets] static/ not found, skipping');
  process.exit(0);
}

const skip = new Set(['.DS_Store', '.preview-maps']);

function copyDir(from, to) {
  mkdirSync(to, { recursive: true });

  for (const entry of readdirSync(from, { withFileTypes: true })) {
    if (skip.has(entry.name)) continue;

    const src = join(from, entry.name);
    const dest = join(to, entry.name);

    if (entry.isDirectory()) {
      copyDir(src, dest);
    } else if (entry.isFile()) {
      cpSync(src, dest);
    }
  }
}

function pruneDir(from, to) {
  if (!existsSync(to)) return;

  for (const entry of readdirSync(to, { withFileTypes: true })) {
    if (skip.has(entry.name)) continue;

    const src = join(from, entry.name);
    const dest = join(to, entry.name);

    if (!existsSync(src)) {
      rmSync(dest, { recursive: true, force: true });
    } else if (entry.isDirectory()) {
      pruneDir(src, dest);
    }
  }
}

copyDir(source, target);
pruneDir(source, target);

console.log(`[sync-assets] static/ -> public/ (${relative(root, target).split(sep).join('/')})`);
