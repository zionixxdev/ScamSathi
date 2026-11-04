const STORAGE_KEY = "scamsathi.client_id";

function generateId(): string {
  const random =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID().replace(/-/g, "")
      : Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
  return `web${random}`.slice(0, 40);
}

/**
 * Anonymous, browser-local identifier.
 *
 * It is not an account and holds no personal data. It only lets the API return
 * this browser's own scan history. Clearing site data removes it for good.
 */
export function getClientId(): string {
  if (typeof window === "undefined") return generateId();
  const existing = window.localStorage.getItem(STORAGE_KEY);
  if (existing && /^[A-Za-z0-9_-]{8,64}$/.test(existing)) return existing;
  const created = generateId();
  window.localStorage.setItem(STORAGE_KEY, created);
  return created;
}

export function forgetClientId(): string {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(STORAGE_KEY);
    window.localStorage.removeItem("scamsathi.results");
  }
  return getClientId();
}
