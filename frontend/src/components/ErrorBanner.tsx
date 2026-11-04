import { AlertCircle, X } from "lucide-react";

export default function ErrorBanner({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-risk-critical/30 bg-risk-critical/10 p-4"
    >
      <AlertCircle className="mt-0.5 shrink-0 text-risk-critical" size={18} aria-hidden="true" />
      <p className="flex-1 text-sm text-slate-200">{message}</p>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="rounded-md p-1 text-slate-400 transition hover:bg-white/10 hover:text-white"
          aria-label="Dismiss error"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
