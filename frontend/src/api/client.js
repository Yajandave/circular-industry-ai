import { recordFrontendRequest } from '../utils/fullDiagnostics.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

async function request(path, options = {}) {
  const start = performance.now();
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
    recordFrontendRequest(path, options.method || 'GET', response.status, performance.now() - start);
  } catch (error) {
    recordFrontendRequest(path, options.method || 'GET', null, performance.now() - start, error?.name || 'NetworkError');
    throw error;
  }
  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await response.json() : await response.text();

  if (!response.ok) {
    const message = typeof body === 'object' && body?.detail ? body.detail : `Request failed: ${response.status}`;
    throw new Error(Array.isArray(message) ? JSON.stringify(message) : message);
  }

  return body;
}

export const api = {
  health: () => request('/health'),
  loadSample: () => request('/api/streams/load-sample', { method: 'POST' }),
  uploadCsv: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/api/streams/upload-csv', { method: 'POST', body: formData });
  },
  listStreams: () => request('/api/streams?limit=500'),
  streamSummary: () => request('/api/streams/summary'),
  runRecommendations: () => request('/api/recommendations/run', { method: 'POST' }),
  listRecommendations: () => request('/api/recommendations?limit=500'),
  recommendationSummary: () => request('/api/recommendations/summary'),
  screenInterventionScenario: (streamId, payload) => request(`/api/scenarios/${encodeURIComponent(streamId)}/screen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  compareInterventionScenarios: (streamId, payload) => request(`/api/scenarios/${encodeURIComponent(streamId)}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  saveInterventionScenario: (streamId, payload) => request(`/api/scenarios/${encodeURIComponent(streamId)}/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  interventionScenarioHistory: (streamId) => request(`/api/scenarios/${encodeURIComponent(streamId)}/history?limit=100`),
  recordObservedScenarioOutcome: (savedScenarioId, payload) => request(`/api/scenarios/saved/${savedScenarioId}/outcomes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  observedScenarioOutcomeHistory: (savedScenarioId) => request(`/api/scenarios/saved/${savedScenarioId}/outcomes?limit=100`),
  reviewObservedOutcomeEvidence: (observedOutcomeId, payload) => request(`/api/scenarios/outcomes/${observedOutcomeId}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  observedOutcomeEvidenceReviewHistory: (observedOutcomeId) => request(`/api/scenarios/outcomes/${observedOutcomeId}/reviews?limit=100`),
  blindDecisionReviewPack: () => request('/api/decision-validation/blind-review-pack'),
  submitBlindDecisionReview: (payload) => request('/api/decision-validation/blind-review-submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  blindReviewAnalysis: () => request('/api/decision-validation/blind-review-analysis'),
  reviewPack: (streamId) => request(`/api/agent/review-pack/${encodeURIComponent(streamId)}`),
  recordDecisionChallenge: (streamId, payload) => request(`/api/governance/decision-challenges/${encodeURIComponent(streamId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  decisionChallengeHistory: (streamId) => request(`/api/governance/decision-challenges/${encodeURIComponent(streamId)}?limit=100`),
  managementSummary: () => request('/api/agent/management-summary'),
  actionPlan: (limit = 12) => request(`/api/agent/action-plan?limit=${limit}`),
  evidenceRegister: () => request('/api/evidence-register'),
  evidenceSummary: () => request('/api/evidence-register/summary'),
  generateEvidenceGapExplanation: (streamId) => request(`/api/evidence-register/${encodeURIComponent(streamId)}/ai-explainer`, { method: 'POST' }),
  runResolutions: () => request('/api/resolutions/run', { method: 'POST' }),
  resolutionPlans: () => request('/api/resolutions'),
  resolutionSummary: () => request('/api/resolutions/summary'),
  resolutionPlan: (streamId) => request(`/api/resolutions/${encodeURIComponent(streamId)}`),
  aiReasoningStatus: () => request('/api/ai-reasoning/status'),
  aiRuntimeStatus: () => request('/api/ai-runtime/status'),
  generateAiReasoning: (streamId) => request(`/api/ai-reasoning/${encodeURIComponent(streamId)}`, { method: 'POST' }),
  materialPlaybooks: () => request('/api/playbooks'),
  materialPlaybookSummary: () => request('/api/playbooks/summary'),
  siteAICopilotSummary: () => request('/api/ai-copilot/site-summary'),
  generateCircularActionReport: (streamId) => request(`/api/reports/streams/${encodeURIComponent(streamId)}/circular-action-report`, { method: 'POST' }),
  runSupplierLoops: () => request('/api/procurement/run', { method: 'POST' }),
  supplierLoopPlans: () => request('/api/procurement/supplier-loops'),
  supplierLoopSummary: () => request('/api/procurement/supplier-loops/summary'),
  generateSupplierEmailDraft: (streamId) => request(`/api/procurement/supplier-loops/${encodeURIComponent(streamId)}/email-draft`, { method: 'POST' }),
  profileCsv: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/api/data-profiler/profile-csv', { method: 'POST', body: formData });
  },
  validateMapping: (payload) => request('/api/data-profiler/validate-mapping', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  buildCircularCoreDraftImport: (payload) => request('/api/data-profiler/build-circular-core-draft-import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  importCircularCoreDraft: (payload) => request('/api/data-profiler/import-circular-core-draft', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }),
};

export { API_BASE_URL };

