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
  const quantityOpportunity = Math.min(normaliseNumber(rec.estimated_annual_waste_diverted_kg) / 1000, 40);
  const cost = Math.min(normaliseNumber(rec.estimated_annual_disposal_cost_avoided) / 250, 35);
  const reviewPenalty = rec.human_review_required ? 35 : 0;
  const riskPenalty = rec.risk_level === 'blocked' ? 50 : rec.risk_level === 'high' ? 35 : rec.risk_level === 'medium' ? 14 : 0;
  return Math.max(0, Math.round(confidence * 0.34 + evidence * 0.26 + quantityOpportunity + cost - reviewPenalty - riskPenalty));
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

function opportunityLabel(bucket) {
  return {
    quick_win: 'Quick win',
    developing: 'Developing',
    evidence_uplift: 'Evidence uplift',
    controlled_review: 'Controlled review',
  }[bucket] || 'Controlled review';
}

function evidenceBucket(rec) {
  const evidence = normaliseNumber(rec.evidence_quality_score);
  if (evidence >= 85) return 'strong_evidence';
  if (evidence >= 70) return 'moderate_evidence';
  return 'evidence_uplift';
}

function evidenceLabel(bucket) {
  return {
    strong_evidence: 'Strong evidence',
    moderate_evidence: 'Moderate evidence',
    evidence_uplift: 'Evidence uplift needed',
  }[bucket] || 'Evidence status';
}

function claimBucket(rec) {
  const evidence = normaliseNumber(rec.evidence_quality_score);
  if (['high', 'blocked'].includes(rec.risk_level)) return 'high_blocked_risk';
  if (rec.human_review_required) return 'controlled_review_gate';
  if (evidence < 70) return 'evidence_uplift_first';
  if (evidence >= 85) return 'ready_for_internal_validation';
  return 'developing_opportunity';
}

function claimLabel(bucket) {
  return {
    ready_for_internal_validation: 'Ready for internal validation',
    developing_opportunity: 'Developing opportunity',
    evidence_uplift_first: 'Evidence uplift first',
    controlled_review_gate: 'Controlled review gate',
    high_blocked_risk: 'High / blocked risk',
  }[bucket] || 'Claim-readiness control';
}

function hasRecordedSupplier(rec) {
  const supplier = rec.stream?.supplier;
  if (!supplier) return false;
  return !['not recorded', 'unknown', 'n/a', 'none'].includes(String(supplier).trim().toLowerCase());
}

function supplierBucket(rec) {
  if (!hasRecordedSupplier(rec)) return 'supplier_data_gap';
  if (rec.human_review_required) return 'controlled_supplier_review';
  if (rec.priority_score >= 68) return 'supplier_loop_candidate';
  return 'lower_readiness_supplier_record';
}

