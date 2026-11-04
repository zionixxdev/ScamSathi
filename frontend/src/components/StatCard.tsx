import type { LucideIcon } from "lucide-react";

interface Props {
  label: string;
  value: string | number;
  hint?: string;
  icon: LucideIcon;
  accent?: string;
}

export default function StatCard({ label, value, hint, icon: Icon, accent = "text-accent" }: Props) {
  return (
    <div className="glass p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">{label}</p>
          <p className="mt-2 font-mono text-3xl font-semibold text-white">{value}</p>
        </div>
        <span className={`rounded-xl border border-white/10 bg-white/[0.04] p-2.5 ${accent}`}>
          <Icon size={18} aria-hidden="true" />
        </span>
      </div>
      {hint && <p className="mt-3 text-xs leading-relaxed text-slate-500">{hint}</p>}
    </div>
  );
}
