import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse } from 'smol-toml';
import type { Lang } from '../types';

type Dictionary = Record<string, string>;
type TomlFile = Record<string, { other?: string }>;

let cache: Record<Lang, Dictionary> | null = null;

function readDictionary(lang: Lang): Dictionary {
  const file = join(process.cwd(), 'i18n', `${lang}.toml`);
  const parsed = parse(readFileSync(file, 'utf8')) as unknown as TomlFile;
  return Object.fromEntries(
    Object.entries(parsed).map(([key, value]) => [
      key,
      typeof value?.other === 'string' ? value.other : String(value),
    ]),
  );
}

function load(): Record<Lang, Dictionary> {
  if (!cache) {
    cache = { en: readDictionary('en'), fa: readDictionary('fa') };
  }
  return cache;
}

export function dictionary(lang: Lang): Dictionary {
  return load()[lang];
}

/** UI string with English fallback, then the key itself. */
export function t(lang: Lang, key: string): string {
  const dicts = load();
  return dicts[lang][key] ?? dicts.en[key] ?? key;
}

export function hasTranslation(lang: Lang, key: string): boolean {
  return key in load()[lang];
}
