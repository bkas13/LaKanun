"use client";

import { useMemo } from "react";
import { useI18n } from "@/contexts/I18nContext";

/**
 * Unified relevance display used across search results, AI tools, and detail modals.
 *
 * Props:
 *   score     – raw score in ANY scale (0-1, 0-100, or arbitrary)
 *   max       – the maximum possible value (default: auto-detect)
 *   size      – "sm" (inline badge) | "md" (card) | "lg" (detail panel)
 *   showBar   – show the animated bar (default: true for md/lg)
 *   showLabel – show the text label (default: true)
 *   className – extra classes
 */

interface Props {
  score: number;
  max?: number;
  size?: "sm" | "md" | "lg";
  showBar?: boolean;
  showLabel?: boolean;
  className?: string;
}

const TIERS = [
  { min: 80, en: "Excellent", ne: "उत्कृष्ट", hi: "उत्कृष्ट", color: "emerald" },
  { min: 60, en: "Strong",   ne: "बलियो",    hi: "मज़बूत",    color: "cyan" },
  { min: 40, en: "Good",     ne: "राम्रो",    hi: "अच्छा",     color: "blue" },
  { min: 20, en: "Fair",     ne: "सामान्य",   hi: "सामान्य",   color: "amber" },
  { min: 0,  en: "Low",      ne: "कम",       hi: "कम",        color: "red" },
];

const COLOR_MAP: Record<string, { bg: string; text: string; bar: string; barBg: string; ring: string }> = {
  emerald: { bg: "bg-emerald-50",   text: "text-emerald-700", bar: "bg-emerald-500", barBg: "bg-emerald-100", ring: "ring-emerald-200" },
  cyan:    { bg: "bg-cyan-50",      text: "text-cyan-700",    bar: "bg-cyan-500",    barBg: "bg-cyan-100",    ring: "ring-cyan-200" },
  blue:    { bg: "bg-blue-50",      text: "text-blue-700",    bar: "bg-blue-500",    barBg: "bg-blue-100",    ring: "ring-blue-200" },
  amber:   { bg: "bg-amber-50",     text: "text-amber-700",   bar: "bg-amber-500",   barBg: "bg-amber-100",   ring: "ring-amber-200" },
  red:     { bg: "bg-red-50",       text: "text-red-700",     bar: "bg-red-500",     barBg: "bg-red-100",     ring: "ring-red-200" },
};

export default function RelevanceBadge({
  score,
  max,
  size = "sm",
  showBar = true,
  showLabel = true,
  className = "",
}: Props) {
  const { locale } = useI18n();

  const { pct, tier } = useMemo(() => {
    // Auto-detect scale: if max > 1.5 assume 0-1 float, else assume 0-100
    const effectiveMax = max ?? (score > 1.5 ? 100 : 1);
    const normalised = Math.round(Math.min(100, Math.max(0, (score / effectiveMax) * 100)));
    const t = TIERS.find((t) => normalised >= t.min) ?? TIERS[TIERS.length - 1];
    return { pct: normalised, tier: t };
  }, [score, max]);

  const colors = COLOR_MAP[tier.color];
  const label = locale === "ne" ? tier.ne : locale === "hi" ? tier.hi : tier.en;

  // ── Small (inline badge) ──────────────────────────────────────────
  if (size === "sm") {
    return (
      <span className={`inline-flex items-center gap-1.5 ${className}`}>
        {showBar && (
          <span className="flex items-end gap-[2px]">
            {[1, 2, 3, 4, 5].map((bar) => (
              <span
                key={bar}
                className={`w-[3px] rounded-t-sm transition-all duration-500 ${
                  bar <= Math.ceil(pct / 20) ? colors.bar : "bg-gray-200"
                }`}
                style={{ height: `${[4, 6, 8, 10, 12][bar - 1]}px` }}
              />
            ))}
          </span>
        )}
        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${colors.bg} ${colors.text}`}>
          {pct}%
        </span>
        {showLabel && (
          <span className={`text-[10px] font-medium ${colors.text}`}>{label}</span>
        )}
      </span>
    );
  }

  // ── Medium (card) ─────────────────────────────────────────────────
  if (size === "md") {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        {/* Bar cluster */}
        <div className="flex items-end gap-[3px]">
          {[1, 2, 3, 4, 5].map((bar) => (
            <span
              key={bar}
              className={`w-[5px] rounded-t-sm transition-all duration-500 ${
                bar <= Math.ceil(pct / 20) ? colors.bar : "bg-gray-200"
              }`}
              style={{ height: `${[6, 9, 12, 15, 18][bar - 1]}px` }}
            />
          ))}
        </div>
        {/* Percentage + label */}
        <div className="flex items-center gap-1.5">
          <span className={`text-xs font-bold ${colors.text}`}>{pct}%</span>
          <span className={`text-[10px] font-medium ${colors.text} opacity-80`}>{label}</span>
        </div>
      </div>
    );
  }

  // ── Large (detail panel) ──────────────────────────────────────────
  return (
    <div className={`${colors.bg} rounded-xl border ${colors.ring} p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-xs font-semibold ${colors.text} uppercase tracking-wider`}>Relevance</span>
        <span className={`text-2xl font-black ${colors.text}`}>{pct}%</span>
      </div>
      {showBar && (
        <div className={`w-full h-2 ${colors.barBg} rounded-full overflow-hidden`}>
          <div
            className={`h-full rounded-full ${colors.bar} transition-all duration-700 ease-out`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      {showLabel && (
        <p className={`mt-1.5 text-xs font-medium ${colors.text}`}>{label} match</p>
      )}
    </div>
  );
}
