interface GaugeProps {
  /** 0 to 1 */
  value: number;
  size?: number;
  strokeWidth?: number;
  trackColor?: string;
  valueColor?: string;
  label?: string;
  sublabel?: string;
}

/**
 * Radial dial in the spirit of a plant control-room gauge.
 * Sweeps 270 degrees (like a physical pressure/temperature gauge) rather than
 * a full circle, so it reads as instrumentation rather than a generic donut chart.
 */
export function Gauge({
  value,
  size = 128,
  strokeWidth = 10,
  trackColor = '#e9e6de',
  valueColor = '#bd7a35',
  label,
  sublabel,
}: GaugeProps) {
  const clamped = Math.max(0, Math.min(1, value));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const sweep = 0.75; // fraction of circle used by the gauge (270deg)
  const arcLength = circumference * sweep;
  const rotation = 135; // start angle so the gap sits at the bottom

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-0">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={trackColor}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(${rotation} ${size / 2} ${size / 2})`}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={valueColor}
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength * clamped} ${circumference}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(${rotation} ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dasharray 600ms cubic-bezier(0.22, 1, 0.36, 1)' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center px-2 text-center">
        {label && <span className="font-display text-xl font-semibold text-ink-800 leading-none">{label}</span>}
        {sublabel && <span className="mt-1 text-[10px] font-medium uppercase tracking-wide text-ink-500">{sublabel}</span>}
      </div>
    </div>
  );
}
