import { useEffect, useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import AssetDetailPage from './pages/AssetDetailPage';

export default function App() {
  const [page, setPage] = useState<'dashboard' | 'asset'>('dashboard');
  const [assetId, setAssetId] = useState<string | null>(null);

  useEffect(() => {
    const onHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash.startsWith('asset/')) {
        setAssetId(hash.replace('asset/', ''));
        setPage('asset');
      } else {
        setPage('dashboard');
      }
    };
    onHashChange();
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  return page === 'asset' && assetId ? <AssetDetailPage assetId={assetId} /> : <DashboardPage onSelectAsset={(id) => { window.location.hash = `asset/${id}`; }} />;
}
