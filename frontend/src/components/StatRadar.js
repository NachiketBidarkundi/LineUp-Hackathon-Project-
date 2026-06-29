import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from "recharts";

export default function StatRadar({ percentiles, comparePercentiles = null, name = "Recruit", compareName = "MLB Comp" }) {
  const data = [
    { metric: "Power",       a: percentiles?.power ?? 0,         b: comparePercentiles?.power },
    { metric: "Contact",     a: percentiles?.contact_pct ?? 0,   b: comparePercentiles?.contact_pct },
    { metric: "Speed",       a: percentiles?.sprint_speed ?? 0,  b: comparePercentiles?.sprint_speed },
    { metric: "Exit Velo",   a: percentiles?.exit_velo_max ?? 0, b: comparePercentiles?.exit_velo_max },
    { metric: "Bat Speed",   a: percentiles?.bat_speed ?? 0,     b: comparePercentiles?.bat_speed },
    { metric: "Discipline",  a: percentiles?.discipline ?? 0,    b: comparePercentiles?.discipline },
  ];

  return (
    <ResponsiveContainer width="100%" height={340}>
      <RadarChart data={data} outerRadius="78%">
        <PolarGrid stroke="rgba(255,255,255,0.12)" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: "#A0A0A0", fontSize: 11, fontWeight: 600, letterSpacing: 1 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#555", fontSize: 9 }} stroke="rgba(255,255,255,0.05)" />
        <Tooltip
          contentStyle={{ backgroundColor: "#121212", border: "1px solid rgba(255,255,255,0.15)", fontSize: 12 }}
          labelStyle={{ color: "#fff", fontWeight: 700, textTransform: "uppercase", letterSpacing: 1 }}
          formatter={(v) => `${v}th pct`}
        />
        <Radar name={name} dataKey="a" stroke="#007AFF" fill="#007AFF" fillOpacity={0.35} strokeWidth={2} />
        {comparePercentiles && (
          <Radar name={compareName} dataKey="b" stroke="#32D74B" fill="#32D74B" fillOpacity={0.18} strokeWidth={2} strokeDasharray="4 3" />
        )}
        {comparePercentiles && <Legend wrapperStyle={{ fontSize: 11, color: "#A0A0A0" }} />}
      </RadarChart>
    </ResponsiveContainer>
  );
}
