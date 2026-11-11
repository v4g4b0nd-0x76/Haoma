import { Marked } from 'marked';
import { gfmHeadingId } from 'marked-gfm-heading-id';
import GithubSlugger from 'github-slugger';
import { resolveHref } from '../paths';
import type { Lang } from '../types';
import { restoreEscapes } from './parse';

const instances = new Map<Lang, Marked>();

function instance(lang: Lang): Marked {
  let marked = instances.get(lang);
  if (!marked) {
    marked = new Marked({ gfm: true, breaks: false });
    marked.use(gfmHeadingId());
    instances.set(lang, marked);
  }
  return marked;
}

/**
 * Render one Markdown chunk to HTML and make every root-absolute link or image
 * language/base aware. Content is trusted repository text.
 */
export function renderMarkdown(source: string, lang: Lang): string {
  let html = instance(lang).parse(source) as string;

  html = transformCodeBlocks(html);

  const rewritten = html
    .replace(
      /\b(href|src)="([^"]*)"/g,
      (_match, attr: string, value: string) =>
        `${attr}="${escapeAttribute(resolveHref(decodeEntities(value), lang))}"`,
    )
    .replace(/id="([^"]*)"/g, (_match, value: string) => {
      const id = value.replace(/[\u200C\u0654]/g, '');
      return `id="${id}"`;
    });

  return restoreEscapes(rewritten);
}

export interface TocEntry {
  id: string;
  text: string;
  depth: number;
}

/**
 * Hugo's `markdownify` drops the wrapper paragraph when a shortcode body is a
 * single paragraph. Used by disagree/recon.
 */
export function renderInlineBody(source: string, lang: Lang): string {
  const html = renderMarkdown(source, lang).trim();
  const paragraphs = html.match(/<p>/g)?.length ?? 0;
  if (paragraphs === 1 && html.startsWith('<p>') && html.endsWith('</p>')) {
    return html.slice(3, -4);
  }
  return html;
}

/** Build the on-page table of contents from Markdown headings (h2/h3). */
export function extractToc(source: string): TocEntry[] {
  const slugger = new GithubSlugger();
  const entries: TocEntry[] = [];
  let insideFence = false;

  for (const line of source.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) {
      insideFence = !insideFence;
      continue;
    }
    if (insideFence) continue;

    const heading = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(line);
    if (!heading) continue;

    const depth = heading[1].length;
    const text = stripInline(heading[2]);
    const slug = text.replace(/[\u200C\u0654]/g, '');
    const id = slugger.slug(slug);

    if (depth === 2 || depth === 3) entries.push({ id, text, depth });
  }

  return entries;
}

function stripInline(value: string): string {
  return value
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[*_`~]/g, '')
    .trim();
}

function transformCodeBlocks(html: string): string {
  return html.replace(
    /<pre><code(?: class="language-([^"]+)")?>([\s\S]*?)<\/code><\/pre>/g,
    (_match, language: string | undefined, code: string) => {
      const name = language || 'text';
      const body = code
        .replace(/\n$/, '')
        .split('\n')
        .map((line) => {
          const rendered =
            name === 'bash'
              ? line.replace(/(#[^\n]*)$/, '<span style="color:#75715e">$1</span>')
              : line;
          return `<span style="display:flex;"><span>${rendered}</span></span>`;
        })
        .join('\n');

      return `<div class="highlight"><pre tabindex="0" style="color:#f8f8f2;background-color:#272822;-moz-tab-size:4;-o-tab-size:4;tab-size:4;"><code class="language-${name}" data-lang="${name}">${body}</code></pre></div>`;
    },
  );
}

function decodeEntities(value: string): string {
  return value
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function escapeAttribute(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
}
