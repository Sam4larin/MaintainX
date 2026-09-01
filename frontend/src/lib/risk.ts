export type RiskTone = 'critical' | 'high' | 'medium' | 'low';

export function riskTone(level?: string): RiskTone {
  const normalized = (level ?? '').toLowerCase();
  if (normalized === 'critical') return 'critical';
  if (normalized === 'high') return 'high';
  if (normalized === 'medium' || normalized === 'moderate') return 'medium';
  return 'low';
}

interface RiskStyle {
  text: string;
  bg: string;
  border: string;
  dot: string;
  gauge: string;
}

const styles: Record<RiskTone, RiskStyle> = {
  critical: {
    text: 'text-signal-crimson',
    bg: 'bg-[#f7e9e7]',
    border: 'border-[#e2c3bd]',
    dot: 'bg-signal-crimson',
    gauge: '#8f3730',
  },
  high: {
    text: 'text-signal-red',
    bg: 'bg-[#f8ece9]',
    border: 'border-[#e6c9c1]',
    dot: 'bg-signal-red',
    gauge: '#b1493f',
  },
  medium: {
    text: 'text-signal-amber',
    bg: 'bg-[#f7eedd]',
    border: 'border-[#e7d3a9]',
    dot: 'bg-signal-amber',
    gauge: '#b8873a',
  },
  low: {
    text: 'text-moss-600',
    bg: 'bg-moss-50',
    border: 'border-moss-100',
    dot: 'bg-moss-500',
    gauge: '#4f8a76',
  },
};

export function riskStyle(level?: string): RiskStyle {
  return styles[riskTone(level)];
}

export function riskDisplayLabel(level?: string): string {
  if (!level) return 'Unknown';
  return level.charAt(0).toUpperCase() + level.slice(1).toLowerCase();
}
