import { asset } from './paths';
import { t } from './i18n';
import type { Lang } from './types';

/** Per-language PWA manifest, matching layouts/index.webmanifest. */
export function webmanifest(lang: Lang): Record<string, unknown> {
  const name = lang === 'fa' ? 'هوم' : 'Haoma';
  const short = lang === 'fa' ? 'هوم' : 'Haoma';
  const home = lang === 'fa' ? '/fa/' : '/';
  const base = import.meta.env.BASE_URL;

  return {
    id: `haoma-${lang}`,
    name,
    short_name: short,
    description: 'A bilingual mythology podcast and wiki.',
    lang,
    dir: lang === 'fa' ? 'rtl' : 'ltr',
    start_url: `${base}${home.replace(/^\//, '')}`,
    scope: base,
    display: 'standalone',
    background_color: '#14161a',
    theme_color: '#14161a',
    icons: [
      { src: asset('img/brand/favicon-192.png'), sizes: '192x192', type: 'image/png' },
      { src: asset('img/brand/favicon-512.png'), sizes: '512x512', type: 'image/png' },
      {
        src: asset('img/brand/favicon-512.png'),
        sizes: '512x512',
        type: 'image/png',
        purpose: 'maskable',
      },
    ],
    shortcuts: [
      {
        name: lang === 'fa' ? 'قسمت‌ها' : 'Episodes',
        short_name: lang === 'fa' ? 'قسمت‌ها' : 'Episodes',
        url: `${base}${lang === 'fa' ? 'fa/' : ''}episodes/`,
      },
      {
        name: lang === 'fa' ? 'داستان‌ها' : 'Stories',
        short_name: lang === 'fa' ? 'داستان‌ها' : 'Stories',
        url: `${base}${lang === 'fa' ? 'fa/' : ''}#story-rail-h`,
      },
      {
        name: t(lang, 'pwaShortcutReadingList'),
        short_name: t(lang, 'pwaShortcutReadingListShort'),
        description: t(lang, 'pwaShortcutReadingListDesc'),
        url: `${base}${lang === 'fa' ? 'fa/' : ''}#reading-list`,
      },
    ],
  };
}
