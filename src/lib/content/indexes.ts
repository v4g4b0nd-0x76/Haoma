import { getContent, resolvePath } from './load';
import { localRoute } from '../paths';
import type { Lang, Page } from '../types';

/** Shapes match layouts/index.searchindex.json and index.relatedindex.json. */

export interface SearchItem {
  t: string;
  g?: string;
  b?: string;
  u: string;
  c?: string;
  k?: string;
  m?: string;
}

export interface RelatedPage {
  k: string;
  u: string;
  t: string;
  g?: string;
  c?: string;
  s?: string;
  m: string[];
  r: string[];
}

export function searchIndex(lang: Lang): { lang: Lang; items: SearchItem[] } {
  const index = getContent();

  const items = index.byLang[lang]
    .filter((page) => page.kind !== 'culture-index')
    .map((page) => ({
      t: page.title,
      g: page.frontmatter.tagline,
      b: plain(page.body).slice(0, 480),
      u: localRoute(lang, page.route),
      c: page.culture,
      k: kindOf(page),
      m: (page.frontmatter.themes ?? []).join(' '),
    }));

  return { lang, items };
}

export function relatedIndex(lang: Lang): { lang: Lang; pages: RelatedPage[] } {
  const index = getContent();

  const pages = index.byLang[lang]
    .filter((page) => page.kind === 'article' || page.kind === 'episode' || page.kind === 'single')
    .map((page) => ({
      k: page.route,
      u: localRoute(lang, page.route),
      t: page.title,
      g: page.frontmatter.tagline,
      c: page.culture,
      s: page.kind === 'episode' ? 'episode' : page.sec,
      m: page.frontmatter.themes ?? [],
      r: (page.frontmatter.related ?? []).map((path) => {
        const resolved = resolvePath(index, lang, path);
        return resolved ? resolved.route : path.replace(/^\/+|\/+$/g, '/');
      }),
    }));

  return { lang, pages };
}

function kindOf(page: Page): string {
  if (page.kind === 'episode') return 'episode';
  if (page.sec) return page.sec;
  if (page.culture) return 'culture';
  return 'page';
}

function plain(body: string): string {
  return body
    .replace(/\{\{<\s*([\w-]+)[^}]*>\}\}[\s\S]*?\{\{<\s*\/\s*\1\s*>\}\}/g, ' ')
    .replace(/\{\{[<%][\s\S]*?[>%]\}\}/g, ' ')
    .replace(/\{\{[<%]\s*\/[\s\S]*?[>%]\}\}/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[#>*_`~[\]()!|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
