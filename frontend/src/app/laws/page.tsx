"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import SearchResultModal from "@/components/SearchResultModal";
import RelevanceBadge from "@/components/RelevanceBadge";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";

interface LawDoc {
  id: string;
  title: string;
  category: string;
  country: string;
  article_number?: string;
  source_document?: string;
  full_text?: string;
}

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

interface Category {
  name: string;
  count: number;
  countries: Record<string, number>;
}

interface PopularLaw {
  provision_id: string;
  title: string;
  country: string;
  category: string;
  view_count: number;
  article_number?: string;
  source_document?: string;
}

interface RecentLaw {
  provision_id: string;
  title: string;
  country: string;
  category: string;
  enactment_year: number;
  article_number?: string;
  source_document?: string;
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

const CAT_ICONS: Record<string, string> = {
  criminal: "⚖️",
  civil: "📋",
  civil_procedure_general: "📋",
  constitutional: "🏛️",
  labor: "👷",
  family: "👨‍👩‍👧",
  commercial: "💼",
  property_law: "🏠",
  consumer_protection_general: "🛒",
};

const DOC_NAMES: Record<string, string> = {
  constitution_of_nepal_2072: "Constitution of Nepal 2072",
  nepal_penal_code: "Nepal Penal Code 2074",
  nepal_criminal_procedure: "Criminal Procedure Code 2074",
  nepal_civil_code: "Nepal Civil Code 2074",
  nepal_civil_procedure: "Civil Procedure Code 2074",
  nepal_labor_act: "Labor Act 2074",
  nepal_domestic_violence: "Domestic Violence Act 2066",
  nepal_narcotic_drugs: "Narcotic Drugs Act 2076",
  nepal_right_to_information: "Right to Information Act 2064",
  nepal_electronic_transactions: "Electronic Transaction Act 2063",
  constitution_of_india: "Constitution of India",
  indian_penal_code: "Indian Penal Code 1860",
  code_of_criminal_procedure: "Code of Criminal Procedure 1973",
  code_of_civil_procedure: "Code of Civil Procedure 1908",
  indian_contract_act: "Indian Contract Act 1872",
  indian_evidence_act: "Indian Evidence Act 1872",
  india_consumer_protection: "Consumer Protection Act 2019",
  india_motor_vehicles: "Motor Vehicles Act 1988",
  india_domestic_violence: "Domestic Violence Act 2005",
  india_information_technology: "IT Act 2000",
  india_negotiable_instruments: "Negotiable Instruments Act 1881",
  india_juvenile_justice: "Juvenile Justice Act 2015",
  india_right_to_information: "Right to Information Act 2005",
  india_sale_of_goods: "Sale of Goods Act 1930",
  india_partnership: "Indian Partnership Act 1932",
  india_transfer_of_property: "Transfer of Property Act 1882",
  india_specific_reliefs: "Specific Relief Act 1963",
  minimum_wages_act: "Minimum Wages Act 1948",
};

function getSourceName(key?: string): string {
  if (!key) return "";
  return DOC_NAMES[key] || key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

const SAMPLE_LAW_TAGS: Record<string, { label: string; query: string }[]> = {
  en: [
    { label: "📜 Constitution of Nepal 2072", query: "Constitution of Nepal 2072" },
    { label: "⚖️ Nepal Penal Code 2074", query: "Nepal Penal Code 2074" },
    { label: "🏠 Transfer of Property", query: "Transfer of Property Act" },
    { label: "👷 Labour Act 2074", query: "Labour Act 2074" },
    { label: "🛡️ Fundamental Rights", query: "Fundamental Rights" },
    { label: "🔍 Criminal Procedure Code", query: "Criminal Procedure Code 2074" },
    { label: "📋 Nepal Civil Code 2074", query: "Nepal Civil Code 2074" },
    { label: "📄 Right to Information", query: "Right to Information Act" },
  ],
  ne: [
    { label: "📜 नेपालको संविधान २०७२", query: "नेपालको संविधान २०७२" },
    { label: "⚖️ मुलुकी अपराध संहिता २०७४", query: "मुलुकी अपराध संहिता २०७४" },
    { label: "🏠 सम्पत्ति हस्तान्तरण ऐन", query: "सम्पत्ति हस्तान्तरण ऐन" },
    { label: "👷 श्रम ऐन २०७४", query: "श्रम ऐन २०७४" },
    { label: "🛡ी मौलिक हक", query: "मौलिक हक" },
    { label: "🔍 फौजदारी प्रक्रिया संहिता २०७४", query: "फौजदारी प्रक्रिया संहिता २०७४" },
    { label: "📋 मुलुकी देवानी संहिता २०७४", query: "मुलुकी देवानी संहिता २०७४" },
    { label: "📄 सूचनाको हक ऐन", query: "सूचनाको हक ऐन" },
  ],
  hi: [
    { label: "📜 नेपाल का संविधान २०७२", query: "नेपाल का संविधान २०७२" },
    { label: "⚖ी नेपाल दंड संहिता २०७४", query: "नेपाल दंड संहिता २०७४" },
    { label: "🏠 संपत्ति अंतरण अधिनियम", query: "संपत्ति अंतरण अधिनियम" },
    { label: "👷 श्रम अधिनियम २०७४", query: "श्रम अधिनियम २०७४" },
    { label: "🛡ी मौलिक अधिकार", query: "मौलिक अधिकार" },
    { label: "🔍 आपराधिक प्रक्रिया संहिता", query: "आपराधिक प्रक्रिया संहिता" },
    { label: "📋 नेपाल नागरिक संहिता २०७४", query: "नेपाल नागरिक संहिता २०७४" },
    { label: "📄 सूचना का अधिकार अधिनियम", query: "सूचना का अधिकार अधिनियम" },
  ],
};

const selectClass = "px-3 py-2 border border-gray-200 rounded-xl text-xs bg-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all hover:border-gray-300";

function LawsPageContent() {
  const { translate, locale, country: ctxCountry } = useI18n();
  const searchParams = useSearchParams();
  const [laws, setLaws] = useState<LawDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [country, setCountry] = useState(ctxCountry === "all" ? "" : ctxCountry);
  const [category, setCategory] = useState("");
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [popularLaws, setPopularLaws] = useState<PopularLaw[]>([]);
  const [recentLaws, setRecentLaws] = useState<RecentLaw[]>([]);
  const [activeTab, setActiveTab] = useState<"browse" | "popular" | "recent">("browse");
  const [categoriesOpen, setCategoriesOpen] = useState(true);
  const [page, setPage] = useState(0);
  const [totalLaws, setTotalLaws] = useState(0);
  const [sortBy, setSortBy] = useState("relevance");
  const [searchMode, setSearchMode] = useState<"laws" | "issues">("laws");
  const [issueResult, setIssueResult] = useState<IssueResult | null>(null);
  const [searchingIssues, setSearchingIssues] = useState(false);

  const hasActiveQuery = query.trim().length > 0 || !!category || searching || searchingIssues || searchResults.length > 0 || issueResult !== null;

  useEffect(() => {
    setCountry(ctxCountry === "all" ? "" : ctxCountry);
  }, [ctxCountry]);

  // Read URL query params on mount
  const [initialized, setInitialized] = useState(false);
  const [resultId, setResultId] = useState<string | null>(null);
  useEffect(() => {
    if (initialized) return;
    const q = searchParams.get("q");
    const mode = searchParams.get("mode");
    const urlCountry = searchParams.get("country");
    const urlCategory = searchParams.get("category");
    const rId = searchParams.get("resultId");
    if (urlCountry) setCountry(urlCountry);
    if (mode === "issues") setSearchMode("issues");
    if (rId) setResultId(rId);
    if (urlCategory) {
      setCategory(urlCategory);
      setActiveTab("browse");
    }
    if (q) {
      setQuery(q);
      setActiveTab("browse");
    }
    setInitialized(true);
  }, [searchParams, initialized]);

  const loadCategories = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (country) params.set("country", country);
      const data = await api<Category[]>(`/api/v1/laws/categories?${params}`, { noAuth: true });
      setCategories(data);
    } catch { setCategories([]); }
  }, [country]);

  const loadPopular = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (country) params.set("country", country);
      const data = await api<PopularLaw[]>(`/api/v1/laws/popular?${params}`, { noAuth: true });
      setPopularLaws(data);
    } catch { setPopularLaws([]); }
  }, [country]);

  const loadRecent = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (country) params.set("country", country);
      const data = await api<RecentLaw[]>(`/api/v1/laws/recent?${params}`, { noAuth: true });
      setRecentLaws(data);
    } catch { setRecentLaws([]); }
  }, [country]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (country) params.set("country", country);
      if (category) params.set("category", category);
      params.set("offset", String(page * 20));
      params.set("limit", "20");
      const data = await api<{ articles: LawDoc[]; total: number }>(`/api/v1/laws/browse?${params}`, { noAuth: true });
      setLaws(data.articles || []);
      setTotalLaws(data.total || 0);
    } catch { setLaws([]); } finally { setLoading(false); }
  }, [country, category, page]);

  useEffect(() => {
    loadCategories();
    loadPopular();
    loadRecent();
  }, [loadCategories, loadPopular, loadRecent]);

  useEffect(() => {
    if (!query.trim()) load();
  }, [load, query]);

  // Auto-search when URL query is initialized
  useEffect(() => {
    if (initialized && query.trim()) {
      doSearch();
    }
  }, [initialized]);

  // Fetch result by ID when resultId is in URL
  useEffect(() => {
    if (!resultId || !initialized) return;
    // Try to find it in current search results first
    const found = searchResults.find(r => r.id === resultId);
    if (found) {
      setSelectedResult(found);
      setResultId(null);
      return;
    }
    // Otherwise fetch from API
    const fetchResult = async () => {
      try {
        const data = await api<SearchResult>(`/api/v1/laws/${resultId}`, { noAuth: true });
        setSelectedResult({
            id: data.id || resultId,
            title: data.title || "",
            full_text: data.full_text || "",
            country: data.country || "",
            category: data.category || "",
            document_type: data.document_type || "",
            article_number: data.article_number || "",
            source_document: data.source_document || "",
            score: data.score || 100,
            enactment_year: data.enactment_year || 0,
            language: data.language,
            confidence: data.confidence,
            citation: data.citation,
            last_verified: data.last_verified,
            source_url: data.source_url,
          });
      } catch {}
      setResultId(null);
    };
    fetchResult();
  }, [resultId, initialized, searchResults]);

  const doSearch = useCallback(async () => {
    if (!query.trim()) { setSearchResults([]); setIssueResult(null); load(); return; }
    if (searchMode === "issues") {
      setSearchingIssues(true);
      setSearchResults([]);
      try {
        const params = new URLSearchParams({ q: query.trim() });
        if (country) params.set("country", country);
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
      return;
    }
    setSearching(true);
    setIssueResult(null);
    try {
      const params = new URLSearchParams({ q: query.trim(), top_k: "20" });
      if (country) params.set("country", country);
      const data = await api<{ results: SearchResult[] }>(`/api/v1/laws/search?${params}`, { noAuth: true });
      setSearchResults(data.results || []);
    } catch { setSearchResults([]); } finally { setSearching(false); }
  }, [query, load, country, searchMode, locale]);

  const handleKeyDown = (e: React.KeyboardEvent) => { if (e.key === "Enter") doSearch(); };

  const handleCategoryClick = (cat: string) => {
    setCategory(cat);
    setQuery("");
    setActiveTab("browse");
    window.history.pushState({}, "", `/laws?category=${cat}`);
  };

  return (
    <>
      <Navbar />
      {selectedResult && <SearchResultModal result={selectedResult} onClose={() => setSelectedResult(null)} />}

      {/* Hero header */}
      <div className="bg-gradient-to-br from-cyan-700 to-cyan-800 text-white">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <h1 className="text-2xl font-bold mb-1">{translate("laws.title")}</h1>
          <p className="text-cyan-200 text-sm mb-5">{translate("laws.search_placeholder")}</p>

          {/* Search */}
          <div className="flex gap-2 max-w-2xl">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={translate("laws.search_placeholder")}
              className="flex-1 px-4 py-2.5 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/50 text-sm focus:outline-none focus:bg-white/20 transition-colors"
            />
            <button
              onClick={doSearch}
              disabled={searching}
              className="px-5 py-2.5 bg-white text-cyan-700 text-sm font-semibold rounded-xl hover:bg-cyan-50 transition-colors disabled:opacity-50"
            >
              {searching ? "..." : translate("laws.search_button")}
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-2 mt-3">
            <select value={country} onChange={(e) => { setCountry(e.target.value); setQuery(""); }} className={selectClass + " bg-white/10 border-white/20 text-white [&>option]:text-gray-800 [&>option]:bg-white"}>
              <option value="">{translate("laws.all_countries")}</option>
              <option value="nepal">🇳🇵 {translate("nepal")}</option>
              <option value="india">🇮🇳 {translate("india")}</option>
            </select>
            <select value={category} onChange={(e) => { setCategory(e.target.value); setQuery(""); }} className={selectClass + " bg-white/10 border-white/20 text-white [&>option]:text-gray-800 [&>option]:bg-white"}>
              <option value="">{translate("laws.all_categories")}</option>
              {categories.map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {CAT_LABELS[cat.name]?.[locale] || cat.name} ({cat.count})
                </option>
              ))}
            </select>
          </div>

          {/* Sample law search tags — localized */}
          {!hasActiveQuery && (
            <div className="mt-5 flex flex-wrap gap-2">
              {(SAMPLE_LAW_TAGS[locale] || SAMPLE_LAW_TAGS.en).map((tag, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(tag.query); setTimeout(doSearch, 50); }}
                  className="text-[11px] px-3 py-1.5 rounded-full bg-white/10 text-white/80 hover:bg-white/20 transition-colors"
                >
                  {tag.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-4 py-5 pb-20 md:pb-6">
        <DisclaimerBanner />

        {/* Query info banner */}
        {(query.trim() || category) && (
          <div className={`mb-5 rounded-2xl border overflow-hidden ${
            searchMode === "issues"
              ? "border-red-200 bg-white"
              : "border-cyan-200 bg-white"
          }`}>
            <div className="px-5 py-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[10px] font-semibold uppercase tracking-wider ${
                      searchMode === "issues" ? "text-red-500" : "text-cyan-500"
                    }`}>
                      {searching || searchingIssues
                        ? (searchMode === "issues" ? "Finding issues..." : "Searching...")
                        : (searchMode === "issues" ? "Issue results for" : "Showing results for")
                      }
                    </span>
                  </div>
                  <h2 className={`text-lg font-bold leading-snug ${
                    searchMode === "issues" ? "text-red-900" : "text-gray-900"
                  }`}>
                    {query.trim() ? <>&ldquo;{query}&rdquo;</> : <>{CAT_LABELS[category]?.[locale] || category}</>}
                  </h2>
                  {!searching && !searchingIssues && (
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      {searchResults.length > 0 && (
                        <span className="text-xs text-gray-500">
                          {searchResults.length} {translate("search.results_found")}
                        </span>
                      )}
                      {query.trim() && category && (
                        <span className="text-xs text-gray-400">
                          in <span className="font-medium text-gray-600">{CAT_LABELS[category]?.[locale] || category}</span>
                        </span>
                      )}
                      {country && (
                        <span className="text-xs text-gray-400">
                          {country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                {!searching && !searchingIssues && (
                  <button
                    onClick={() => {
                      setQuery("");
                      setCategory("");
                      setSearchResults([]);
                      setIssueResult(null);
                      setResultId(null);
                      window.history.pushState({}, "", "/laws");
                    }}
                    className={`group shrink-0 flex items-center gap-1.5 text-[11px] font-medium px-3 py-1.5 rounded-lg transition-all ${
                      searchMode === "issues"
                        ? "text-red-500 hover:bg-red-50 hover:text-red-700"
                        : "text-cyan-600 hover:bg-cyan-50 hover:text-cyan-800"
                    }`}
                  >
                    <svg className="w-3.5 h-3.5 transition-transform group-hover:rotate-90 duration-200" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tabs — hidden when searching */}
        {!hasActiveQuery && (
          <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 w-fit">
            <button
              onClick={() => setActiveTab("browse")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === "browse" ? "bg-white text-cyan-700 shadow-sm" : "text-gray-600 hover:text-gray-900"}`}
            >
              {translate("laws.all_categories")}
            </button>
            <button
              onClick={() => setActiveTab("popular")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === "popular" ? "bg-white text-cyan-700 shadow-sm" : "text-gray-600 hover:text-gray-900"}`}
            >
              {translate("laws.popular")}
            </button>
            <button
              onClick={() => setActiveTab("recent")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === "recent" ? "bg-white text-cyan-700 shadow-sm" : "text-gray-600 hover:text-gray-900"}`}
            >
              {translate("laws.recent")}
            </button>
          </div>
        )}

        {/* Category tiles — full grid when idle, compact pill bar when searching */}
        {activeTab === "browse" && categories.length > 0 && (
          <>
            {hasActiveQuery ? (
              /* Compact horizontal scrollable pills during search */
              <div className="mb-4 -mx-4 px-4">
                <div className="flex gap-1.5 overflow-x-auto pb-2 scrollbar-none">
                  {categories.map((cat) => {
                    const icon = CAT_ICONS[cat.name] || "📖";
                    const isSelected = category === cat.name;
                    return (
                      <button
                        key={cat.name}
                        onClick={() => handleCategoryClick(cat.name)}
                        className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-medium border transition-all ${
                          isSelected
                            ? "bg-cyan-100 text-cyan-700 border-cyan-300 shadow-sm"
                            : "bg-white text-gray-600 border-gray-200 hover:border-cyan-200 hover:bg-cyan-50"
                        }`}
                      >
                        <span className="text-xs">{icon}</span>
                        <span>{CAT_LABELS[cat.name]?.[locale] || cat.name}</span>
                        <span className="text-[9px] text-gray-400 ml-0.5">{cat.count}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : (
              /* Full category grid when idle — collapsible */
              <div className="mb-6">
                <button
                  onClick={() => setCategoriesOpen(!categoriesOpen)}
                  className="w-full flex items-center justify-between gap-2 mb-3 group"
                >
                  <h2 className="text-sm font-semibold text-gray-700 group-hover:text-gray-900 transition-colors">
                    {translate("laws.categories.title")}
                    <span className="text-xs font-normal text-gray-400 ml-1.5">({categories.length})</span>
                  </h2>
                  <svg
                    className={`w-4 h-4 text-gray-400 group-hover:text-gray-600 transition-all duration-200 ${
                      categoriesOpen ? "rotate-180" : ""
                    }`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </button>
                <div className={`transition-all duration-300 overflow-hidden ${
                  categoriesOpen ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
                }`}>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
                    {categories.map((cat) => {
                      const color = CAT_COLORS[cat.name] || "bg-gray-50 text-gray-600 border-gray-100";
                      const icon = CAT_ICONS[cat.name] || "📖";
                      const isSelected = category === cat.name;
                      return (
                        <button
                          key={cat.name}
                          onClick={() => handleCategoryClick(cat.name)}
                          className={`p-3 rounded-xl border-2 transition-all duration-200 text-left ${
                            isSelected
                              ? "border-cyan-500 bg-cyan-50 shadow-md"
                              : "border-gray-100 bg-white hover:shadow-md hover:border-cyan-200"
                          }`}
                        >
                          <div className="text-xl mb-1">{icon}</div>
                          <h3 className="font-semibold text-sm text-gray-900">{CAT_LABELS[cat.name]?.[locale] || cat.name}</h3>
                          <p className="text-[10px] text-gray-500 mt-0.5">{cat.count} {translate("laws.provisions")}</p>
                          <div className="flex gap-2 mt-1">
                            {cat.countries.nepal && <span className="text-[9px] text-gray-400">🇳🇵 {cat.countries.nepal}</span>}
                            {cat.countries.india && <span className="text-[9px] text-gray-400">🇮🇳 {cat.countries.india}</span>}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Loading skeleton */}
        {(loading || searching || searchingIssues) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 p-4 animate-pulse">
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
        {!searching && !searchingIssues && issueResult?.identified && issueResult.guidance && (
          <div className="mb-4 p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-200 mt-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">⚖️</span>
              <h3 className="font-semibold text-sm text-amber-800">{issueResult.title}</h3>
            </div>
            <p className="text-[11px] text-amber-700 leading-relaxed">{issueResult.guidance}</p>
            {issueResult.provisions && issueResult.provisions.length > 0 && (
              <div className="mt-3 space-y-2">
                {issueResult.provisions.map((prov) => (
                  <div key={prov.country} className="flex items-start gap-2">
                    <span className="text-xs font-semibold text-amber-600 shrink-0 mt-0.5">
                      {prov.country === "nepal" ? "🇳🇵" : "🇮🇳"} {prov.country === "nepal" ? "Nepal" : "India"}:
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {prov.articles.slice(0, 5).map((a) => (
                        <span key={a.id} className="text-[10px] px-2 py-0.5 bg-white rounded-full border border-amber-200 text-amber-700">
                          {a.title}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Search results */}
        {!searching && !searchingIssues && searchResults.length > 0 && (
          <div className="space-y-2 mt-4">
            {searchResults.map((r) => {
              const catColor = CAT_COLORS[r.category] || "bg-gray-50 text-gray-600 border-gray-100";
              return (
                <button
                  key={r.id}
                  onClick={() => setSelectedResult(r)}
                  className="w-full text-left bg-white rounded-2xl border border-gray-100 p-4 hover:shadow-md hover:border-cyan-200 active:scale-[0.99] transition-all duration-150 group"
                >
                  <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                      {CAT_LABELS[r.category]?.[locale] || r.category}
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
                      {r.source_document?.replace(/_/g, " ")}
                      {r.enactment_year > 0 && <span className="ml-1 text-cyan-500 font-medium">({r.enactment_year})</span>}
                    </p>
                    <span className="text-[9px] text-cyan-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                      {translate("laws.view_details") || "View details"}
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Popular laws */}
        {activeTab === "popular" && !searching && !searchingIssues && searchResults.length === 0 && (
          <div className="mt-4">
            <p className="text-xs text-gray-400 mb-4">{translate("laws.essential_provisions")}</p>
            {popularLaws.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {popularLaws.map((law, idx) => {
                  const catColor = CAT_COLORS[law.category] || "bg-gray-50 text-gray-600 border-gray-100";
                  const isTop3 = idx < 3;
                  return (
                    <button
                      key={law.provision_id}
                      onClick={() => {
                        setQuery(law.title);
                        setTimeout(() => doSearch(), 50);
                      }}
                      className={`w-full text-left rounded-2xl border p-4 transition-all duration-200 group ${
                        isTop3
                          ? "bg-gradient-to-br from-cyan-50 to-white border-cyan-100 hover:shadow-md hover:border-cyan-300"
                          : "bg-white border-gray-100 hover:shadow-md hover:border-cyan-200"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {/* Rank badge */}
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
                              {CAT_LABELS[law.category]?.[locale] || law.category}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                              {law.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                            </span>
                            {law.article_number && (
                              <span className="text-[10px] text-gray-400 font-mono">Art. {law.article_number}</span>
                            )}
                          </div>
                          <h3 className="font-semibold text-sm text-gray-900 group-hover:text-cyan-700 transition-colors leading-snug">{law.title}</h3>
                          {law.source_document && (
                            <p className="text-[10px] text-gray-400 mt-1.5">{getSourceName(law.source_document)}</p>
                          )}
                          {law.view_count > 0 && (
                            <div className="flex items-center gap-1 mt-2">
                              <svg className="w-3 h-3 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                              <span className="text-[10px] text-cyan-500 font-medium">{law.view_count} {translate("laws.views")}</span>
                            </div>
                          )}
                        </div>
                        <svg className="w-4 h-4 text-gray-300 group-hover:text-cyan-500 shrink-0 mt-1 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                      </div>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-2xl">
                <div className="text-3xl mb-2">📊</div>
                <p className="text-sm text-gray-500">{translate("laws.no_popular")}</p>
              </div>
            )}
          </div>
        )}

        {/* Recent laws */}
        {activeTab === "recent" && !searching && !searchingIssues && searchResults.length === 0 && (
          <div className="mt-4">
            <p className="text-xs text-gray-400 mb-4">{translate("laws.newest_laws")}</p>
            {recentLaws.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recentLaws.map((law) => {
                  const catColor = CAT_COLORS[law.category] || "bg-gray-50 text-gray-600 border-gray-100";
                  return (
                    <button
                      key={law.provision_id}
                      onClick={() => {
                        setQuery(law.title);
                        setTimeout(() => doSearch(), 50);
                      }}
                      className="w-full text-left bg-white rounded-2xl border border-gray-100 p-4 hover:shadow-md hover:border-cyan-200 transition-all duration-200 group"
                    >
                      <div className="flex items-start gap-3">
                        {/* Year badge */}
                        <div className="w-14 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex flex-col items-center justify-center shrink-0">
                          <span className="text-[10px] text-white/70 leading-none"> enacted</span>
                          <span className="text-xs font-bold text-white leading-none">{law.enactment_year}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                              {CAT_LABELS[law.category]?.[locale] || law.category}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                              {law.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                            </span>
                            {law.article_number && (
                              <span className="text-[10px] text-gray-400 font-mono">Art. {law.article_number}</span>
                            )}
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
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-2xl">
                <div className="text-3xl mb-2">📅</div>
                <p className="text-sm text-gray-500">{translate("laws.no_recent")}</p>
              </div>
            )}
          </div>
        )}

        {/* Browse results */}
        {activeTab === "browse" && !searching && !searchingIssues && searchResults.length === 0 && !loading && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs text-gray-500 font-medium">{laws.length} {translate("laws.documents")}</p>
              <div className="flex items-center gap-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-[10px] px-2 py-1 border border-gray-200 rounded-lg bg-white focus:ring-2 focus:ring-cyan-500 outline-none"
                >
                  <option value="relevance">{translate("search.sorted_by_relevance")}</option>
                  <option value="date_newest">{translate("laws.recent")}</option>
                  <option value="country">{translate("laws.all_countries")}</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {laws.map((law) => {
                const catColor = CAT_COLORS[law.category] || "bg-gray-50 text-gray-600 border-gray-100";
                return (
                  <div
                    key={law.id}
                    onClick={() => {
                      setQuery(law.title);
                      setTimeout(() => doSearch(), 50);
                    }}
                    className="bg-white rounded-2xl border border-gray-100 p-4 hover:shadow-md hover:border-cyan-200 transition-all duration-200 cursor-pointer group"
                  >
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                        {CAT_LABELS[law.category]?.[locale] || law.category}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                        {law.country === "nepal" ? "🇳🇵" : "🇮🇳"}
                      </span>
                    </div>
                    <h3 className="font-semibold text-sm text-gray-900 group-hover:text-cyan-700 transition-colors">{law.title}</h3>
                  </div>
                );
              })}
            </div>
            {/* Pagination */}
            {totalLaws > 20 && (
              <div className="flex items-center justify-center gap-2 mt-4">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="px-3 py-1.5 text-xs rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {translate("laws.pagination.previous")}
                </button>
                <span className="text-xs text-gray-500">
                  {translate("laws.pagination.page_of").replace("{current}", String(page + 1)).replace("{total}", String(Math.ceil(totalLaws / 20)))}
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={(page + 1) * 20 >= totalLaws}
                  className="px-3 py-1.5 text-xs rounded-lg border border-gray-200 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {translate("laws.pagination.next")}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!loading && !searching && !searchingIssues && laws.length === 0 && searchResults.length === 0 && (
          <div className="text-center py-16">
            <div className="text-4xl mb-3">📚</div>
            <p className="text-sm text-gray-500">{translate("laws.no_laws_found")}</p>
          </div>
        )}
      </main>
    </>
  );
}

export default function LawsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-sm text-gray-500">Loading...</div>
      </div>
    }>
      <LawsPageContent />
    </Suspense>
  );
}