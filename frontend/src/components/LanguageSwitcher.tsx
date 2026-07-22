"use client";

import { useI18n, type Locale } from "@/contexts/I18nContext";

const LANGUAGES: {
  value: Locale;
  labelKey: string;
  short: string;
}[] = [
  { value: "en", labelKey: "language_switcher.english", short: "EN" },
  { value: "ne", labelKey: "language_switcher.nepali_short", short: "NE" },
  { value: "hi", labelKey: "language_switcher.hindi_short", short: "HI" },
];

interface LanguageSwitcherProps {
  variant?: "dark" | "light";
}

export default function LanguageSwitcher({ variant = "dark" }: LanguageSwitcherProps) {
  const { locale, setLocale, translate } = useI18n();

  const baseClasses = "px-2 py-1 rounded-md text-[11px] font-semibold transition-all duration-200";
  const darkActive = "bg-white text-gray-800 shadow-sm";
  const darkInactive = "text-white/70 hover:text-white hover:bg-white/15";
  const lightActive = "bg-cyan-600 text-white shadow-sm";
  const lightInactive = "text-gray-600 hover:text-gray-900 hover:bg-gray-100";

  return (
    <div className={`flex items-center gap-0.5 rounded-lg p-0.5 ${variant === "dark" ? "bg-white/10" : "bg-gray-100"}`}>
      {LANGUAGES.map((l) => {
        const active = locale === l.value;
        return (
          <button
            key={l.value}
            onClick={() => setLocale(l.value)}
            className={`${baseClasses} ${active ? (variant === "dark" ? darkActive : lightActive) : (variant === "dark" ? darkInactive : lightInactive)}`}
            title={translate(l.labelKey)}
          >
            {l.short}
          </button>
        );
      })}
    </div>
  );
}