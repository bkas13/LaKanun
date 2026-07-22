"use client";
import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { api, ApiError } from "@/lib/api";
import RelevanceBadge from "@/components/RelevanceBadge";

interface Precedent {
  id?: string;
  title: string;
  article_number: string;
  source_document: string;
  country: string;
  category: string;
  relevance_score: number;
  excerpt: string;
}

interface CrossCountryMatch {
  id?: string;
  title: string;
  country: string;
  article_number: string;
  relevance_score: number;
}

interface PrecedentResult {
  query: string;
  precedents: Precedent[];
  cross_country_matches: CrossCountryMatch[];
  legal_principles: string[];
}

const EXAMPLES: Array<{ en: string; ne: string; hi: string }> = [
  { en: "Property inheritance dispute", ne: "सम्पत्ति उत्तराधिकार विवाद", hi: "संपत्ति विरासत विवाद" },
  { en: "Wrongful termination from job", ne: "रोजगारबाट गलत समाप्ति", hi: "नौकरी से गलत समाप्ति" },
  { en: "Consumer fraud complaint", ne: "उपभोक्ता धोका शिकायत", hi: "उपभोक्ता धोखा शिकायत" },
  { en: "Contract breach remedies", ne: "अनुबन्ध उल्लंघन उपाय", hi: "अनुबंध उल्लंघन उपाय" },
  { en: "Criminal liability defenses", ne: "फौजदारी दायित्व बचाव", hi: "आपराधिक दायित्व बचाव" },
  { en: "Labor rights violation", ne: "श्रमिक अधिकार उल्लंघन", hi: "श्रमिक अधिकार उल्लंघन" },
];

