export default function Controls({ onLoadSample, onUploadCsv, onRunRecommendations, onRefresh, busy }) {
  return (
    <section className="controls-card">
      <div>
        <h2>Data and analysis controls</h2>
        <p>
          Load the sample manufacturing dataset or upload a CSV that follows the data dictionary. Then run the locked
          rules engine before opening review packs.
        </p>
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
