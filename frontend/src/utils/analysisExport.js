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
    schema_version: 1,
    application: 'Circular Industry AI',
    export_type: 'circular_core_analysis',
    exported_at: new Date().toISOString(),
    interpretation: {
      decision_source: 'Existing deterministic rules engine; export does not recalculate decisions.',
      limits: 'Screened costs, quantities and opportunities are estimates, not verified savings, diversion, legal compliance or environmental impact.',
      data_scope: 'Current loaded Circular Core workspace, including potentially confidential industrial stream details. Review before sharing.',
      profiler_note: 'Data Profiler outputs are not included in this first Circular Core export.',
    },
    summary: { streamSummary, recommendationSummary, evidenceSummary, supplierLoopSummary },
    material_streams: streams,
    recommendations,
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
export function exportAnalysisCsv({ recommendations }) {
  const fields = [
    'stream_id', 'stream_name', 'material', 'circular_strategy_category',
    'recommended_circular_action', 'rule_applied', 'risk_level',
    'human_review_required', 'confidence_score', 'evidence_quality_score',
    'estimated_annual_waste_diverted_kg', 'estimated_annual_disposal_cost_avoided',
  ];
  const header = fields.map(csvEscape).join(',');
  const rows = recommendations.map(rec => fields.map(key => csvEscape(rec[key])).join(','));
  // BOM improves spreadsheet compatibility; cell strings are escaped against formula injection.
  saveFile(`circular-industry-recommendations-${stamp()}.csv`, '\ufeff' + [header, ...rows].join('\r\n'), 'text/csv;charset=utf-8');
}
