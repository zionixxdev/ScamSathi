import { Link } from "react-router-dom";
import { ArrowLeft, Compass } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <span className="rounded-2xl border border-white/10 bg-white/[0.04] p-3 text-accent">
        <Compass size={22} aria-hidden="true" />
      </span>
      <h1 className="mt-5 text-2xl font-semibold text-white">Page not found</h1>
      <p className="mt-2 max-w-sm text-sm text-slate-400">
        The page you were looking for does not exist. The dashboard is a good place to start again.
      </p>
      <Link to="/dashboard" className="btn-primary mt-6">
        <ArrowLeft size={15} /> Go to dashboard
      </Link>
    </div>
  );
}