function supplierLabel(bucket) {
  return {
    supplier_loop_candidate: 'Supplier-loop candidates',
    controlled_supplier_review: 'Controlled supplier reviews',
    supplier_data_gap: 'Supplier data gaps',
    lower_readiness_supplier_record: 'Lower-readiness supplier records',
  }[bucket] || 'Supplier-loop profile';
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
    const opportunity = rec.opportunity_bucket || classifyOpportunity(rec);
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

function buildParetoRows(items, labelSelector, valueSelector, limit = 8, extraSelector = () => ({})) {
  const rows = items
    .map((item) => ({
      label: labelSelector(item),
      value: normaliseNumber(valueSelector(item)),
      ...extraSelector(item),
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

function countRowsByBucket(records, bucketKey, labelFn) {
  const counts = records.reduce((acc, record) => {
    const bucket = record[bucketKey] || 'unknown';
    acc[bucket] = (acc[bucket] || 0) + 1;
    return acc;
  }, {});

  return Object.entries(counts)
    .map(([bucket, value]) => ({
      bucket,
      label: labelFn(bucket),
      value,
    }))
    .filter((row) => row.value > 0);
}

function buildEvidenceMaturity(records) {
  const order = ['strong_evidence', 'moderate_evidence', 'evidence_uplift'];
  const tones = {
    strong_evidence: '#1f5b43',
    moderate_evidence: '#7ea58d',
    evidence_uplift: '#d39a2f',
  };
  const rows = countRowsByBucket(records, 'evidence_bucket', evidenceLabel);

  return order
    .map((bucket) => rows.find((row) => row.bucket === bucket))
    .filter(Boolean)
    .map((row) => ({ ...row, tone: tones[row.bucket] || '#1f5b43' }));
}

function buildClaimReadiness(records) {
  const order = [
    'ready_for_internal_validation',
    'developing_opportunity',
    'evidence_uplift_first',
    'controlled_review_gate',
    'high_blocked_risk',
  ];
  const rows = countRowsByBucket(records, 'claim_bucket', claimLabel);
  return order.map((bucket) => rows.find((row) => row.bucket === bucket)).filter(Boolean);
}

function buildSupplierLoopProfile(records) {
  const order = [
    'supplier_loop_candidate',
    'controlled_supplier_review',
    'supplier_data_gap',
    'lower_readiness_supplier_record',
  ];
  const rows = countRowsByBucket(records, 'supplier_bucket', supplierLabel);
  return order.map((bucket) => rows.find((row) => row.bucket === bucket)).filter(Boolean);
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

function buildDrilldownRecords(enriched) {
  return enriched.map((rec) => {
    const stream = rec.stream || {};
    const opportunity = classifyOpportunity(rec);
    const evidence = evidenceBucket(rec);
    const claim = claimBucket(rec);
    const supplier = supplierBucket(rec);

    return {
      stream_id: rec.stream_id,
      stream_name: stream.stream_name || rec.recommended_circular_action || 'Unnamed stream',
      material: stream.material || 'unknown material',
      department: stream.department || 'unknown department',
      supplier: stream.supplier || 'not recorded',
      source_process: stream.source_process || 'unknown process',
      risk_level: rec.risk_level || 'unknown',
      priority_band: rec.priority_band,
      priority_score: rec.priority_score,
      evidence_quality_score: normaliseNumber(rec.evidence_quality_score),
      confidence_score: normaliseNumber(rec.confidence_score),
      human_review_required: Boolean(rec.human_review_required),
      estimated_annual_disposal_cost_avoided: normaliseNumber(rec.estimated_annual_disposal_cost_avoided),
      estimated_annual_waste_diverted_kg: normaliseNumber(rec.estimated_annual_waste_diverted_kg),
      screened_cost_exposure: normaliseNumber(rec.estimated_annual_disposal_cost_avoided),
      screened_quantity_opportunity_kg: normaliseNumber(rec.estimated_annual_waste_diverted_kg),
      recommended_circular_action: rec.recommended_circular_action || 'No recommendation recorded.',
      next_action: rec.next_action || 'No next action recorded.',
      opportunity_bucket: opportunity,
      opportunity_label: opportunityLabel(opportunity),
      evidence_bucket: evidence,
      evidence_label: evidenceLabel(evidence),
      claim_bucket: claim,
      claim_label: claimLabel(claim),
      supplier_bucket: supplier,
      supplier_label: supplierLabel(supplier),
      scenario: scenarioText(rec),
    };
  });
}

function buildScenarioItems(records) {
  return [...records]
    .sort((a, b) => {
      const costDelta = normaliseNumber(b.estimated_annual_disposal_cost_avoided) - normaliseNumber(a.estimated_annual_disposal_cost_avoided);
      if (costDelta !== 0) return costDelta;
      return b.priority_score - a.priority_score;
    })
    .slice(0, 6)
    .map((record) => ({
      stream_id: record.stream_id,
      stream_name: record.stream_name,
      priority_score: record.priority_score,
      scenario: record.scenario,
    }));
}

function buildVisualAnalyticsData(enriched, streams) {
  const drilldownRecords = buildDrilldownRecords(enriched);
  const materialPareto = buildParetoRows(
    streams,
    (stream) => stream.material || 'unknown material',
    (stream) => normaliseNumber(stream.monthly_quantity_kg) * 12,
    8,
    (stream) => ({ material: stream.material || 'unknown material' }),
  );
  const costPareto = buildParetoRows(
    drilldownRecords,
    (record) => `${record.stream_id} · ${record.stream_name}`,
    (record) => record.estimated_annual_disposal_cost_avoided,
    8,
    (record) => ({ stream_id: record.stream_id }),
  );

  return {
    totalRecords: drilldownRecords.length,
    matrix: buildRiskOpportunityMatrix(drilldownRecords),
    materialPareto,
    costPareto,
    evidenceMaturity: buildEvidenceMaturity(drilldownRecords),
    claimReadiness: buildClaimReadiness(drilldownRecords),
    supplierLoopProfile: buildSupplierLoopProfile(drilldownRecords),
    scenarioItems: buildScenarioItems(drilldownRecords),
    drilldownRecords,
    controlSummary: {
      humanReview: drilldownRecords.filter((record) => record.human_review_required).length,
      lowEvidence: drilldownRecords.filter((record) => record.evidence_bucket === 'evidence_uplift').length,
      supplierDataGaps: drilldownRecords.filter((record) => record.supplier_bucket === 'supplier_data_gap').length,
      boundary: 'rules_locked_screening',
    },
  };
}

export function buildDashboardData(recommendations, streams) {
  const enriched = enrichRecommendations(recommendations, streams).map((rec) => ({
    ...rec,
    screened_cost_exposure: normaliseNumber(rec.estimated_annual_disposal_cost_avoided),
    screened_quantity_opportunity_kg: normaliseNumber(rec.estimated_annual_waste_diverted_kg),
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
