/** Hugo-compatible `urlize` for theme anchors, ids and data attributes. */
export function urlize(value: string): string {
  const slug = value
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}\s-]/gu, '')
    .trim()
    .replace(/\s+/g, '-');

  return Array.from(slug)
    .map((char) => (/^[A-Za-z0-9._~-]$/.test(char) ? char : encodeURIComponent(char)))
    .join('');
}

export function truncate(value: string, limit: number): string {
  const text = value.trim();
  return text.length > limit ? `${text.slice(0, limit - 1).trimEnd()}…` : text;
}

/** Plain-text excerpt from a Markdown body (shortcodes and markup removed). */
export function plainSummary(body: string, limit = 90): string {
  const text = body
    .replace(/\{\{<\s*([\w-]+)[^}]*>\}\}[\s\S]*?\{\{<\s*\/\s*\1\s*>\}\}/g, ' ')
    .replace(/\{\{[<%][\s\S]*?[>%]\}\}/g, ' ')
    .replace(/\{\{%[\s\S]*?%\}/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[#>*_`~[\]()!|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return truncate(text, limit);
}
