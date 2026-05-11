import { useMemo, useState } from 'react';
import { getDomainWorkspaceContent } from '../config/domainWorkspaces.js';

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
  const content = useMemo(() => getDomainWorkspaceContent(domain.id), [domain.id]);

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
          <p className="domain-parser-status">{content.parserStatus}</p>
        </div>
        <label className="file-button domain-file-button">
          Select CSV
          <input type="file" accept=".csv" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
        </label>
      </div>

      {selectedFile && (
        <div className="domain-selected-file">
          <strong>Selected file:</strong> {selectedFile.name}
          <span>Domain parser not yet activated. This milestone establishes the workspace contract and architecture boundary.</span>
        </div>
      )}

      <div className="domain-info-grid">
        <ListCard title="Required data" items={content.requiredColumns} />
        <ListCard title="Optional signals" items={content.optionalColumns} />
        <ListCard title="Valid outputs" items={content.validOutputs} />
        <ListCard title="Unavailable or blocked outputs" items={content.blockedOutputs} />
        <ListCard title="Evidence requirements" items={content.evidenceRequirements} />
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
