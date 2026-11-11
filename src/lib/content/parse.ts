import { localRoute } from '../paths';
import type { Block, Lang, ShortcodeBlock } from '../types';

/**
 * Hugo shortcodes are not Markdown. This parser turns a body into a list of
 * plain-Markdown chunks and shortcode nodes, recursively for containers.
 *
 * Handles both delimiters: `{{< raw >}}` and `{{% markdown %}}`. A shortcode is
 * self-closing unless a matching closing tag exists later in the body.
 */

const MARKDOWN_BODY = new Set(['grid', 'col', 'infobox', 'disagree', 'recon', 'note']);

const TOKEN_RE = /\{\{([<%])\s*(\/?)\s*([A-Za-z][\w-]*)([\s\S]*?)([>%])\}\}/g;

interface TokenMatch {
  index: number;
  end: number;
  open: '<' | '%';
  isClose: boolean;
  name: string;
  suffix: string;
}

export function parseBlocks(source: string, lang: Lang): Block[] {
  const text = preprocess(protectEscapes(source), lang);
  const blocks: Block[] = [];
  let cursor = 0;

  while (cursor < text.length) {
    const token = nextToken(text, cursor);

    if (!token) {
      pushMarkdown(blocks, text.slice(cursor));
      break;
    }

    if (token.isClose) {
      cursor = token.end;
      continue;
    }

    pushMarkdown(blocks, text.slice(cursor, token.index));

    const { attrs, positional } = parseAttributes(token.suffix);
    const close = findClose(text, token.end, token.name, token.open);

    if (close) {
      const body = text.slice(token.end, close.index);
      const block: ShortcodeBlock = {
        type: 'shortcode',
        name: token.name,
        attrs,
        positional,
        body,
        raw: text.slice(token.index, close.end),
      };
      if (MARKDOWN_BODY.has(token.name)) {
        block.blocks = parseBlocks(body, lang);
      }
      blocks.push(block);
      cursor = close.end;
    } else {
      blocks.push({
        type: 'shortcode',
        name: token.name,
        attrs,
        positional,
        body: '',
        raw: text.slice(token.index, token.end),
      });
      cursor = token.end;
    }
  }

  return blocks;
}

function pushMarkdown(blocks: Block[], source: string): void {
  if (source.trim()) blocks.push({ type: 'markdown', source });
}

function nextToken(text: string, from: number): TokenMatch | null {
  TOKEN_RE.lastIndex = from;

  let match: RegExpExecArray | null;
  while ((match = TOKEN_RE.exec(text))) {
    const [raw, open, slash, name, suffix, close] = match;
    if (open === '<' && close !== '>') continue;
    if (open === '%' && close !== '%') continue;

    return {
      index: match.index,
      end: match.index + raw.length,
      open: open as '<' | '%',
      isClose: slash === '/',
      name,
      suffix,
    };
  }

  return null;
}

function findClose(
  text: string,
  from: number,
  name: string,
  open: '<' | '%',
): { index: number; end: number } | null {
  const pattern =
    open === '%'
      ? new RegExp(`\\{\\{%\\s*\\/\\s*${name}\\s*%\\}\\}`, 'g')
      : new RegExp(`\\{\\{<\\s*\\/\\s*${name}\\s*>\\}\\}`, 'g');

  pattern.lastIndex = from;

  const match = pattern.exec(text);
  return match ? { index: match.index, end: match.index + match[0].length } : null;
}

export interface ParsedAttributes {
  attrs: Record<string, string>;
  positional: string[];
}

/** Parse `key="value" bare=1` plus quoted positional values. */
export function parseAttributes(suffix: string): ParsedAttributes {
  const attrs: Record<string, string> = {};

  const named = /([A-Za-z_][\w-]*)\s*=\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'|([^\s"']+))/g;

  const remaining = suffix.replace(
    named,
    (_match, key: string, doubleQuoted?: string, singleQuoted?: string, bare?: string) => {
      attrs[key] = unescapeValue(doubleQuoted ?? singleQuoted ?? bare ?? '');
      return ' ';
    },
  );

  const positional = [...remaining.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((match) =>
    unescapeValue(match[1]),
  );

  return { attrs, positional };
}

function unescapeValue(value: string): string {
  return value.replace(/\\(["'\\])/g, '$1');
}

/*
 * Escaped shortcode examples used by the guide must survive parsing and render
 * as literal text, so hide them behind sentinels.
 */
const ESCAPED_RE = /\{\{<\/\*\s*([\s\S]*?)\s*\*\/>\}\}/g;

function protectEscapes(source: string): string {
  return source.replace(ESCAPED_RE, (_match, inner: string) => `\u0000${inner}\u0000`);
}

/*
 * Two shortcodes are inline rather than block-level: `relref` becomes a URL,
 * and `note` becomes a span, so both stay inside their paragraph.
 */
const RELREF_RE = /\{\{<\s*relref\s+"([^"]+)"\s*>\}\}/g;
const NOTE_RE = /\{\{<\s*note\b([^}]*?)>\}\}([\s\S]*?)\{\{<\s*\/\s*note\s*>\}\}/g;

function preprocess(source: string, lang: Lang): string {
  return source
    .replace(RELREF_RE, (_match, path: string) => localRoute(lang, path))
    .replace(NOTE_RE, (_match, rawAttrs: string, inner: string) => {
      const { attrs } = parseAttributes(rawAttrs);
      return `<span class="note" tabindex="0">${inner}<span class="note-pop" role="tooltip">${escapeHtml(attrs.text ?? '')}</span></span>`;
    });
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function restoreEscapes(html: string): string {
  return html.replace(/\u0000([\s\S]*?)\u0000/g, (_match, inner: string) => `{{< ${inner.trim()} >}}`);
}
