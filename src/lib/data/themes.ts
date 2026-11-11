import themesJson from '../../../data/themes.json';

export interface Theme {
  accent: string;
  bg: string;
  surface: string;
  border: string;
  text: string;
  muted: string;
  anim: 'fall' | 'drift' | 'rise' | 'none';
  pattern: 'none' | 'meander' | 'rosette' | 'zigzag' | 'waves';
  glyphs: string;
  banner: string;
}

export const themes = themesJson as Record<string, Theme>;

export function themeFor(culture?: string): Theme {
  return themes[culture ?? 'base'] ?? themes.base;
}
