import type { ReactNode } from 'react';

export type ViewId = 'overview' | 'analytics';
export type AnalyticsTab = 'failure-risk' | 'anomaly' | 'rul' | 'forecast';

interface SidebarProps {
  activeView: ViewId;
  setActiveView: (view: ViewId) => void;
  activeTab: AnalyticsTab;
  setActiveTab: (tab: AnalyticsTab) => void;
  health: string;
  healthDetail?: string | null;
  fleetCount: number;
  alertCount: number;
}

function GaugeMark() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
      <path strokeLinecap="round" d="M12 4a8 8 0 1 0 5.66 2.34" />
      <path strokeLinecap="round" d="M12 4v4" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 12l3.2-2.6" />
    </svg>
  );
}

function GridMark() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.7}>
      <rect x="4" y="4" width="7" height="7" rx="1.5" />
      <rect x="13" y="4" width="7" height="7" rx="1.5" />
      <rect x="4" y="13" width="7" height="7" rx="1.5" />
      <rect x="13" y="13" width="7" height="7" rx="1.5" />
    </svg>
  );
}

const analyticsTabs: { id: AnalyticsTab; label: string; icon: ReactNode }[] = [
  {
    id: 'failure-risk',
    label: 'Failure risk',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.5m0 3.5h.01M5.07 19h13.86c1.4 0 2.28-1.53 1.58-2.75L13.58 4.5c-.7-1.22-2.46-1.22-3.16 0L3.5 16.25c-.7 1.22.18 2.75 1.57 2.75z" />
      </svg>
    ),
  },
  {
    id: 'anomaly',
    label: 'Anomaly detection',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h4l2-7 4 14 2-7h6" />
      </svg>
    ),
  },
  {
    id: 'rul',
    label: 'Remaining useful life',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={1.8}>
        <circle cx="12" cy="12" r="8.2" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 7.5V12l3 2" />
      </svg>
    ),
  },
  {
    id: 'forecast',
    label: 'Sensor forecast',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={1.8}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 17l4.5-5 3.5 3 4-6L20 12" />
      </svg>
    ),
  },
];

export function Sidebar({
  activeView,
  setActiveView,
  activeTab,
  setActiveTab,
  health,
  healthDetail,
  fleetCount,
  alertCount,
}: SidebarProps) {
  const isHealthy = health === 'healthy' || health === 'ok';
  const isDegraded = health === 'degraded';

  return (
    <aside className="flex w-full shrink-0 flex-col border-r border-ink-700/60 bg-ink-900 text-ink-100 md:min-h-screen md:w-64">
      <div className="flex items-center gap-3 border-b border-ink-700/60 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-rust-500 text-ink-950">
          <GaugeMark />
        </div>
        <div>
          <h1 className="font-display text-[15px] font-semibold leading-tight tracking-tight text-white">Maintora</h1>
          <p className="text-[11px] font-medium text-ink-500">Condition monitoring</p>
        </div>
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto p-3">
        <div>
          <button
            onClick={() => setActiveView('overview')}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              activeView === 'overview'
                ? 'bg-ink-800 text-white'
                : 'text-paper-100 hover:bg-ink-800/60 hover:text-white'
            }`}
          >
            <GridMark />
            <span className="flex-1 text-left">Overview</span>
            {alertCount > 0 && (
              <span className="rounded-full bg-signal-red/90 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                {alertCount}
              </span>
            )}
          </button>
        </div>

        <div>
          <button
            onClick={() => setActiveView('analytics')}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              activeView === 'analytics'
                ? 'bg-ink-800 text-white'
                : 'text-paper-100 hover:bg-ink-800/60 hover:text-white'
            }`}
          >
            <GaugeMark />
            <span className="flex-1 text-left">Analytics</span>
          </button>

          {activeView === 'analytics' && (
            <div className="ml-4 mt-1 space-y-0.5 border-l border-ink-700/60 pl-3.5">
              {analyticsTabs.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-[13px] font-medium transition-colors ${
                      isActive ? 'bg-rust-500/15 text-rust-300' : 'text-paper-200/80 hover:bg-ink-800/60 hover:text-ink-100'
                    }`}
                  >
                    <span className={isActive ? 'text-rust-400' : 'text-paper-300/70'}>{tab.icon}</span>
                    <span className="truncate text-left">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </nav>

      <div className="space-y-3 border-t border-ink-700/60 p-4">
        <div className="flex items-center justify-between text-xs">
          <span className="font-medium text-paper-200/80">Fleet monitored</span>
          <span className="font-display font-semibold text-white">{fleetCount}</span>
        </div>
        <div
          className="flex items-center justify-between rounded-md bg-ink-950/60 px-3 py-2 text-xs"
          title={healthDetail ?? undefined}
        >
          <span className="font-medium text-paper-200/80">Inference API</span>
          <div className="flex items-center gap-1.5">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isHealthy ? 'bg-moss-500' : isDegraded ? 'bg-signal-amber' : health === 'checking' ? 'bg-signal-amber' : 'bg-signal-red'
              } ${isHealthy ? 'animate-pulse' : ''}`}
            />
            <span
              className={`font-medium capitalize ${
                isHealthy ? 'text-moss-300' : isDegraded ? 'text-signal-amber' : health === 'checking' ? 'text-signal-amber' : 'text-signal-red'
              }`}
            >
              {health}
            </span>
          </div>
        </div>
        {healthDetail && (
          <p className="text-[10px] leading-snug text-paper-300/70">{healthDetail}</p>
        )}
      </div>
    </aside>
  );
}
