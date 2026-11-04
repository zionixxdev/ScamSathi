import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, api } from "../api";

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("sends the anonymous client id header", async () => {
    const spy = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    globalThis.fetch = spy as unknown as typeof fetch;

    await api.health();

    const [, init] = spy.mock.calls[0];
    expect((init as RequestInit).headers).toMatchObject({ "X-Client-Id": expect.any(String) });
  });

  it("turns the API error envelope into an ApiError", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: "invalid_scheme", message: "Only http and https URLs" } }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      }),
    ) as unknown as typeof fetch;

    await expect(api.analyzeUrl("javascript:alert(1)")).rejects.toMatchObject({
      name: "ApiError",
      code: "invalid_scheme",
      status: 400,
    });
  });

  it("reports a network failure clearly", async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error("boom")) as unknown as typeof fetch;
    const error = await api.stats().catch((err: unknown) => err);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).code).toBe("network_error");
  });

  it("handles 204 responses without body", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 })) as unknown as typeof fetch;
    await expect(api.deleteScan("abc")).resolves.toBeUndefined();
  });
});
