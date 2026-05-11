export const DOMAIN_WORKSPACES = [
  {
    id: 'circular-core',
    label: 'Circular Core',
    eyebrow: 'Main system',
    helper: 'Industrial material-flow, waste/resource stream and circular procurement decision support.',
  },
  {
    id: 'esg',
    label: 'ESG',
    eyebrow: 'Supporting intelligence',
    helper: 'ESG score, evidence and sustainability performance context.',
  },
  {
    id: 'ghg-net-zero',
    label: 'GHG & Net Zero',
    eyebrow: 'Supporting intelligence',
    helper: 'Scope 1, 2 and 3 emissions, reduction opportunities and net zero readiness.',
  },
  {
    id: 'eia',
    label: 'EIA',
    eyebrow: 'Environmental Impact Assessment',
    helper: 'Environmental Impact Assessment issue, receptor, mitigation, residual-effect and evidence-gap intelligence.',
  },
  {
    id: 'greenwashing-claims',
    label: 'Greenwashing / Claims',
    eyebrow: 'Evidence control',
    helper: 'Sustainability claim screening, evidence sufficiency and safer wording routes.',
  },
  {
    id: 'supplier-procurement',
    label: 'Supplier & Procurement',
    eyebrow: 'Supporting intelligence',
    helper: 'Supplier sustainability, circular procurement and evidence-request intelligence.',
  },
  {
    id: 'data-profiler',
    label: 'Data Profiler',
    eyebrow: 'Fallback profiler',
    helper: 'Generic CSV profiling, column intelligence and recommended analysis route detection.',
  },
];

