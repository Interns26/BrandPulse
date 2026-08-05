import { NavLink } from "react-router-dom";
import { Icon } from "@iconify/react";

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-[var(--border)] bg-[var(--card)] p-4 flex flex-col gap-6 shrink-0 min-h-[calc(100vh-3.5rem)]">
      {/* Live Monitoring Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--positive-bg)] text-[var(--positive-text)] text-xs font-semibold w-fit">
        <span className="w-2 h-2 rounded-full bg-[var(--accent)] animate-pulse" />
        <span>Live Monitoring</span>
      </div>

      {/* Sprint 1 Navigation */}
      <div className="space-y-2">
        <span className="text-[11px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase px-2">
          Sprint 1
        </span>
        <nav className="space-y-1">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]"
              }`
            }
          >
            <Icon icon="lucide:pie-chart" className="w-5 h-5" />
            <span>Dashboard</span>
          </NavLink>
        </nav>
      </div>

      {/* Sprint 2 Navigation */}
      <div className="space-y-2">
        <span className="text-[11px] font-bold tracking-wider text-[var(--muted-foreground)] uppercase px-2">
          Sprint 2
        </span>
        <nav className="space-y-1">
          <NavLink
            to="/competitive-intel"
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]"
              }`
            }
          >
            <div className="flex items-center gap-3">
              <Icon icon="lucide:disc" className="w-5 h-5" />
              <span>Competitive Intel</span>
            </div>
            <span className="bg-rose-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
              2
            </span>
          </NavLink>

          <NavLink
            to="/raw-data-pipeline"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-[var(--positive-bg)] text-[var(--positive-text)]"
                  : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]"
              }`
            }
          >
            <Icon icon="lucide:database" className="w-5 h-5" />
            <span>Raw Data Pipeline</span>
          </NavLink>
        </nav>
      </div>
    </aside>
  );
}