export default function PercentileBar({ label, value, unit = "" }) {
  const color = value >= 80 ? "#32D74B" : value >= 60 ? "#007AFF" : value >= 40 ? "#D4A437" : "#FF453A";
  return (
    <div className="flex items-center gap-3 py-1.5">
      <div className="w-28 text-[11px] uppercase tracking-widest text-white/50 font-medium">{label}</div>
      <div className="flex-1 h-1.5 bg-white/5 relative overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 transition-all duration-500"
          style={{ width: `${Math.min(100, value)}%`, backgroundColor: color }}
        />
        <div className="absolute inset-y-0 left-1/2 w-px bg-white/15" />
      </div>
      <div className="w-12 text-right tabular text-sm font-semibold text-white">
        {value}
        <span className="text-[9px] text-white/40 ml-0.5">{unit || "pct"}</span>
      </div>
    </div>
  );
}