export const DOMAIN_WORKSPACE_CONTENT = {
  esg: {
    title: 'ESG intelligence workspace',
    purpose: 'Analyse ESG score, rating, evidence and performance-context datasets as supporting sustainability intelligence.',
    uploadLabel: 'Upload ESG CSV',
    parserStatus: 'Architecture contract only. Domain parser and calculations are not activated in this milestone.',
    requiredColumns: ['year or date', 'company or site', 'ESG score or rating value', 'rating provider or internal scoring source'],
    optionalColumns: ['theme', 'evidence reference', 'status', 'environmental score', 'social score', 'governance score', 'comments'],
    validOutputs: [
      'ESG score trend and year-on-year movement',
      'Evidence gap and rating-context review',
      'Performance volatility and direction-of-travel summary',
      'Claim limitation and reporting-boundary note',
    ],
    blockedOutputs: [
      'Verified ESG performance improvement',
      'External rating approval',
      'Legal or assurance-grade ESG conclusion',
    ],
    evidenceRequirements: [
      'Rating source and date',
      'Score methodology or provider context',
      'Evidence source behind material movements',
      'Boundary between internal tracking and external disclosure',
    ],
  },
  'ghg-net-zero': {
    title: 'GHG and net zero intelligence workspace',
    purpose: 'Screen emissions, Scope 1/2/3, source and target datasets as supporting carbon-management intelligence.',
    uploadLabel: 'Upload GHG / net zero CSV',
    parserStatus: 'Architecture contract only. Emissions calculation and factor logic are not activated in this milestone.',
    requiredColumns: ['emissions source or category', 'scope', 'emissions value', 'unit or tCO2e basis', 'year or period'],
    optionalColumns: ['activity data', 'emission factor', 'factor source', 'baseline year', 'target year', 'supplier', 'market-based/location-based flag'],
    validOutputs: [
      'Scope 1, 2 and 3 breakdown',
      'Emissions trend and source concentration',
      'Net zero target readiness screen',
      'Carbon claim and data-quality risk note',
    ],
    blockedOutputs: [
      'Verified carbon neutrality',
      'Verified net zero achievement',
      'Calculated emissions where activity data or factors are missing',
    ],
    evidenceRequirements: [
      'Emission factor source and year',
      'Activity data basis',
      'Organisational and operational boundary',
      'Treatment of Scope 3 gaps, residual emissions, offsets and removals',
    ],
  },
  eia: {
    title: 'EIA intelligence workspace',
    purpose: 'Organise Environmental Impact Assessment issue, receptor, mitigation and residual-effect datasets.',
    uploadLabel: 'Upload EIA CSV',
    parserStatus: 'Architecture contract only. EIA register parsing and matrices are not activated in this milestone.',
    requiredColumns: ['topic', 'receptor', 'impact or effect', 'phase', 'mitigation or control', 'status'],
    optionalColumns: ['magnitude', 'sensitivity', 'significance', 'residual effect', 'monitoring', 'stakeholder', 'consultee', 'owner', 'deadline'],
    validOutputs: [
      'EIA issue register profiling',
      'Topic materiality and receptor/impact mapping',
      'Mitigation gap and residual-effect review',
      'Scoping, evidence and stakeholder issue summary',
    ],
    blockedOutputs: [
      'Statutory EIA significance determination',
      'Planning acceptability judgement',
      'Legal compliance or consent-risk conclusion',
    ],
    evidenceRequirements: [
      'Project-specific receptor context',
      'Assessment method and topic boundary',
      'Mitigation commitment source',
      'Competent professional review of significance and residual effects',
    ],
  },
  'greenwashing-claims': {
    title: 'Greenwashing and claims workspace',
    purpose: 'Screen sustainability claims, evidence type, scope and substantiation risk.',
    uploadLabel: 'Upload claims CSV',
    parserStatus: 'Architecture contract only. Claim classification and evidence scoring are not activated in this milestone.',
    requiredColumns: ['claim text', 'product or service', 'evidence type', 'scope or boundary', 'date'],
    optionalColumns: ['certificate', 'standard', 'verification status', 'supplier', 'geography', 'claim channel', 'review owner'],
    validOutputs: [
      'Claim type classification',
      'Evidence sufficiency and missing substantiation review',
      'Unsupported wording and greenwashing-risk flags',
      'Safer wording and evidence request suggestions',
    ],
    blockedOutputs: [
      'Legal approval of claims',
      'Certification of evidence',
      'Validation of carbon neutral, net zero or recycled-content claims without substantiation',
    ],
    evidenceRequirements: [
      'Claim scope, date and geography',
      'Evidence source and verification status',
      'Product-level or organisation-level boundary',
      'Standard, certificate or methodology details where relevant',
    ],
  },
  'supplier-procurement': {
    title: 'Supplier and procurement workspace',
    purpose: 'Profile supplier sustainability, circular procurement, evidence gaps and commercial exposure datasets.',
    uploadLabel: 'Upload supplier / procurement CSV',
    parserStatus: 'Architecture contract only. Supplier risk and procurement analysis are not activated in this milestone.',
    requiredColumns: ['supplier or vendor', 'category', 'spend or volume', 'risk or status'],
    optionalColumns: ['country', 'certification', 'take-back availability', 'recycled content', 'contract status', 'Scope 3 category', 'evidence date'],
    validOutputs: [
      'Supplier risk and evidence-gap profile',
      'Spend exposure and category concentration',
      'Circular procurement and take-back opportunity screen',
      'Supplier evidence request and contract leverage list',
    ],
    blockedOutputs: [
      'Verified supplier compliance',
      'Certification validity confirmation',
      'Legal contract review or procurement approval',
    ],
    evidenceRequirements: [
      'Supplier evidence source and date',
      'Contract or purchasing context',
      'Take-back acceptance criteria',
      'Certification scope and validity boundary',
    ],
  },
  'data-profiler': {
    title: 'Universal data profiler',
    purpose: 'Fallback workspace for unknown CSVs. Profiles columns, missing data and possible routes into the professional intelligence domains.',
    uploadLabel: 'Upload any CSV for profiling',
    parserStatus: 'Architecture contract only. Generic profiling engine is not activated in this milestone.',
    requiredColumns: ['structured CSV columns with headers'],
    optionalColumns: ['date fields', 'numeric fields', 'categorical fields', 'cost fields', 'quantity fields', 'status fields', 'free-text notes'],
    validOutputs: [
      'Column and type detection',
      'Missing-value and duplicate-row profile',
      'Suggested sustainability, ESG, EIA, GHG or circular-economy route',
      'Required columns to unlock deeper domain analysis',
    ],
    blockedOutputs: [
      'Invented missing values',
      'Forced workspace routing without matching fields',
      'Circular Core recommendation when industrial material-flow fields are missing',
    ],
    evidenceRequirements: [
      'Readable headers',
      'Clear units where quantities or costs are used',
      'Enough columns to infer dataset type',
      'Explicit note where a domain analysis route is unavailable',
    ],
  },
};

export function getDomainWorkspaceMeta(domainId) {
  return DOMAIN_WORKSPACES.find((domain) => domain.id === domainId) || DOMAIN_WORKSPACES[0];
}

export function getDomainWorkspaceContent(domainId) {
  return DOMAIN_WORKSPACE_CONTENT[domainId] || DOMAIN_WORKSPACE_CONTENT['data-profiler'];
}
