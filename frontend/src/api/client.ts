import type {
  Ai4iPayload,
  AnomalyResponse,
  AssetDetail,
  AssetSummary,
  FailureRiskResponse,
  ForecastResponse,
  RulResponse,
  SensorHistoryPayload,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<{ status: string }>('/health');
}

export function getAssets() {
  return request<AssetSummary[]>('/assets');
}

export function getAsset(assetId: string) {
  return request<AssetDetail>(`/assets/${assetId}`);
}

export function predictFailureRisk(payload: Ai4iPayload) {
  return request<FailureRiskResponse>('/predict/failure-risk', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function predictRUL(payload: SensorHistoryPayload) {
  return request<RulResponse>('/predict/rul', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function predictAnomaly(payload: Ai4iPayload) {
  return request<AnomalyResponse>('/predict/anomaly', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function predictForecast(payload: SensorHistoryPayload) {
  return request<ForecastResponse>('/predict/forecast', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
