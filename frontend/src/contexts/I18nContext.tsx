"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import en from "@/i18n/en.json";
import ne from "@/i18n/ne.json";
import hi from "@/i18n/hi.json";

type Locale = "en" | "ne" | "hi";
type Country = "all" | "nepal" | "india";

const dictionaries: Record<Locale, typeof en> = { en, ne, hi };

function getNestedValue(obj: any, path: string): string {
  if (!path) return "";
  const keys = path.split(".");
  let current = obj;
  for (const key of keys) {
    if (current === undefined || current === null) return path;
    const match = key.match(/^(.+)\[(\d+)\]$/);
    if (match) {
      current = current?.[match[1]]?.[parseInt(match[2])];
    } else {
      current = current?.[key];
    }
  }
  return current ?? path;
}

interface I18nContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: typeof en;
  translate: (path: string) => string;
  dir: "ltr" | "rtl";
  country: Country;
  setCountry: (c: Country) => void;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

const VALID_LOCALES: Locale[] = ["en", "ne", "hi"];
const VALID_COUNTRIES: Country[] = ["all", "nepal", "india"];

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [country, setCountryState] = useState<Country>("all");
  const [hydrated, setHydrated] = useState(false);

  // Read localStorage after hydration — single useEffect, runs once
  useEffect(() => {
    try {
      const storedLocale = localStorage.getItem("locale") as Locale | null;
      if (storedLocale && VALID_LOCALES.includes(storedLocale)) {
        setLocaleState(storedLocale);
        document.documentElement.lang = storedLocale;
      }
      const storedCountry = localStorage.getItem("country") as Country | null;
      if (storedCountry && VALID_COUNTRIES.includes(storedCountry)) {
        setCountryState(storedCountry);
        setHydrated(true);
        return;
      }
      // No stored country — detect from IP geolocation
      fetch("https://ipapi.co/json/", { signal: AbortSignal.timeout(3000) })
        .then(res => res.json())
        .then(data => {
          const cc = (data?.country_code || "").toUpperCase();
          if (cc === "NP") {
            setCountryState("nepal");
            localStorage.setItem("country", "nepal");
          } else if (cc === "IN") {
            setCountryState("india");
            localStorage.setItem("country", "india");
          }
          // else keep "all" default
        })
        .catch(() => {}) // silently fail — keep "all"
        .finally(() => setHydrated(true));
    } catch {
      setHydrated(true);
    }
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("locale", l);
    document.documentElement.lang = l;
  }, []);

  const setCountry = useCallback((c: Country) => {
    setCountryState(c);
    localStorage.setItem("country", c);
  }, []);

  const dict = useMemo(() => dictionaries[locale], [locale]);
  const translate = useCallback(
    (path: string) => getNestedValue(dict, path),
    [dict]
  );

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      t: dict,
      translate,
      dir: "ltr" as const,
      country,
      setCountry,
    }),
    [locale, setLocale, dict, translate, country, setCountry],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}

export type { Locale, Country };
export const LOCALES: { value: Locale; label: string; flag: string }[] = [
  { value: "en", label: "English", flag: "🌐" },
  { value: "ne", label: "नेपाली", flag: "🇳🇵" },
  { value: "hi", label: "हिन्दी", flag: "🇮🇳" },
];