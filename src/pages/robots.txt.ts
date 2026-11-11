import type { APIRoute } from 'astro';
import { absoluteUrl, BASE_PATH } from '@/lib/paths';

export const prerender = true;

export const GET: APIRoute = () => {
  const body = [
    'User-agent: *',
    'Allow: /',
    'Disallow: /tools/',
    `Sitemap: ${absoluteUrl(`${BASE_PATH}/sitemap-index.xml`)}`,
    '',
  ].join('\n');

  return new Response(body, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
