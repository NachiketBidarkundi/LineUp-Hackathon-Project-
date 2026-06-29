import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";
import StatRadar from "@/components/StatRadar";

function percentilesFromMlb(mlb) {
  // Synthesize percentile-like values for MLB ref so they overlay on the same radar (1-100 scale)
  // Anchored to top of distribution.
  const s = mlb.stats || {};
  return {
    power:          Math.min(100, Math.round(((s.slg ?? 0.5) - 0.38) / (0.7 - 0.38) * 100)),
    contact_pct:    Math.min(100, Math.round(((s.avg ?? 0.27) - 0.22) / (0.42 - 0.22) * 100)),
    sprint_speed:   Math.min(100, Math.round(((s.sprint_speed ?? 27) - 25) / (30 - 25) * 100)),
    exit_velo_max:  Math.min(100, Math.round(((s.exit_velo_max ?? 110) - 100) / 22 * 100)),
    bat_speed:      Math.min(100, Math.round(((s.bat_speed ?? 73) - 64) / 16 * 100)),
    discipline:     Math.min(100, Math.round(((s.obp ?? 0.35) - (s.avg ?? 0.27) - 0.04) / 0.09 * 100)),
  };
}

export default function ComparePage() {
  const [params] = useSearchParams();
  const [allPlayers, setAllPlayers] = useState([]);
  const [mlb, setMlb] = useState([]);
  const [aId, setAId] = useState(params.get("a") || "");
  const [bId, setBId] = useState(params.get("b") || "");

  useEffect(() => {
    api.listPlayers().then((d) => {
      setAllPlayers(d.players);
      if (!params.get("a") && d.players[0]) setAId(d.players[0].player_id);
    });
    api.mlbReference().then((d) => {
      setMlb(d.mlb_reference);
      if (!params.get("b") && d.mlb_reference[0]) setBId(d.mlb_reference[0].player_id);
    });
    /* eslint-disable-next-line */
  }, []);

  const combined = useMemo(() => {
    return [
      ...allPlayers.map((p) => ({ id: p.player_id, label: `🎓 ${p.name} (${p.position})`, type: "college", raw: p })),
      ...mlb.map((p) => ({ id: p.player_id, label: `⚾ ${p.name} · MLB`, type: "mlb", raw: p })),
    ];
  }, [allPlayers, mlb]);

  const a = combined.find((x) => x.id === aId)?.raw;
  const b = combined.find((x) => x.id === bId)?.raw;

  const pctA = a?.percentiles_vs_mlb || (a ? percentilesFromMlb(a) : null);
  const pctB = b?.percentiles_vs_mlb || (b ? percentilesFromMlb(b) : null);

  return (
    <div>
      <div className="overline text-white/40">Side-by-Side</div>
      <h1 className="font-display text-5xl font-black uppercase tracking-tighter mt-1 mb-8">Compare</h1>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <PlayerPicker label="Player A" value={aId} onChange={setAId} options={combined} color="#007AFF" testId="picker-a" />
        <PlayerPicker label="Player B" value={bId} onChange={setBId} options={combined} color="#32D74B" testId="picker-b" />
      </div>

      {a && b && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="surface p-6 lg:col-span-2">
            <div className="overline text-white/40 mb-2">Overlay Radar</div>
            <StatRadar percentiles={pctA} comparePercentiles={pctB} name={a.name} compareName={b.name} />
          </div>

          <div className="surface p-6">
            <div className="overline text-white/40 mb-4">Head-to-Head</div>
            <StatRow label="AVG"        a={a.stats?.avg?.toFixed(3)}        b={b.stats?.avg?.toFixed(3)}        higher="a" cmpA={a.stats?.avg} cmpB={b.stats?.avg} />
            <StatRow label="OPS"        a={a.stats?.ops?.toFixed(3)}        b={b.stats?.ops?.toFixed(3)}        cmpA={a.stats?.ops} cmpB={b.stats?.ops} />
            <StatRow label="Max EV"     a={a.stats?.exit_velo_max?.toFixed(1)} b={b.stats?.exit_velo_max?.toFixed(1)} cmpA={a.stats?.exit_velo_max} cmpB={b.stats?.exit_velo_max} unit="mph" />
            <StatRow label="Bat Speed"  a={a.stats?.bat_speed?.toFixed(1)}  b={b.stats?.bat_speed?.toFixed(1)}  cmpA={a.stats?.bat_speed} cmpB={b.stats?.bat_speed} unit="mph" />
            <StatRow label="Sprint"     a={a.stats?.sprint_speed?.toFixed(1)} b={b.stats?.sprint_speed?.toFixed(1)} cmpA={a.stats?.sprint_speed} cmpB={b.stats?.sprint_speed} unit="ft/s" />
            {a.biomech_score && b.biomech_score && (
              <StatRow label="Biomech"  a={a.biomech_score} b={b.biomech_score} cmpA={a.biomech_score} cmpB={b.biomech_score} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function PlayerPicker({ label, value, onChange, options, color, testId }) {
  return (
    <div className="surface p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
        <span className="overline">{label}</span>
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        data-testid={testId}
        className="w-full bg-[#0A0A0A] border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-[#007AFF]"
      >
        <option value="">— Select —</option>
        <optgroup label="College">
          {options.filter((o) => o.type === "college").map((o) => (<option key={o.id} value={o.id}>{o.label}</option>))}
        </optgroup>
        <optgroup label="MLB Reference">
          {options.filter((o) => o.type === "mlb").map((o) => (<option key={o.id} value={o.id}>{o.label}</option>))}
        </optgroup>
      </select>
    </div>
  );
}

function StatRow({ label, a, b, cmpA, cmpB, unit }) {
  const aWins = cmpA != null && cmpB != null && cmpA > cmpB;
  const bWins = cmpA != null && cmpB != null && cmpB > cmpA;
  return (
    <div className="grid grid-cols-3 items-center py-2 border-b border-white/5 last:border-0">
      <div className={`tabular text-lg font-semibold ${aWins ? "text-[#007AFF]" : "text-white/70"}`}>
        {a ?? "—"} {unit && a && <span className="text-[10px] text-white/40 ml-1">{unit}</span>}
      </div>
      <div className="text-center overline">{label}</div>
      <div className={`tabular text-lg font-semibold text-right ${bWins ? "text-[#32D74B]" : "text-white/70"}`}>
        {b ?? "—"} {unit && b && <span className="text-[10px] text-white/40 ml-1">{unit}</span>}
      </div>
    </div>
  );
}
