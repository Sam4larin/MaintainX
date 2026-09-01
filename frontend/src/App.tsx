import { FormEvent, useEffect, useMemo, useState } from 'react';
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
  ParsedAi4iRow,
  RulResponse,
} from './types';
import { Sidebar, type AnalyticsTab, type ViewId } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { Analytics } from './pages/Analytics';
import { riskTone } from './lib/risk';

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

const viewTitles: Record<ViewId, string> = {
  overview: 'Fleet overview',
  analytics: 'Predictive analytics',
};

export default function App() {
  const [activeView, setActiveView] = useState<ViewId>('overview');
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('failure-risk');
  const [health, setHealth] = useState<string>('checking');
  const [healthDetail, setHealthDetail] = useState<string | null>(null);
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
    getHealth()
      .then((data) => {
        setHealth(data.status);
        setHealthDetail(data.detail);
      })
      .catch((err) => {
        setHealth('unreachable');
        setHealthDetail(err instanceof Error ? err.message : null);
      });
    getAssets()
      .then(setAssets)
      .catch(() => setAssets([]));
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

  function loadAi4iRow(row: ParsedAi4iRow) {
    setAi4i({
      Air_temperature_K: row.Air_temperature_K,
      Process_temperature_K: row.Process_temperature_K,
      Rotational_speed_rpm: row.Rotational_speed_rpm,
      Torque_Nm: row.Torque_Nm,
      Tool_wear_min: row.Tool_wear_min,
      Type: row.Type,
      temp_diff: row.temp_diff,
      power: row.power,
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

  function selectAssetHandler(assetId: string) {
    setLoading('asset-fetch');
    getAsset(assetId)
      .then(setSelectedAsset)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(null));
  }

  const alertCount = useMemo(
    () => assets.filter((a) => ['critical', 'high'].includes(riskTone(a.risk_level))).length,
    [assets],
  );

  return (
    <div className="flex min-h-screen flex-col bg-paper-50 font-sans text-ink-800 md:flex-row">
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        healthDetail={healthDetail}
        fleetCount={assets.length}
        alertCount={alertCount}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-paper-300/70 bg-white/90 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Predictive maintenance</p>
            <h1 className="font-display text-lg font-semibold tracking-tight text-ink-800">{viewTitles[activeView]}</h1>
          </div>
          <div className="hidden items-center gap-2 sm:flex">
            {alertCount > 0 && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-[#e6c9c1] bg-[#f8ece9] px-3 py-1 text-xs font-semibold text-signal-red">
                <span className="h-1.5 w-1.5 rounded-full bg-signal-red" />
                {alertCount} asset{alertCount === 1 ? '' : 's'} need attention
              </span>
            )}
            <span className="rounded-full border border-paper-300 bg-paper-100 px-3 py-1 text-xs font-medium text-ink-500">
              Production ML environment
            </span>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl flex-1 space-y-6 p-6">
          {error && (
            <div className="flex items-center justify-between rounded-xl border border-[#e6c9c1] bg-[#f8ece9] p-4 text-sm text-signal-crimson shadow-panel">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 shrink-0 text-signal-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{error}</span>
              </div>
              <button type="button" onClick={() => setError(null)} className="text-xs font-semibold text-signal-red hover:text-signal-crimson">
                Dismiss
              </button>
            </div>
          )}

          {activeView === 'overview' && (
            <Overview
              assets={assets}
              selectedAsset={selectedAsset}
              onSelectAsset={selectAssetHandler}
              assetLoading={loading === 'asset-fetch'}
            />
          )}

          {activeView === 'analytics' && (
            <Analytics
              activeTab={activeTab}
              ai4i={ai4i}
              updateAi4i={updateAi4i}
              loadAi4iSample={() => setAi4i(ai4iSample)}
              loadAi4iRow={loadAi4iRow}
              historyText={historyText}
              setHistoryText={setHistoryText}
              loadHistorySample={() => setHistoryText(JSON.stringify(cmapssSample, null, 2))}
              loading={loading}
              failureResult={failureResult}
              anomalyResult={anomalyResult}
              rulResult={rulResult}
              forecastResult={forecastResult}
              runFailure={runFailure}
              runAnomaly={runAnomaly}
              runRul={runRul}
              runForecast={runForecast}
            />
          )}
        </main>
      </div>
    </div>
  );
}
