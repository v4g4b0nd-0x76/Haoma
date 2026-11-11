export type Lang = 'en' | 'fa';

export type PageKind =
  | 'culture-index'
  | 'culture-hub'
  | 'section'
  | 'article'
  | 'episodes-index'
  | 'episode'
  | 'list'
  | 'single';

/** Front matter as it is actually written across content/ (see AI.md §3). */
export interface Frontmatter {
  title: string;
  tagline?: string;
  culture?: string;
  /** Section slug inherited through cascade; not usually written directly. */
  sec?: string;
  quote?: string;
  quoteSource?: string;
  atlas_path?: string[];
  cascade?: {
    culture?: string;
    sec?: string;
    draft?: boolean;
  };
  wide?: boolean;
  grade?: string;
  reviewed?: string;
  pronounce?: string;
  subculture?: string;
  themes?: string[];
  facts?: string[];
  sources?: string[];
  related?: string[];
  card_bg?: string;
  card_bg_kind?: 'static' | 'gif';
  pair?: string[];
  date?: string;
  audio?: string;
  youtube?: string;
  spotify?: string;
  draft?: boolean;
  dropcap?: boolean;
}

export interface Page {
  lang: Lang;
  /** Content id without extension, e.g. "cultures/iranian/characters/mehr". */
  id: string;
  /** Language-relative route with trailing slash, e.g. "/cultures/iranian/". */
  route: string;
  /** Top-level folder, e.g. "cultures" or "episodes". */
  section: string;
  kind: PageKind;
  culture?: string;
  sec?: string;
  slug: string;
  title: string;
  date?: string;
  frontmatter: Frontmatter;
  /** Raw Markdown body, shortcodes included. */
  body: string;
  filePath: string;
  children: Page[];
  translations: Partial<Record<Lang, Page>>;
}

export interface ContentIndex {
  pages: Page[];
  byLangId: Record<Lang, Map<string, Page>>;
  /** Pages grouped by language, ordered for listings. */
  byLang: Record<Lang, Page[]>;
}

export interface ShortcodeBlock {
  type: 'shortcode';
  name: string;
  attrs: Record<string, string>;
  positional: string[];
  body: string;
  blocks?: Block[];
  raw: string;
}

export interface MarkdownBlock {
  type: 'markdown';
  source: string;
}

export type Block = MarkdownBlock | ShortcodeBlock;
