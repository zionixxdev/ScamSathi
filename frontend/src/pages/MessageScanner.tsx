import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, MessageSquareWarning, ShieldCheck, Sparkles } from "lucide-react";
import ErrorBanner from "../components/ErrorBanner";
import { api } from "../lib/api";
import { rememberResult } from "../lib/resultsCache";
import type { Channel, Language } from "../lib/types";

const CHANNELS: { value: Channel; label: string }[] = [
  { value: "sms", label: "SMS" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "email", label: "Email" },
  { value: "job_offer", label: "Job offer" },
  { value: "payment_request", label: "Payment request" },
  { value: "other", label: "Other" },
];

const LANGUAGES: { value: Language; label: string }[] = [
  { value: "auto", label: "Auto detect" },
  { value: "en", label: "English" },
  { value: "hinglish", label: "Hinglish" },
  { value: "hi", label: "हिन्दी" },
];

const SAMPLES = [
  {
    label: "Fake KYC",
    text:
      "Dear Customer, your SBI account will be blocked today. Complete your KYC immediately at " +
      "http://sbi-kyc-verify.top/update or your account will be suspended.",
  },
  {
    label: "Hinglish phishing",
    text:
      "Aapka bank account block hone wala hai. KYC update nahi kiya toh SIM band ho jayega. " +
      "Turant is link par click karein http://bit.ly/3xYz",
  },
  {
    label: "Fake job",
    text:
      "Work from home part time job. Earn Rs 5000 daily. Pay registration fee Rs 499 to join. " +
      "Contact HR on WhatsApp 9876543210.",
  },
  {
    label: "Genuine alert",
    text:
      "Rs.500.00 debited from A/c XX1234 on 04-11-26 to VPA amazon@ybl. Avl Bal Rs.12,340.00. " +
      "Not you? Call 18001234.",
  },
];

const MAX_CHARS = 5000;

export default function MessageScanner() {
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [channel, setChannel] = useState<Channel>("sms");
  const [language, setLanguage] = useState<Language>("auto");
  const [senderId, setSenderId] = useState("");
  const [store, setStore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tooLong = content.length > MAX_CHARS;
  const canSubmit = content.trim().length > 0 && !tooLong && !loading;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.analyzeMessage({
        content,
        channel,
        language,
        sender_id: senderId.trim() || null,
        store,
      });
      rememberResult(result);
      navigate(`/result/${result.scan_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The scan failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">Message scanner</h1>
        <p className="mt-1.5 max-w-2xl text-sm text-slate-400">
          Paste the full message exactly as you received it. The engine reads English, Hindi and Hinglish,
          and never executes or renders anything you submit.
        </p>
      </header>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <form onSubmit={handleSubmit} className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <div className="glass p-5">
          <label className="label" htmlFor="content">
            Message content
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(event) => setContent(event.target.value)}
            rows={9}
            maxLength={MAX_CHARS + 200}
            placeholder="Paste the SMS, WhatsApp message, email or job offer here…"
            className="input resize-y font-mono text-[13px] leading-relaxed"
            aria-describedby="content-help"
            required
          />
          <div className="mt-2 flex items-center justify-between text-xs">
            <span id="content-help" className="text-slate-500">
              Up to {MAX_CHARS.toLocaleString("en-IN")} characters. Nothing is sent anywhere except this API.
            </span>
            <span className={tooLong ? "font-semibold text-risk-critical" : "text-slate-500"}>
              {content.length.toLocaleString("en-IN")} / {MAX_CHARS.toLocaleString("en-IN")}
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="channel">
                Where did it come from?
              </label>
              <select
                id="channel"
                value={channel}
                onChange={(event) => setChannel(event.target.value as Channel)}
                className="input"
              >
                {CHANNELS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label" htmlFor="language">
                Explanation language
              </label>
              <select
                id="language"
                value={language}
                onChange={(event) => setLanguage(event.target.value as Language)}
                className="input"
              >
                {LANGUAGES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="label" htmlFor="sender">
              Sender id (optional)
            </label>
            <input
              id="sender"
              value={senderId}
              onChange={(event) => setSenderId(event.target.value)}
              maxLength={32}
              placeholder="e.g. VM-SBIINB — helps recognise genuine DLT senders"
              className="input"
            />
          </div>

          <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-white/[0.07] bg-white/[0.02] p-3">
            <input
              type="checkbox"
              checked={store}
              onChange={(event) => setStore(event.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-white/20 bg-ink-900 text-accent focus:ring-accent"
            />
            <span className="text-xs leading-relaxed text-slate-400">
              Save a redacted summary to my scan history. OTPs, card and account numbers are masked before
              anything is stored.
            </span>
          </label>

          <button type="submit" className="btn-primary mt-5 w-full" disabled={!canSubmit}>
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Analysing…
              </>
            ) : (
              <>
                <ShieldCheck size={16} /> Analyse message
              </>
            )}
          </button>
        </div>

        <aside className="space-y-4">
          <div className="glass p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
              <Sparkles size={15} className="text-accent" aria-hidden="true" /> Try a sample
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Load a real-world style example to see how the engine explains itself.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {SAMPLES.map((sample) => (
                <button
                  key={sample.label}
                  type="button"
                  onClick={() => {
                    setContent(sample.text);
                    setError(null);
                  }}
                  className="chip transition hover:border-accent/40 hover:text-white"
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          <div className="glass p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
              <MessageSquareWarning size={15} className="text-accent-mint" aria-hidden="true" /> What gets checked
            </h2>
            <ul className="mt-3 space-y-2 text-xs leading-relaxed text-slate-400">
              <li>• Requests for OTP, PIN, CVV, passwords or bank details</li>
              <li>• Urgency, threats and artificial deadlines</li>
              <li>• Impersonation of banks, regulators and schemes</li>
              <li>• Prize, refund and easy-money lures</li>
              <li>• Job offers that ask for a fee first</li>
              <li>• Every link inside the message, analysed without opening it</li>
            </ul>
          </div>

          <div className="rounded-xl border border-risk-medium/25 bg-risk-medium/[0.07] p-4 text-xs leading-relaxed text-slate-300">
            Never send your OTP, PIN or password to anyone — including someone claiming to be from ScamSathi.
          </div>
        </aside>
      </form>
    </div>
  );
}
