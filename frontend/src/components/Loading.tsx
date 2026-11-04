export default function Loading({ label = "Analysing…" }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <div className="relative flex h-16 w-16 items-center justify-center">
        <span className="absolute inset-0 animate-pulse-ring rounded-full border border-accent/40" />
        <span className="absolute inset-2 animate-pulse-ring rounded-full border border-accent/30 [animation-delay:600ms]" />
        <span className="h-3 w-3 rounded-full bg-accent shadow-glow" />
      </div>
      <p className="text-sm text-slate-400" role="status">
        {label}
      </p>
    </div>
  );
}
