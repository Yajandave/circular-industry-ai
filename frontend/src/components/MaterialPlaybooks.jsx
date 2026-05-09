import { API_BASE_URL } from '../api/client.js';
import { formatNumber } from '../utils/formatters.js';

function ExportButton({ href, children }) {
  return (
    <a className="secondary-button" href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  );
}

function PillList({ title, items }) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <div className="playbook-pill-section">
      <h4>{title}</h4>
      <div className="pill-list">
        {safeItems.map((item, index) => (
          <span key={`${title}-${index}`} className="text-pill">{item}</span>
        ))}
      </div>
    </div>
  );
}

function ListBlock({ title, items }) {
  const safeItems = Array.isArray(items) ? items : [];
  return (
    <div className="playbook-list-block">
      <h4>{title}</h4>
      {safeItems.length ? (
        <ul>
          {safeItems.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
        </ul>
      ) : (
        <p>None recorded.</p>
      )}
    </div>
  );
}

function PlaybookCard({ playbook }) {
  return (
    <article className="material-playbook-card">
      <div className="material-playbook-header">
        <div>
          <span>{playbook.material_cycle}</span>
          <h3>{playbook.material_family}</h3>
          <p>{playbook.core_circularity_question}</p>
        </div>
        <strong>{playbook.best_fit_streams?.length || 0} stream patterns</strong>
      </div>

      <PillList title="Best-fit streams" items={playbook.best_fit_streams} />

      <div className="material-playbook-grid">
        <ListBlock title="High-value intervention patterns" items={playbook.high_value_intervention_patterns} />
        <ListBlock title="Prevention and design levers" items={playbook.prevention_and_design_levers} />
        <ListBlock title="Supplier and procurement levers" items={playbook.supplier_and_procurement_levers} />
        <ListBlock title="Evidence tests" items={playbook.evidence_tests} />
        <ListBlock title="Red flags" items={playbook.red_flags} />
        <ListBlock title="Routes to avoid" items={playbook.routes_to_avoid} />
        <ListBlock title="Pilot patterns" items={playbook.pilot_patterns} />
        <ListBlock title="KPIs" items={playbook.kpis} />
      </div>

      <div className="playbook-footer-grid">
        <div>
          <h4>Industrial symbiosis partner types</h4>
          <p>{(playbook.industrial_symbiosis_partner_types || []).join('; ')}</p>
        </div>
        <div>
          <h4>Claim controls</h4>
          <p>{(playbook.claim_controls || []).join('; ')}</p>
        </div>
        <div>
          <h4>ESRS E5 mapping</h4>
          <p>{(playbook.esrs_e5_mapping || []).join('; ')}</p>
        </div>
        <div>
          <h4>CTI-style metrics</h4>
          <p>{(playbook.cti_style_metrics || []).join('; ')}</p>
        </div>
      </div>
    </article>
  );
}

export default function MaterialPlaybooks({ playbooks = [], summary = null }) {
  return (
    <section className="material-playbooks-section">
      <div className="section-heading">
        <div>
          <h2>Material-specific circular playbooks</h2>
          <p>
            Domain playbooks that stop the agent from giving generic waste-management advice. Each playbook defines
            circular interventions, evidence tests, red flags, supplier levers, pilot patterns and claim controls.
          </p>
        </div>
        <div className="export-actions">
          <ExportButton href={`${API_BASE_URL}/api/export/material-playbooks.csv`}>Export playbooks CSV</ExportButton>
        </div>
      </div>

      <div className="resolution-summary-grid">
        <div className="metric-card">
          <span>Playbooks</span>
          <strong>{formatNumber(summary?.total_playbooks || playbooks.length)}</strong>
          <small>material-family knowledge modules</small>
        </div>
        <div className="metric-card">
          <span>Technical cycles</span>
          <strong>{formatNumber(summary?.technical_cycle_count || 0)}</strong>
          <small>metals, plastics, packaging, WEEE and minerals</small>
        </div>
        <div className="metric-card">
          <span>Biological / water / energy</span>
          <strong>{formatNumber(summary?.biological_or_water_energy_count || 0)}</strong>
          <small>organic residues, water and heat streams</small>
        </div>
      </div>

      {summary?.coverage_note && (
        <div className="evidence-governance-note resolution-note">
          <h4>Coverage note</h4>
          <p>{summary.coverage_note}</p>
        </div>
      )}

      <div className="playbook-card-stack">
        {playbooks.map((playbook) => <PlaybookCard key={playbook.material_family} playbook={playbook} />)}
      </div>
    </section>
  );
}
