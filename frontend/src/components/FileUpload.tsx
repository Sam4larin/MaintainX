import { useRef, useState } from 'react';
import type { UploadParseResponse } from '../types';
import { uploadEquipmentFile } from '../api/client';

interface FileUploadProps {
  /** Which shape this tab expects, so we can warn on a mismatch. */
  expects: 'ai4i' | 'cmapss';
  onParsed: (result: UploadParseResponse) => void;
}

const formatLabel: Record<string, string> = {
  ai4i: 'Machine process data (AI4I-style)',
  cmapss: 'Sensor time-series (C-MAPSS-style)',
  unknown: 'Unrecognized format',
};

export function FileUpload({ expects, onParsed }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadParseResponse | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    setResult(null);
    setFileName(file.name);
    try {
      const parsed = await uploadEquipmentFile(file);
      setResult(parsed);
      if (parsed.detected_format !== 'unknown') {
        onParsed(parsed);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not parse this file.');
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void handleFile(file);
  }

  const mismatch = result && result.detected_format !== 'unknown' && result.detected_format !== expects;

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-6 text-center transition-colors ${
          dragOver ? 'border-rust-500 bg-rust-50' : 'border-paper-300 bg-paper-50 hover:border-rust-300'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.txt"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleFile(file);
            e.target.value = '';
          }}
        />
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-ink-500 shadow-sm">
          <svg viewBox="0 0 24 24" className="h-4.5 w-4.5" fill="none" stroke="currentColor" strokeWidth={1.7}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0L7 9m5-5l5 5M5 20h14" />
          </svg>
        </div>
        <p className="text-xs font-semibold text-ink-700">
          {loading ? 'Reading file…' : 'Drop your equipment data file here, or click to browse'}
        </p>
        <p className="text-[11px] text-ink-500">.csv, .xlsx, or .txt · exported from your CMMS, historian, or a spreadsheet</p>
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-[#e6c9c1] bg-[#f8ece9] p-3 text-xs text-signal-crimson">
          <svg className="mt-0.5 h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="space-y-2 rounded-md border border-paper-200 bg-paper-50 p-3">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold text-ink-700">{fileName}</p>
              <p className="text-[11px] text-ink-500">
                {formatLabel[result.detected_format]} · {result.row_count} row{result.row_count === 1 ? '' : 's'} found
              </p>
            </div>
            {result.detected_format !== 'unknown' && !mismatch && (
              <span className="shrink-0 rounded-full bg-moss-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-moss-600">
                Loaded
              </span>
            )}
          </div>

          {mismatch && (
            <p className="rounded border border-[#e7d3a9] bg-[#f7eedd] px-2.5 py-1.5 text-[11px] text-signal-amber">
              This looks like {formatLabel[result.detected_format].toLowerCase()}, but this tab expects{' '}
              {formatLabel[expects].toLowerCase()}. Try this file on the matching tab instead.
            </p>
          )}

          {result.detected_format === 'unknown' && (
            <p className="rounded border border-[#e7d3a9] bg-[#f7eedd] px-2.5 py-1.5 text-[11px] text-signal-amber">
              Columns found: {result.columns_found.slice(0, 6).join(', ')}
              {result.columns_found.length > 6 ? '…' : ''}
            </p>
          )}

          {result.warnings.length > 0 && (
            <ul className="space-y-1">
              {result.warnings.map((w, i) => (
                <li key={i} className="flex items-start gap-1.5 text-[11px] text-ink-500">
                  <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-ink-400" />
                  {w}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
