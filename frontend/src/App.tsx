import { FormEvent, ReactNode, useEffect, useState } from 'react';
import {
  getAsset,
  getAssets,
  getHealth,
  predictAnomaly,
  predictFailureRisk,
  predictForecast,
  predictRUL,
} from './api/client';
import type {
  Ai4iPayload,
  AnomalyResponse,
  AssetDetail,
  AssetSummary,
  FailureRiskResponse,
  ForecastResponse,
  RulResponse,
} from './types';

const ai4iSample: Ai4iPayload = {
  Air_temperature_K: 298.1,
  Process_temperature_K: 308.6,
  Rotational_speed_rpm: 1551,
  Torque_Nm: 42.8,
  Tool_wear_min: 0,
  Type: 1,
  temp_diff: 10.5,
  power: 66382.8,
};

const cmapssSampleRows = [
  [1, 1, 0.0023, 0.0003, 100, 518.67, 643.02, 1585.29, 1398.21, 14.62, 21.61, 553.9, 2388.04, 9050.17, 1.3, 47.2, 521.72, 2388.03, 8125.55, 8.4052, 0.03, 392, 2388, 100, 38.86, 23.3735],
  [1, 2, -0.0027, -0.0003, 100, 518.67, 641.71, 1588.45, 1395.42, 14.62, 21.61, 554.85, 2388.01, 9054.42, 1.3, 47.5, 522.16, 2388.06, 8139.62, 8.3803, 0.03, 393, 2388, 100, 39.02, 23.3916],
  [1, 3, 0.0003, 0.0001, 100, 518.67, 642.46, 1586.94, 1401.34, 14.62, 21.61, 554.11, 2388.05, 9056.96, 1.3, 47.5, 521.97, 2388.03, 8130.1, 8.4441, 0.03, 393, 2388, 100, 39.08, 23.4166],
  [1, 4, 0.0042, 0, 100, 518.67, 642.44, 1584.12, 1406.42, 14.62, 21.61, 554.07, 2388.03, 9045.29, 1.3, 47.28, 521.38, 2388.05, 8132.9, 8.3917, 0.03, 391, 2388, 100, 39, 23.3737],
  [1, 5, 0.0014, 0, 100, 518.67, 642.51, 1587.19, 1401.92, 14.62, 21.61, 554.16, 2388.01, 9044.55, 1.3, 47.31, 522.15, 2388.03, 8129.54, 8.4031, 0.03, 390, 2388, 100, 38.99, 23.413],
  [1, 6, 0.0012, 0.0003, 100, 518.67, 642.11, 1579.12, 1395.13, 14.62, 21.61, 554.22, 2388, 9050.96, 1.3, 47.26, 521.92, 2388.08, 8127.46, 8.4238, 0.03, 392, 2388, 100, 38.91, 23.3467],
  [1, 7, 0, 0.0002, 100, 518.67, 642.11, 1583.34, 1404.84, 14.62, 21.61, 553.89, 2388.05, 9051.39, 1.3, 47.31, 522.01, 2388.06, 8134.97, 8.3914, 0.03, 391, 2388, 100, 38.85, 23.3952],
  [1, 8, 0.0006, 0, 100, 518.67, 642.54, 1580.89, 1400.89, 14.62, 21.61, 553.59, 2388.05, 9052.86, 1.3, 47.21, 522.09, 2388.06, 8125.93, 8.4213, 0.03, 393, 2388, 100, 39.05, 23.3224],
];

const cmapssSample = cmapssSampleRows.map((row) => {
  const reading: Record<string, number> = { time_in_cycles: row[1] };
  for (let index = 1; index <= 21; index += 1) {
    reading[`sensor_measurement_${index}`] = row[index + 4];
  }
  return reading;
});

