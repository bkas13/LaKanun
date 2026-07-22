"use client";

import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";
import RelevanceBadge from "./RelevanceBadge";

interface SearchResult {
  id: string;
  title: string;
  full_text: string;
  country: string;
  category: string;
  document_type: string;
  article_number: string;
  source_document: string;
  score: number;
  enactment_year: number;
  language?: string;
  confidence?: string;
  citation?: string;
  last_verified?: string;
  source_url?: string;
  effective_date?: string;
}

interface PopularLaw {
  id: string;
  title: string;
  full_text: string;
  category: string;
  country: string;
  article_number?: string;
  source_document?: string;
  score?: number;
  view_count?: number;
}

interface IssueResult {
  identified: boolean;
  issue_id?: string;
  title?: string;
  provisions?: { country: string; articles: { id: string; title: string; article_number: string; source_document: string }[] }[];
  guidance?: string;
}

const CAT_COLORS: Record<string, string> = {
  criminal: "bg-red-50 text-red-600 border-red-100",
  civil: "bg-blue-50 text-blue-600 border-blue-100",
  constitutional: "bg-violet-50 text-violet-600 border-violet-100",
  labor: "bg-amber-50 text-amber-600 border-amber-100",
  family: "bg-pink-50 text-pink-600 border-pink-100",
  commercial: "bg-emerald-50 text-emerald-600 border-emerald-100",
  property_law: "bg-orange-50 text-orange-600 border-orange-100",
};

const CAT_LABELS: Record<string, { en: string; ne: string; hi: string }> = {
  criminal: { en: "Criminal", ne: "फौजदारी", hi: "आपराधिक" },
  civil: { en: "Civil", ne: "दीवानी", hi: "दीवानी" },
  civil_procedure_general: { en: "Civil Procedure", ne: "दीवानी प्रक्रिया", hi: "दीवानी प्रक्रिया" },
  constitutional: { en: "Constitutional", ne: "संवैधानिक", hi: "संवैधानिक" },
  labor: { en: "Labor", ne: "श्रम", hi: "श्रम" },
  family: { en: "Family", ne: "पारिवारिक", hi: "पारिवारिक" },
  commercial: { en: "Commercial", ne: "व्यापारिक", hi: "व्यापारिक" },
  property_law: { en: "Property", ne: "सम्पत्ति", hi: "संपत्ति" },
  consumer_protection_general: { en: "Consumer", ne: "उपभोक्ता", hi: "उपभोक्ता" },
};

function getSourceName(key: string): string {
  const map: Record<string, string> = {
    constitution_of_nepal_2072: "Constitution of Nepal 2072",
    nepal_civil_code: "Nepal Civil Code",
    nepal_civil_procedure: "Nepal Civil Procedure",
    nepal_penal_code: "Nepal Penal Code",
    nepal_criminal_procedure: "Nepal Criminal Procedure",
    nepal_labor_act: "Nepal Labor Act",
    nepal_electronic_transactions: "Electronic Transactions Act",
    nepal_right_to_information: "Right to Information Act",
    constitution_of_india: "Constitution of India 1950",
    indian_penal_code: "Indian Penal Code 1860",
    code_of_criminal_procedure: "Code of Criminal Procedure 1973",
    code_of_civil_procedure: "Code of Civil Procedure 1908",
    indian_contract_act: "Indian Contract Act 1872",
    minimum_wages_act: "Minimum Wages Act 1948",
  };
  return map[key] || key.replace(/_/g, " ");
}

type SearchMode = "laws" | "issues";

interface SearchModalProps {
  open: boolean;
  onClose: () => void;
  initialQuery?: string;
  initialMode?: SearchMode;
}

