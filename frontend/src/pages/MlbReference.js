import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function MlbReference() {
  const [refs, setRefs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.mlbReference().then((d) => { setRefs(d.mlb_reference); setLoading(false); });
  }, []);

  return (
    <div>
      <div className="overline text-white/40">Benchmarks</div>
      <h1 className="font-display text-5xl font-black uppercase tracking-tighter mt-1 mb-2">MLB Reference</h1>
      <p className="text-white/50 text-sm mb-8 max-w-2xl">
        Live career batting from the MLB Stats API where available. Statcast-grade velocity/bat-speed values overlaid from public sources.
      </p>

      {loading && <div className="text-white/40 py-20 text-center">Loading MLB feed…</div>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {refs.map((p, i) => (
          <div key={p.player_id} className="surface p-5 fade-up" style={{ animationDelay: `${i * 40}ms` }} data-testid={`mlb-card-${p.player_id}`}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="overline text-[10px] text-white/40">{p.team} · {p.position}</div>
                <div className="font-display text-2xl font-black uppercase tracking-tight">{p.name}</div>
              </div>
              <span className={`pill ${p.live_stats_loaded ? "bg-[#32D74B]/15 text-[#32D74B] border border-[#32D74B]/30" : "bg-white/5 text-white/50 border border-white/10"}`}>
                {p.live_stats_loaded ? "LIVE" : "CACHED"}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 pb-3 border-b border-white/5">
              <Mini label="AVG" value={p.stats.avg.toFixed(3)} />
              <Mini label="OPS" value={p.stats.ops.toFixed(3)} />
              <Mini label="OBP" value={p.stats.obp.toFixed(3)} />
              <Mini label="SLG" value={p.stats.slg.toFixed(3)} />
            </div>
            <div className="grid grid-cols-3 gap-3 mt-3">
              <Mini label="Max EV" value={`${p.stats.exit_velo_max.toFixed(1)}`} unit="mph" color="#32D74B" />
              <Mini label="Bat Speed" value={`${p.stats.bat_speed.toFixed(1)}`} unit="mph" color="#007AFF" />
              <Mini label="Sprint" value={`${p.stats.sprint_speed.toFixed(1)}`} unit="ft/s" color="#D4A437" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Mini({ label, value, unit, color }) {
  return (
    <div>
      <div className="overline text-[9px] text-white/40">{label}</div>
      <div className="font-display text-xl font-bold tabular" style={{ color: color || "#FFFFFF" }}>
        {value}
        {unit && <span className="text-[9px] text-white/40 ml-1">{unit}</span>}
      </div>
    </div>
  );
}
