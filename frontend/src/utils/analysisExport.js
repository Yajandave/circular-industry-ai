// Export the current, loaded Circular Core analysis. No recalculation or rules changes.
function saveFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
const stamp = () => new Date().toISOString().slice(0, 10);
export function buildAnalysisExport({ streams, recommendations, streamSummary, recommendationSummary, evidenceRecords, evidenceSummary, supplierLoopPlans, supplierLoopSummary }) {
  return {
    schema_version: 2,
    application: 'Circular Industry AI',
    export_type: 'circular_core_analysis',
    exported_at: new Date().toISOString(),
    interpretation: {
      decision_source: 'Existing deterministic rules engine; export does not recalculate decisions.',
      limits: 'Legacy backend estimated diversion and avoided-cost fields reflect annualised input throughput/cost exposure, NOT achievable or verified benefits. They are retained inside legacy_rule_outputs solely for traceability; do not add them as savings.',
      benefit_estimation_status: 'not_modelled',
      data_scope: 'Current loaded Circular Core workspace, including potentially confidential industrial stream details. Review before sharing.',
      profiler_note: 'Data Profiler outputs are not included in this first Circular Core export.',
    },
    summary: {
      annual_material_throughput_kg: streamSummary?.total_annual_quantity_kg ?? null,
      annual_disposal_cost_exposure: streamSummary?.total_annual_disposal_cost ?? null,
      achievable_annual_diversion_kg: null,
      achievable_annual_savings: null,
      benefits_verification: 'not_estimated',
      risk_counts: recommendationSummary ? { low: recommendationSummary.low_risk, medium: recommendationSummary.medium_risk, high: recommendationSummary.high_risk, blocked: recommendationSummary.blocked, human_review_required: recommendationSummary.human_review_required } : null,
      evidenceSummary,
      supplierLoopSummary,
    },
    material_streams: streams,
    recommendations: recommendations.map(({ estimated_annual_waste_diverted_kg, estimated_annual_disposal_cost_avoided, ...rec }) => ({ ...rec,
      screened_annual_quantity_kg: estimated_annual_waste_diverted_kg,
      screened_annual_disposal_cost_exposure: estimated_annual_disposal_cost_avoided,
      achievable_annual_diversion_kg: null,
      achievable_annual_savings: null,
      benefit_status: 'not_estimated',
      legacy_rule_outputs: { estimated_annual_waste_diverted_kg, estimated_annual_disposal_cost_avoided },
    })),
    evidence_register: evidenceRecords,
    supplier_loops: supplierLoopPlans,
  };
}
export function exportAnalysisJson(input) {
  const report = buildAnalysisExport(input);
  saveFile(`circular-industry-analysis-${stamp()}.json`, JSON.stringify(report, null, 2), 'application/json');
}
const csvEscape = (value) => {
  const string = value == null ? '' : typeof value === 'object' ? JSON.stringify(value) : String(value);
  const safe = /^[\\s]*[=+@-]/.test(string) ? "'" + string : string;
  return '"' + safe.replace(/"/g, '""') + '"';
};
export function exportAnalysisCsv({ recommendations, streams }) {
  const byId = new Map(streams.map(s => [s.stream_id, s]));
  const fields = [
    'stream_id', 'stream_name', 'material', 'circular_strategy_category',
    'recommended_circular_action', 'rule_applied', 'risk_level',
    'human_review_required', 'confidence_score', 'evidence_quality_score',
    'screened_annual_quantity_kg', 'screened_annual_disposal_cost_exposure',
    'achievable_annual_diversion_kg', 'achievable_annual_savings', 'benefit_status',
  ];
  const header = fields.map(csvEscape).join(',');
  const rows = recommendations.map(rec => {
    const stream = byId.get(rec.stream_id) || {};
    const output = { ...rec, stream_name: stream.stream_name, material: stream.material,
      screened_annual_quantity_kg: Number(stream.monthly_quantity_kg || 0) * 12,
      screened_annual_disposal_cost_exposure: Number(stream.disposal_cost_per_month || 0) * 12,
      achievable_annual_diversion_kg: null, achievable_annual_savings: null,
      benefit_status: 'not_estimated' };
    return fields.map(key => csvEscape(output[key])).join(',');
  });
  // BOM improves spreadsheet compatibility; cell strings are escaped against formula injection.
  saveFile(`circular-industry-recommendations-${stamp()}.csv`, '\ufeff' + [header, ...rows].join('\r\n'), 'text/csv;charset=utf-8');
}
