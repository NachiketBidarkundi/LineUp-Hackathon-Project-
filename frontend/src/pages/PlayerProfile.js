import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Bookmark, BookmarkCheck, Download, Activity, Award, MapPin } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import StatRadar from "@/components/StatRadar";
import PercentileBar from "@/components/PercentileBar";

export default function PlayerProfile() {
  const { id } = useParams();
  const nav = useNavigate();
  const [p, setP] = useState(null);
  const [shortlist, setShortlist] = useState([]);
  const [running, setRunning] = useState(false);

  const load = async () => {
    const [pl, sl] = await Promise.all([api.getPlayer(id), api.getShortlist()]);
    setP(pl);
    setShortlist(sl.shortlist);
  };
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [id]);

  if (!p) return <div className="text-white/50 py-20 text-center">Loading recruit…</div>;

  const inList = shortlist.includes(p.player_id);

  const toggleShortlist = async () => {
    if (inList) {
      const r = await api.removeShortlist(p.player_id);
      setShortlist(r.shortlist);
      toast.success(`${p.name} removed from Scouting Board`);
    } else {
      const r = await api.addShortlist(p.player_id);
      setShortlist(r.shortlist);
      toast.success(`${p.name} added to Scouting Board`);
    }
  };

  const runBiomech = async () => {
    setRunning(true);
    try {
      await api.analyzeBiomech(p.player_id, null);
      await load();
      toast.success("Biomech analysis complete");
    } catch (e) {
      toast.error("Analysis failed");
    } finally { setRunning(false); }
  };

  const scoreColor = p.biomech_score >= 85 ? "#32D74B" : p.biomech_score >= 75 ? "#007AFF" : p.biomech_score >= 65 ? "#D4A437" : "#FF453A";

  return (
    <div className="space-y-6">
      <button onClick={() => nav(-1)} className="flex items-center gap-2 text-sm text-white/50 hover:text-white" data-testid="back-button">
        <ArrowLeft className="w-4 h-4" /> Back to search
      </button>

      {/* Header */}
      <div className="surface p-6 flex flex-col lg:flex-row gap-6 items-start">
        <div className="flex-shrink-0 w-28 h-28 bg-gradient-to-br from-[#007AFF]/30 to-[#007AFF]/0 border border-white/10 flex items-center justify-center">
          <span className="font-display text-5xl font-black text-white/90">
            {p.name.split(" ").map((n) => n[0]).slice(0, 2).join("")}
          </span>
        </div>
        <div className="flex-1">
          <div className="overline text-white/40">Recruit · {p.player_id}</div>
          <h1 className="font-display text-6xl font-black uppercase tracking-tighter leading-none mt-1">{p.name}</h1>
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-white/60">
            <span className="pill bg-[#007AFF]/15 text-[#007AFF] border border-[#007AFF]/30">{p.position}</span>
            <span>Age {p.age}</span>
            <span>{Math.floor(p.height_in / 12)}&apos;{p.height_in % 12}&quot; · {p.weight_lb} lb</span>
            <span>B/T: {p.bats}/{p.throws}</span>
            <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {p.school}</span>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          <button
            data-testid="add-to-shortlist-btn"
            onClick={toggleShortlist}
            className={`inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold transition-all duration-150 ${
              inList ? "bg-[#32D74B] text-black hover:bg-[#28b842]" : "bg-[#007AFF] text-white hover:bg-[#005bb5]"
            }`}
          >
            {inList ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
            {inList ? "On Board" : "Add to Board"}
          </button>
          <a
            href={api.reportUrl(p.player_id)}
            target="_blank"
            rel="noreferrer"
            data-testid="export-pdf-btn"
            className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border border-white/20 hover:border-white/50 transition-colors"
          >
            <Download className="w-4 h-4" /> Export PDF
          </a>
        </div>
      </div>

      {/* Bento grid: top row */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Biomech & MLB Comp card */}
        <div className="surface p-6 lg:row-span-2">
          <div className="overline text-white/40 mb-4">North Star</div>

          <div className="mb-8">
            <div className="overline text-[10px] text-white/40 mb-2">Biomech Score</div>
            <div className="flex items-baseline gap-2">
              <span className="font-display text-8xl font-black tabular" style={{ color: scoreColor }}>{p.biomech_score}</span>
              <span className="text-white/30 text-2xl">/100</span>
            </div>
            <div className="h-1 mt-3 bg-white/5 relative">
              <div className="absolute inset-y-0 left-0" style={{ width: `${p.biomech_score}%`, backgroundColor: scoreColor }} />
            </div>
          </div>

          <div className="mb-8 pb-6 border-b border-white/10">
            <div className="overline text-[10px] text-white/40 mb-2 flex items-center gap-1.5"><Award className="w-3 h-3" /> MLB Comp</div>
            <div className="font-display text-3xl font-black uppercase tracking-tight text-[#D4A437]">{p.mlb_comp}</div>
            <div className="text-xs text-white/50 mt-1">
              <span className="tabular text-white font-semibold">{Math.round(p.mlb_comp_similarity * 100)}%</span> swing similarity
            </div>
          </div>

          <div className="mb-6">
            <div className="overline text-[10px] text-white/40 mb-2">Fit Score</div>
            <div className="flex items-baseline gap-2">
              <span className="font-display text-5xl font-black text-[#007AFF] tabular">{p.fit_score}</span>
              <span className="text-white/30">/100</span>
            </div>
            <div className="text-[10px] text-white/40 mt-1 uppercase tracking-widest">Weighted: power 40% · contact 30% · speed 20% · biomech 10%</div>
          </div>

          <button
            data-testid="run-biomech-btn"
            onClick={runBiomech}
            disabled={running}
            className="w-full inline-flex items-center justify-center gap-2 border border-white/20 hover:border-[#007AFF] text-sm py-2.5 transition-colors disabled:opacity-50"
          >
            <Activity className="w-4 h-4" />
            {running ? "Analyzing swing…" : "Re-run Biomech Analysis"}
          </button>
        </div>

        {/* Video clip placeholder */}
        <div className="surface lg:col-span-2 p-6">
          <div className="overline text-white/40 mb-4">Swing Clip</div>
          <div
            className="aspect-video bg-[#0A0A0A] border border-white/10 grain overflow-hidden relative flex items-center justify-center"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1633809786904-90d4c03ca502?crop=entropy&cs=srgb&fm=jpg&q=85')",
              backgroundSize: "cover", backgroundPosition: "center",
            }}
          >
            <div className="absolute inset-0 bg-black/50" />
            <div className="relative text-center">
              <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md border border-white/30 mx-auto flex items-center justify-center mb-3">
                <div className="w-0 h-0 border-y-[10px] border-y-transparent border-l-[16px] border-l-white ml-1" />
              </div>
              <div className="text-xs uppercase tracking-widest text-white/70">Slow-motion swing · 240fps</div>
              <div className="text-[10px] text-white/40 mt-1 font-mono">{p.video_url}</div>
            </div>
          </div>
        </div>

        {/* Radar */}
        <div className="surface lg:col-span-2 p-6">
          <div className="flex justify-between items-center mb-2">
            <div>
              <div className="overline text-white/40">vs MLB Population</div>
              <div className="font-display text-2xl font-bold uppercase tracking-tight">Percentile Radar</div>
            </div>
          </div>
          <StatRadar percentiles={p.percentiles_vs_mlb} name={p.name} />
        </div>
      </div>

      {/* Granular stats + biomech detail */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="surface p-6">
          <div className="overline text-white/40 mb-4">Statcast Card</div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-1">
            <PercentileBar label="Power" value={p.percentiles_vs_mlb.power} />
            <PercentileBar label="Contact" value={p.percentiles_vs_mlb.contact_pct} />
            <PercentileBar label="Exit Velo Max" value={p.percentiles_vs_mlb.exit_velo_max} />
            <PercentileBar label="Bat Speed" value={p.percentiles_vs_mlb.bat_speed} />
            <PercentileBar label="Sprint Speed" value={p.percentiles_vs_mlb.sprint_speed} />
            <PercentileBar label="Discipline" value={p.percentiles_vs_mlb.discipline} />
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 grid grid-cols-4 gap-4">
            <RawStat label="AVG" value={p.stats.avg.toFixed(3)} />
            <RawStat label="OBP" value={p.stats.obp.toFixed(3)} />
            <RawStat label="SLG" value={p.stats.slg.toFixed(3)} />
            <RawStat label="OPS" value={p.stats.ops.toFixed(3)} />
            <RawStat label="EV Avg" value={`${p.stats.exit_velo_avg.toFixed(1)}`} unit="mph" />
            <RawStat label="EV Max" value={`${p.stats.exit_velo_max.toFixed(1)}`} unit="mph" />
            <RawStat label="Bat Speed" value={`${p.stats.bat_speed.toFixed(1)}`} unit="mph" />
            <RawStat label="Sprint" value={`${p.stats.sprint_speed.toFixed(1)}`} unit="ft/s" />
          </div>
        </div>

        {/* Biomech diagnostics */}
        <div className="surface p-6">
          <div className="overline text-white/40 mb-4">Biomech Diagnostics</div>
          {!p.biomech_result && (
            <div className="text-sm text-white/50 py-8 text-center">
              No detailed biomech run yet. Click &quot;Re-run Biomech Analysis&quot; to generate diagnostics.
            </div>
          )}
          {p.biomech_result && (
            <div className="space-y-4">
              {p.biomech_result.diagnoses?.map((d, i) => (
                <div key={i} className="border border-white/10 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="pill"
                      style={{
                        backgroundColor: d.severity === "critical" ? "rgba(255,69,58,0.15)" : "rgba(212,164,55,0.15)",
                        color: d.severity === "critical" ? "#FF453A" : "#D4A437",
                        border: `1px solid ${d.severity === "critical" ? "rgba(255,69,58,0.4)" : "rgba(212,164,55,0.4)"}`,
                      }}
                    >
                      {d.severity}
                    </span>
                    <span className="text-[10px] text-white/40 uppercase tracking-widest">{d.feature.replace(/_/g, " ")}</span>
                  </div>
                  <p className="text-sm text-white/80">{d.message}</p>
                  <div className="mt-2 text-xs text-[#FF453A]">Cost: {d.estimated_cost}</div>
                  <div className="mt-1 text-xs text-[#32D74B]"><span className="font-bold">FIX:</span> {d.fix}</div>
                </div>
              ))}
              {p.biomech_result.strengths?.length > 0 && (
                <div className="border border-[#32D74B]/30 bg-[#32D74B]/5 p-4">
                  <div className="overline text-[#32D74B] mb-2">Strengths</div>
                  {p.biomech_result.strengths.map((s, i) => (
                    <div key={i} className="text-sm text-white/80 mb-1">• {s.message}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <Link
        to={`/compare?a=${p.player_id}`}
        className="block surface p-6 surface-hover text-center text-sm text-white/70 hover:text-white"
        data-testid="compare-link"
      >
        Compare {p.name} side-by-side with another recruit or MLB player →
      </Link>
    </div>
  );
}

function RawStat({ label, value, unit }) {
  return (
    <div>
      <div className="overline text-[9px] text-white/40">{label}</div>
      <div className="font-display text-xl font-bold tabular">
        {value}
        {unit && <span className="text-[10px] text-white/40 ml-1">{unit}</span>}
      </div>
    </div>
  );
}
