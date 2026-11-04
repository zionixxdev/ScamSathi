import { describe, expect, it } from "vitest";
import { channelLabel, formatRelative, percent, riskStyle } from "../format";
import { getClientId } from "../clientId";

describe("formatting helpers", () => {
  it("maps every risk level to a colour style", () => {
    for (const level of ["Low", "Medium", "High", "Critical", "Uncertain"]) {
      expect(riskStyle(level).hex).toMatch(/^#[0-9a-f]{6}$/i);
    }
  });

  it("falls back to the uncertain style for unknown levels", () => {
    expect(riskStyle("Nonsense").hex).toBe(riskStyle("Uncertain").hex);
  });

  it("formats confidence as a percentage", () => {
    expect(percent(0.62)).toBe("62%");
  });

  it("labels channels in human language", () => {
    expect(channelLabel("whatsapp")).toBe("WhatsApp");
    expect(channelLabel("mystery")).toBe("mystery");
  });

  it("describes recent timestamps relatively", () => {
    expect(formatRelative(new Date().toISOString())).toBe("just now");
  });
});

describe("client id", () => {
  it("creates a stable, valid anonymous id", () => {
    const first = getClientId();
    expect(getClientId()).toBe(first);
    expect(first).toMatch(/^[A-Za-z0-9_-]{8,64}$/);
  });
});
