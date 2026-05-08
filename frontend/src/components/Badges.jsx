import { scoreLabel } from '../utils/formatters.js';

export function RiskBadge({ value }) {
  const risk = value || 'unknown';
  return <span className={`badge risk risk-${risk}`}>{risk}</span>;
}

export function ScoreBadge({ label, value }) {
  const safeValue = Number(value ?? 0);
  return (
    <span className={`badge score score-${scoreLabel(safeValue)}`}>
      {label}: {safeValue}/100
    </span>
  );
}

export function ReviewBadge({ required }) {
  return (
    <span className={`badge review ${required ? 'review-required' : 'review-clear'}`}>
      {required ? 'Human review' : 'Rules-cleared'}
    </span>
  );
}
