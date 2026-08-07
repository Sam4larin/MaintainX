const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getAssets() {
  return request<any[]>('/assets');
}

export async function getAsset(assetId: string) {
  return request<any>(`/assets/${assetId}`);
}

export async function predictFailureRisk(payload: any) {
  return request<any>('/predict/failure-risk', { method: 'POST', body: JSON.stringify(payload) });
}

export async function predictRUL(payload: any) {
  return request<any>('/predict/rul', { method: 'POST', body: JSON.stringify(payload) });
}

export async function predictAnomaly(payload: any) {
  return request<any>('/predict/anomaly', { method: 'POST', body: JSON.stringify(payload) });
}

export async function predictForecast(payload: any) {
  return request<any>('/predict/forecast', { method: 'POST', body: JSON.stringify(payload) });
}
