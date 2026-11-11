import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { asset } from '../paths';
import type { Lang } from '../types';

interface LocalizedText {
  en?: string;
  fa?: string;
}

interface ManifestFile {
  title?: LocalizedText | string;
  kind?: string;
  url?: string;
  href?: string;
  categories?: string[];
}

interface Manifest {
  categories?: { id: string; title: LocalizedText | string; pages?: string[] }[];
  files?: Record<string, ManifestFile>;
}

export interface LibraryEntry {
  name: string;
  title: string;
  ext: string;
  kind: string;
  cats: string[];
  catLabels: string[];
  href: string;
}

export interface LibraryData {
  entries: LibraryEntry[];
  categories: { id: string; label: string }[];
}

const KIND_BY_EXT: Record<string, string> = {
  pdf: 'pdf',
  epub: 'epub',
  md: 'md',
  markdown: 'md',
  txt: 'text',
  png: 'image',
  jpg: 'image',
  jpeg: 'image',
  gif: 'image',
  webp: 'image',
  svg: 'image',
};

export function libraryData(lang: Lang): LibraryData {
  const root = join(process.cwd(), 'static', 'library');
  if (!existsSync(root)) return { entries: [], categories: [] };

  const manifestFile = join(root, 'manifest.json');
  const manifest: Manifest = existsSync(manifestFile)
    ? (JSON.parse(readFileSync(manifestFile, 'utf8')) as Manifest)
    : {};

  const categoryLabel = new Map<string, string>();
  const categories = (manifest.categories ?? []).map((category) => {
    const label = localize(category.title, lang) || category.id;
    categoryLabel.set(category.id, label);
    return { id: category.id, label };
  });

  const entries: LibraryEntry[] = [];
  const seen = new Set<string>();

  for (const name of readdirSync(root)) {
    if (
      name === 'README.md' ||
      name === '.gitkeep' ||
      name === 'manifest.json' ||
      name.startsWith('.')
    ) {
      continue;
    }

    const ext = extension(name);
    const meta = manifest.files?.[name] ?? {};
    const remote = meta.url ?? meta.href ?? '';
    const cats = meta.categories ?? [];

    entries.push({
      name,
      title: localize(meta.title, lang) || titleFromName(name),
      ext,
      kind: meta.kind ?? KIND_BY_EXT[ext] ?? 'file',
      cats,
      catLabels: cats.map((id) => categoryLabel.get(id)).filter((value): value is string => Boolean(value)),
      href: /^https?:\/\//.test(remote) ? remote : asset(`library/${name}`),
    });
    seen.add(name);
  }

  for (const [name, meta] of Object.entries(manifest.files ?? {})) {
    if (!meta || seen.has(name)) continue;

    const remote = meta.url ?? meta.href ?? '';
    if (!/^https?:\/\//.test(remote)) continue;

    const ext = extension(name) || extension(remote);
    const cats = meta.categories ?? [];

    entries.push({
      name,
      title: localize(meta.title, lang) || titleFromName(name),
      ext,
      kind: meta.kind ?? KIND_BY_EXT[ext] ?? 'file',
      cats,
      catLabels: cats.map((id) => categoryLabel.get(id)).filter((value): value is string => Boolean(value)),
      href: remote,
    });
  }

  return { entries, categories };
}

function localize(value: LocalizedText | string | undefined, lang: Lang): string {
  if (!value) return '';
  if (typeof value === 'string') return value;
  return value[lang] ?? value.en ?? value.fa ?? '';
}

function extension(value: string): string {
  return value.split('.').pop()?.toLowerCase() ?? '';
}

function titleFromName(name: string): string {
  return name
    .replace(/\.[^.]+$/, '')
    .replace(/[.\-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
