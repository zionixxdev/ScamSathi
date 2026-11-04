import { useEffect, useState } from "react";
import { NavLink, Outlet, Link } from "react-router-dom";
import {
  BookOpen,
  History,
  Info,
  LayoutDashboard,
  Link2,
  Menu,
  MessageSquareWarning,
  Radar,
  ShieldCheck,
  X,
} from "lucide-react";
import { api } from "../lib/api";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/scan/message", label: "Message Scanner", icon: MessageSquareWarning },
  { to: "/scan/url", label: "URL Scanner", icon: Link2 },
  { to: "/history", label: "Scan History", icon: History },
  { to: "/intelligence", label: "Scam Intelligence", icon: Radar },
  { to: "/guide", label: "Safety Guide", icon: BookOpen },
  { to: "/about", label: "About & Privacy", icon: Info },
];

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2.5" aria-label="ScamSathi home">
      <span className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-accent/30 bg-accent/10">
        <ShieldCheck size={18} className="text-accent" aria-hidden="true" />
      </span>
      <span className="flex flex-col leading-none">
        <span className="text-base font-semibold tracking-tight text-white">ScamSathi</span>
        <span className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-500">scam analysis</span>
      </span>
    </Link>
  );
}

function ApiStatus() {
  const [state, setState] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    let active = true;
    api
      .health()
      .then(() => active && setState("online"))
      .catch(() => active && setState("offline"));
    return () => {
      active = false;
    };
  }, []);

  const styles = {
    checking: "bg-slate-500",
    online: "bg-risk-low",
    offline: "bg-risk-critical",
  }[state];
  const label = {
    checking: "Checking API",
    online: "Engine online",
    offline: "API unreachable",
  }[state];

  return (
    <span className="chip">
      <span className={`h-1.5 w-1.5 rounded-full ${styles}`} aria-hidden="true" />
      {label}
    </span>
  );
}

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen lg:flex">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2 focus:text-ink-950"
      >
        Skip to content
      </a>

      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-white/[0.06] bg-ink-900/40 px-5 py-6 backdrop-blur-xl lg:flex">
        <Logo />
        <nav className="mt-8 flex-1 space-y-1" aria-label="Main">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                  isActive
                    ? "border border-accent/25 bg-accent/10 font-semibold text-white"
                    : "border border-transparent text-slate-400 hover:bg-white/[0.05] hover:text-slate-200"
                }`
              }
            >
              <Icon size={17} aria-hidden="true" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="space-y-3 border-t border-white/[0.06] pt-4">
          <ApiStatus />
          <p className="text-[11px] leading-relaxed text-slate-500">
            Educational tool. Not a substitute for your bank or the police.
          </p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-white/[0.06] bg-ink-950/85 px-4 py-3 backdrop-blur-xl lg:hidden">
          <Logo />
          <button
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            className="rounded-lg border border-white/10 p-2 text-slate-300"
            aria-expanded={menuOpen}
            aria-label="Toggle navigation"
          >
            {menuOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </header>

        {menuOpen && (
          <nav
            className="border-b border-white/[0.06] bg-ink-900/95 px-4 py-3 lg:hidden"
            aria-label="Mobile"
          >
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${
                    isActive ? "bg-accent/10 font-semibold text-white" : "text-slate-400"
                  }`
                }
              >
                <Icon size={16} aria-hidden="true" />
                {label}
              </NavLink>
            ))}
          </nav>
        )}

        <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 pb-24 pt-6 sm:px-6 lg:pb-12 lg:pt-10">
          <Outlet />
        </main>

        <footer className="border-t border-white/[0.06] px-4 py-6 text-center text-xs text-slate-500 sm:px-6">
          ScamSathi · Understand the scam before it catches you. Report fraud at{" "}
          <a className="text-accent hover:underline" href="https://cybercrime.gov.in/" target="_blank" rel="noreferrer noopener">
            cybercrime.gov.in
          </a>{" "}
          or call 1930.
        </footer>
      </div>

      {/* Mobile quick actions */}
      <nav
        className="fixed inset-x-0 bottom-0 z-30 flex justify-around border-t border-white/[0.08] bg-ink-900/95 px-2 py-2 backdrop-blur-xl lg:hidden"
        aria-label="Quick actions"
      >
        {NAV.slice(0, 4).map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-1 rounded-lg py-1 text-[10px] ${
                isActive ? "text-accent" : "text-slate-500"
              }`
            }
          >
            <Icon size={18} aria-hidden="true" />
            {label.split(" ")[0]}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
