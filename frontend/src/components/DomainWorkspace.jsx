import { useMemo, useState } from 'react';

const DOMAIN_CONTENT = {
  esg: {
    title: 'ESG intelligence workspace',
    purpose: 'Analyse ESG score, rating, evidence and performance-context datasets as supporting sustainability intelligence.',
    uploadLabel: 'Upload ESG CSV',
    supportedColumns: ['year', 'date', 'company', 'esg score', 'rating', 'theme', 'evidence', 'status', 'provider'],
    analysisRoutes: [
      'ESG score trend and year-on-year movement',
      'Evidence gap and rating-context review',
      'Performance volatility and direction-of-travel summary',
      'Claim limitation and reporting-boundary note',
    ],
    notFor: [
      'Does not verify ESG performance or external ratings.',
      'Does not unlock industrial circular recommendations unless material-flow fields are also present.',
    ],
  },
  'ghg-net-zero': {
    title: 'GHG and net zero intelligence workspace',
    purpose: 'Screen emissions, Scope 1/2/3, source and target datasets as supporting carbon-management intelligence.',
    uploadLabel: 'Upload GHG / net zero CSV',
    supportedColumns: ['scope', 'scope 1', 'scope 2', 'scope 3', 'emissions', 'tco2e', 'source', 'fuel', 'electricity', 'baseline year', 'target year'],
    analysisRoutes: [
      'Scope 1, 2 and 3 breakdown',
      'Emissions trend and source concentration',
      'Net zero target readiness screen',
      'Carbon claim and data-quality risk note',
    ],
    notFor: [
      'Does not verify carbon neutrality or net zero achievement.',
      'Does not calculate emissions from missing activity data or missing factors.',
    ],
  },
  eia: {
    title: 'EIA intelligence workspace',
    purpose: 'Organise Environmental Impact Assessment issue, receptor, mitigation and residual-effect datasets.',
    uploadLabel: 'Upload EIA CSV',
    supportedColumns: ['topic', 'receptor', 'impact', 'effect', 'magnitude', 'sensitivity', 'significance', 'mitigation', 'residual effect', 'monitoring', 'stakeholder', 'consultee'],
    analysisRoutes: [
      'EIA issue register profiling',
      'Topic materiality and receptor/impact mapping',
      'Mitigation gap and residual-effect review',
      'Scoping, evidence and stakeholder issue summary',
    ],
    notFor: [
      'Does not determine statutory EIA significance or planning acceptability.',
      'Does not replace project-specific professional environmental assessment.',
    ],
  },
  'greenwashing-claims': {
    title: 'Greenwashing and claims workspace',
    purpose: 'Screen sustainability claims, evidence type, scope and substantiation risk.',
    uploadLabel: 'Upload claims CSV',
    supportedColumns: ['claim', 'product', 'evidence', 'certificate', 'standard', 'scope', 'date', 'verification status', 'supplier'],
    analysisRoutes: [
      'Claim type classification',
      'Evidence sufficiency and missing substantiation review',
      'Unsupported wording and greenwashing-risk flags',
      'Safer wording and evidence request suggestions',
    ],
    notFor: [
      'Does not legally approve claims or certify evidence.',
      'Does not validate carbon neutral, net zero or recycled-content claims without evidence.',
    ],
  },
  'supplier-procurement': {
    title: 'Supplier and procurement workspace',
    purpose: 'Profile supplier sustainability, circular procurement, evidence gaps and commercial exposure datasets.',
    uploadLabel: 'Upload supplier / procurement CSV',
    supportedColumns: ['supplier', 'vendor', 'spend', 'category', 'country', 'risk', 'certification', 'takeback', 'recycled content', 'contract status'],
    analysisRoutes: [
      'Supplier risk and evidence-gap profile',
      'Spend exposure and category concentration',
      'Circular procurement and take-back opportunity screen',
      'Supplier evidence request and contract leverage list',
    ],
    notFor: [
      'Does not verify supplier compliance or certification validity.',
      'Does not replace procurement due diligence or legal contract review.',
    ],
  },
  'data-profiler': {
    title: 'Universal data profiler',
    purpose: 'Fallback workspace for unknown CSVs. Profiles columns, missing data and possible routes into the professional intelligence domains.',
    uploadLabel: 'Upload any CSV for profiling',
    supportedColumns: ['any structured CSV columns'],
    analysisRoutes: [
      'Column and type detection',
      'Missing-value and duplicate-row profile',
      'Suggested sustainability, ESG, EIA, GHG or circular-economy route',
      'Required columns to unlock deeper domain analysis',
    ],
    notFor: [
      'Does not invent missing data or force unsupported analysis.',
      'Does not route to Circular Core unless industrial material-flow fields exist.',
    ],
  },
};

function ListCard({ title, items }) {
  return (
    <article className="domain-info-card">
      <h3>{title}</h3>
      <ul>
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </article>
  );
}

export default function DomainWorkspace({ domain, onBackToCore }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const content = useMemo(() => DOMAIN_CONTENT[domain.id] || DOMAIN_CONTENT['data-profiler'], [domain.id]);

  return (
    <section className="domain-workspace-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">{domain.eyebrow}</span>
          <h2>{content.title}</h2>
          <p>{content.purpose}</p>
        </div>
        <button type="button" className="secondary-button" onClick={onBackToCore}>Return to Circular Core</button>
      </div>

      <div className="domain-upload-zone">
        <div>
          <h3>{content.uploadLabel}</h3>
          <p>
            This workspace is separated from the Circular Core upload so the system does not force ESG, GHG,
            EIA, claims or supplier datasets into industrial material-flow rules. Domain-specific analysis will be
            added progressively while keeping Circular Industry AI's main identity intact.
          </p>
        </div>
        <label className="file-button domain-file-button">
          Select CSV
          <input type="file" accept=".csv" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
        </label>
      </div>

      {selectedFile && (
        <div className="domain-selected-file">
          <strong>Selected file:</strong> {selectedFile.name}
          <span>Domain parser not yet activated. This milestone establishes the workspace architecture and upload separation.</span>
        </div>
      )}

      <div className="domain-info-grid">
        <ListCard title="Supported columns and signals" items={content.supportedColumns} />
        <ListCard title="Planned analysis routes" items={content.analysisRoutes} />
        <ListCard title="Professional boundaries" items={content.notFor} />
      </div>

      <div className="domain-core-compatibility-note">
        <h3>Relationship to Circular Industry AI core</h3>
        <p>
          These domain workspaces support industrial circular economy decision-making, but they do not replace the core
          Circular Industry AI workflow. Full rules-locked circular recommendations remain available only for compatible
          industrial material-flow, waste/resource stream and circular procurement datasets.
        </p>
      </div>
    </section>
  );
}
