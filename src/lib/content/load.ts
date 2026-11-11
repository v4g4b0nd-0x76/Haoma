import { readdirSync, readFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import matter from 'gray-matter';
import type { ContentIndex, Frontmatter, Lang, Page, PageKind } from '../types';

const LANGS: Lang[] = ['en', 'fa'];
const CONTENT_ROOT = join(process.cwd(), 'content');
const INCLUDE_DRAFTS = process.env.INCLUDE_DRAFTS === '1';

interface RawEntry {
  id: string;
  filePath: string;
  data: Frontmatter;
  body: string;
}

let cache: ContentIndex | null = null;

/**
 * Build the whole content index once. 100 Markdown files, read at build time —
 * no database, no server, no generated copies.
 */
export function getContent(): ContentIndex {
  if (!cache) cache = buildIndex();
  return cache;
}

function buildIndex(): ContentIndex {
  const rawMaps: Record<Lang, Map<string, RawEntry>> = {
    en: new Map(),
    fa: new Map(),
  };
  const byLangId: Record<Lang, Map<string, Page>> = {
    en: new Map(),
    fa: new Map(),
  };

  for (const lang of LANGS) {
    for (const file of markdownFiles(join(CONTENT_ROOT, lang))) {
      const id = pageId(file);
      if (!id) continue;

      const parsed = matter(readFileSync(file, 'utf8'));
      rawMaps[lang].set(id, {
        id,
        filePath: file,
        data: normalizeFrontmatter(parsed.data as Frontmatter),
        body: parsed.content,
      });
    }
  }

  for (const lang of LANGS) {
    const raws = rawMaps[lang];
    for (const raw of raws.values()) {
      if (!INCLUDE_DRAFTS && isDraft(raws, raw.id)) continue;
      byLangId[lang].set(raw.id, toPage(lang, raw, raws));
    }
  }

  linkTranslations(byLangId);

  const byLang: Record<Lang, Page[]> = { en: [], fa: [] };
  for (const lang of LANGS) {
    const pages = [...byLangId[lang].values()];
    const parentOf = new Map(pages.map((page) => [page.id, parentId(page.id)]));

    for (const page of pages) {
      page.children = pages
        .filter((candidate) => parentOf.get(candidate.id) === page.id)
        .sort(comparePages);
    }

    byLang[lang] = pages;
  }

  return { pages: [...byLang.en, ...byLang.fa], byLangId, byLang };
}

function toPage(lang: Lang, raw: RawEntry, raws: Map<string, RawEntry>): Page {
  const kind = kindFor(raw.id);
  const parts = raw.id.split('/');

  return {
    lang,
    id: raw.id,
    route: `/${raw.id}/`,
    section: parts[0],
    kind,
    culture: resolveField(raws, raw.id, 'culture'),
    sec: resolveField(raws, raw.id, 'sec'),
    slug: parts[parts.length - 1],
    title: raw.data.title ?? parts[parts.length - 1],
    date: isoDate(raw.data.date),
    frontmatter: raw.data,
    body: raw.body,
    filePath: raw.filePath,
    children: [],
    translations: {},
  };
}

function linkTranslations(byLangId: Record<Lang, Map<string, Page>>): void {
  for (const lang of LANGS) {
    const other: Lang = lang === 'en' ? 'fa' : 'en';
    for (const [id, page] of byLangId[lang]) {
      page.translations[lang] = page;
      const twin = byLangId[other].get(id);
      if (twin) {
        page.translations[other] = twin;
        twin.translations[lang] = page;
      }
    }
  }
}

/* ------------------------------------------------------------------ paths */

function markdownFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) return markdownFiles(full);
    return entry.isFile() && entry.name.endsWith('.md') ? [full] : [];
  });
}

/** content/en/cultures/iranian/_index.md -> "cultures/iranian" */
function pageId(file: string): string {
  const relativePath = relative(CONTENT_ROOT, file).split(sep).slice(1).join('/');
  const parts = relativePath.replace(/\.md$/, '').split('/');
  const last = parts[parts.length - 1];
  if (last === '_index' || last === 'index') parts.pop();
  return parts.join('/');
}

function parentId(id: string): string {
  return id.split('/').slice(0, -1).join('/');
}

function kindFor(id: string): PageKind {
  const parts = id.split('/');
  const top = parts[0];

  if (top === 'cultures') {
    if (parts.length === 1) return 'culture-index';
    if (parts.length === 2) return 'culture-hub';
    if (parts.length === 3) return 'section';
    return 'article';
  }
  if (top === 'episodes') return parts.length === 1 ? 'episodes-index' : 'episode';
  if (top === 'compare') return parts.length === 1 ? 'list' : 'single';
  return parts.length === 1 ? 'list' : 'single';
}

/* --------------------------------------------------------------- cascade */

/** Deepest id first, e.g. [leaf, section, culture, cultures]. */
function ancestorIds(id: string): string[] {
  const parts = id.split('/');
  return parts.map((_part, index) => parts.slice(0, parts.length - index).join('/'));
}

function resolveField(
  raws: Map<string, RawEntry>,
  id: string,
  key: 'culture' | 'sec',
): string | undefined {
  for (const ancestor of ancestorIds(id)) {
    const data = raws.get(ancestor)?.data;
    if (!data) continue;

    const value =
      ancestor === id
        ? (data[key] ?? data.cascade?.[key])
        : data.cascade?.[key];

    if (value) return value;
  }
  return undefined;
}

function isDraft(raws: Map<string, RawEntry>, id: string): boolean {
  return ancestorIds(id).some((ancestor) => {
    const data = raws.get(ancestor)?.data;
    if (!data) return false;
    return data.draft === true || data.cascade?.draft === true;
  });
}

/* ---------------------------------------------------------------- helpers */

function normalizeFrontmatter(data: Frontmatter): Frontmatter {
  return {
    ...data,
    reviewed: isoDate(data.reviewed),
    date: isoDate(data.date),
  };
}

function isoDate(value: unknown): string | undefined {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === 'string' && value) return value;
  return undefined;
}

function comparePages(a: Page, b: Page): number {
  if (a.date && b.date) return b.date.localeCompare(a.date);
  return a.title.localeCompare(b.title);
}

/* ---------------------------------------------------------------- queries */

export function resolvePath(index: ContentIndex, lang: Lang, path: string): Page | undefined {
  const id = path.replace(/^\/+|\/+$/g, '');
  return index.byLangId[lang].get(id);
}

export function cultures(index: ContentIndex, lang: Lang): Page[] {
  return index.byLangId[lang].get('cultures')?.children ?? [];
}

export function episodes(index: ContentIndex, lang: Lang): Page[] {
  return (index.byLangId[lang].get('episodes')?.children ?? []).slice().sort(comparePages);
}

export function leaves(index: ContentIndex, lang: Lang): Page[] {
  return index.byLang[lang]
    .filter((page) => page.kind === 'article')
    .sort(comparePages);
}

export function pageHref(page: Page): string {
  return page.lang === 'fa' ? `${'/fa'}${page.route}` : page.route;
}
