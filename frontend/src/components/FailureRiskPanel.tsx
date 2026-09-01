import React, { useState } from 'react';
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { Ai4iPayload, FailureRiskResponse, ParsedAi4iRow, UploadParseResponse } from '../types';
import { Panel } from './ui/Panel';
import { Gauge } from './ui/Gauge';
import { GhostButton, NumberField, PrimaryButton, RawJson } from './ui/Fields';
import { riskStyle, riskDisplayLabel } from '../lib/risk';
import { FileUpload } from './FileUpload';

interface Props {
  ai4i: Ai4iPayload;
  onUpdateAi4i: (k: keyof Ai4iPayload, v: number) => void;
  onLoadSample: () => void;
  onLoadRow: (row: ParsedAi4iRow) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  result: FailureRiskResponse | null;
}

export function FailureRiskPanel({ ai4i, onUpdateAi4i, onLoadSample, onLoadRow, onSubmit, loading, result }: Props) {
  const [uploadedRows, setUploadedRows] = useState<ParsedAi4iRow[]>([]);
  const [selectedRow, setSelectedRow] = useState(0);

  function handleParsed(parsed: UploadParseResponse) {
    if (parsed.ai4i_rows.length === 0) return;
    setUploadedRows(parsed.ai4i_rows);
    setSelectedRow(0);
    onLoadRow(parsed.ai4i_rows[0]);
  }

  function selectRow(index: number) {
    setSelectedRow(index);
    onLoadRow(uploadedRows[index]);
  }

  const chartData = result?.failure_type_probabilities
    ? Object.entries(result.failure_type_probabilities)
        .map(([name, prob]) => ({ name: name.replace(' Failure', ''), percentage: Number((prob * 100).toFixed(1)) }))
        .sort((a, b) => b.percentage - a.percentage)
    : [];

  const style = result ? riskStyle(result.risk_level) : null;

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_1.1fr]">
      <div className="space-y-6">
        <Panel title="Upload your own data" eyebrow="Optional · CSV or Excel">
          <FileUpload expects="ai4i" onParsed={handleParsed} />
          {uploadedRows.length > 1 && (
            <div className="mt-3">
              <label className="mb-1 block text-[11px] font-medium text-ink-500">
                Row to score ({uploadedRows.length} rows available)
              </label>
              <select
                className="w-full rounded-md border border-paper-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-ink-700 focus:border-rust-500 focus:outline-none"
                value={selectedRow}
                onChange={(e) => selectRow(Number(e.target.value))}
              >
                {uploadedRows.map((row, i) => (
                  <option key={i} value={i}>
                    Row {row.source_row} — {row.Air_temperature_K}K / {row.Torque_Nm}Nm / {row.Rotational_speed_rpm}rpm
                  </option>
                ))}
              </select>
            </div>
          )}
        </Panel>

        <Panel
          title="Failure risk model"
          eyebrow="AI4I · multi-class classifier"
          action={<GhostButton onClick={onLoadSample}>Load sample</GhostButton>}
        >
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Air temperature" unit="K" value={ai4i.Air_temperature_K} onChange={(v) => onUpdateAi4i('Air_temperature_K', v)} />
              <NumberField label="Process temperature" unit="K" value={ai4i.Process_temperature_K} onChange={(v) => onUpdateAi4i('Process_temperature_K', v)} />
              <NumberField label="Rotational speed" unit="rpm" value={ai4i.Rotational_speed_rpm} onChange={(v) => onUpdateAi4i('Rotational_speed_rpm', v)} />
              <NumberField label="Torque" unit="Nm" value={ai4i.Torque_Nm} onChange={(v) => onUpdateAi4i('Torque_Nm', v)} />
              <NumberField label="Tool wear" unit="min" value={ai4i.Tool_wear_min} onChange={(v) => onUpdateAi4i('Tool_wear_min', v)} />
              <NumberField label="Type (0=L, 1=M, 2=H)" step="1" value={ai4i.Type} onChange={(v) => onUpdateAi4i('Type', v)} />
            </div>
            <div className="flex items-center justify-between rounded-md bg-paper-50 px-3 py-2 text-[11px] text-ink-500">
              <span>Derived — Δtemp: <strong className="text-ink-700">{ai4i.temp_diff.toFixed(2)} K</strong></span>
              <span>Power: <strong className="text-ink-700">{ai4i.power.toFixed(0)} W</strong></span>
            </div>
            <PrimaryButton type="submit" loading={loading} loadingText="Scoring telemetry…">
              Predict failure risk
            </PrimaryButton>
          </form>
        </Panel>
      </div>

      <Panel title="Prediction" eyebrow="Model output">
        {!result && (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
            <p className="text-sm text-ink-500">Run the model with the telemetry on the left to see a risk breakdown.</p>
          </div>
        )}
        {result && style && (
          <div className="space-y-5">
            <div className="flex items-center gap-5">
              <Gauge
                value={result.failure_probability}
                size={112}
                strokeWidth={9}
                valueColor={style.gauge}
                label={`${(result.failure_probability * 100).toFixed(0)}%`}
                sublabel="Failure prob."
              />
              <div className="flex-1 space-y-2">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Risk level</p>
                  <span
                    className={`mt-1 inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${style.bg} ${style.text} ${style.border}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                    {riskDisplayLabel(result.risk_level)}
                  </span>
                </div>
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">Predicted mode</p>
                  <p className="font-display text-sm font-semibold text-ink-800">{result.failure_type_prediction}</p>
                </div>
              </div>
            </div>

            {chartData.length > 0 && (
              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-500">
                  Failure mode probabilities
                </p>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
                      <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 10, fill: '#4d5a68' }} axisLine={false} tickLine={false} />
                      <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#37424f' }} width={80} axisLine={false} tickLine={false} />
                      <Tooltip
                        cursor={{ fill: 'rgba(189,122,53,0.06)' }}
                        formatter={(v: number) => [`${v}%`, 'Probability']}
                        contentStyle={{ borderRadius: 8, border: '1px solid #e9e6de', fontSize: 12 }}
                      />
                      <Bar dataKey="percentage" radius={[0, 4, 4, 0]} barSize={16}>
                        {chartData.map((entry, idx) => (
                          <Cell
                            key={idx}
                            fill={entry.name === 'No' ? '#4f8a76' : entry.percentage > 20 ? '#b1493f' : '#dba15b'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            <RawJson data={result} />
          </div>
        )}
      </Panel>
    </div>
  );
}
