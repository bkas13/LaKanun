"use client";

import { useState, useRef, useEffect } from "react";
import { useI18n, type Country } from "@/contexts/I18nContext";

const COUNTRIES: {
  value: Country;
  labelKey: string;
  shortLabelKey: string;
  flag: string;
  color: string;
  ringColor: string;
}[] = [
  { value: "all", labelKey: "country_switcher.all_laws", shortLabelKey: "country_switcher.all_laws_short", flag: "🌐", color: "bg-slate-100 text-slate-700 border-slate-300", ringColor: "ring-slate-400" },
  { value: "nepal", labelKey: "country_switcher.nepal_laws", shortLabelKey: "country_switcher.nepal_short", flag: "🇳🇵", color: "bg-red-50 text-red-700 border-red-300", ringColor: "ring-red-400" },
  { value: "india", labelKey: "country_switcher.india_laws", shortLabelKey: "country_switcher.india_short", flag: "🇮🇳", color: "bg-orange-50 text-orange-700 border-orange-300", ringColor: "ring-orange-400" },
];

export default function CountrySwitcher() {
  const { country, setCountry, translate } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selected = COUNTRIES.find((c) => c.value === country) || COUNTRIES[0];

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-all duration-200 ${selected.color} ${open ? "ring-2 ring-offset-2" : "hover:border-gray-300"} ${selected.ringColor}`}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span className="text-sm">{selected.flag}</span>
        <span className="text-[11px] font-medium hidden sm:inline">{translate(selected.shortLabelKey)}</span>
        <svg className={`w-3 h-3 transition-transform ${open ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 mt-1.5 w-40 bg-white rounded-xl shadow-lg border border-gray-200 py-1.5 z-50 animate-in fade-in-0 zoom-in-95 duration-150">
          <div className="px-3 py-1.5 text-[10px] font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-100">
            {translate("country_switcher.select_country")}
          </div>
          {COUNTRIES.map((c) => (
            <button
              key={c.value}
              onClick={() => { setCountry(c.value); setOpen(false); }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors ${
                country === c.value
                  ? `${c.color} font-semibold`
                  : "text-gray-700 hover:bg-gray-50"
              }`}
              role="option"
              aria-selected={country === c.value}
            >
              <span className="text-base">{c.flag}</span>
              <span className="font-medium">{translate(c.labelKey)}</span>
              {country === c.value && (
                <svg className="ml-auto w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}