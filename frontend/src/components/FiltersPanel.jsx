export default function FiltersPanel({ filters, onChange, materials, strategies, priorities, resultCount, totalCount }) {
  function update(key, value) {
    onChange({ ...filters, [key]: value });
  }

  function reset() {
    onChange({
      search: '',
      material: 'all',
      risk: 'all',
      strategy: 'all',
      review: 'all',
      priority: 'all',
      minConfidence: 0,
      minEvidence: 0,
      sortBy: 'priority',
    });
  }

  return (
    <section className="filters-card advanced-filters">
      <div className="section-heading compact-heading">
        <div>
          <h2>Recommendation filters and ranking</h2>
          <p>Filter the decision table by material, strategy, risk, evidence maturity and review status.</p>
        </div>
        <span>{resultCount} of {totalCount} shown</span>
      </div>

      <div className="filters-grid">
        <label className="search-label">
          Search streams, suppliers or actions
          <input
            value={filters.search}
            placeholder="e.g. aluminium, supplier take-back, hazardous, packaging"
            onChange={(event) => update('search', event.target.value)}
          />
        </label>
        <label>
          Material
          <select value={filters.material} onChange={(event) => update('material', event.target.value)}>
            {materials.map((material) => <option key={material} value={material}>{material}</option>)}
          </select>
        </label>
        <label>
          Strategy
          <select value={filters.strategy} onChange={(event) => update('strategy', event.target.value)}>
            {strategies.map((strategy) => <option key={strategy} value={strategy}>{strategy}</option>)}
          </select>
        </label>
        <label>
          Risk
          <select value={filters.risk} onChange={(event) => update('risk', event.target.value)}>
            <option value="all">all</option>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
            <option value="blocked">blocked</option>
          </select>
        </label>
        <label>
          Review status
          <select value={filters.review} onChange={(event) => update('review', event.target.value)}>
            <option value="all">all</option>
            <option value="required">human review required</option>
            <option value="clear">rules-cleared</option>
          </select>
        </label>
        <label>
          Priority band
          <select value={filters.priority} onChange={(event) => update('priority', event.target.value)}>
            {priorities.map((priority) => <option key={priority} value={priority}>{priority}</option>)}
          </select>
        </label>
        <label>
          Minimum confidence
          <input type="number" min="0" max="100" value={filters.minConfidence} onChange={(event) => update('minConfidence', event.target.value)} />
        </label>
        <label>
          Minimum evidence
          <input type="number" min="0" max="100" value={filters.minEvidence} onChange={(event) => update('minEvidence', event.target.value)} />
        </label>
        <label>
          Sort by
          <select value={filters.sortBy} onChange={(event) => update('sortBy', event.target.value)}>
            <option value="priority">priority score</option>
            <option value="cost">annual cost exposure</option>
            <option value="diversion">annual diversion potential</option>
            <option value="risk">risk severity</option>
            <option value="confidence">confidence score</option>
            <option value="evidence">evidence quality score</option>
          </select>
        </label>
        <button className="secondary reset-button" onClick={reset}>Reset filters</button>
      </div>
    </section>
  );
}
