import { formatCurrency, formatKg } from '../utils/formatters.js';

export default function SummaryCards({ streamSummary, recommendationSummary, agentSummary }) {
  const cards = [
    {
      label: 'Material streams',
      value: streamSummary?.total_streams ?? recommendationSummary?.total_recommendations ?? '—',
      helper: 'Rows currently loaded',
    },
    {
      label: 'Annual quantity reviewed',
      value: formatKg(streamSummary?.total_annual_quantity_kg),
      helper: 'Calculated from uploaded monthly quantities',
    },
    {
      label: 'Human review required',
      value: recommendationSummary?.human_review_required ?? agentSummary?.human_review_required ?? '—',
      helper: 'High-risk or evidence-sensitive streams',
    },
    {
      label: 'Estimated annual cost exposure',
      value: formatCurrency(recommendationSummary?.total_estimated_annual_disposal_cost_avoided ?? streamSummary?.total_annual_disposal_cost),
      helper: 'Screening estimate, not verified savings',
    },
  ];

  return (
    <section className="summary-grid">
      {cards.map((card) => (
        <article className="summary-card" key={card.label}>
          <span>{card.label}</span>
          <strong>{card.value}</strong>
          <small>{card.helper}</small>
        </article>
      ))}
    </section>
  );
}
