import { Link } from "react-router-dom";
import { Fingerprint, Gauge, Info, ShieldAlert, Trash2 } from "lucide-react";
import { forgetClientId } from "../lib/clientId";
import { useState } from "react";

const PIPELINE = [
  { title: "Rule engine", body: "Weighted regular expressions for 30+ warning signs across English, Hinglish and Hindi." },
  { title: "NLP layer", body: "Script detection, capitalisation, punctuation, link density and obfuscation checks." },
  { title: "Link analysis", body: "Lexical domain analysis of every URL in the message. Nothing is fetched." },
  { title: "Contextual AI (optional)", body: "An OpenAI-compatible provider may adjust the score by at most ±10 and add one rationale sentence." },
  { title: "Scoring", body: "Diminishing returns across indicators, category coherence, known combinations, minus legitimate-signal mitigators." },
  { title: "Explanation", body: "Built from the indicators that actually matched, in English, Hindi or Hinglish." },
];

export default function About() {
  const [cleared, setCleared] = useState(false);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
          <Info size={22} className="text-accent" aria-hidden="true" /> About &amp; privacy
        </h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          ScamSathi is an independent, open-source safety tool for Indian users. It explains suspicious
          content instead of asking you to trust a black box.
        </p>
      </header>

      <section className="glass p-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-white">
          <Gauge size={17} className="text-accent" aria-hidden="true" /> How the score works
        </h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {PIPELINE.map((step, index) => (
            <div key={step.title} className="rounded-xl border border-white/[0.07] bg-white/[0.03] p-4">
              <p className="font-mono text-[11px] text-slate-600">0{index + 1}</p>
              <p className="mt-1 text-sm font-semibold text-white">{step.title}</p>
              <p className="mt-1 text-xs leading-relaxed text-slate-400">{step.body}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 rounded-xl border border-risk-medium/25 bg-risk-medium/[0.07] p-4 text-xs leading-relaxed text-slate-300">
          The risk score is a heuristic index from 0 to 100, not a calibrated probability that a message is
          fraudulent. It is not a statistical model output and must not be read as one. Low risk means no
          known pattern matched — never that the message is proven genuine.
        </p>
      </section>

      <section className="glass p-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-white">
          <Fingerprint size={17} className="text-accent-mint" aria-hidden="true" /> Privacy and data
        </h2>
        <ul className="mt-3 space-y-2 text-sm leading-relaxed text-slate-300">
          <li>• No accounts, no email, no phone number, no login.</li>
          <li>• A random id in your browser's local storage links scans to you — nothing else does.</li>
          <li>• Only a redacted preview (OTP, card, account, email and phone numbers masked) is stored, never the full message.</li>
          <li>• A salted hash of the content is kept so duplicate detection can work without the text.</li>
          <li>• Submitted URLs are never opened, resolved or screenshotted. Query strings are stripped before storage.</li>
          <li>• Request logs contain route, status and timing only — never message content.</li>
          <li>• Every record can be deleted from history; deleting clears it from the database permanently.</li>
          <li>• If an AI or reputation provider is configured by the operator, only redacted text and the bare URL are sent to it.</li>
        </ul>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="btn-ghost text-risk-critical"
            onClick={() => {
              forgetClientId();
              setCleared(true);
            }}
          >
            <Trash2 size={15} /> Forget my local id and cached results
          </button>
          {cleared && (
            <span className="text-xs text-risk-low">
              Local id cleared. Your previous history is no longer reachable from this browser.
            </span>
          )}
        </div>
      </section>

      <section className="glass p-5">
        <h2 className="flex items-center gap-2 text-base font-semibold text-white">
          <ShieldAlert size={17} className="text-risk-high" aria-hidden="true" /> Limits you should know
        </h2>
        <ul className="mt-3 space-y-2 text-sm leading-relaxed text-slate-300">
          <li>• The engine cannot verify who sent a message, whether a phone number is real, or what a website does.</li>
          <li>• Rule-based detection can miss novel scams and can be fooled by careful wording.</li>
          <li>• No accuracy figure is claimed here. The engine has not been validated on a labelled production dataset.</li>
          <li>• Absence of a warning sign is not a safety guarantee. Verify anything involving money or credentials.</li>
          <li>• This tool is not a substitute for your bank, the police, or legal and financial advice.</li>
        </ul>
      </section>

      <section className="glass p-5">
        <h2 className="text-base font-semibold text-white">Built with</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-400">
          React, TypeScript, Vite and Tailwind CSS on the frontend. FastAPI, Pydantic and SQLAlchemy on the
          backend, with a rule engine and lightweight NLP that run entirely offline. AI and URL reputation
          providers are optional plugins — the application is fully functional without either.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {["React", "TypeScript", "Vite", "Tailwind", "FastAPI", "Pydantic", "SQLAlchemy", "Pytest", "Lucide"].map(
            (tech) => (
              <span key={tech} className="chip">
                {tech}
              </span>
            ),
          )}
        </div>
        <p className="mt-4 text-xs text-slate-500">
          Report fraud at{" "}
          <a className="text-accent hover:underline" href="https://cybercrime.gov.in/" target="_blank" rel="noreferrer noopener">
            cybercrime.gov.in
          </a>{" "}
          or call 1930.{" "}
          <Link to="/guide" className="text-accent hover:underline">
            Read the safety guide
          </Link>
          .
        </p>
      </section>
    </div>
  );
}