export default function SearchModal({ open, onClose, initialQuery = "", initialMode = "laws" }: SearchModalProps) {
  const { translate, locale, country, setCountry } = useI18n();
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [mode, setMode] = useState<SearchMode>(initialMode);
  const [popularLaws, setPopularLaws] = useState<PopularLaw[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [issueResult, setIssueResult] = useState<IssueResult | null>(null);
  const [searchingIssues, setSearchingIssues] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const queryRef = useRef(query);
  const abortRef = useRef<AbortController | null>(null);

  // Keep queryRef in sync
  useEffect(() => { queryRef.current = query; }, [query]);

  useEffect(() => {
    if (open) {
      setQuery(initialQuery);
      setMode(initialMode);
      setSearchResults([]);
      setIssueResult(null);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open, initialQuery, initialMode]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (!open) return;
    document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const loadPopular = useCallback(async () => {
    try {
      const params = new URLSearchParams({ limit: "12" });
      if (country && country !== "all") params.set("country", country);
      const data = await api<any>(`/api/v1/laws/popular?${params}`, { noAuth: true });
      setPopularLaws(data.results || data || []);
    } catch { setPopularLaws([]); } finally { setLoading(false); }
  }, [country]);

  useEffect(() => { if (open && !query.trim()) loadPopular(); }, [open, loadPopular, query]);

  // Abort previous request when query changes
  useEffect(() => {
    return () => { abortRef.current?.abort(); };
  }, []);

  const executeLawSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setSearchResults([]); return; }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setSearching(true);
    setIssueResult(null);
    try {
      const params = new URLSearchParams({ q: q.trim(), top_k: "20" });
      if (country && country !== "all") params.set("country", country);
      const data = await api<any>(`/api/v1/laws/search?${params}`, { noAuth: true, signal: controller.signal });
      setSearchResults(data.results || []);
    } catch { if (!controller.signal.aborted) setSearchResults([]); } finally { if (!controller.signal.aborted) setSearching(false); }
  }, [country]);

  const executeIssueSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setIssueResult(null); return; }
    setSearchingIssues(true);
    setSearchResults([]);
    try {
      const params = new URLSearchParams({ q: q.trim() });
      if (country && country !== "all") params.set("country", country);
      params.set("lang", locale);
      const data = await api<any>(`/api/v1/issues/find?${params}`, { noAuth: true });
      setIssueResult({
        identified: data.issue_identified,
        issue_id: data.issue_id,
        title: data.title,
        provisions: data.provisions,
        guidance: data.guidance,
      });
      setSearchResults(data.search_results || []);
    } catch { setIssueResult(null); setSearchResults([]); } finally { setSearchingIssues(false); }
  }, [country, locale]);

  // Debounced live search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const trimmed = query.trim();
    if (!trimmed) {
      setSearchResults([]);
      setIssueResult(null);
      if (mode === "laws") loadPopular();
      return;
    }
    debounceRef.current = setTimeout(() => {
      if (mode === "issues") {
        executeIssueSearch(trimmed);
      } else {
        executeLawSearch(trimmed);
      }
    }, 350);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query, mode, executeLawSearch, executeIssueSearch, loadPopular]);

  // Enter key navigates to the results page
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && query.trim()) {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      const params = new URLSearchParams({ q: query.trim() });
      if (country && country !== "all") params.set("country", country);
      if (mode === "issues") {
        router.push(`/issues?${params}`);
      } else {
        router.push(`/laws?${params}`);
      }
      onClose();
    }
  };

  const handleResultClick = (r: SearchResult) => {
    const params = new URLSearchParams({ q: query.trim(), resultId: r.id });
    if (country && country !== "all") params.set("country", country);
    if (mode === "issues") {
      router.push(`/issues?${params}`);
    } else {
      router.push(`/laws?${params}`);
    }
    onClose();
  };

  const handleViewAllResults = () => {
    if (!query.trim()) return;
    const params = new URLSearchParams({ q: query.trim() });
    if (country && country !== "all") params.set("country", country);
    if (mode === "issues") {
      router.push(`/issues?${params}`);
    } else {
      router.push(`/laws?${params}`);
    }
    onClose();
  };

  const handleProvisionClick = (article: { id: string; title: string }) => {
    const params = new URLSearchParams({ q: article.title, resultId: article.id });
    if (country && country !== "all") params.set("country", country);
    router.push(`/laws?${params}`);
    onClose();
  };

  if (!open) return null;

  const QUICK_TOPICS = ["property", "family", "labor", "criminal", "environment", "business", "constitutional", "contracts"];
  const QUICK_ISSUES = ["encroachment", "unpaid_wages", "domestic_violence", "wrongful_termination", "property_dispute", "consumer_complaint", "divorce", "arrest_rights"];
  const activeTopics = mode === "issues" ? QUICK_ISSUES : QUICK_TOPICS;
  const topicPrefix = mode === "issues" ? "quick_issues" : "quick_topics";
  const isSearching = mode === "issues" ? searchingIssues : searching;
  const hasResults = searchResults.length > 0 || (issueResult?.identified);
  const hasQuery = query.trim().length > 0;

  return (
    <div className="fixed inset-0 z-[80] flex items-start justify-center pt-[5vh] px-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />

      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden">
        {/* Header: mode toggle + search input */}
        <div className={`px-5 py-4 transition-colors duration-300 shrink-0 ${
          mode === "issues"
            ? "bg-gradient-to-br from-red-600 via-red-700 to-rose-800"
            : "bg-gradient-to-br from-cyan-700 to-cyan-800"
        }`}>
          {/* Mode toggle */}
          <div className="flex items-center gap-1 mb-3 bg-white/10 rounded-lg p-0.5 w-fit">
            <button
              onClick={() => { setMode("laws"); setSearchResults([]); setIssueResult(null); }}
              className={`px-3.5 py-1.5 rounded-md text-[11px] font-semibold transition-all ${
                mode === "laws"
                  ? "bg-white text-cyan-700 shadow-sm"
                  : "text-white/60 hover:text-white/90 hover:bg-white/5"
              }`}
            >
              <span className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                {translate("search.mode_laws")}
              </span>
            </button>
            <button
              onClick={() => { setMode("issues"); setSearchResults([]); setIssueResult(null); }}
              className={`px-3.5 py-1.5 rounded-md text-[11px] font-semibold transition-all ${
                mode === "issues"
                  ? "bg-white text-red-600 shadow-sm"
                  : "text-white/60 hover:text-white/90 hover:bg-white/5"
              }`}
            >
              <span className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                {translate("search.mode_issues")}
              </span>
            </button>
          </div>

          {/* Search input */}
          <div className="flex items-center gap-3">
            {isSearching ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0" />
            ) : (
              <svg className="w-5 h-5 text-white/50 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            )}
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={mode === "issues" ? translate("search.issues_placeholder") : translate("search.placeholder")}
              className="flex-1 bg-transparent text-white placeholder-white/40 text-sm outline-none"
            />
            {query && (
              <button onClick={() => { setQuery(""); setSearchResults([]); setIssueResult(null); }} className="text-white/40 hover:text-white/70 transition-colors shrink-0" aria-label="Clear">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            <button onClick={onClose} className="text-white/50 hover:text-white transition-colors shrink-0" aria-label="Close">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Quick topics — changes per mode */}
          {!hasQuery && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {activeTopics.map((k) => (
                <button
                  key={`qt-${mode}-${k}`}
                  onClick={() => setQuery(translate(`${topicPrefix}.${k}`))}
                  className="text-[10px] px-2.5 py-1 rounded-full bg-white/10 text-white/70 hover:bg-white/20 transition-colors"
                >
                  {translate(`${topicPrefix}.${k}`)}
                </button>
              ))}
            </div>
          )}

          {/* Filters row */}
          <div className="flex items-center gap-2 mt-3">
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value as any)}
              className="text-[10px] px-2 py-1 rounded-lg bg-white/10 border border-white/20 text-white focus:ring-2 focus:ring-white/40 outline-none [&>option]:text-gray-800 [&>option]:bg-white"
            >
              <option value="all">{translate("homepage.country_all")}</option>
              <option value="nepal">{translate("homepage.country_nepal")}</option>
              <option value="india">{translate("homepage.country_india")}</option>
            </select>
            <button onClick={() => { setCountry("all"); setQuery(""); }} className="text-[10px] text-white/50 hover:text-white underline">
              {translate("homepage.clear_filters")}
            </button>
          </div>
        </div>

        {/* Scrollable results area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          {/* Loading skeleton */}
          {isSearching && (
            <div className="px-5 py-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={`skel-${i}`} className="bg-gray-50 rounded-2xl border border-gray-100 p-4 animate-pulse">
                  <div className="flex items-center gap-1.5 mb-2">
                    <div className="h-5 w-16 bg-gray-200 rounded-full" />
                    <div className="h-5 w-12 bg-gray-100 rounded-full" />
                  </div>
                  <div className="h-4 w-3/4 bg-gray-200 rounded mb-2" />
                  <div className="h-3 w-full bg-gray-100 rounded" />
                </div>
              ))}
            </div>
          )}

          {/* Issue guidance banner */}
          {!isSearching && issueResult?.identified && issueResult.guidance && (
            <div className="mx-5 mt-4 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-7 h-7 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </span>
                <h3 className="font-semibold text-sm text-red-800">{issueResult.title}</h3>
              </div>
              <p className="text-[11px] text-red-700/80 leading-relaxed">{issueResult.guidance}</p>
              {issueResult.provisions && issueResult.provisions.length > 0 && (
                <div className="mt-3 space-y-2">
                  {issueResult.provisions.map((prov) => (
                    <div key={prov.country} className="flex items-start gap-2">
                      <span className="text-xs font-semibold text-red-600 shrink-0 mt-0.5">
                        {prov.country === "nepal" ? "🇳🇵" : "🇮🇳"} {prov.country === "nepal" ? "Nepal" : "India"}:
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {prov.articles.slice(0, 3).map((a) => (
                          <button
                            key={a.id}
                            onClick={() => handleProvisionClick(a)}
                            className="text-[10px] px-2 py-0.5 bg-white rounded-full border border-red-200 text-red-700 hover:bg-red-100 hover:border-red-300 transition-colors cursor-pointer"
                          >
                            {a.title}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Search results */}
          {!isSearching && searchResults.length > 0 && (
            <div className="px-5 py-4 space-y-2">
              <p className="text-xs text-gray-400 font-medium">{searchResults.length} {translate("search.results_found")}</p>
              {searchResults.map((r) => {
                const catColor = CAT_COLORS[r.category] || "bg-gray-50 text-gray-600 border-gray-100";
                return (
                  <button
                    key={`sr-${r.id}`}
                    onClick={() => handleResultClick(r)}
                    className="w-full text-left bg-white rounded-2xl border border-gray-100 p-4 hover:shadow-md hover:border-cyan-200 active:scale-[0.99] transition-all duration-150 group"
                  >
                    <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                        {CAT_LABELS[r.category]?.[locale as "en" | "ne" | "hi"] || r.category}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                        {r.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                      </span>
                      {r.article_number && (
                        <span className="text-[10px] text-gray-400 font-mono">Art. {r.article_number}</span>
                      )}
                      <span className="ml-auto">
                        <RelevanceBadge score={r.score} size="sm" />
                      </span>
                    </div>
                    <h3 className="font-semibold text-sm text-gray-900 group-hover:text-cyan-700 transition-colors">{r.title}</h3>
                    <p className="text-[11px] text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">{r.full_text}</p>
                    <div className="flex items-center justify-between mt-2">
                      <p className="text-[10px] text-gray-400">
                        {getSourceName(r.source_document)}
                        {r.enactment_year > 0 && <span className="ml-1 text-cyan-500 font-medium">({r.enactment_year})</span>}
                      </p>
                      <span className="text-[9px] text-cyan-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                        View details
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Popular Laws (when idle in laws mode) */}
          {mode === "laws" && !isSearching && searchResults.length === 0 && !loading && popularLaws.length > 0 && (
            <div className="px-5 py-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-gray-500 font-medium">{translate("laws.popular")}</p>
                <Link href="/laws" onClick={onClose} className="text-[10px] text-cyan-600 hover:text-cyan-700 font-medium">{translate("nav.browse_laws")} →</Link>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {popularLaws.slice(0, 8).map((law, idx) => {
                  const catColor = CAT_COLORS[law.category] || "bg-gray-50 text-gray-600 border-gray-100";
                  const isTop3 = idx < 3;
                  return (
                    <button
                      key={`pop-${law.id}-${idx}`}
                      onClick={() => handleResultClick(law as SearchResult)}
                      className={`w-full text-left rounded-2xl border p-4 transition-all duration-200 group ${
                        isTop3
                          ? "bg-gradient-to-br from-cyan-50 to-white border-cyan-100 hover:shadow-md hover:border-cyan-300"
                          : "bg-white border-gray-100 hover:shadow-md hover:border-cyan-200"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                          idx === 0 ? "bg-cyan-600 text-white" :
                          idx === 1 ? "bg-cyan-500 text-white" :
                          idx === 2 ? "bg-cyan-400 text-white" :
                          "bg-gray-100 text-gray-500"
                        }`}>
                          {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                              {CAT_LABELS[law.category]?.[locale as "en" | "ne" | "hi"] || law.category}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                              {law.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                            </span>
                          </div>
                          <h3 className="font-semibold text-sm text-gray-900 group-hover:text-cyan-700 transition-colors leading-snug">{law.title}</h3>
                          {law.source_document && (
                            <p className="text-[10px] text-gray-400 mt-1.5">{getSourceName(law.source_document)}</p>
                          )}
                        </div>
                        <svg className="w-4 h-4 text-gray-300 group-hover:text-cyan-500 shrink-0 mt-1 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Issues idle state */}
          {mode === "issues" && !isSearching && searchResults.length === 0 && !issueResult && (
            <div className="py-8 px-5">
              <div className="text-center mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-red-500 to-rose-600 flex items-center justify-center mx-auto mb-3 shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-gray-700 mb-1">{translate("search.issues_hint")}</p>
                <p className="text-xs text-gray-400 max-w-xs mx-auto">{translate("search.issues_hint_desc")}</p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {QUICK_ISSUES.map((k) => (
                  <button
                    key={`issue-prompt-${k}`}
                    onClick={() => setQuery(translate(`quick_issues.${k}`))}
                    className="text-left p-3 rounded-xl border border-gray-100 bg-white hover:bg-red-50 hover:border-red-200 transition-all group"
                  >
                    <p className="text-[11px] font-medium text-gray-700 group-hover:text-red-700 transition-colors leading-snug">{translate(`quick_issues.${k}`)}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Empty state */}
          {!loading && !isSearching && popularLaws.length === 0 && searchResults.length === 0 && !issueResult && (
            <div className="text-center py-10 px-5">
              <div className="w-14 h-14 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-3">
                <svg className="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-700 mb-1">{translate("search.placeholder")}</p>
              <p className="text-xs text-gray-400">{translate("cta.desc")}</p>
            </div>
          )}
        </div>

        {/* Sticky footer: View all results */}
        {hasQuery && !isSearching && (
          <div className={`shrink-0 border-t px-5 py-3 transition-colors duration-300 ${
            mode === "issues"
              ? "bg-gradient-to-r from-red-50 to-orange-50 border-red-100"
              : "bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-100"
          }`}>
            <button
              onClick={handleViewAllResults}
              className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-sm hover:shadow-md ${
                mode === "issues"
                  ? "bg-red-600 text-white hover:bg-red-700"
                  : "bg-cyan-600 text-white hover:bg-cyan-700"
              }`}
            >
              {hasResults ? (
                <>
                  {translate("search.view_all_results")}
                  <span className="text-xs opacity-80">({searchResults.length} {translate("search.results_found").split(" ")[0]})</span>
                </>
              ) : (
                translate("search.view_all_results")
              )}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
            </button>
            {hasResults && (
              <p className="text-center text-[10px] text-gray-400 mt-1.5">
                {translate("search.view_all_results_hint") || "Full results with details on Browse Laws page"}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
