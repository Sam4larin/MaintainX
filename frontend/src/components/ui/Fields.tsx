import { useState, type ReactNode } from 'react';

export function NumberField({
  label,
  value,
  onChange,
  step = 'any',
  unit,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: string;
  unit?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-[11px] font-medium text-ink-500">{label}</span>
      <div className="relative">
        <input
          type="number"
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full rounded-md border border-paper-300 bg-paper-50 px-2.5 py-1.5 text-sm font-medium text-ink-800 tabular-nums transition-colors focus:border-rust-500 focus:bg-white focus:outline-none"
        />
        {unit && (
          <span className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] font-medium text-ink-400">
            {unit}
          </span>
        )}
      </div>
    </label>
  );
}

export function PrimaryButton({
  children,
  loading,
  loadingText = 'Running…',
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean; loadingText?: string }) {
  return (
    <button
      {...rest}
      disabled={loading || rest.disabled}
      className="flex w-full items-center justify-center gap-2 rounded-md bg-rust-500 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-rust-600 disabled:cursor-not-allowed disabled:opacity-60"
    >
      {loading && (
        <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
      )}
      {loading ? loadingText : children}
    </button>
  );
}

export function GhostButton({ children, ...rest }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...rest}
      className="rounded-md border border-paper-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-ink-600 transition-colors hover:border-rust-300 hover:text-rust-600"
    >
      {children}
    </button>
  );
}

export function RawJson({ data }: { data: unknown }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 text-[11px] font-semibold text-ink-500 hover:text-ink-700"
      >
        <svg
          viewBox="0 0 24 24"
          className={`h-3 w-3 transition-transform ${open ? 'rotate-90' : ''}`}
          fill="none"
          stroke="currentColor"
          strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 6l6 6-6 6" />
        </svg>
        {open ? 'Hide raw response' : 'View raw response'}
      </button>
      {open && (
        <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-ink-950 p-3 font-mono text-[11px] leading-relaxed text-moss-300">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}

export function EmptyState({ icon, text }: { icon: ReactNode; text: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-paper-300 py-8 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-paper-100 text-ink-400">{icon}</div>
      <p className="max-w-[220px] text-xs text-ink-500">{text}</p>
    </div>
  );
}
