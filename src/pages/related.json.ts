import type { APIRoute } from 'astro';
import { relatedIndex } from '@/lib/content/indexes';

export const prerender = true;

export const GET: APIRoute = () =>
  new Response(JSON.stringify(relatedIndex('en')), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
