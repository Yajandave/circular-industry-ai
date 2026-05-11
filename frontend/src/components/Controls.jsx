export default function Controls({ onLoadSample, onUploadCsv, onRunRecommendations, onRefresh, busy }) {
  return (
    <section className="controls-card">
      <div>
        <h2>Data and analysis controls</h2>
        <p>Use this Circular Core upload for industrial material/waste stream datasets that follow the data dictionary. ESG, GHG, EIA, claims, supplier and generic CSVs now have their own domain workspaces from the top bar.</p>
      </div>
      <div className="controls-row">
        <button onClick={onLoadSample} disabled={busy}>Load sample dataset</button>
        <label className="file-button">
          Upload CSV
          <input type="file" accept=".csv" onChange={(event) => onUploadCsv(event.target.files?.[0])} disabled={busy} />
        </label>
        <button onClick={onRunRecommendations} disabled={busy}>Run recommendations</button>
        <button className="secondary" onClick={onRefresh} disabled={busy}>Refresh view</button>
      </div>
    </section>
  );
}
