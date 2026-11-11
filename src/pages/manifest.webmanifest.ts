import type { APIRoute } from 'astro';
import { webmanifest } from '@/lib/manifest';

export const prerender = true;

export const GET: APIRoute = () =>
  new Response(JSON.stringify(webmanifest('en')), {
    headers: { 'content-type': 'application/manifest+json; charset=utf-8' },
  });
