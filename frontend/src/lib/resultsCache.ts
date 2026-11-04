import type { AnalysisResult } from "./types";

const KEY = "scamsathi.results";
const LIMIT = 20;

type Cache = Record<string, AnalysisResult>;

function read(): Cache {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.sessionStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Cache) : {};
  } catch {
    return {};
  }
}

export function rememberResult(result: AnalysisResult): void {
  const cache = read();
  cache[result.scan_id] = result;
  const entries = Object.entries(cache).slice(-LIMIT);
  try {
    window.sessionStorage.setItem(KEY, JSON.stringify(Object.fromEntries(entries)));
  } catch {
    // Session storage full or unavailable: the result is still on screen.
  }
}

export function recallResult(scanId: string): AnalysisResult | null {
  return read()[scanId] ?? null;
}

export function forgetResult(scanId: string): void {
  const cache = read();
  delete cache[scanId];
  window.sessionStorage.setItem(KEY, JSON.stringify(cache));
}
