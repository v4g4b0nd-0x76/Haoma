import { getContent } from './load';
import type { Lang } from '../types';

export interface StaticRoute {
  lang: Lang;
  /** Content id, or null for the home page. */
  id: string | null;
  /** URL segments after the base path, e.g. ["fa", "cultures", "iranian"]. */
  segments: string[];
}

/** Every URL the static build must emit, in both languages. */
export function getStaticRoutes(): StaticRoute[] {
  const index = getContent();
  const routes: StaticRoute[] = [];

  for (const lang of ['en', 'fa'] as const) {
    const languagePrefix = lang === 'fa' ? ['fa'] : [];
    routes.push({ lang, id: null, segments: languagePrefix });

    for (const page of index.byLang[lang]) {
      routes.push({
        lang,
        id: page.id,
        segments: [...languagePrefix, ...page.id.split('/')],
      });
    }
  }

  return routes;
}
