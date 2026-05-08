export function getStreamForRecommendation(rec, streams) {
  return streams.find((stream) => stream.stream_id === rec.stream_id) || null;
}

export function enrichRecommendations(recommendations, streams) {
  return recommendations.map((rec) => ({
    ...rec,
    stream: getStreamForRecommendation(rec, streams),
  }));
}

export function normaliseNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function sumBy(items, selector) {
  return items.reduce((total, item) => total + normaliseNumber(selector(item)), 0);
}

export function countBy(items, selector) {
  return items.reduce((acc, item) => {
    const key = selector(item) || 'unknown';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

export function sumGroupBy(items, groupSelector, valueSelector) {
  return items.reduce((acc, item) => {
    const key = groupSelector(item) || 'unknown';
    acc[key] = (acc[key] || 0) + normaliseNumber(valueSelector(item));
    return acc;
  }, {});
}

export function mapObjectToSortedRows(map, { labelKey = 'label', valueKey = 'value', limit = 10 } = {}) {
  return Object.entries(map)
    .map(([label, value]) => ({ [labelKey]: label, [valueKey]: value }))
    .sort((a, b) => b[valueKey] - a[valueKey])
    .slice(0, limit);
}

export function getPriorityScore(rec) {
  const confidence = normaliseNumber(rec.confidence_score);
  const evidence = normaliseNumber(rec.evidence_quality_score);
  const diversion = Math.min(normaliseNumber(rec.estimated_annual_waste_diverted_kg) / 1000, 40);
  const cost = Math.min(normaliseNumber(rec.estimated_annual_disposal_cost_avoided) / 250, 35);
  const reviewPenalty = rec.human_review_required ? 35 : 0;
  const riskPenalty = rec.risk_level === 'blocked' ? 50 : rec.risk_level === 'high' ? 35 : rec.risk_level === 'medium' ? 14 : 0;
  return Math.max(0, Math.round(confidence * 0.34 + evidence * 0.26 + diversion + cost - reviewPenalty - riskPenalty));
}

export function classifyPriority(rec) {
  if (rec.human_review_required || ['high', 'blocked'].includes(rec.risk_level)) return 'controlled review';
  const score = getPriorityScore(rec);
  if (score >= 88) return 'quick win';
  if (score >= 68) return 'opportunity development';
  return 'evidence improvement';
}

export function buildDashboardData(recommendations, streams) {
  const enriched = enrichRecommendations(recommendations, streams).map((rec) => ({
    ...rec,
    priority_band: classifyPriority(rec),
    priority_score: getPriorityScore(rec),
  }));

  const riskBreakdown = mapObjectToSortedRows(countBy(enriched, (rec) => rec.risk_level), {
    labelKey: 'risk',
    valueKey: 'count',
  });
  const strategyBreakdown = mapObjectToSortedRows(countBy(enriched, (rec) => rec.circular_strategy_category), {
    labelKey: 'strategy',
    valueKey: 'count',
  });
  const priorityBreakdown = mapObjectToSortedRows(countBy(enriched, (rec) => rec.priority_band), {
    labelKey: 'priority',
    valueKey: 'count',
  });
  const materialQuantity = mapObjectToSortedRows(sumGroupBy(streams, (stream) => stream.material, (stream) => stream.monthly_quantity_kg * 12), {
    labelKey: 'material',
    valueKey: 'annualKg',
  });
  const topCostCandidates = [...enriched]
    .sort((a, b) => normaliseNumber(b.estimated_annual_disposal_cost_avoided) - normaliseNumber(a.estimated_annual_disposal_cost_avoided))
    .slice(0, 6);
  const topDiversionCandidates = [...enriched]
    .sort((a, b) => normaliseNumber(b.estimated_annual_waste_diverted_kg) - normaliseNumber(a.estimated_annual_waste_diverted_kg))
    .slice(0, 6);
  const evidenceGaps = enriched.filter((rec) => normaliseNumber(rec.evidence_quality_score) < 70).length;
  const reviewRequired = enriched.filter((rec) => rec.human_review_required).length;
  const quickWins = enriched.filter((rec) => rec.priority_band === 'quick win').length;
  const controlledReview = enriched.filter((rec) => rec.priority_band === 'controlled review').length;

  return {
    enriched,
    riskBreakdown,
    strategyBreakdown,
    priorityBreakdown,
    materialQuantity,
    topCostCandidates,
    topDiversionCandidates,
    evidenceGaps,
    reviewRequired,
    quickWins,
    controlledReview,
    totalCostExposure: sumBy(enriched, (rec) => rec.estimated_annual_disposal_cost_avoided),
    totalDiversionPotential: sumBy(enriched, (rec) => rec.estimated_annual_waste_diverted_kg),
  };
}

export function applyRecommendationFilters(enrichedRecommendations, filters) {
  const search = filters.search.trim().toLowerCase();
  const minConfidence = normaliseNumber(filters.minConfidence);
  const minEvidence = normaliseNumber(filters.minEvidence);

  return enrichedRecommendations.filter((rec) => {
    const stream = rec.stream;
    const text = [
      rec.stream_id,
      rec.recommended_circular_action,
      rec.circular_strategy_category,
      rec.next_action,
      stream?.stream_name,
      stream?.material,
      stream?.source_process,
      stream?.supplier,
      stream?.department,
    ].filter(Boolean).join(' ').toLowerCase();

    const searchMatch = !search || text.includes(search);
    const materialMatch = filters.material === 'all' || stream?.material === filters.material;
    const riskMatch = filters.risk === 'all' || rec.risk_level === filters.risk;
    const strategyMatch = filters.strategy === 'all' || rec.circular_strategy_category === filters.strategy;
    const priorityMatch = filters.priority === 'all' || rec.priority_band === filters.priority;
    const reviewMatch =
      filters.review === 'all' ||
      (filters.review === 'required' && rec.human_review_required) ||
      (filters.review === 'clear' && !rec.human_review_required);
    const confidenceMatch = normaliseNumber(rec.confidence_score) >= minConfidence;
    const evidenceMatch = normaliseNumber(rec.evidence_quality_score) >= minEvidence;

    return searchMatch && materialMatch && riskMatch && strategyMatch && priorityMatch && reviewMatch && confidenceMatch && evidenceMatch;
  });
}

export function sortRecommendations(recommendations, sortBy) {
  const sorted = [...recommendations];
  const selectors = {
    priority: (rec) => rec.priority_score,
    cost: (rec) => normaliseNumber(rec.estimated_annual_disposal_cost_avoided),
    diversion: (rec) => normaliseNumber(rec.estimated_annual_waste_diverted_kg),
    confidence: (rec) => normaliseNumber(rec.confidence_score),
    evidence: (rec) => normaliseNumber(rec.evidence_quality_score),
    risk: (rec) => ({ blocked: 4, high: 3, medium: 2, low: 1 }[rec.risk_level] || 0),
  };
  const selector = selectors[sortBy] || selectors.priority;
  return sorted.sort((a, b) => selector(b) - selector(a));
}
