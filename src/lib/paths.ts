import type { Lang } from './types';

/**
 * The site is served from a sub-path on GitHub Pages (/Haoma). Astro exposes
 * that as BASE_URL, so every internal link and asset goes through this module.
 */
export const BASE_PATH = import.meta.env.BASE_URL.replace(/\/+$/, '');

const STATIC_PREFIXES = [
  'library/',
  'img/',
  'audio/',
  'video/',
  'fonts/',
  'tools/',
  'css/',
  'js/',
];

/** Path inside public/, base-aware. Accepts "img/x.svg" or "/img/x.svg". */
export function asset(path: string): string {
  const clean = path.replace(/^\/+/, '');
  return `${BASE_PATH}/${clean}`;
}

/** Language-relative route -> deployable path. */
export function localRoute(lang: Lang, path: string): string {
  const clean = path.replace(/^\/+|\/+$/g, '');
  const prefix = lang === 'fa' ? 'fa/' : '';
  return `${BASE_PATH}/${prefix}${clean}${clean ? '/' : ''}`;
}

/** Absolute URL for canonical / OG tags. */
export function absoluteUrl(path: string): string {
  const site = (import.meta.env.SITE ?? '').replace(/\/+$/, '');
  return `${site}${path.startsWith('/') ? path : `/${path}`}`;
}

/** Resolve a link found in content: static asset or page route. */
export function resolveHref(destination: string, lang: Lang): string {
  if (/^(https?:|mailto:|tel:|#)/.test(destination)) return destination;

  // relref already produced a deployable path; do not prefix the base twice.
  if (BASE_PATH && (destination === BASE_PATH || destination.startsWith(`${BASE_PATH}/`))) {
    return destination;
  }

  if (!destination.startsWith('/')) return destination;

  const clean = destination.replace(/^\/+/, '');

  if (STATIC_PREFIXES.some((prefix) => clean.startsWith(prefix))) {
    return asset(clean);
  }

  // Some Farsi pages already write /fa/… explicitly; never add it twice.
  if (clean === 'fa' || clean.startsWith('fa/')) return asset(clean);
  if (clean === 'en') return localRoute('en', '');
  if (clean.startsWith('en/')) return localRoute('en', clean.slice(3));

  return localRoute(lang, clean);
}
