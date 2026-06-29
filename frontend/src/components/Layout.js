import { NavLink, Link, useLocation } from "react-router-dom";
import { Search, Users, GitCompareArrows, Bookmark, Upload, Activity } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";

const navItems = [
  { to: "/search", label: "Recruits", icon: Search, testId: "nav-search" },
  { to: "/mlb", label: "MLB Ref", icon: Users, testId: "nav-mlb" },
  { to: "/compare", label: "Compare", icon: GitCompareArrows, testId: "nav-compare" },
  { to: "/shortlist", label: "Scouting Board", icon: Bookmark, testId: "nav-shortlist" },
  { to: "/upload", label: "Biomech Lab", icon: Upload, testId: "nav-upload" },
];

export default function Layout({ children }) {
  const loc = useLocation();
  const isLanding = loc.pathname === "/";
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">
      <header className="sticky top-0 z-40 border-b border-white/10 bg-[#0A0A0A]/80 backdrop-blur-md">
        <div className="max-w-[1440px] mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2" data-testid="brand-link">
            <div className="w-8 h-8 bg-[#007AFF] flex items-center justify-center" style={{ clipPath: "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)" }}>
              <Activity className="w-4 h-4 text-white" />
            </div>
            <div>
              <div className="font-display text-2xl font-black tracking-tighter leading-none">LINEUP</div>
              <div className="text-[9px] uppercase tracking-[0.25em] text-white/40 leading-none mt-0.5">Scouting Intelligence</div>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon, testId }) => (
              <NavLink
                key={to}
                to={to}
                data-testid={testId}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 text-sm font-medium transition-all duration-150 border-b-2 ${
                    isActive
                      ? "text-white border-[#007AFF]"
                      : "text-white/60 border-transparent hover:text-white hover:border-white/20"
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span className="hidden lg:inline">{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10">
              <div className="w-1.5 h-1.5 bg-[#32D74B] rounded-full animate-pulse" />
              <span className="text-[10px] uppercase tracking-widest text-white/60">Live · MLB Stats API</span>
            </div>
          </div>
        </div>

        {/* Mobile nav */}
        <nav className="md:hidden flex items-center gap-1 px-4 pb-2 overflow-x-auto">
          {navItems.map(({ to, label, icon: Icon, testId }) => (
            <NavLink
              key={to}
              to={to}
              data-testid={`${testId}-mobile`}
              className={({ isActive }) =>
                `flex items-center gap-1 px-2 py-1 text-xs whitespace-nowrap ${
                  isActive ? "text-white border-b border-[#007AFF]" : "text-white/60"
                }`
              }
            >
              <Icon className="w-3 h-3" />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className={isLanding ? "" : "max-w-[1440px] mx-auto px-6 py-8"}>{children}</main>

      <footer className="border-t border-white/10 mt-20">
        <div className="max-w-[1440px] mx-auto px-6 py-6 flex items-center justify-between text-xs text-white/40">
          <div>LINEUP · MLB-Grade Scouting for Everyone</div>
          <div className="font-mono">v0.1 · Hackathon Build</div>
        </div>
      </footer>

      <Toaster theme="dark" position="bottom-right" />
    </div>
  );
}
