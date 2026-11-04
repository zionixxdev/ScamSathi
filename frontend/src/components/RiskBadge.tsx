import { riskStyle } from "../lib/format";

interface Props {
  level: string;
  score?: number;
  size?: "sm" | "md";
}

export default function RiskBadge({ level, score, size = "sm" }: Props) {
  const style = riskStyle(level);
  const sizing = size === "md" ? "px-3 py-1.5 text-sm" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold ring-1 ${style.bg} ${style.text} ${style.ring} ${sizing}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.text} bg-current`} aria-hidden="true" />
      {level}
      {typeof score === "number" && <span className="font-mono opacity-70">{score}</span>}
    </span>
  );
}
