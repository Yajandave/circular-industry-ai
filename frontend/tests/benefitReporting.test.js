import test from 'node:test';
import assert from 'node:assert/strict';
import { buildDashboardData } from '../src/utils/analytics.js';
import { buildAnalysisExport } from '../src/utils/analysisExport.js';

const streams = [
  { stream_id: 'BLOCK', monthly_quantity_kg: 100, disposal_cost_per_month: 500, material: 'chemicals' },
  { stream_id: 'SAFE', monthly_quantity_kg: 25, disposal_cost_per_month: 20, material: 'metals' },
];
const recommendations = [
  { stream_id: 'BLOCK', risk_level: 'blocked', human_review_required: true, estimated_annual_waste_diverted_kg: 1200, estimated_annual_disposal_cost_avoided: 6000 },
  { stream_id: 'SAFE', risk_level: 'low', human_review_required: false, estimated_annual_waste_diverted_kg: 300, estimated_annual_disposal_cost_avoided: 240 },
];

test('headline figures are throughput and cost exposure, not estimated savings', () => {
  const data = buildDashboardData(recommendations, streams);
  assert.equal(data.totalDiversionPotential, 1500);
  assert.equal(data.totalCostExposure, 6240);
  assert.equal(data.enriched[0].priority_band, 'controlled review');
  assert.equal(data.enriched[0].screened_cost_exposure, 6000);
  assert.equal(data.enriched[0].screened_quantity_opportunity_kg, 1200);
});

test('blocked streams retain exposure but never receive achievable-benefit estimates', () => {
  const report = buildAnalysisExport({
    streams, recommendations,
    streamSummary: { total_annual_quantity_kg: 1500, total_annual_disposal_cost: 6240 },
    recommendationSummary: { low_risk: 1, medium_risk: 0, high_risk: 0, blocked: 1, human_review_required: 1 },
    evidenceRecords: [], supplierLoopPlans: [],
  });
  assert.equal(report.schema_version, 2);
  assert.equal(report.summary.achievable_annual_diversion_kg, null);
  assert.equal(report.summary.achievable_annual_savings, null);
  assert.equal(report.recommendations[0].achievable_annual_diversion_kg, null);
  assert.equal(report.recommendations[0].achievable_annual_savings, null);
  assert.equal(report.recommendations[0].screened_annual_disposal_cost_exposure, 6000);
  assert.equal(report.recommendations[0].legacy_rule_outputs.estimated_annual_disposal_cost_avoided, 6000);
  assert.equal(report.recommendations[0].benefit_status, 'not_estimated');
});
