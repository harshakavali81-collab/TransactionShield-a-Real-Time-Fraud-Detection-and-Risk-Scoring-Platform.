import React from 'react';

export default function Monitoring({report, refresh}) {
  const drift = report?.drift || {};
  const flags = drift.flagged_features || [];
  return <section>
    <div className="page-heading"><div><h1>Model &amp; data monitoring</h1>
      <p>Observability of recent <strong>synthetic demo</strong> predictions — not actual fraud outcomes.</p></div>
      <button className="primary-button" onClick={refresh}>Refresh monitoring</button></div>
    <div className="panel" style={{padding:24,marginBottom:20}}>
      <h2>Recent prediction window</h2>
      <p><strong>{report?.sample_count ?? '—'}</strong> predictions analysed; <strong>{report?.feature_samples ?? '—'}</strong> numeric feature snapshots.</p>
      <p>Drift heuristic: {drift.method || drift.status || 'No reference available'}</p>
      <p>Features with elevated mean shifts: <strong>{flags.length ? flags.join(', ') : 'None identified'}</strong></p>
    </div>
    <div className="panel" style={{padding:24}}>
      <h2>Evidence &amp; limitations</h2>
      <p>Live model precision and recall are <strong>unavailable</strong> without independently confirmed delayed labels.</p>
      <ul>{(report?.limitations || ['Start the backend to load monitoring']).map(s=><li key={s}>{s}</li>)}</ul>
    </div>
  </section>;
}