function ResultBlock({ value }: { value: unknown }) {
  if (!value) return null;
  return <pre className="mt-3 max-h-72 overflow-auto rounded border bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify(value, null, 2)}</pre>;
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="grid gap-1 text-sm">
      <span className="font-medium text-slate-700">{label}</span>
      <input className="rounded border border-slate-300 px-3 py-2" type="number" step="any" value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function Panel({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      {children}
    </section>
  );
}

export default function App() {
  const [health, setHealth] = useState<string>('checking');
  const [assets, setAssets] = useState<AssetSummary[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<AssetDetail | null>(null);
  const [ai4i, setAi4i] = useState<Ai4iPayload>(ai4iSample);
  const [historyText, setHistoryText] = useState(JSON.stringify(cmapssSample, null, 2));
  const [failureResult, setFailureResult] = useState<FailureRiskResponse | null>(null);
  const [rulResult, setRulResult] = useState<RulResponse | null>(null);
  const [anomalyResult, setAnomalyResult] = useState<AnomalyResponse | null>(null);
  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then((data) => setHealth(data.status)).catch((err) => setHealth(`error: ${err.message}`));
    getAssets().then(setAssets).catch(() => setAssets([]));
  }, []);

  async function submit<T>(name: string, action: () => Promise<T>, setter: (value: T) => void) {
    setError(null);
    setLoading(name);
    try {
      setter(await action());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown request error');
    } finally {
      setLoading(null);
    }
  }

  function updateAi4i(key: keyof Ai4iPayload, value: number) {
    setAi4i((current) => {
      const next = { ...current, [key]: value };
      next.temp_diff = Number((next.Process_temperature_K - next.Air_temperature_K).toFixed(4));
      next.power = Number((next.Torque_Nm * next.Rotational_speed_rpm).toFixed(4));
      return next;
    });
  }

  function runFailure(event: FormEvent) {
    event.preventDefault();
    void submit('failure-risk', () => predictFailureRisk(ai4i), setFailureResult);
  }

  function runAnomaly(event: FormEvent) {
    event.preventDefault();
    void submit('anomaly', () => predictAnomaly(ai4i), setAnomalyResult);
  }

  function runRul(event: FormEvent) {
    event.preventDefault();
    void submit('rul', () => predictRUL({ sensor_history: JSON.parse(historyText) }), setRulResult);
  }

  function runForecast(event: FormEvent) {
    event.preventDefault();
    void submit('forecast', () => predictForecast({ sensor_history: JSON.parse(historyText) }), setForecastResult);
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 text-slate-900 md:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">MaintainX Demo Console</h1>
            <p className="mt-1 text-slate-600">Real FastAPI predictions from the trained local model artifacts.</p>
          </div>
          <div className="rounded border border-slate-300 bg-white px-3 py-2 text-sm">API health: <strong>{health}</strong></div>
        </header>

        {error && <div className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-800">{error}</div>}

        <Panel title="Assets">
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            {assets.map((asset) => (
              <button
                className="rounded border border-slate-200 p-3 text-left hover:border-slate-500"
                key={asset.id}
                onClick={() => getAsset(asset.id).then(setSelectedAsset).catch((err) => setError(err.message))}
              >
                <div className="font-semibold">{asset.name}</div>
                <div className="text-sm text-slate-600">{asset.type} · {asset.risk_level} · {asset.maintenance_days} days</div>
              </button>
            ))}
          </div>
          <ResultBlock value={selectedAsset} />
        </Panel>

        <div className="grid gap-6 lg:grid-cols-2">
          <Panel title="Failure Risk">
            <form className="mt-4 grid gap-3 md:grid-cols-2" onSubmit={runFailure}>
              {Object.entries(ai4i).map(([key, value]) => (
                <NumberField key={key} label={key} value={value} onChange={(next) => updateAi4i(key as keyof Ai4iPayload, next)} />
              ))}
              <div className="flex gap-2 md:col-span-2">
                <button className="rounded bg-slate-900 px-4 py-2 text-white" disabled={loading === 'failure-risk'}>{loading === 'failure-risk' ? 'Running...' : 'Predict failure risk'}</button>
                <button className="rounded border px-4 py-2" type="button" onClick={() => setAi4i(ai4iSample)}>Load AI4I sample</button>
              </div>
            </form>
            <ResultBlock value={failureResult} />
          </Panel>

          <Panel title="Anomaly Detection">
            <form className="mt-4 space-y-3" onSubmit={runAnomaly}>
              <p className="text-sm text-slate-600">Uses the same editable AI4I payload as the failure-risk panel.</p>
              <button className="rounded bg-slate-900 px-4 py-2 text-white" disabled={loading === 'anomaly'}>{loading === 'anomaly' ? 'Running...' : 'Predict anomaly'}</button>
            </form>
            <ResultBlock value={anomalyResult} />
          </Panel>

          <Panel title="Remaining Useful Life">
            <form className="mt-4 space-y-3" onSubmit={runRul}>
              <textarea className="h-72 w-full rounded border border-slate-300 p-3 font-mono text-xs" value={historyText} onChange={(event) => setHistoryText(event.target.value)} />
              <div className="flex gap-2">
                <button className="rounded bg-slate-900 px-4 py-2 text-white" disabled={loading === 'rul'}>{loading === 'rul' ? 'Running...' : 'Predict RUL'}</button>
                <button className="rounded border px-4 py-2" type="button" onClick={() => setHistoryText(JSON.stringify(cmapssSample, null, 2))}>Load C-MAPSS sample</button>
              </div>
            </form>
            <ResultBlock value={rulResult} />
          </Panel>

          <Panel title="Sensor Forecast">
            <form className="mt-4 space-y-3" onSubmit={runForecast}>
              <p className="text-sm text-slate-600">Uses the editable C-MAPSS sensor history JSON from the RUL panel.</p>
              <button className="rounded bg-slate-900 px-4 py-2 text-white" disabled={loading === 'forecast'}>{loading === 'forecast' ? 'Running...' : 'Predict forecast'}</button>
            </form>
            <ResultBlock value={forecastResult} />
          </Panel>
        </div>
      </div>
    </main>
  );
}
