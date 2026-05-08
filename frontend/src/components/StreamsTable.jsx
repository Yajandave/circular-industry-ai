import { formatCurrency, formatKg } from '../utils/formatters.js';

export default function StreamsTable({ streams }) {
  return (
    <section className="table-card">
      <div className="section-heading">
        <h2>Industrial material streams</h2>
        <span>{streams.length} loaded</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Stream</th>
              <th>Material</th>
              <th>Source process</th>
              <th>Monthly quantity</th>
              <th>Current route</th>
              <th>Monthly cost</th>
              <th>Hazard</th>
            </tr>
          </thead>
          <tbody>
            {streams.map((stream) => (
              <tr key={stream.stream_id}>
                <td>{stream.stream_id}</td>
                <td>{stream.stream_name}</td>
                <td>{stream.material}</td>
                <td>{stream.source_process}</td>
                <td>{formatKg(stream.monthly_quantity_kg)}</td>
                <td>{stream.current_route}</td>
                <td>{formatCurrency(stream.disposal_cost_per_month)}</td>
                <td>{stream.hazardous_flag}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
