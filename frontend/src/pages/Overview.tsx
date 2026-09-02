import { useMemo } from 'react';
import type { AssetDetail, AssetSummary } from '../types';
import { Gauge } from '../components/ui/Gauge';
import { Panel, StatCard } from '../components/ui/Panel';
import { riskStyle, riskTone, riskDisplayLabel } from '../lib/risk';

interface OverviewProps {
  assets: AssetSummary[];
  selectedAsset: AssetDetail | null;
  onSelectAsset: (assetId: string) => void;
  assetLoading: boolean;
}

function AssetIcon({ type }: { type: string }) {
  const t = type.toLowerCase();
  if (t.includes('pump')) {
    return (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
        <circle cx="10" cy="12" r="6.2" />
        <path strokeLinecap="round" d="M16 9.5L21 6v9l-5-3.5" />
      </svg>
    );
  }
  if (t.includes('hvac')) {
    return (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M4.5 6.5l15 11M19.5 6.5l-15 11" />
      </svg>
    );
  }
  if (t.includes('elevator')) {
    return (
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
        <rect x="5" y="3.5" width="14" height="17" rx="1.5" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 9L12 7.5 13.5 9M10.5 15l1.5 1.5 1.5-1.5" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <path strokeLinecap="round" d="M9 9h6v6H9z" />
    </svg>
  );
}

export function Overview({ assets, selectedAsset, onSelectAsset, assetLoading }: OverviewProps) {
  const stats = useMemo(() => {
    const total = assets.length;
    const critical = assets.filter((a) => riskTone(a.risk_level) === 'critical').length;
    const high = assets.filter((a) => riskTone(a.risk_level) === 'high').length;
    const healthy = assets.filter((a) => riskTone(a.risk_level) === 'low').length;
    const avgDays =
      total > 0 ? Math.round(assets.reduce((sum, a) => sum + a.maintenance_days, 0) / total) : 0;
    const nextDue = total > 0 ? Math.min(...assets.map((a) => a.maintenance_days)) : 0;
    const fleetScore = total > 0 ? Math.max(0, 1 - (critical * 1 + high * 0.5) / total) : 1;
    return { total, critical, high, healthy, avgDays, nextDue, fleetScore };
  }, [assets]);

  const sortedAssets = useMemo(
    () => [...assets].sort((a, b) => a.maintenance_days - b.maintenance_days),
    [assets],
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-ink-800">Fleet overview</h2>
        <p className="text-sm text-ink-500">A plain-language snapshot of every monitored asset. Open Analytics for model-level detail.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[auto_1fr]">
        <Panel className="flex flex-col items-center justify-center gap-3 lg:w-56">
          <Gauge
            value={stats.fleetScore}
            size={140}
            valueColor={stats.fleetScore > 0.75 ? '#4f8a76' : stats.fleetScore > 0.5 ? '#b8873a' : '#b1493f'}
            label={`${Math.round(stats.fleetScore * 100)}%`}
            sublabel="Fleet health"
          />
          <p className="text-center text-xs text-ink-500">
            Weighted across {stats.total} asset{stats.total === 1 ? '' : 's'} by current risk level
          </p>
        </Panel>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Assets monitored" value={stats.total} sub="Across all sites" />
          <StatCard
            label="Critical / high risk"
            value={stats.critical + stats.high}
            sub={`${stats.critical} critical, ${stats.high} high`}
            tone={stats.critical + stats.high > 0 ? 'signal' : 'default'}
          />
          <StatCard label="Healthy assets" value={stats.healthy} sub="Low risk classification" tone="moss" />
          <StatCard
            label="Next service due"
            value={stats.total > 0 ? `${stats.nextDue}d` : '—'}
            sub={`Fleet average ${stats.avgDays}d`}
            tone="rust"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Panel title="Asset fleet" eyebrow="Sorted by urgency" padded={false}>
          <div className="divide-y divide-paper-200">
            {sortedAssets.length === 0 && (
              <p className="px-5 py-8 text-center text-sm text-ink-500">No assets returned by the API yet.</p>
            )}
            {sortedAssets.map((asset) => {
              const style = riskStyle(asset.risk_level);
              const isSelected = selectedAsset?.id === asset.id;
              const urgent = asset.maintenance_days <= 10;
              return (
                <button
                  key={asset.id}
                  onClick={() => onSelectAsset(asset.id)}
                  className={`flex w-full items-center gap-4 border-l-[3px] px-5 py-3.5 text-left transition-colors hover:bg-paper-50 ${
                    isSelected ? 'border-l-rust-500 bg-rust-50' : 'border-l-transparent'
                  }`}
                >
                  <div
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${style.bg} ${style.text}`}
                  >
                    <AssetIcon type={asset.type} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-semibold text-ink-800">{asset.name}</p>
                      <span
                        className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${style.bg} ${style.text} ${style.border}`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
                        {riskDisplayLabel(asset.risk_level)}
                      </span>
                    </div>
                    <p className="mt-0.5 text-xs text-ink-500">{asset.type}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className={`font-display text-sm font-semibold ${urgent ? 'text-signal-red' : 'text-ink-700'}`}>
                      {asset.maintenance_days}d
                    </p>
                    <p className="text-[11px] text-ink-500">until service</p>
                  </div>
                </button>
              );
            })}
          </div>
        </Panel>

        <Panel title="Asset detail" eyebrow={selectedAsset ? selectedAsset.id : 'Select an asset'}>
          {assetLoading && <p className="text-sm text-ink-500">Loading asset detail…</p>}
          {!assetLoading && !selectedAsset && (
            <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-paper-100 text-ink-400">
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.6}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-sm text-ink-500">Click an asset in the list to view its recent sensor history.</p>
            </div>
          )}
          {!assetLoading && selectedAsset && (
            <div className="space-y-4">
              <div className="flex items-center justify-between rounded-lg bg-paper-50 px-4 py-3">
                <div>
                  <p className="font-display text-base font-semibold text-ink-800">{selectedAsset.name}</p>
                  <p className="text-xs text-ink-500">{selectedAsset.type}</p>
                </div>
                <span
                  className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold ${riskStyle(selectedAsset.risk_level).bg} ${riskStyle(selectedAsset.risk_level).text} ${riskStyle(selectedAsset.risk_level).border}`}
                >
                  {riskDisplayLabel(selectedAsset.risk_level)}
                </span>
              </div>

              <div>
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-500">
                  Recent sensor readings
                </p>
                <div className="space-y-2">
                  {selectedAsset.history.length === 0 && (
                    <p className="text-sm text-ink-500">No history recorded for this asset.</p>
                  )}
                  {selectedAsset.history.map((entry, idx) => {
                    const sensorLabel = String(entry.sensor ?? `Reading ${idx + 1}`);
                    const raw = entry.value;
                    const numeric = typeof raw === 'number' ? raw : Number(raw);
                    const pct = Number.isFinite(numeric) ? Math.max(0, Math.min(1, numeric)) : 0;
                    return (
                      <div key={idx} className="flex items-center gap-3">
                        <span className="w-24 shrink-0 text-xs font-medium capitalize text-ink-600">
                          {sensorLabel}
                        </span>
                        <div className="h-2 flex-1 overflow-hidden rounded-full bg-paper-200">
                          <div
                            className={`h-full rounded-full ${pct > 0.7 ? 'bg-signal-red' : pct > 0.4 ? 'bg-signal-amber' : 'bg-moss-500'}`}
                            style={{ width: `${pct * 100}%` }}
                          />
                        </div>
                        <span className="w-12 shrink-0 text-right font-display text-xs font-semibold text-ink-700">
                          {Number.isFinite(numeric) ? numeric.toFixed(2) : String(raw)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-lg border border-paper-200 bg-paper-50 px-4 py-3">
                <p className="text-xs text-ink-500">
                  Next scheduled maintenance in{' '}
                  <span className="font-display font-semibold text-ink-800">{selectedAsset.maintenance_days} days</span>.
                  For a full model breakdown, open the Analytics tab and load this asset's telemetry into the relevant engine.
                </p>
              </div>
            </div>
          )}
        </Panel>
      </div>
    </div>
  );
}
