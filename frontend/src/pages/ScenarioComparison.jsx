import React, {useState} from 'react';
import {RotateCcw, GitCompareArrows, Loader} from 'lucide-react';
import {api, STATIC_DEMO} from '../api/client';
import RiskBadge from '../components/RiskBadge';

// Only fabricated values. Both transactions are intentionally anonymous.
const baseline = {
  amount: 600, hour: 14, account_age_days: 450, velocity_24h: 2,
  prior_chargebacks: 0, ip_risk_score: .12, is_international: 0,
  is_new_device: 0, merchant_category: 'retail', transaction_type: 'card',
};
const initialScenario = {...baseline, velocity_24h: 10, is_new_device: 1};
const fields = [
  ['amount', 'Amount (fictional ₹)', 0, 1000000, .01],
  ['hour', 'Hour', 0, 23, 1],
  ['account_age_days', 'Account age (days)', 0, 100000, 1],
  ['velocity_24h', 'Transactions in past 24h', 0, 10000, 1],
  ['prior_chargebacks', 'Previous chargebacks', 0, 100, 1],
  ['ip_risk_score', 'IP risk indicator', 0, 1, .01],
];

export default function ScenarioComparison() {
  const [scenario, setScenario] = useState(initialScenario);
  const [comparison, setComparison] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const update = (field, value) => setScenario(prev => ({...prev, [field]: value}));

  async function compare(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    setComparison(null);
    try {
      setComparison(await api.whatIf({baseline, scenario}));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return <>
    <div className="page-title"><div>
      <div className="eyebrow">EXPERIMENTAL MODEL BEHAVIOR</div>
      <h1>What-if <span>Comparison</span></h1>
      <p>Change fictional inputs, compare estimated scores, and learn what the model responds to.</p>
    </div></div>
    <div className="form-grid">
      <form className="panel" onSubmit={compare}>
        <div className="panel-head"><div><h2>Change the synthetic scenario</h2>
          <p>Baseline: ₹600, 2 recent transactions, established account and known device.</p>
        </div></div>
        <div className="input-grid">
          {fields.map(([field, label, min, max, step]) =>
            <label key={field}>{label}
              <input type="number" required min={min} max={max} step={step}
                value={scenario[field]} onChange={e => update(field, Number(e.target.value))}/>
            </label>
          )}
          {['is_international', 'is_new_device'].map(field =>
            <label key={field}>{field === 'is_international' ? 'International payment' : 'New device'}
              <select value={scenario[field]} onChange={e => update(field, Number(e.target.value))}>
                <option value={0}>No</option><option value={1}>Yes</option>
              </select>
            </label>
          )}
          <label>Merchant category
            <select value={scenario.merchant_category} onChange={e => update('merchant_category', e.target.value)}>
              {['retail', 'travel', 'digital', 'groceries', 'gaming'].map(x => <option key={x}>{x}</option>)}
            </select>
          </label>
          <label>Transaction type
            <select value={scenario.transaction_type} onChange={e => update('transaction_type', e.target.value)}>
              {['card', 'bank_transfer', 'wallet', 'ecommerce'].map(x => <option key={x}>{x}</option>)}
            </select>
          </label>
        </div>
        <div className="actions">
          <button className="button secondary" type="button" onClick={() => {setScenario(initialScenario); setComparison(null); setError('');}}>
            <RotateCcw size={16}/> Reset
          </button>
          <button className="button primary" type="submit" disabled={busy}>
            {busy ? <Loader size={16}/> : <GitCompareArrows size={16}/>} Compare scenarios
          </button>
        </div>
        {error && <div className="error" role="alert">{error}</div>}
      </form>
      <section className="panel results">
        <h2>Model response</h2>
        {comparison ? <>
          {['baseline', 'scenario'].map(key => <div key={key} className="result-line">
            <span>{key === 'baseline' ? 'Baseline' : 'Modified scenario'}</span>
            <b>{(comparison[key].fraud_probability * 100).toFixed(2)}%</b>
            <RiskBadge risk={comparison[key].risk_level}/>
          </div>)}
          <div className="result-line"><span>Difference in score</span><b>{comparison.delta_probability > 0 ? '+' : ''}{(comparison.delta_probability * 100).toFixed(2)} percentage points</b></div>
          <div className="result-line"><span>Review decision changed</span><b>{comparison.flag_changed ? 'Yes' : 'No'}</b></div>
          <h3>Features that changed</h3>
          <p>{comparison.changed_features.join(', ') || 'No changes'}</p>
          <p className="fineprint">{comparison.disclaimer}</p>
        </> : <div className="empty-state">Compare two hypothetical transactions to see an illustrative change in scores.</div>}
        <p className="fineprint">{STATIC_DEMO ? 'This offline preview runs fictional rules, not an ML model.' : 'No comparison is written to the database.'}</p>
      </section>
    </div>
  </>;
}
