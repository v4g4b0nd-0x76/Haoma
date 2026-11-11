import { parseAttributes } from './parse';

/** Structured bodies used by the map, slider, art-strip, verse and tree shortcodes. */

export interface MapPoint {
  x: number;
  y: number;
}

export interface MapPin {
  x: string;
  y: string;
  label: string;
  note?: string;
  color?: string;
  era?: string;
  id?: string;
  href?: string;
}

export interface MapRegion {
  points: MapPoint[];
  label: string;
  note?: string;
  color?: string;
  era?: string;
  id?: string;
  href?: string;
}

export interface MapData {
  pins: MapPin[];
  regions: MapRegion[];
}

export function parseMapBody(body: string): MapData {
  const pins: MapPin[] = [];
  const regions: MapRegion[] = [];

  for (const line of lines(body)) {
    if (line.startsWith('pin ')) {
      const { attrs } = parseAttributes(line.slice(4).replace(/\/\s*$/, ''));
      pins.push({
        x: attrs.x ?? '0%',
        y: attrs.y ?? '0%',
        label: attrs.label ?? '',
        note: attrs.note,
        color: attrs.color,
        era: attrs.era,
        id: attrs.id,
        href: attrs.href,
      });
    } else if (line.startsWith('region ')) {
      const { attrs } = parseAttributes(line.slice(7).replace(/\/\s*$/, ''));
      regions.push({
        points: parsePoints(attrs.points ?? ''),
        label: attrs.label ?? '',
        note: attrs.note,
        color: attrs.color,
        era: attrs.era,
        id: attrs.id,
        href: attrs.href,
      });
    }
  }

  return { pins, regions };
}

export function parsePoints(value: string): MapPoint[] {
  return value
    .trim()
    .split(/\s+/)
    .map((pair) => {
      const [x, y] = pair.split(',').map(Number);
      return { x, y };
    })
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));
}

export interface MediaItemData {
  src: string;
  caption: string;
}

/** `path | caption` lines used by slider and art-strip. */
export function parsePipeMedia(body: string): MediaItemData[] {
  return lines(body).map((line) => {
    const [src, ...caption] = line.split('|');
    return { src: src.trim(), caption: caption.join('|').trim() };
  });
}

export interface VerseLine {
  left: string;
  right?: string;
}

/** `hemistich | hemistich` lines. */
export function parseVerseBody(body: string): VerseLine[] {
  return lines(body).map((line) => {
    const [left, ...rest] = line.split('|');
    return { left: left.trim(), right: rest.join('|').trim() || undefined };
  });
}

/** One row per line, e.g. `Kronos = Rhea > Zeus`. */
export function parseTreeBody(body: string): string[] {
  return lines(body);
}

function lines(body: string): string[] {
  return body
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}
