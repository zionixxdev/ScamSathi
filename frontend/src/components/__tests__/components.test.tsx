import { describe, expect, it } from "vitest";
import { ShieldCheck } from "lucide-react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import RiskBadge from "../RiskBadge";
import RiskGauge from "../RiskGauge";
import { IndicatorCards, MitigatorList } from "../IndicatorList";
import EmptyState from "../EmptyState";
import { CategoryDonut } from "../CategoryChart";
import type { Indicator } from "../../lib/types";

const indicator: Indicator = {
  id: "credential_request",
  label: "Asks you to share a secret credential",
  category: "otp_account_takeover",
  weight: 30,
  severity: "high",
  evidence: "…share your OTP…",
  explanation: "No bank ever asks for an OTP.",
  source: "rule",
};

describe("RiskBadge", () => {
  it("shows the level and the score", () => {
    render(<RiskBadge level="Critical" score={92} />);
    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByText("92")).toBeInTheDocument();
  });
});

describe("RiskGauge", () => {
  it("exposes an accessible label with the score", () => {
    render(<RiskGauge score={57} level="High" confidence={0.7} />);
    expect(screen.getByRole("img")).toHaveAttribute("aria-label", "Risk score 57 out of 100, High");
    expect(screen.getByText("High risk")).toBeInTheDocument();
    expect(screen.getByText(/70%/)).toBeInTheDocument();
  });
});

describe("IndicatorCards", () => {
  it("renders each indicator with its explanation and evidence", () => {
    render(<IndicatorCards indicators={[indicator]} />);
    expect(screen.getByText(indicator.label)).toBeInTheDocument();
    expect(screen.getByText(indicator.explanation)).toBeInTheDocument();
    expect(screen.getByText("+30")).toBeInTheDocument();
  });

  it("states clearly that no match is not proof of safety", () => {
    render(<IndicatorCards indicators={[]} />);
    expect(screen.getByText(/does not prove the message is genuine/i)).toBeInTheDocument();
  });
});

describe("MitigatorList", () => {
  it("renders nothing when there are no mitigators", () => {
    const { container } = render(<MitigatorList mitigators={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("lists signals that lowered the score", () => {
    render(<MitigatorList mitigators={[{ id: "x", label: "Reads like a genuine transaction alert", explanation: "" }]} />);
    expect(screen.getByText(/lowered the score/i)).toBeInTheDocument();
  });
});

describe("CategoryDonut", () => {
  it("shows an empty message with no data", () => {
    render(<CategoryDonut data={[]} />);
    expect(screen.getByText(/No scans yet/i)).toBeInTheDocument();
  });

  it("summarises counts when data exists", () => {
    render(<CategoryDonut data={[{ category: "phishing", label: "Phishing", count: 3 }]} />);
    expect(screen.getAllByText("3").length).toBeGreaterThan(0);
    expect(screen.getByText("Phishing")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /category distribution/i })).toBeInTheDocument();
  });
});

describe("EmptyState", () => {
  it("renders title, description and an action", () => {
    render(
      <MemoryRouter>
        <EmptyState icon={ShieldCheck} title="No scans yet" description="Run a scan." action={<a href="/x">Go</a>} />
      </MemoryRouter>,
    );
    expect(screen.getByText("No scans yet")).toBeInTheDocument();
    expect(screen.getByText("Go")).toBeInTheDocument();
  });
});
