import type {
  Ai4iPayload,
  AnomalyResponse,
  AssetDetail,
  AssetSummary,
  FailureRiskResponse,
  ForecastResponse,
  HealthResponse,
  RulResponse,
  SensorHistoryPayload,
  UploadParseResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch {
    // fetch() throws a generic "Failed to fetch" TypeError for every kind of
    // network failure (backend not running, wrong port, CORS rejection,
    // DNS failure, mixed-content block) with no distinguishing detail. That
    // one message was the entire symptom reported when the backend was down
    // -- so surface something actionable instead of repeating the browser's
    // opaque wording.
    throw new Error(
      `Could not reach the API at ${API_BASE_URL}. Is the backend running ` +
        `(uvicorn backend.app.main:app) and is VITE_API_BASE_URL set correctly?`,
    );
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function requestForm<T>(path: string, formData: FormData): Promise<T> {
  let response: Response;
  try {
    // Do NOT set Content-Type manually here -- the browser must set it
    // (including the multipart boundary) itself for FormData bodies.
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      body: formData,
    });
  } catch {
    throw new Error(
      `Could not reach the API at ${API_BASE_URL}. Is the backend running and is VITE_API_BASE_URL set correctly?`,
    );
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<HealthResponse>('/health');
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

export function uploadEquipmentFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return requestForm<UploadParseResponse>('/upload/parse', formData);
}
