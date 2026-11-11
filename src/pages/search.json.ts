import type { APIRoute } from 'astro';
import { searchIndex } from '@/lib/content/indexes';

export const prerender = true;

export const GET: APIRoute = () =>
  new Response(JSON.stringify(searchIndex('en')), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