export default function PrecedentFinderPage() {
  const { user } = useAuth();
  const { t, locale } = useI18n();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PrecedentResult | null>(null);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});
  const [showPrinciples, setShowPrinciples] = useState(true);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data: PrecedentResult = await api("/api/v1/ai/find-precedent", {
        method: "POST",
        body: {
          query: query.trim(),
          country: country || undefined,
          max_results: 20,
        },
      });
      setResults(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 401) { router.push("/login"); return; }
      setError(err instanceof ApiError ? (err.data as any)?.detail || err.message : err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  }, [query, country, router]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const handleExampleClick = (ex: { en: string; ne: string; hi: string }) => {
    setQuery(ex[locale as keyof typeof ex] || ex.en);
    inputRef.current?.focus();
  };

  const handlePrecedentClick = (p: Precedent) => {
    const q = p.title || p.article_number;
    const url = `/laws?q=${encodeURIComponent(q)}${p.id ? `&resultId=${p.id}` : ""}`;
    router.push(url);
  };

  const toggleExpand = (i: number) => {
    setExpanded(prev => ({ ...prev, [i]: !prev[i] }));
  };

  const nepalCount = results?.cross_country_matches.filter(m => m.country === "nepal").length || 0;
  const indiaCount = results?.cross_country_matches.filter(m => m.country === "india").length || 0;
  const categories = [...new Set(results?.precedents.map(p => p.category).filter(Boolean))];
  const topCategory = categories[0] || "";

  if (user?.role !== "lawyer" && user?.role !== "judge") {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="text-4xl mb-4">🔒</div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">{t.ai_tools?.locked_title || "Access Restricted"}</h1>
        <p className="text-sm text-gray-500">{t.ai_tools?.locked_desc || "This feature is available to lawyers and judges only."}</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 text-white rounded-xl p-6 sm:p-8 mb-6">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-48 h-48 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-purple-300 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold">{t.ai_tools?.precedent?.title || "Precedent Finder"}</h1>
          </div>
          <p className="text-purple-100 text-sm max-w-xl">{t.ai_tools?.precedent?.description || "Find similar legal precedents and cross-country matches"}</p>
        </div>
      </div>

      {/* Examples */}
      <div className="mb-4">
        <div className="text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-2">
          {t.ai_tools?.precedent?.examples_title || "Try these searches"}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => handleExampleClick(ex)}
              className="text-[11px] px-2.5 py-1 rounded-full border border-purple-200 text-purple-700 bg-white hover:bg-purple-50 hover:border-purple-300 transition-colors cursor-pointer"
            >
              {ex[locale as keyof typeof ex] || ex.en}
            </button>
          ))}
        </div>
      </div>

      {/* Search form */}
      <div className="bg-white rounded-xl border border-purple-100 shadow-sm p-4 mb-4">
        <textarea
          ref={inputRef}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t.ai_tools?.precedent?.query_placeholder || "Describe the legal question or case to find similar precedents..."}
          className="w-full h-28 text-sm border border-purple-200 rounded-lg p-3 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100 resize-none"
        />
        <div className="flex items-center gap-2 mt-3">
          <select
            value={country}
            onChange={e => setCountry(e.target.value)}
            className="text-xs border border-purple-200 rounded-lg px-3 py-2 focus:outline-none focus:border-purple-400 text-gray-700"
          >
            <option value="">{t.ai_tools?.precedent?.country || "Country (Optional)"}</option>
            <option value="nepal">🇳🇵 Nepal</option>
            <option value="india">🇮🇳 India</option>
          </select>
          <div className="flex-1" />
          <span className="text-[10px] text-gray-400 hidden sm:block">{t.ai_tools?.precedent?.search_tip || "Be specific for better results"}</span>
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 disabled:opacity-40 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all shadow-sm cursor-pointer"
          >
            {loading ? `⏳ ${t.ai_tools?.precedent?.searching || "Searching..."}` : `🔍 ${t.ai_tools?.precedent?.find || "Find Precedents"}`}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 mb-4">{error}</div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center gap-3 py-12">
          <div className="w-10 h-10 border-3 border-purple-200 border-t-purple-600 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">{t.ai_tools?.precedent?.searching || "Searching across legal databases..."}</p>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="space-y-4">
          {/* Summary bar */}
          <div className="flex flex-wrap items-center gap-3 bg-white rounded-lg border border-purple-100 px-4 py-2.5">
            <span className="text-sm font-semibold text-purple-700">
              {t.ai_tools?.precedent?.results_summary?.replace("{{count}}", String(results.precedents.length)) || `${results.precedents.length} precedents found`}
            </span>
            {categories.length > 0 && (
              <span className="text-[11px] text-gray-500">
                {t.ai_tools?.precedent?.areas_summary?.replace("{{areas}}", String(categories.length)) || `across ${categories.length} legal areas`}
              </span>
            )}
            {nepalCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-50 text-red-600 font-medium">
                🇳🇵 {t.ai_tools?.precedent?.nepal_count?.replace("{{count}}", String(nepalCount)) || `${nepalCount} Nepal`}
              </span>
            )}
            {indiaCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 font-medium">
                🇮🇳 {t.ai_tools?.precedent?.india_count?.replace("{{count}}", String(indiaCount)) || `${indiaCount} India`}
              </span>
            )}
            {topCategory && (
              <span className="text-[11px] text-gray-400">
                {t.ai_tools?.precedent?.top_category?.replace("{{category}}", topCategory) || `Most relevant: ${topCategory}`}
              </span>
            )}
          </div>

          {/* No results */}
          {results.precedents.length === 0 && (
            <div className="text-center py-8">
              <div className="text-3xl mb-2">📭</div>
              <p className="text-sm text-gray-500">{t.ai_tools?.precedent?.no_results || "No precedents found. Try a different query."}</p>
            </div>
          )}

          {/* Precedent cards */}
          {results.precedents.map((p, i) => {
            return (
              <button
                key={i}
                onClick={() => handlePrecedentClick(p)}
                className="w-full text-left bg-white rounded-xl border border-purple-100 hover:border-purple-300 hover:shadow-md transition-all p-4 group cursor-pointer"
              >
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-100 to-violet-100 flex items-center justify-center shrink-0">
                    <span className="text-xs font-bold text-purple-600">{p.country === "nepal" ? "NP" : p.country === "india" ? "IN" : p.article_number?.slice(0, 3) || "•"}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {p.category && <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 font-medium">{p.category}</span>}
                      <RelevanceBadge score={p.relevance_score} size="sm" />
                      <div className="flex-1" />
                      <span className="text-[10px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                        {t.ai_tools?.precedent?.view_details || "View full details"} →
                      </span>
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 group-hover:text-purple-700 transition-colors leading-snug">
                      {p.title || "Untitled"}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      {p.article_number && (
                        <span className="text-[10px] text-gray-500">
                          {t.ai_tools?.precedent?.article || "Art."} {p.article_number}
                        </span>
                      )}
                      {p.source_document && (
                        <span className="text-[10px] text-gray-400">
                          {t.ai_tools?.precedent?.source || "Source"}: {p.source_document}
                        </span>
                      )}
                    </div>
                    {p.excerpt && (
                      <p className="text-xs text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">{p.excerpt}</p>
                    )}
                  </div>
                </div>
              </button>
            );
          })}

          {/* Legal Principles */}
          {results.legal_principles.length > 0 && (
            <div className="bg-white rounded-xl border border-purple-100 overflow-hidden">
              <button
                onClick={() => setShowPrinciples(!showPrinciples)}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm font-semibold text-purple-700 hover:bg-purple-50 transition-colors cursor-pointer"
              >
                <span className={`transition-transform text-xs ${showPrinciples ? "rotate-90" : ""}`}>▶</span>
                {t.ai_tools?.precedent?.principles || "Legal Principles Identified"}
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-purple-100 text-purple-600">{results.legal_principles.length}</span>
              </button>
              {showPrinciples && (
                <div className="px-4 pb-3 grid sm:grid-cols-2 gap-1.5">
                  {results.legal_principles.map((pr, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-400 shrink-0 mt-1" />
                      {pr}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Cross-Country Comparison */}
          {results.cross_country_matches.length > 0 && (
            <div className="bg-white rounded-xl border border-purple-100 p-4">
              <h3 className="text-sm font-semibold text-purple-700 mb-3">
                🌐 {t.ai_tools?.precedent?.cross_country || "Cross-Country Comparison"}
              </h3>
              <div className="grid sm:grid-cols-2 gap-3">
                {["nepal", "india"].map(countryKey => {
                  const matches = results.cross_country_matches.filter(m => m.country === countryKey);
                  if (matches.length === 0) return null;
                  return (
                    <div key={countryKey} className="rounded-lg border border-purple-50 p-3">
                      <div className="text-xs font-semibold text-gray-700 mb-2">
                        {countryKey === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                      </div>
                      <div className="space-y-1.5">
                        {matches.map((m, i) => (
                          <button
                            key={i}
                            onClick={() => {
                              const url = `/laws?q=${encodeURIComponent(m.title)}${m.id ? `&resultId=${m.id}` : ""}`;
                              router.push(url);
                            }}
                            className="w-full text-left text-xs text-gray-600 hover:text-purple-700 hover:bg-purple-50 rounded p-1.5 transition-colors cursor-pointer flex items-center gap-1.5"
                          >
                            <span className="w-1 h-1 rounded-full bg-purple-300 shrink-0" />
                            <span className="truncate flex-1">{m.title}</span>
                            <span className="text-[10px] text-gray-400 shrink-0">Art. {m.article_number}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}