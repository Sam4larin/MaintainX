import React, { useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ForecastResponse, UploadParseResponse } from '../types';
import { Panel } from './ui/Panel';
import { PrimaryButton, RawJson } from './ui/Fields';
import { FileUpload } from './FileUpload';

interface Props {
  onSubmit: (e: React.FormEvent) => void;
  onLoadHistory: (historyJson: string) => void;
  loading: boolean;
  result: ForecastResponse | null;
}

export function SensorForecastPanel({ onSubmit, onLoadHistory, loading, result }: Props) {
  const [selectedSensor, setSelectedSensor] = useState<string>('');

  const sensorKeys = result ? Object.keys(result.forecasted_sensor_values) : [];
  const activeSensorKey = selectedSensor || (sensorKeys.length > 0 ? sensorKeys[0] : '');

  const chartData =
    result && activeSensorKey
      ? result.forecasted_cycles.map((cycle, index) => ({
          cycle: `C${cycle}`,
          value: result.forecasted_sensor_values[activeSensorKey]?.[index] ?? 0,
        }))
      : [];

  function handleParsed(parsed: UploadParseResponse) {
    if (parsed.sensor_history.length > 0) {
      onLoadHistory(JSON.stringify(parsed.sensor_history, null, 2));
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1.3fr]">
      <div className="space-y-6">
        <Panel title="Upload your own data" eyebrow="Optional · CSV, Excel, or raw C-MAPSS .txt">
          <FileUpload expects="cmapss" onParsed={handleParsed} />
        </Panel>

        <Panel title="Sensor forecast" eyebrow="Turbofan trajectory projection">
          <form onSubmit={onSubmit} className="space-y-4">
            <p className="rounded-md border border-paper-200 bg-paper-50 p-3 text-xs leading-relaxed text-ink-600">
              Uses the same sensor history loaded on the RUL tab (or uploaded above) to project future cycle values
              across every sensor channel, so you can see where a reading is trending before it crosses a threshold.
            </p>
            <PrimaryButton type="submit" loading={loading} loadingText="Projecting trajectory…">
              Run forecast
            </PrimaryButton>
          </form>
        </Panel>
      </div>

      <Panel title="Projected trajectory" eyebrow="Model output">
        {!result && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <p className="text-sm text-ink-500">Run a forecast to chart projected sensor values across future cycles.</p>
          </div>
        )}
        {result && (
          <div className="space-y-4">
            {sensorKeys.length > 0 && (
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Sensor trajectory</p>
                  <select
                    className="rounded-md border border-paper-300 bg-white px-2 py-1 text-xs font-semibold text-ink-700 focus:border-rust-500 focus:outline-none"
                    value={activeSensorKey}
                    onChange={(e) => setSelectedSensor(e.target.value)}
                  >
                    {sensorKeys.map((s) => (
                      <option key={s} value={s}>
                        {s.replace('sensor_measurement_', 'Sensor #')}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 5, right: 12, left: -18, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e9e6de" vertical={false} />
                      <XAxis dataKey="cycle" tick={{ fontSize: 10, fill: '#4d5a68' }} axisLine={false} tickLine={false} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10, fill: '#4d5a68' }} axisLine={false} tickLine={false} />
                      <Tooltip
                        formatter={(v: number) => [v.toFixed(2), 'Predicted']}
                        contentStyle={{ borderRadius: 8, border: '1px solid #e9e6de', fontSize: 12 }}
                      />
                      <Line type="monotone" dataKey="value" stroke="#bd7a35" strokeWidth={2.5} dot={{ r: 3, fill: '#bd7a35' }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            <div>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-500">All forecast values</p>
              <div className="grid max-h-40 grid-cols-1 gap-2 overflow-y-auto pr-1 sm:grid-cols-2">
                {Object.entries(result.forecasted_sensor_values).map(([sKey, values]) => (
                  <div key={sKey} className="rounded-md border border-paper-200 bg-paper-50 p-2.5">
                    <p className="text-xs font-semibold text-ink-700">{sKey.replace('sensor_measurement_', 'Sensor #')}</p>
                    <p className="truncate font-mono text-[10px] text-ink-500">
                      [{values.map((v) => v.toFixed(2)).join(', ')}]
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <RawJson data={result} />
          </div>
        )}
      </Panel>
    </div>
  );
}
