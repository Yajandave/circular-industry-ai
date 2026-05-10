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

function orderRiskRows(cells) {
  const riskOrder = ['blocked', 'high', 'medium', 'low', 'unknown'];
  const risks = new Set(cells.map((cell) => cell.risk));
  return riskOrder
    .filter((risk) => risks.has(risk))
    .map((risk) => ({ key: risk, label: risk.replaceAll('_', ' ') }));
}

function classifyOpportunity(rec) {
  if (rec.priority_band === 'quick win') return 'quick_win';
  if (rec.priority_band === 'opportunity development') return 'developing';
  if (rec.priority_band === 'evidence improvement') return 'evidence_uplift';
  return 'controlled_review';
}

function buildRiskOpportunityMatrix(enriched) {
  const columns = [
    { key: 'quick_win', label: 'Quick win' },
    { key: 'developing', label: 'Developing' },
    { key: 'evidence_uplift', label: 'Evidence uplift' },
    { key: 'controlled_review', label: 'Controlled review' },
  ];

  const cellMap = enriched.reduce((acc, rec) => {
    const risk = rec.risk_level || 'unknown';
    const opportunity = classifyOpportunity(rec);
    const key = `${risk}::${opportunity}`;
    if (!acc[key]) {
      acc[key] = { risk, opportunity, count: 0, exposure: 0 };
    }
    acc[key].count += 1;
    acc[key].exposure += normaliseNumber(rec.estimated_annual_disposal_cost_avoided);
    return acc;
  }, {});

  const cells = Object.values(cellMap);
  return {
    rows: orderRiskRows(cells),
    columns,
    cells,
  };
}

function buildParetoRows(items, labelSelector, valueSelector, limit = 8) {
  const rows = items
    .map((item) => ({
      label: labelSelector(item),
      value: normaliseNumber(valueSelector(item)),
    }))
    .filter((row) => row.value > 0)
    .sort((a, b) => b.value - a.value)
    .slice(0, limit);

  const total = rows.reduce((sum, row) => sum + row.value, 0);
  let cumulative = 0;

  return rows.map((row) => {
    const share = total > 0 ? (row.value / total) * 100 : 0;
    cumulative += share;
    return {
      ...row,
      share,
      cumulativeShare: cumulative,
    };
  });
}

function buildEvidenceMaturity(enriched) {
  const rows = [
    { label: 'Strong evidence', value: enriched.filter((rec) => normaliseNumber(rec.evidence_quality_score) >= 85).length, tone: '#1f5b43' },
    { label: 'Moderate evidence', value: enriched.filter((rec) => normaliseNumber(rec.evidence_quality_score) >= 70 && normaliseNumber(rec.evidence_quality_score) < 85).length, tone: '#7ea58d' },
    { label: 'Evidence uplift needed', value: enriched.filter((rec) => normaliseNumber(rec.evidence_quality_score) < 70).length, tone: '#d39a2f' },
  ];
  return rows.filter((row) => row.value > 0);
}

function buildClaimReadiness(enriched) {
  const ready = enriched.filter((rec) => !rec.human_review_required && !['high', 'blocked'].includes(rec.risk_level) && normaliseNumber(rec.evidence_quality_score) >= 85).length;
  const controlledReview = enriched.filter((rec) => rec.human_review_required).length;
  const evidenceUplift = enriched.filter((rec) => !rec.human_review_required && normaliseNumber(rec.evidence_quality_score) < 70).length;
  const riskBlocked = enriched.filter((rec) => ['high', 'blocked'].includes(rec.risk_level)).length;
  const developing = Math.max(0, enriched.length - ready - controlledReview - evidenceUplift - riskBlocked);

  return [
    { label: 'Ready for internal validation', value: ready },
    { label: 'Developing opportunity', value: developing },
    { label: 'Evidence uplift first', value: evidenceUplift },
    { label: 'Controlled review gate', value: controlledReview },
    { label: 'High / blocked risk', value: riskBlocked },
  ].filter((row) => row.value > 0);
}

