import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Braces,
  Eye,
  FileSearch,
  Fingerprint,
  Link2,
  Lock,
  MessageSquareWarning,
  Radar,
  ShieldCheck,
  Sparkles,
  Trash2,
} from "lucide-react";

const FEATURES = [
  {
    icon: MessageSquareWarning,
    title: "Message scanner",
    body: "Paste an SMS, WhatsApp forward, email or job offer. The engine reads English, Hindi and Hinglish.",
  },
  {
    icon: Link2,
    title: "URL scanner",
    body: "Checks domain structure, lookalikes, shorteners and bait paths — without ever opening the link.",
  },
  {
    icon: Eye,
    title: "Explainable risk",
    body: "Every score comes with the exact indicators, the evidence snippet and a plain-language reason.",
  },
  {
    icon: Radar,
    title: "Scam categories",
    body: "Bank/KYC, UPI, phishing, fake jobs, lottery, government impersonation, OTP takeover and more.",
  },
  {
    icon: Braces,
    title: "Hybrid engine",
    body: "Deterministic rules plus lightweight NLP. An LLM is optional and can only nudge the score.",
  },
  {
    icon: Lock,
    title: "Privacy by default",
    body: "No accounts. Only redacted excerpts are stored, and you can delete any record in one tap.",
  },
];

const STEPS = [
  {
    icon: FileSearch,
    title: "Submit the content",
    body: "Paste the message or link. Nothing is executed, rendered or opened.",
  },
  {
    icon: Fingerprint,
    title: "The engine reads it",
    body: "Rules, NLP and link analysis run together and produce weighted indicators.",
  },
  {
    icon: ShieldCheck,
    title: "You get a decision you can act on",
    body: "Risk level, evidence, category and the exact next steps — in your language.",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-accent/30 bg-accent/10">
            <ShieldCheck size={18} className="text-accent" aria-hidden="true" />
          </span>
          <span className="text-base font-semibold tracking-tight text-white">ScamSathi</span>
        </div>
        <nav className="flex items-center gap-2 text-sm">
          <Link to="/guide" className="hidden rounded-lg px-3 py-2 text-slate-400 hover:text-white sm:block">
            Safety guide
          </Link>
          <Link to="/about" className="hidden rounded-lg px-3 py-2 text-slate-400 hover:text-white sm:block">
            About
          </Link>
          <Link to="/dashboard" className="btn-primary">
            Open dashboard <ArrowRight size={16} />
          </Link>
        </nav>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-5 pb-16 pt-10 sm:pt-16">
          <div className="grid items-center gap-10 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="animate-fade-up">
              <span className="chip">
                <Sparkles size={13} className="text-accent" aria-hidden="true" />
                Built for Indian scam patterns
              </span>
              <h1 className="mt-5 text-4xl font-semibold leading-[1.08] tracking-tight text-white sm:text-5xl lg:text-6xl">
                Understand the scam
                <span className="block bg-gradient-to-r from-accent via-accent-mint to-risk-uncertain bg-clip-text text-transparent">
                  before it catches you.
                </span>
              </h1>
              <p className="mt-5 max-w-xl text-base leading-relaxed text-slate-400">
                ScamSathi analyses suspicious messages, job offers, payment requests and links, scores the
                risk from 0 to 100, shows the evidence behind the score and tells you exactly what to do
                next.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/scan/message" className="btn-primary">
                  <MessageSquareWarning size={16} /> Scan a message
                </Link>
                <Link to="/scan/url" className="btn-ghost">
                  <Link2 size={16} /> Check a link
                </Link>
              </div>
              <p className="mt-6 max-w-lg text-xs leading-relaxed text-slate-500">
                The risk score is a heuristic index, not the probability that a message is fraudulent.
                ScamSathi cannot verify senders, phone numbers or websites.
              </p>
            </div>

            <div className="glass-strong animate-fade-up p-6 [animation-delay:120ms]">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                Example reading
              </p>
              <p className="mt-3 rounded-xl border border-white/5 bg-ink-950/70 p-3 font-mono text-xs leading-relaxed text-slate-400">
                “Dear Customer, your SBI account will be blocked today. Complete your KYC immediately at
                sbi-kyc-verify.top/update”
              </p>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm text-slate-300">Bank / KYC fraud</span>
                <span className="rounded-full bg-risk-critical/15 px-3 py-1 text-xs font-semibold text-risk-critical ring-1 ring-risk-critical/30">
                  Critical · 100
                </span>
              </div>
              <ul className="mt-4 space-y-2 text-sm text-slate-400">
                <li>• Demands an urgent KYC update</li>
                <li>• Threatens to block the account</li>
                <li>• Link imitates a bank on a throwaway domain</li>
                <li>• Generic “Dear Customer” greeting</li>
              </ul>
              <p className="mt-4 text-xs text-slate-500">
                Illustrative output of the rule engine for this sample message.
              </p>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-16">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon: Icon, title, body }) => (
              <article key={title} className="glass p-5 transition hover:border-white/15">
                <span className="inline-flex rounded-xl border border-white/10 bg-white/[0.04] p-2.5 text-accent">
                  <Icon size={18} aria-hidden="true" />
                </span>
                <h3 className="mt-4 text-sm font-semibold text-white">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{body}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-16">
          <h2 className="section-title">How a scan works</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {STEPS.map(({ icon: Icon, title, body }, index) => (
              <div key={title} className="glass p-5">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-600">0{index + 1}</span>
                  <Icon size={18} className="text-accent-mint" aria-hidden="true" />
                </div>
                <h3 className="mt-3 text-sm font-semibold text-white">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-20">
          <div className="glass-strong flex flex-col items-start gap-6 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <span className="rounded-xl border border-risk-low/25 bg-risk-low/10 p-2.5 text-risk-low">
                <Trash2 size={18} aria-hidden="true" />
              </span>
              <div>
                <h3 className="text-base font-semibold text-white">Nothing leaves your device unless you scan</h3>
                <p className="mt-1 max-w-xl text-sm text-slate-400">
                  There are no accounts and no trackers. Scan history is tied to an anonymous id in your
                  browser and can be deleted at any time.
                </p>
              </div>
            </div>
            <Link to="/about" className="btn-ghost shrink-0">
              Read the privacy note <ArrowRight size={15} />
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/[0.06] px-5 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-xs text-slate-500 sm:flex-row">
          <p>ScamSathi · an independent safety tool for Indian users</p>
          <div className="flex items-center gap-4">
            <a href="https://cybercrime.gov.in/" target="_blank" rel="noreferrer noopener" className="hover:text-accent">
              cybercrime.gov.in
            </a>
            <a href="https://www.cert-in.org.in/" target="_blank" rel="noreferrer noopener" className="hover:text-accent">
              cert-in.org.in
            </a>
            <Link to="/guide" className="inline-flex items-center gap-1 hover:text-accent">
              <BookOpen size={13} /> Safety guide
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
