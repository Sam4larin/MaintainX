import type { ReactNode } from 'react';

interface PanelProps {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  padded?: boolean;
}

export function Panel({ title, eyebrow, action, children, className = '', padded = true }: PanelProps) {
  return (
    <section
      className={`rounded-xl border border-paper-300/70 bg-white shadow-panel ${padded ? 'p-5' : ''} ${className}`}
    >
      {(title || action) && (
        <div className={`flex items-start justify-between gap-3 ${padded ? 'mb-4' : 'p-5 pb-4'}`}>
          <div>
            {eyebrow && (
              <p className="mb-0.5 text-[11px] font-semibold uppercase tracking-wide text-ink-500">{eyebrow}</p>
            )}
            {title && <h3 className="font-display text-[15px] font-semibold text-ink-800">{title}</h3>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function StatCard({
  label,
  value,
  sub,
  tone = 'default',
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  tone?: 'default' | 'rust' | 'moss' | 'signal';
}) {
  const valueColor =
    tone === 'rust' ? 'text-rust-600' : tone === 'moss' ? 'text-moss-600' : tone === 'signal' ? 'text-signal-red' : 'text-ink-800';
  return (
    <div className="rounded-xl border border-paper-300/70 bg-white p-4 shadow-panel">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-ink-500">{label}</p>
      <p className={`mt-1.5 font-display text-2xl font-semibold leading-none ${valueColor}`}>{value}</p>
      {sub && <p className="mt-1.5 text-xs text-ink-500">{sub}</p>}
    </div>
  );
}
