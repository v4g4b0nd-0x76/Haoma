import rss from '@astrojs/rss';
import { episodes, getContent } from '@/lib/content/load';
import { absoluteUrl, localRoute } from '@/lib/paths';
import type { Lang } from '@/lib/types';

export function feed(lang: Lang) {
  const index = getContent();
  const site = lang === 'fa' ? 'هوم' : 'Haoma';

  return rss({
    title: site,
    description: 'A bilingual mythology podcast and wiki.',
    site: absoluteUrl('/'),
    items: episodes(index, lang).map((episode) => ({
      title: episode.title,
      description: episode.frontmatter.tagline ?? '',
      link: absoluteUrl(localRoute(lang, episode.route)),
      pubDate: episode.date ? new Date(episode.date) : new Date(),
    })),
  });
}
