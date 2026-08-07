import { useEffect, useState } from 'react';
import { getAsset, predictAnomaly, predictForecast, predictFailureRisk, predictRUL } from '../api/client';

interface AssetDetailPageProps {
  assetId: string;
}

export default function AssetDetailPage({ assetId }: AssetDetailPageProps) {
  const [asset, setAsset] = useState<any>(null);
  const [failureRisk, setFailureRisk] = useState<any>(null);
  const [rul, setRul] = useState<any>(null);
  const [anomaly, setAnomaly] = useState<any>(null);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getAsset(assetId), predictFailureRisk({
      'Air temperature [K]': 298.2,
      'Process temperature [K]': 308.7,
      'Rotational speed [rpm]': 1551,
      'Torque [Nm]': 42.8,
      'Tool wear [min]': 0,
      Type: 0,
      temp_diff: 10.5,
      power: 66400,
    }), predictRUL({ sensor_history: [{ value: 1 }] }), predictAnomaly({
      'Air temperature [K]': 298.2,
      'Process temperature [K]': 308.7,
      'Rotational speed [rpm]': 1551,
      'Torque [Nm]': 42.8,
      'Tool wear [min]': 0,
      Type: 0,
      temp_diff: 10.5,
      power: 66400,
    }), predictForecast({ sensor_history: [{ value: 1 }, { value: 2 }, { value: 3 }] })])
      .then(([assetData, failureData, rulData, anomalyData, forecastData]) => {
        setAsset(assetData);
        setFailureRisk(failureData);
        setRul(rulData);
        setAnomaly(anomalyData);
        setForecast(forecastData);
      })
      .catch(() => setError('Unable to load asset details'))
      .finally(() => setLoading(false));
  }, [assetId]);

  if (loading) return <div className="p-8">Loading…</div>;
  if (error || !asset) return <div className="p-8 text-red-700">{error ?? 'Asset not found'}</div>;

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="rounded-2xl bg-white p-6 shadow">
          <h1 className="text-3xl font-semibold">{asset.name}</h1>
          <p className="mt-2 text-slate-600">{asset.type} • {asset.risk_level}</p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Failure Risk</h2>
            <p className="mt-4 text-sm text-slate-500">Probability</p>
            <p className="text-4xl font-semibold">{Math.round((failureRisk?.failure_probability ?? 0) * 100)}%</p>
            <div className="mt-4 inline-block rounded-full bg-red-100 px-3 py-1 text-sm text-red-700">{failureRisk?.risk_level}</div>
            <div className="mt-6">
              <p className="text-sm font-medium">Failure Type Probabilities</p>
              <div className="mt-3 space-y-2">
                {Object.entries(failureRisk?.failure_type_probabilities ?? {}).map(([key, value]) => <div key={key}><div className="flex justify-between text-sm"><span>{key}</span><span>{Math.round((value as number) * 100)}%</span></div><div className="h-2 rounded bg-slate-100"><div className="h-2 rounded bg-sky-600" style={{ width: `${(value as number) * 100}%` }} /></div></div>)}
              </div>
            </div>
          </div>
          <div className="rounded-2xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">RUL</h2>
            <p className="mt-4 text-sm text-slate-500">XGBoost prediction</p>
            <p className="text-3xl font-semibold">{rul?.xgboost_prediction?.toFixed(1)} cycles</p>
            <p className="mt-2 text-sm text-slate-500">LSTM prediction</p>
            <p className="text-3xl font-semibold">{rul?.lstm_prediction?.toFixed(1)} cycles</p>
            <div className="mt-6 rounded-xl border border-sky-200 bg-sky-50 p-4">Recommended Maintenance: Within {rul?.recommended_maintenance_window_days ?? 7} days</div>
          </div>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Anomaly Status</h2>
            <p className="mt-4 text-sm text-slate-500">Anomaly threshold</p>
            <p className="text-3xl font-semibold">{anomaly?.anomaly_threshold?.toFixed(2)}</p>
            <p className="mt-4 text-sm text-slate-500">Current status</p>
            <p className={`text-2xl font-semibold ${anomaly?.is_anomaly ? 'text-red-600' : 'text-emerald-600'}`}>{anomaly?.is_anomaly ? 'Flagged' : 'Normal'}</p>
          </div>
          <div className="rounded-2xl bg-white p-6 shadow">
            <h2 className="text-xl font-semibold">Forecast</h2>
            <p className="mt-2 text-slate-600">Historical vs forecasted sensor values</p>
            <pre className="mt-4 overflow-auto rounded bg-slate-50 p-4 text-sm">{JSON.stringify(forecast, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
