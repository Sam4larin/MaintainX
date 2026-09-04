import React from 'react';
import type { RulResponse } from '../types';
import { Panel } from './ui/Panel';
import { Gauge } from './ui/Gauge';
import { GhostButton, PrimaryButton, RawJson } from './ui/Fields';

interface Props {
  historyText: string;
  setHistoryText: (text: string) => void;
  onLoadSample: () => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  result: RulResponse | null;
  uploadedFileName: string | null;
}

export function RulPanel({ historyText, setHistoryText, onLoadSample, onSubmit, loading, result, uploadedFileName }: Props) {
  const rulTone = result
    ? result.recommended_maintenance_window_days <= 7
      ? { text: 'text-signal-red', bg: 'bg-[#f8ece9]', border: 'border-[#e6c9c1]', gauge: '#b1493f' }
      : result.recommended_maintenance_window_days <= 20
        ? { text: 'text-signal-amber', bg: 'bg-[#f7eedd]', border: 'border-[#e7d3a9]', gauge: '#b8873a' }
        : { text: 'text-moss-600', bg: 'bg-moss-50', border: 'border-moss-100', gauge: '#4f8a76' }
    : null;

  const gaugeFraction = result ? Math.max(0, Math.min(1, result.predicted_rul_days / 120)) : 0;

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1.1fr]">
      <div className="space-y-6">
        {uploadedFileName && (
          <Panel title="Using uploaded data" eyebrow={uploadedFileName}>
            <p className="text-xs text-ink-500">
              The sensor history below was loaded from your uploaded file — edit it directly if needed.
            </p>
          </Panel>
        )}

        <Panel
          title="Remaining useful life"
          eyebrow="C-MAPSS · time-to-failure regression"
          action={<GhostButton onClick={onLoadSample}>Load sample</GhostButton>}
        >
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-[11px] font-medium text-ink-500">
                Sensor history (JSON array of time-series cycles)
              </label>
              <textarea
                className="h-44 w-full rounded-lg border border-ink-700 bg-ink-950 p-3 font-mono text-[11px] leading-relaxed text-moss-300 focus:border-rust-500 focus:outline-none"
                value={historyText}
                onChange={(e) => setHistoryText(e.target.value)}
                spellCheck={false}
              />
            </div>
            <PrimaryButton type="submit" loading={loading} loadingText="Calculating RUL…">
              Predict remaining useful life
            </PrimaryButton>
          </form>
        </Panel>
      </div>

      <Panel title="Prediction" eyebrow="Model output">
        {!result && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <p className="text-sm text-ink-500">Submit a sensor history to estimate remaining service life.</p>
          </div>
        )}
        {result && rulTone && (
          <div className="space-y-5">
            <div className="flex items-center gap-5">
              <Gauge
                value={gaugeFraction}
                size={112}
                strokeWidth={9}
                valueColor={rulTone.gauge}
                label={result.predicted_rul_days.toFixed(0)}
                sublabel="Days left"
              />
              <div className="flex-1 space-y-2">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Predicted cycles</p>
                  <p className="font-display text-lg font-semibold text-ink-800">
                    {result.predicted_rul_cycles} <span className="text-xs font-normal text-ink-500">cycles</span>
                  </p>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Model used</p>
                  <span className="inline-block rounded-full bg-rust-50 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-rust-600">
                    {result.model_used}
                  </span>
                </div>
              </div>
            </div>

            <div className={`flex items-center justify-between rounded-lg border px-4 py-3 ${rulTone.bg} ${rulTone.border}`}>
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Maintenance window</p>
                <p className={`font-display text-sm font-semibold ${rulTone.text}`}>
                  Schedule service within {result.recommended_maintenance_window_days} days
                </p>
              </div>
              <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide ${rulTone.text} ${rulTone.bg} border ${rulTone.border}`}>
                Action needed
              </span>
            </div>

            <div className="rounded-md border border-paper-200 bg-paper-50 p-3.5">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-500">Ensemble breakdown</p>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-ink-500">XGBoost regression</p>
                  <p className="font-display font-semibold text-ink-800">{result.xgboost_prediction.toFixed(1)} cycles</p>
                </div>
                <div>
                  <p className="text-ink-500">LSTM network</p>
                  <p className="font-display font-semibold text-ink-800">
                    {result.lstm_prediction !== null ? `${result.lstm_prediction.toFixed(1)} cycles` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <RawJson data={result} />
          </div>
        )}
      </Panel>
    </div>
  );
}
