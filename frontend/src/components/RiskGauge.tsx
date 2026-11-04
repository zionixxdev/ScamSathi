import { riskStyle } from "../lib/format";

interface Props {
  score: number;
  level: string;
  confidence?: number;
}

export default function RiskGauge({ score, level, confidence }: Props) {
  const style = riskStyle(level);
  const radius = 68;
  const circumference = Math.PI * radius; // half circle
  const progress = Math.min(100, Math.max(0, score)) / 100;
  const offset = circumference * (1 - progress);

  return (
    <div className="flex flex-col items-center">
      <svg
        viewBox="0 0 180 104"
        className="w-full max-w-[260px]"
        role="img"
        aria-label={`Risk score ${score} out of 100, ${level}`}
      >
        <path
          d="M 22 92 A 68 68 0 0 1 158 92"
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d="M 22 92 A 68 68 0 0 1 158 92"
          fill="none"
          stroke={style.hex}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 700ms ease-out" }}
        />
      </svg>
      <div className="-mt-12 flex flex-col items-center">
        <span className="font-mono text-4xl font-semibold text-white">{score}</span>
        <span className="text-xs uppercase tracking-[0.18em] text-slate-500">out of 100</span>
        <span className={`mt-2 text-sm font-semibold ${style.text}`}>{level} risk</span>
        {typeof confidence === "number" && (
          <span className="mt-1 text-xs text-slate-500">
            Engine confidence {Math.round(confidence * 100)}%
          </span>
        )}
      </div>
    </div>
  );
}
