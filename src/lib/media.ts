export function youtubeId(value?: string): string | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (/^[\w-]{11}$/.test(trimmed)) return trimmed;

  const patterns = [
    /youtu\.be\/([\w-]{11})/,
    /[?&]v=([\w-]{11})/,
    /\/embed\/([\w-]{11})/,
    /\/shorts\/([\w-]{11})/,
    /\/live\/([\w-]{11})/,
  ];

  for (const pattern of patterns) {
    const match = pattern.exec(trimmed);
    if (match) return match[1];
  }
  return null;
}

export function spotifyEmbed(value?: string): { type: string; id: string } | null {
  if (!value) return null;
  const trimmed = value.trim();
  const direct = /^(episode|track|album|playlist|show):([\w]+)$/.exec(trimmed);
  if (direct) return { type: direct[1], id: direct[2] };

  const linked = /open\.spotify\.com\/(episode|track|album|playlist|show)\/([\w]+)/.exec(trimmed);
  return linked ? { type: linked[1], id: linked[2] } : null;
}
