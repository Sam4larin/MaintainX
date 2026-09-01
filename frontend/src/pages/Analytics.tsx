import type { FormEvent } from 'react';
import type { AnalyticsTab } from '../components/Sidebar';
import { FailureRiskPanel } from '../components/FailureRiskPanel';
import { AnomalyDetectionPanel } from '../components/AnomalyDetectionPanel';
import { RulPanel } from '../components/RulPanel';
import { SensorForecastPanel } from '../components/SensorForecastPanel';
import type {
  Ai4iPayload,
  AnomalyResponse,
  FailureRiskResponse,
  ForecastResponse,
  ParsedAi4iRow,
  RulResponse,
} from '../types';

interface AnalyticsProps {
  activeTab: AnalyticsTab;
  ai4i: Ai4iPayload;
  updateAi4i: (key: keyof Ai4iPayload, value: number) => void;
  loadAi4iSample: () => void;
  loadAi4iRow: (row: ParsedAi4iRow) => void;
  historyText: string;
  setHistoryText: (text: string) => void;
  loadHistorySample: () => void;
  loading: string | null;
  failureResult: FailureRiskResponse | null;
  anomalyResult: AnomalyResponse | null;
  rulResult: RulResponse | null;
  forecastResult: ForecastResponse | null;
  runFailure: (e: FormEvent) => void;
  runAnomaly: (e: FormEvent) => void;
  runRul: (e: FormEvent) => void;
  runForecast: (e: FormEvent) => void;
}

const tabMeta: Record<AnalyticsTab, { title: string; description: string }> = {
  'failure-risk': {
    title: 'Failure risk',
    description: 'Multi-class classifier trained on the AI4I industrial dataset to flag likely failure modes.',
  },
  anomaly: {
    title: 'Anomaly detection',
    description: 'Unsupervised autoencoder and isolation-forest ensemble for catching out-of-distribution readings.',
  },
  rul: {
    title: 'Remaining useful life',
    description: 'C-MAPSS-trained regression ensemble estimating cycles and days until service is required.',
  },
  forecast: {
    title: 'Sensor forecast',
    description: 'Projects sensor channels forward in time so drift is visible before it becomes a fault.',
  },
};

export function Analytics(props: AnalyticsProps) {
  const meta = tabMeta[props.activeTab];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-ink-800">{meta.title}</h2>
        <p className="text-sm text-ink-500">{meta.description}</p>
      </div>

      {props.activeTab === 'failure-risk' && (
        <FailureRiskPanel
          ai4i={props.ai4i}
          onUpdateAi4i={props.updateAi4i}
          onLoadSample={props.loadAi4iSample}
          onLoadRow={props.loadAi4iRow}
          onSubmit={props.runFailure}
          loading={props.loading === 'failure-risk'}
          result={props.failureResult}
        />
      )}

      {props.activeTab === 'anomaly' && (
        <AnomalyDetectionPanel
          onSubmit={props.runAnomaly}
          onLoadRow={props.loadAi4iRow}
          loading={props.loading === 'anomaly'}
          result={props.anomalyResult}
        />
      )}

      {props.activeTab === 'rul' && (
        <RulPanel
          historyText={props.historyText}
          setHistoryText={props.setHistoryText}
          onLoadSample={props.loadHistorySample}
          onSubmit={props.runRul}
          loading={props.loading === 'rul'}
          result={props.rulResult}
        />
      )}

      {props.activeTab === 'forecast' && (
        <SensorForecastPanel
          onSubmit={props.runForecast}
          onLoadHistory={props.setHistoryText}
          loading={props.loading === 'forecast'}
          result={props.forecastResult}
        />
      )}
    </div>
  );
}
