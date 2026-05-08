export function formatKg(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })} kg`;
}

export function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `£${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export function scoreLabel(score) {
  if (score >= 85) return 'strong';
  if (score >= 60) return 'moderate';
  return 'weak';
}

export function humanise(text) {
  if (!text) return '—';
  return String(text).replaceAll('_', ' ');
}
