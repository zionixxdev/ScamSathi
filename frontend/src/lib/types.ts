export type RiskLevel = "Low" | "Medium" | "High" | "Critical" | "Uncertain";

export type Channel =
  | "sms"
  | "whatsapp"
  | "email"
  | "job_offer"
  | "payment_request"
  | "other";

export type Language = "auto" | "en" | "hi" | "hinglish";

export interface Category {
  key: string;
  label: string;
}

export interface SecondaryCategory extends Category {
  score: number;
}

export interface Indicator {
  id: string;
  label: string;
  category: string;
  weight: number;
  severity: "info" | "low" | "medium" | "high";
  evidence: string;
  explanation: string;
  source: "rule" | "nlp" | "url" | "ai";
}

export interface Mitigator {
  id: string;
  label: string;
  explanation: string;
}

export interface UrlFinding {
  id: string;
  label: string;
  weight: number;
  evidence: string;
  explanation: string;
}

export interface Reputation {
  checked: boolean;
  provider: string | null;
  verdict: string;
  note: string;
}

export interface UrlAnalysis {
  submitted: string;
  normalized: string;
  host: string;
  scheme: string;
  https: boolean;
  is_ip_literal: boolean;
  is_shortener: boolean;
  is_punycode: boolean;
  lookalike_of: string | null;
  risk_score: number;
  risk_level: string;
  findings: UrlFinding[];
  reputation: Reputation;
  disclaimer: string;
}

export interface AiInsight {
  used: boolean;
  provider: string | null;
  rationale: string | null;
  score_adjustment: number;
  note: string | null;
}

export interface AnalysisResult {
  scan_id: string;
  scan_type: "message" | "url";
  channel: string;
  created_at: string;
  risk_score: number;
  risk_level: RiskLevel;
  category: Category;
  secondary_categories: SecondaryCategory[];
  confidence: number;
  uncertainty: string | null;
  language: string;
  indicators: Indicator[];
  mitigators: Mitigator[];
  explanation: string;
  recommended_actions: string[];
  excerpt: string;
  ai: AiInsight;
  url_analysis: UrlAnalysis | null;
  stored: boolean;
  disclaimer: string;
}

export interface HistoryItem {
  scan_id: string;
  scan_type: string;
  channel: string;
  risk_score: number;
  risk_level: string;
  category: Category;
  confidence: number;
  excerpt: string;
  created_at: string;
}

export interface HistoryPage {
  items: HistoryItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface Stats {
  total_scans: number;
  high_risk_scans: number;
  by_risk_level: Record<string, number>;
  by_category: { category: string; label: string; count: number }[];
  recent: HistoryItem[];
  demo_data: boolean;
  note: string;
}

export interface Health {
  status: string;
  version: string;
  environment: string;
  ai_provider: string;
  url_reputation_provider: string;
  database: string;
  timestamp: string;
}
