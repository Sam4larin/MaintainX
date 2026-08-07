export interface AssetSummary {
  id: string;
  name: string;
  type: string;
  risk_level: string;
  maintenance_days: number;
}

export interface AssetDetail extends AssetSummary {
  history: Array<{ sensor: string; value: number }>;
}
