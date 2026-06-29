import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Activity, Zap, Target, Brain } from "lucide-react";
import { api } from "@/lib/api";

export default function Landing() {
  const [stats, setStats] = useState({ total_players: 20, max_exit_velo: 106.8, avg_biomech: 78.0 });
  useEffect(() => { api.statsSummary().then(setStats).catch(() => {}); }, []);

  return (
    <div className="bg-[#0A0A0A] text-white">
      {/* HERO */}
      <section className="relative grain overflow-hidden">
        <div
          className="absolute inset-0 opacity-25"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1660892425121-e7461fc9991c?crop=entropy&cs=srgb&fm=jpg&q=85')",
            backgroundSize: "cover", backgroundPosition: "center",
            maskImage: "linear-gradient(to bottom, black 30%, transparent 100%)",
            WebkitMaskImage: "linear-gradient(to bottom, black 30%, transparent 100%)",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0A0A]/70 to-[#0A0A0A]" />

        <div className="relative max-w-[1440px] mx-auto px-6 pt-24 pb-32">
          <div className="flex items-center gap-2 mb-6">
            <div className="h-px w-12 bg-[#007AFF]" />
            <span className="overline text-[#007AFF]">MLB-Grade Scouting · Built for Everyone</span>
          </div>

          <h1 className="font-display text-6xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-[0.85] max-w-5xl">
            See the swing<br />
            <span className="text-white/40">before the</span><br />
            scoreboard does.
          </h1>

          <p className="mt-8 max-w-2xl text-lg text-white/70 leading-relaxed">
            D1 programs spend <span className="text-white font-semibold">$200K/year</span> on scouting tech. Everyone else flies blind.
            Lineup gives <span className="text-[#007AFF] font-semibold">any coach</span> Statcast-grade metrics on <span className="text-white font-semibold">college recruits</span>, biomech swing analysis,
            and ranked transfer-portal boards &mdash; for the price of an iPhone.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              to="/search"
              data-testid="cta-explore-recruits"
              className="group inline-flex items-center gap-2 bg-[#007AFF] hover:bg-[#005bb5] text-white px-6 py-3 font-semibold transition-all duration-150"
            >
              Explore Recruits
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/upload"
              data-testid="cta-biomech-lab"
              className="inline-flex items-center gap-2 border border-white/20 hover:border-white/50 px-6 py-3 font-semibold transition-all duration-150"
            >
              Try the Biomech Lab
            </Link>
          </div>

          {/* Live stat strip */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5 border border-white/10 max-w-4xl">
            {[
              { label: "Recruits Indexed", value: stats.total_players, icon: Target },
              { label: "Max Exit Velo (mph)", value: stats.max_exit_velo, icon: Zap },
              { label: "Avg Biomech Score", value: stats.avg_biomech, icon: Brain },
              { label: "Live MLB Feed", value: "ON", icon: Activity, accent: true },
            ].map((s, i) => (
              <div key={i} className="bg-[#0A0A0A] p-5">
                <s.icon className={`w-4 h-4 mb-3 ${s.accent ? "text-[#32D74B]" : "text-white/40"}`} />
                <div className="font-display text-3xl font-black tabular">{s.value}</div>
                <div className="overline mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES STRIP */}
      <section className="max-w-[1440px] mx-auto px-6 py-24">
        <div className="overline mb-3 text-white/40">What&apos;s inside</div>
        <h2 className="font-display text-5xl font-black uppercase tracking-tight mb-12">
          A scouting room <span className="text-white/40">in your pocket.</span>
        </h2>

        <div className="grid md:grid-cols-3 gap-px bg-white/5 border border-white/10">
          {[
            { title: "Statcast Percentiles", body: "Every amateur metric ranked against the MLB population. Exit velo, bat speed, sprint, contact, power, discipline.", num: "01" },
          { title: "Biomechanical Swing Lab", body: "Upload any swing clip. Get a score, MLB comp, and 2-3 prescriptive drills — derived from elite-swing kinematics.", num: "02" },
            { title: "PDF Scouting Packets", body: "Export polished one-page reports. Bring them to your AD, your booster club, your transfer portal calls.", num: "03" },
          ].map((f) => (
            <div key={f.num} className="bg-[#0A0A0A] p-8 surface-hover">
              <div className="font-mono text-xs text-[#007AFF] mb-4">{f.num}</div>
              <h3 className="font-display text-2xl font-bold uppercase tracking-tight mb-3">{f.title}</h3>
              <p className="text-white/60 text-sm leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA STRIP */}
      <section className="border-t border-white/10">
        <div className="max-w-[1440px] mx-auto px-6 py-16 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="overline text-[#007AFF]">For coaches who can&apos;t afford to fly blind</div>
            <div className="font-display text-4xl font-black uppercase tracking-tight mt-2">
              500K HS players. 800+ D2/D3/JUCO programs.
            </div>
          </div>
          <Link
            to="/search"
            data-testid="cta-secondary-explore"
            className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 font-semibold hover:bg-white/90 transition-colors"
          >
            Start scouting
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
