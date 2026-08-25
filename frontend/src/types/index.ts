export interface AssetSummary {
  id: string;
  name: string;
  type: string;
  risk_level: string;
  maintenance_days: number;
  details?: Record<string, unknown> | null;
}

export interface AssetDetail extends AssetSummary {
  history: Array<Record<string, unknown>>;
}

export interface Ai4iPayload {
  Air_temperature_K: number;
  Process_temperature_K: number;
  Rotational_speed_rpm: number;
  Torque_Nm: number;
  Tool_wear_min: number;
  Type: number;
  temp_diff: number;
  power: number;
}

export interface FailureRiskResponse {
  failure_probability: number;
  risk_level: string;
  failure_type_prediction: string;
  failure_type_probabilities: Record<string, number>;
}

export interface RulResponse {
  predicted_rul_cycles: number;
  predicted_rul_days: number;
  recommended_maintenance_window_days: number;
  model_used: string;
  xgboost_prediction: number;
  lstm_prediction: number | null;
}

export interface AnomalyResponse {
  is_anomaly: boolean;
  isolation_forest_score: number;
  autoencoder_reconstruction_error: number;
  anomaly_threshold: number;
}

export interface SensorHistoryPayload {
  sensor_history: Array<Record<string, number>>;
}

export interface ForecastResponse {
  forecasted_cycles: number[];
  forecasted_sensor_values: Record<string, number[]>;
}