function hasRecordedSupplier(rec) {
  const supplier = rec.stream?.supplier;
  if (!supplier) return false;
  return !['not recorded', 'unknown', 'n/a', 'none'].includes(String(supplier).trim().toLowerCase());
}

function buildSupplierLoopProfile(enriched) {
  const supplierCandidates = enriched.filter((rec) => hasRecordedSupplier(rec) && !rec.human_review_required && rec.priority_score >= 68).length;
  const controlledSupplierReviews = enriched.filter((rec) => hasRecordedSupplier(rec) && rec.human_review_required).length;
  const supplierDataGaps = enriched.filter((rec) => !hasRecordedSupplier(rec)).length;
  const lowReadinessSupplierRecords = Math.max(0, enriched.length - supplierCandidates - controlledSupplierReviews - supplierDataGaps);

  return [
    { label: 'Supplier-loop candidates', value: supplierCandidates },
    { label: 'Controlled supplier reviews', value: controlledSupplierReviews },
    { label: 'Supplier data gaps', value: supplierDataGaps },
    { label: 'Lower-readiness supplier records', value: lowReadinessSupplierRecords },
  ].filter((row) => row.value > 0);
}

function scenarioText(rec) {
  if (rec.human_review_required || ['high', 'blocked'].includes(rec.risk_level)) {
    return 'Controlled-review scenario: resolve risk, compliance and evidence gates before action.';
  }
  if (normaliseNumber(rec.evidence_quality_score) < 70) {
    return 'Evidence-uplift scenario: collect missing records before claim or implementation.';
  }
  if (rec.priority_band === 'quick win') {
    return 'Pilot scenario: suitable for validation planning, with claim wording still controlled.';
  }
  return 'Opportunity-development scenario: useful candidate for operational and supplier feasibility checks.';
}

function buildScenarioItems(enriched) {
  return [...enriched]
    .sort((a, b) => {
      const costDelta = normaliseNumber(b.estimated_annual_disposal_cost_avoided) - normaliseNumber(a.estimated_annual_disposal_cost_avoided);
      if (costDelta !== 0) return costDelta;
      return b.priority_score - a.priority_score;
    })
    .slice(0, 6)
    .map((rec) => ({
      stream_id: rec.stream_id,
      stream_name: rec.stream?.stream_name || rec.recommended_circular_action || 'Unnamed stream',
      priority_score: rec.priority_score,
      scenario: scenarioText(rec),
    }));
}

function buildVisualAnalyticsData(enriched, streams) {
  const materialPareto = buildParetoRows(
    streams,
    (stream) => stream.material || 'unknown material',
    (stream) => normaliseNumber(stream.monthly_quantity_kg) * 12,
    8,
  );
  const costPareto = buildParetoRows(
    enriched,
    (rec) => `${rec.stream_id} · ${rec.stream?.stream_name || rec.stream?.material || 'stream'}`,
    (rec) => rec.estimated_annual_disposal_cost_avoided,
    8,
  );

  return {
    totalRecords: enriched.length,
    matrix: buildRiskOpportunityMatrix(enriched),
    materialPareto,
    costPareto,
    evidenceMaturity: buildEvidenceMaturity(enriched),
    claimReadiness: buildClaimReadiness(enriched),
    supplierLoopProfile: buildSupplierLoopProfile(enriched),
    scenarioItems: buildScenarioItems(enriched),
    controlSummary: {
      humanReview: enriched.filter((rec) => rec.human_review_required).length,
      lowEvidence: enriched.filter((rec) => normaliseNumber(rec.evidence_quality_score) < 70).length,
      supplierDataGaps: enriched.filter((rec) => !hasRecordedSupplier(rec)).length,
      boundary: 'rules_locked_screening',
    },
  };
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
    visualAnalytics: buildVisualAnalyticsData(enriched, streams),
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
