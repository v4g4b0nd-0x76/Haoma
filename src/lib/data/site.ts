import navJson from '../../../data/nav.json';
import siteJson from '../../../data/site.json';
import sectionsJson from '../../../data/site-sections.json';
import storiesJson from '../../../data/stories.json';
import type { Lang } from '../types';

export interface NavItem {
  name: string;
  url: string;
}

export const nav = navJson as Record<Lang, NavItem[]>;

export const site = siteJson as { repo: string; branch: string };

interface SectionToggle {
  enabled?: boolean;
  cultures?: Record<string, boolean>;
}

const sections = sectionsJson as Record<string, SectionToggle>;

/** Site-wide flag with optional per-culture override (data/site-sections.json). */
export function sectionEnabled(name: string, culture?: string): boolean {
  const entry = sections[name];
  if (!entry) return true;
  if (culture && entry.cultures && culture in entry.cultures) {
    return Boolean(entry.cultures[culture]);
  }
  return entry.enabled !== false;
}

export interface StoryLink {
  path: string;
  label: string;
}

export interface StoryCard {
  id: string;
  culture: string;
  title: string;
  blurb: string;
  motif: 'none' | 'rosette' | 'meander' | 'zigzag' | 'waves';
  animated?: boolean;
  links: StoryLink[];
}

const stories = storiesJson as Record<Lang, StoryCard[]>;

export function storyCards(lang: Lang, culture?: string): StoryCard[] {
  const all = stories[lang] ?? stories.en;
  if (!culture) return all;
  return all.filter((card) => card.culture === culture);
}
