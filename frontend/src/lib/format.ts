import type { RiskLevel } from "./types";

export const RISK_COLORS: Record<RiskLevel, { text: string; bg: string; ring: string; hex: string }> = {
  Low: { text: "text-risk-low", bg: "bg-risk-low/12", ring: "ring-risk-low/40", hex: "#34d399" },
  Medium: { text: "text-risk-medium", bg: "bg-risk-medium/12", ring: "ring-risk-medium/40", hex: "#fbbf24" },
  High: { text: "text-risk-high", bg: "bg-risk-high/12", ring: "ring-risk-high/40", hex: "#fb923c" },
  Critical: { text: "text-risk-critical", bg: "bg-risk-critical/12", ring: "ring-risk-critical/40", hex: "#f43f5e" },
  Uncertain: { text: "text-risk-uncertain", bg: "bg-risk-uncertain/12", ring: "ring-risk-uncertain/40", hex: "#a78bfa" },
};

export function riskStyle(level: string) {
  return RISK_COLORS[(level as RiskLevel) in RISK_COLORS ? (level as RiskLevel) : "Uncertain"];
}

export function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelative(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const diff = Date.now() - date.getTime();
  const minutes = Math.round(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hr ago`;
  const days = Math.round(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;
  return formatDateTime(iso);
}

export function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export const CHANNEL_LABELS: Record<string, string> = {
  sms: "SMS",
  whatsapp: "WhatsApp",
  email: "Email",
  job_offer: "Job offer",
  payment_request: "Payment request",
  other: "Other",
  url: "Link",
};

export function channelLabel(channel: string): string {
  return CHANNEL_LABELS[channel] ?? channel;
}
