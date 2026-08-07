import { useEffect, useMemo, useState } from 'react';
import { getAssets } from '../api/client';

interface DashboardProps {
  onSelectAsset: (id: string) => void;
}

export default function DashboardPage({ onSelectAsset }: DashboardProps) {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assetType, setAssetType] = useState('all');
  const [riskLevel, setRiskLevel] = useState('all');

  useEffect(() => {
    getAssets()
      .then((data) => setAssets(data))
      .catch(() => setError('Unable to load assets'))
      .finally(() => setLoading(false));
  }, []);

  const filteredAssets = useMemo(() => assets.filter((asset) => {
    const typeMatch = assetType === 'all' || asset.type.toLowerCase() === assetType.toLowerCase();
    const riskMatch = riskLevel === 'all' || asset.risk_level.toLowerCase() === riskLevel.toLowerCase();
    return typeMatch && riskMatch;
  }), [assets, assetType, riskLevel]);

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="rounded-2xl bg-white p-6 shadow">
          <h1 className="text-3xl font-semibold">MaintainX Facility Dashboard</h1>
          <p className="mt-2 text-slate-600">A unified fleet view for predictive maintenance insights.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl bg-white p-4 shadow"><p className="text-sm text-slate-500">Total assets</p><p className="text-2xl font-semibold">{assets.length}</p></div>
          <div className="rounded-2xl bg-white p-4 shadow"><p className="text-sm text-slate-500">Critical assets</p><p className="text-2xl font-semibold">{assets.filter((a) => a.risk_level === 'Critical').length}</p></div>
          <div className="rounded-2xl bg-white p-4 shadow"><p className="text-sm text-slate-500">Average fleet health</p><p className="text-2xl font-semibold">{Math.round(100 - assets.reduce((acc, a) => acc + (a.maintenance_days || 0), 0) / Math.max(1, assets.length))}%</p></div>
        </div>
        <div className="flex gap-4 rounded-2xl bg-white p-4 shadow">
          <select className="rounded border px-3 py-2" value={assetType} onChange={(e) => setAssetType(e.target.value)}>
            <option value="all">All types</option>
            <option value="elevator">Elevator</option>
            <option value="hvac">HVAC</option>
            <option value="pump">Pump</option>
          </select>
          <select className="rounded border px-3 py-2" value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
            <option value="all">All risks</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        {loading ? <div className="rounded-2xl bg-white p-8 shadow text-center">Loading…</div> : error ? <div className="rounded-2xl bg-red-100 p-8 shadow text-center">{error}</div> : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{filteredAssets.map((asset) => (
          <button key={asset.id} className="rounded-2xl bg-white p-6 text-left shadow hover:shadow-lg" onClick={() => onSelectAsset(asset.id)}>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">{asset.name}</h2>
              <span className={`rounded-full px-3 py-1 text-sm ${asset.risk_level === 'Critical' ? 'bg-red-100 text-red-700' : asset.risk_level === 'High' ? 'bg-orange-100 text-orange-700' : asset.risk_level === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>{asset.risk_level}</span>
            </div>
            <p className="mt-2 text-slate-600">Type: {asset.type}</p>
            <p className="mt-4 text-sm text-slate-500">Recommended maintenance: {asset.maintenance_days} days</p>
          </button>
        ))}</div>}
      </div>
    </div>
  );
}
