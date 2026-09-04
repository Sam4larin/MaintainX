import React from 'react';
import type { AnomalyResponse, ParsedAi4iRow } from '../types';
import { Panel } from './ui/Panel';
import { PrimaryButton, RawJson } from './ui/Fields';

interface Props {
  onSubmit: (e: React.FormEvent) => void;
  onLoadRow: (row: ParsedAi4iRow) => void;
  loading: boolean;
  result: AnomalyResponse | null;
  uploadedFileName: string | null;
  uploadedRows: ParsedAi4iRow[];
}

export function AnomalyDetectionPanel({ loading, result, onSubmit, uploadedFileName, uploadedRows }: Props) {
  const errorPercent = result
    ? Math.min(100, Math.round((result.autoencoder_reconstruction_error / result.anomaly_threshold) * 100))
    : 0;

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1.1fr]">
      <div className="space-y-6">
        {uploadedRows.length > 0 && (
          <Panel title="Using uploaded data" eyebrow={uploadedFileName ?? 'From sidebar upload'}>
            <p className="text-xs text-ink-500">
              Scoring against the telemetry loaded from your uploaded file (same reading used on the Failure Risk tab).
            </p>
          </Panel>
        )}

        <Panel title="Anomaly detection" eyebrow="Autoencoder + Isolation Forest">
          <form onSubmit={onSubmit} className="space-y-4">
            <p className="rounded-md border border-paper-200 bg-paper-50 p-3 text-xs leading-relaxed text-ink-600">
              Evaluates the currently loaded telemetry payload against unsupervised reconstruction-error thresholds and
              an isolation-forest density boundary. Update values on the Failure Risk tab or upload a file in the
              sidebar, then run this check on the same reading.
            </p>
            <PrimaryButton type="submit" loading={loading} loadingText="Auditing telemetry…">
              Run anomaly check
            </PrimaryButton>
          </form>
        </Panel>
      </div>

      <Panel title="Detection result" eyebrow="Model output">
        {!result && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <p className="text-sm text-ink-500">Run the check to compare this reading against learned normal behavior.</p>
          </div>
        )}
        {result && (
          <div className="space-y-4">
            <div
              className={`flex items-center justify-between rounded-lg border px-4 py-3 ${
                result.is_anomaly ? 'border-[#e6c9c1] bg-[#f8ece9]' : 'border-moss-100 bg-moss-50'
              }`}
            >
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Detection status</p>
                <p className={`font-display text-base font-semibold ${result.is_anomaly ? 'text-signal-red' : 'text-moss-600'}`}>
                  {result.is_anomaly ? 'Anomaly detected' : 'Normal operating conditions'}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-[11px] font-bold tracking-wide ${
                  result.is_anomaly ? 'bg-signal-red text-white' : 'bg-moss-500 text-white'
                }`}
              >
                {result.is_anomaly ? 'ALERT' : 'HEALTHY'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md border border-paper-200 bg-paper-50 p-3">
                <p className="text-[11px] font-medium text-ink-500">Reconstruction error</p>
                <p className="font-display text-lg font-semibold text-ink-800">
                  {result.autoencoder_reconstruction_error.toFixed(4)}
                </p>
              </div>
              <div className="rounded-md border border-paper-200 bg-paper-50 p-3">
                <p className="text-[11px] font-medium text-ink-500">Isolation forest score</p>
                <p className="font-display text-lg font-semibold text-ink-800">
                  {result.isolation_forest_score.toFixed(4)}
                </p>
              </div>
            </div>

            <div className="rounded-md border border-paper-200 bg-paper-50 p-3.5">
              <div className="mb-1.5 flex items-center justify-between text-xs font-semibold">
                <span className="text-ink-600">Reconstruction error vs. threshold</span>
                <span className={result.is_anomaly ? 'text-signal-red' : 'text-ink-500'}>{errorPercent}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-paper-200">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${result.is_anomaly ? 'bg-signal-red' : 'bg-moss-500'}`}
                  style={{ width: `${errorPercent}%` }}
                />
              </div>
              <div className="mt-1.5 flex justify-between text-[10px] text-ink-400">
                <span>0.0000</span>
                <span>Threshold: {result.anomaly_threshold.toFixed(4)}</span>
              </div>
            </div>

            <RawJson data={result} />
          </div>
        )}
      </Panel>
    </div>
  );
}
