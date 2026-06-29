import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Download, X, ExternalLink, Bookmark } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function Shortlist() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const data = await api.getShortlist();
    setPlayers(data.players);
    setLoading(false);
  };
  useEffect(() => { load(); }, []);

  const remove = async (id, name) => {
    await api.removeShortlist(id);
    setPlayers((prev) => prev.filter((p) => p.player_id !== id));
    toast.success(`${name} removed from Scouting Board`);
  };

  return (
    <div>
      <div className="flex items-end justify-between mb-8 flex-wrap gap-4">
        <div>
          <div className="overline text-white/40">Your Pipeline</div>
          <h1 className="font-display text-5xl font-black uppercase tracking-tighter mt-1">Scouting Board</h1>
          <p className="text-white/50 text-sm mt-2">
            {players.length} {players.length === 1 ? "recruit" : "recruits"} shortlisted
          </p>
        </div>
        {players.length > 0 && (
          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => players.forEach((p) => window.open(api.reportUrl(p.player_id), "_blank"))}
              data-testid="export-all-pdf-btn"
              className="inline-flex items-center gap-2 bg-[#007AFF] hover:bg-[#005bb5] text-white px-4 py-2.5 text-sm font-semibold transition-colors"
            >
              <Download className="w-4 h-4" /> Export All as PDF
            </button>
          </div>
        )}
      </div>

      {loading && <div className="text-white/40 text-center py-20">Loading…</div>}

      {!loading && players.length === 0 && (
        <div className="surface p-16 text-center">
          <Bookmark className="w-10 h-10 text-white/30 mx-auto mb-4" />
          <div className="font-display text-2xl font-bold uppercase tracking-tight mb-2">Your scouting board is empty</div>
          <p className="text-white/50 text-sm mb-6">Add recruits from the search page or any player profile.</p>
          <Link to="/search" className="inline-flex items-center gap-2 bg-[#007AFF] hover:bg-[#005bb5] text-white px-5 py-2.5 text-sm font-semibold" data-testid="shortlist-go-search">
            Browse Recruits
          </Link>
        </div>
      )}

      {!loading && players.length > 0 && (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {players.map((p, i) => (
            <div key={p.player_id} className="surface p-5 fade-up surface-hover" style={{ animationDelay: `${i * 30}ms` }} data-testid={`shortlist-card-${p.player_id}`}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="overline text-[10px] text-white/40">{p.player_id}</div>
                  <Link to={`/player/${p.player_id}`} className="font-display text-2xl font-black uppercase tracking-tight hover:text-[#007AFF]">
                    {p.name}
                  </Link>
                  <div className="text-xs text-white/50 mt-1">{p.position} · {p.school}</div>
                </div>
                <button onClick={() => remove(p.player_id, p.name)} data-testid={`remove-${p.player_id}`} className="text-white/40 hover:text-[#FF453A] p-1">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2">
                <Mini label="OPS" value={p.stats.ops.toFixed(3)} />
                <Mini label="Max EV" value={p.stats.exit_velo_max.toFixed(1)} accent />
                <Mini label="Fit" value={p.fit_score} highlight />
              </div>

              <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-widest text-white/40">MLB Comp</div>
                  <div className="text-sm font-semibold text-[#D4A437]">{p.mlb_comp}</div>
                </div>
                <a
                  href={api.reportUrl(p.player_id)}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs border border-white/20 hover:border-white/50 px-3 py-1.5"
                  data-testid={`export-${p.player_id}`}
                >
                  <Download className="w-3 h-3" /> PDF
                </a>
              </div>

              <Link to={`/player/${p.player_id}`} className="mt-3 flex items-center justify-center gap-1.5 text-[11px] text-white/40 hover:text-white">
                Open profile <ExternalLink className="w-3 h-3" />
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Mini({ label, value, accent, highlight }) {
  return (
    <div>
      <div className="overline text-[9px] text-white/40">{label}</div>
      <div className={`font-display text-xl font-bold tabular ${highlight ? "text-[#007AFF]" : accent ? "text-[#32D74B]" : "text-white"}`}>{value}</div>
    </div>
  );
}
