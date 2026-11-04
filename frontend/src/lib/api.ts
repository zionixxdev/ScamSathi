import { getClientId } from "./clientId";
import type {
  AnalysisResult,
  Channel,
  Health,
  HistoryPage,
  Language,
  Stats,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status: number, code: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

interface ErrorEnvelope {
  error?: { code?: string; message?: string };
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Client-Id": getClientId(),
    ...(init.headers as Record<string, string> | undefined),
  };

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(
      "Could not reach the ScamSathi API. Check that the backend is running and VITE_API_BASE_URL is correct.",
      0,
      "network_error",
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const payload = text ? (JSON.parse(text) as unknown) : null;

  if (!response.ok) {
    const envelope = (payload ?? {}) as ErrorEnvelope;
    throw new ApiError(
      envelope.error?.message ?? "The request failed. Please try again.",
      response.status,
      envelope.error?.code ?? "request_failed",
    );
  }

  return payload as T;
}

export interface MessageScanInput {
  content: string;
  channel: Channel;
  language: Language;
  sender_id?: string | null;
  store?: boolean;
}

export const api = {
  baseUrl: BASE_URL,

  health: () => request<Health>("/api/v1/health"),

  analyzeMessage: (input: MessageScanInput) =>
    request<AnalysisResult>("/api/v1/analyze/message", {
      method: "POST",
      body: JSON.stringify({
        content: input.content,
        channel: input.channel,
        language: input.language,
        sender_id: input.sender_id || null,
        store: input.store ?? true,
      }),
    }),

  analyzeUrl: (url: string, store = true) =>
    request<AnalysisResult>("/api/v1/analyze/url", {
      method: "POST",
      body: JSON.stringify({ url, store }),
    }),

  history: (params: { limit?: number; offset?: number; risk_level?: string } = {}) => {
    const search = new URLSearchParams();
    if (params.limit) search.set("limit", String(params.limit));
    if (params.offset) search.set("offset", String(params.offset));
    if (params.risk_level) search.set("risk_level", params.risk_level);
    const query = search.toString();
    return request<HistoryPage>(`/api/v1/history${query ? `?${query}` : ""}`);
  },

  scan: (scanId: string) => request<AnalysisResult>(`/api/v1/history/${encodeURIComponent(scanId)}`),

  deleteScan: (scanId: string) =>
    request<void>(`/api/v1/history/${encodeURIComponent(scanId)}`, { method: "DELETE" }),

  stats: () => request<Stats>("/api/v1/stats"),
};
