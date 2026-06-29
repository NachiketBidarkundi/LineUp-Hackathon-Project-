import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Filter, ChevronUp, ChevronDown, Search as SearchIcon } from "lucide-react";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";

const POSITIONS = ["ALL", "C", "1B", "2B", "3B", "SS", "OF"];
const REGIONS = ["ALL", "TX", "CA", "FL", "GA", "NC", "OH", "TN", "LA", "VA"];
const BATS = ["ALL", "L", "R", "S"];

export default function SearchPage() {
  const nav = useNavigate();
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    position: "ALL", region: "ALL", bats: "ALL", min_ops: "", min_exit_velo: "",
  });
  const [sortBy, setSortBy] = useState("fit_score");
  const [search, setSearch] = useState("");

  const fetchPlayers = async () => {
    setLoading(true);
    const params = { sort_by: sortBy };
    if (filters.position !== "ALL") params.position = filters.position;
    if (filters.region !== "ALL") params.region = filters.region;
    if (filters.bats !== "ALL") params.bats = filters.bats;
    if (filters.min_ops) params.min_ops = parseFloat(filters.min_ops);
    if (filters.min_exit_velo) params.min_exit_velo = parseFloat(filters.min_exit_velo);
    const data = await api.listPlayers(params);
    setPlayers(data.players);
    setLoading(false);
  };

  useEffect(() => { fetchPlayers(); /* eslint-disable-next-line */ }, [filters, sortBy]);

  const filtered = useMemo(() => {
    if (!search) return players;
    const s = search.toLowerCase();
    return players.filter((p) => p.name.toLowerCase().includes(s) || p.school.toLowerCase().includes(s));
  }, [players, search]);

  return (
    <div>
      <div className="flex items-end justify-between mb-6 flex-wrap gap-4">
        <div>
          <div className="overline text-white/40">Database</div>
          <h1 className="font-display text-5xl font-black uppercase tracking-tighter mt-1">Recruit Search</h1>
          <p className="text-white/50 text-sm mt-2">{filtered.length} of {players.length} college players · ranked by {sortBy.replace("stats.", "")}</p>
        </div>
        <div className="relative w-full sm:w-80">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or school…"
            className="pl-9 bg-[#121212] border-white/10 text-white placeholder:text-white/30 focus-visible:ring-[#007AFF]"
            data-testid="recruit-search-input"
          />
        </div>
      </div>

      {/* Filters bar */}
      <div className="surface p-4 mb-6 flex flex-wrap gap-3 items-center">
        <Filter className="w-4 h-4 text-white/40" />
        <FilterSelect label="POS" value={filters.position} options={POSITIONS} onChange={(v) => setFilters({ ...filters, position: v })} testId="filter-position" />
        <FilterSelect label="REGION" value={filters.region} options={REGIONS} onChange={(v) => setFilters({ ...filters, region: v })} testId="filter-region" />
        <FilterSelect label="BATS" value={filters.bats} options={BATS} onChange={(v) => setFilters({ ...filters, bats: v })} testId="filter-bats" />
        <FilterNum label="MIN OPS" value={filters.min_ops} step="0.01" onChange={(v) => setFilters({ ...filters, min_ops: v })} testId="filter-min-ops" />
        <FilterNum label="MIN MAX EV" value={filters.min_exit_velo} step="0.5" onChange={(v) => setFilters({ ...filters, min_exit_velo: v })} testId="filter-min-exit-velo" />
        <button
          onClick={() => setFilters({ position: "ALL", region: "ALL", bats: "ALL", min_ops: "", min_exit_velo: "" })}
          className="ml-auto text-xs text-white/40 hover:text-white"
          data-testid="filter-reset"
        >
          RESET
        </button>
      </div>

      {/* Table */}
      <div className="surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-white/5 border-b border-white/10">
              <tr className="text-[10px] uppercase tracking-[0.2em] text-white/50">
                <Th onClick={() => setSortBy("name")} active={sortBy === "name"}>Player</Th>
                <Th>Pos</Th>
                <Th>School</Th>
                <Th onClick={() => setSortBy("stats.avg")} active={sortBy === "stats.avg"} right>AVG</Th>
                <Th onClick={() => setSortBy("stats.ops")} active={sortBy === "stats.ops"} right>OPS</Th>
                <Th onClick={() => setSortBy("stats.exit_velo_max")} active={sortBy === "stats.exit_velo_max"} right>MAX EV</Th>
                <Th right>BAT SPD</Th>
                <Th onClick={() => setSortBy("biomech_score")} active={sortBy === "biomech_score"} right>BIOMECH</Th>
                <Th onClick={() => setSortBy("fit_score")} active={sortBy === "fit_score"} right>FIT</Th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={9} className="text-center py-12 text-white/40">Loading…</td></tr>
              )}
              {!loading && filtered.length === 0 && (
                <tr><td colSpan={9} className="text-center py-12 text-white/40">No recruits match these filters.</td></tr>
              )}
              {filtered.map((p, i) => (
                <tr
                  key={p.player_id}
                  data-testid={`row-${p.player_id}`}
                  onClick={() => nav(`/player/${p.player_id}`)}
                  className="border-b border-white/5 hover:bg-white/[0.04] cursor-pointer transition-colors fade-up"
                  style={{ animationDelay: `${i * 20}ms` }}
                >
                  <td className="px-4 py-3">
                    <div className="font-semibold">{p.name}</div>
                    <div className="text-[10px] text-white/40 uppercase tracking-widest">{p.bats}/{p.throws} · Age {p.age}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="pill bg-white/5 text-white border border-white/10">{p.position}</span>
                  </td>
                  <td className="px-4 py-3 text-white/60 text-xs">{p.school}</td>
                  <td className="px-4 py-3 tabular text-right">{p.stats.avg.toFixed(3)}</td>
                  <td className="px-4 py-3 tabular text-right">{p.stats.ops.toFixed(3)}</td>
                  <td className="px-4 py-3 tabular text-right">{p.stats.exit_velo_max.toFixed(1)}</td>
                  <td className="px-4 py-3 tabular text-right text-white/70">{p.stats.bat_speed.toFixed(1)}</td>
                  <td className="px-4 py-3 tabular text-right">
                    <BiomechBadge score={p.biomech_score} />
                  </td>
                  <td className="px-4 py-3 tabular text-right">
                    <span className="font-display text-lg font-black text-[#007AFF]">{p.fit_score}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Th({ children, onClick, active, right }) {
  return (
    <th
      onClick={onClick}
      className={`px-4 py-3 font-semibold ${right ? "text-right" : "text-left"} ${onClick ? "cursor-pointer hover:text-white" : ""} ${active ? "text-[#007AFF]" : ""}`}
    >
      <span className="inline-flex items-center gap-1">
        {children}
        {active && <ChevronDown className="w-3 h-3" />}
      </span>
    </th>
  );
}

function FilterSelect({ label, value, options, onChange, testId }) {
  return (
    <div className="flex items-center gap-2">
      <span className="overline text-[10px]">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        data-testid={testId}
        className="bg-[#0A0A0A] border border-white/10 text-white text-xs px-2 py-1.5 focus:outline-none focus:border-[#007AFF]"
      >
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function FilterNum({ label, value, onChange, testId, step }) {
  return (
    <div className="flex items-center gap-2">
      <span className="overline text-[10px]">{label}</span>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        data-testid={testId}
        placeholder="—"
        className="bg-[#0A0A0A] border border-white/10 text-white text-xs px-2 py-1.5 w-20 focus:outline-none focus:border-[#007AFF] tabular"
      />
    </div>
  );
}

function BiomechBadge({ score }) {
  const color = score >= 85 ? "#32D74B" : score >= 75 ? "#007AFF" : score >= 65 ? "#D4A437" : "#FF453A";
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
      <span className="font-semibold" style={{ color }}>{score}</span>
    </span>
  );
}
