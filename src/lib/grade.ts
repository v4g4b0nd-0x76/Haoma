/** Grade labels map both English and Farsi values used in front matter. */
import { t } from './i18n';
import type { Lang } from './types';

const GRADE_KEYS: Record<string, string> = {
  'primary text': 'gradePrimary',
  primary: 'gradePrimary',
  'later compilation': 'gradeLater',
  later: 'gradeLater',
  archaeology: 'gradeArchaeology',
  'modern scholarship': 'gradeScholarship',
  scholarship: 'gradeScholarship',
  draft: 'gradeDraft',
  guide: 'gradeGuide',
};

export function gradeKey(value: string): string {
  return GRADE_KEYS[value.trim().toLowerCase()] ?? value;
}

export function gradeLabel(lang: Lang, value: string): string {
  return t(lang, gradeKey(value));
}
