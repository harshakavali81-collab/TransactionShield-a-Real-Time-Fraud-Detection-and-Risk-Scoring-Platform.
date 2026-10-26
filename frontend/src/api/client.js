const BASE = import.meta.env.VITE_API_URL || '/api';
async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(`${BASE}${path}`, { ...options, signal: controller.signal,
      headers: {'Content-Type': 'application/json', ...options.headers } });
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : `Server error ${response.status}`);
    return data;
  } finally {clearTimeout(timer);}
}
export const api = {
  health: () => request('/health'),
  ready: () => request('/ready'),
  monitoring: () => request('/monitoring/overview'),
  demoFeedbackMetrics: () => request('/monitoring/demo-feedback-metrics'),
  statistics: () => request('/statistics'),
  analytics: () => request('/analytics'),
  metrics: () => request('/metrics'),
  history: (limit=100) => request(`/history?limit=${limit}`),
  predict: (payload) => request('/predict', {method:'POST', body:JSON.stringify(payload)})
};
