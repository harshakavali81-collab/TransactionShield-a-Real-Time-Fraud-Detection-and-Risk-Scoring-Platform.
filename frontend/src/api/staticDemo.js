/**
 * Offline, static GitHub Pages demonstration. NO ML MODEL is executed in browser.
 * All records and scores are fictional; nothing is sent to or stored by a server.
 */
import syntheticModelMetrics from '../../../artifacts/models/metrics.json';

const categories = ['retail', 'travel', 'digital', 'groceries', 'gaming'];
const methods = ['card', 'bank_transfer', 'wallet', 'ecommerce'];
let records = [];
let nextNumber = 1;

function simulatedReview(features) {
  // This intentionally is NOT an inference from the trained LightGBM model.
  const score = Math.min(94, Math.max(2, Math.round(
    6 + (features.amount > 1000 ? 13 : 0) + (features.hour < 6 ? 9 : 0) +
    (features.account_age_days < 30 ? 11 : 0) + Math.min(18, features.velocity_24h * 2) +
    15 * Math.min(3, features.prior_chargebacks) + (features.is_new_device ? 11 : 0) +
    (features.is_international ? 10 : 0) + 18 * features.ip_risk_score +
    (features.merchant_category === 'gaming' ? 5 : 0)
  )));
  const reasons = [];
  if (features.is_new_device) reasons.push('New device');
  if (features.is_international) reasons.push('International transaction');
  if (features.velocity_24h >= 8) reasons.push('Elevated transaction velocity');
  if (features.prior_chargebacks) reasons.push('Prior chargeback signal');
  if (!reasons.length) reasons.push('No example review rules triggered');
  return {
    risk_score: score, fraud_probability: score / 100,
    risk_level: score >= 65 ? 'HIGH' : score >= 30 ? 'MEDIUM' : 'LOW',
    is_flagged: score >= 65, reasons,
    model_version: 'OFFLINE RULE SIMULATION — not trained ML'
  };
}

function seedRecords() {
  if (records.length) return;
  for (let i = 0; i < 72; i++) {
    const features = {
      amount: 30 + ((i * 79 + 143) % 3600), hour: (i * 7) % 24,
      account_age_days: (i * 83 + 15) % 1500, velocity_24h: (i * 11) % 14,
      prior_chargebacks: i % 17 === 0 ? 1 : 0, ip_risk_score: ((i * 17) % 100) / 100,
      is_international: i % 13 === 0 ? 1 : 0, is_new_device: i % 9 === 0 ? 1 : 0,
      merchant_category: categories[i % categories.length],
      transaction_type: methods[i % methods.length]
    };
    records.push({
      transaction_id: `STATIC-DEMO-${String(nextNumber++).padStart(4, '0')}`,
      created_at: new Date(Date.UTC(2026, 9, 15, 12, 0) - i * 1800000).toISOString(),
      amount: features.amount, ...simulatedReview(features)
    });
  }
}

function distribution() {
  return Object.fromEntries(['LOW', 'MEDIUM', 'HIGH'].map(risk => [risk, records.filter(r => r.risk_level === risk).length]));
}
function statistics() {
  const count = records.length;
  const flagged = records.filter(r => r.is_flagged).length;
  return {total_transactions: count, flagged_transactions: flagged, flag_rate: count ? flagged / count : 0,
    average_risk_score: count ? Math.round(records.reduce((sum, r) => sum + r.risk_score, 0) / count) : 0};
}
seedRecords();
export const staticDemoApi = {
  health: async () => ({status: 'offline_static_demo', model_ready: false, demo_only: true}),
  ready: async () => ({status: 'offline_static_demo', model_ready: false, demo_only: true}),
  monitoring: async () => ({scope: 'fictional local-only preview', sample_count: records.length,
    feature_samples: 0, model_performance: 'not available from static demo', drift: {status: 'not_available'},
    limitations: ['Rule-based sample scores are not ML predictions', 'No server or transaction feed is connected']}),
  demoFeedbackMetrics: async () => ({status: 'not_available', count: 0, not_production_ground_truth: true}),
  statistics: async () => statistics(),
  analytics: async () => ({summary: statistics(), distribution: distribution(),
    note: 'All entries are fictional and generated in your browser; no real fraud outcomes.'}),
  metrics: async () => syntheticModelMetrics,
  history: async (limit = 100) => [...records].slice(0, limit),
  predict: async features => {
    const rec = {transaction_id: `STATIC-DEMO-${String(nextNumber++).padStart(4, '0')}`,
      created_at: new Date().toISOString(), amount: Number(features.amount), ...simulatedReview(features)};
    records.unshift(rec);
    return rec;
  }
};
