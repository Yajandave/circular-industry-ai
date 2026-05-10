const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
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
  reviewPack: (streamId) => request(`/api/agent/review-pack/${encodeURIComponent(streamId)}`),
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
};

export { API_BASE_URL };





