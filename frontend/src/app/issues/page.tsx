"use client";

import { useState, useEffect, useCallback } from "react";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import SearchResultModal from "@/components/SearchResultModal";
import RelevanceBadge from "@/components/RelevanceBadge";

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

interface IssueResult {
  issue_identified: boolean;
  issue_id?: string;
  title?: string;
  search_results: SearchResult[];
  provisions?: { country: string; articles: { id: string; title: string; article_number: string; source_document: string }[] }[];
  guidance?: string;
}

const SAMPLE_ISSUES = {
  en: [
    "I was arrested by police",
    "My husband beats me",
    "My tenant won't leave my house",
    "My employer fired me without notice",
    "I bought a defective product",
    "My father died and siblings are fighting over property",
    "Someone hacked my bank account",
    "I need a lawyer but can't afford one",
  ],
  ne: [
    "मलाई प्रहरीले गिरफ्तार गर्यो",
    "मेरो शोहरले मलाई मार्छ",
    "मेरो किरायादारले घर छोड्दैन",
    "मेरो रोजगारदाताले सूचना बिना निकाल्यो",
    "मैले दोषपूर्ण उत्पादन किनें",
    "मेरो बुबा गुम्नुभयो र भाइबहिनी सम्पत्तिमा झगडा गर्दैछन्",
    "कसैले मेरो बैंक खाता ह्याक गर्यो",
    "मलाई वकील चाहिन्छ तर भाडा गर्न सक्दिन",
  ],
  hi: [
    "मुझे पुलिस ने गिरफ्तार कर लिया",
    "मेरा पति मुझे मारता है",
    "मेरा किरायेदार घर नहीं छोड़ रहा",
    "मेरे नियोक्ता ने बिना नोटिस निकाल दिया",
    "मैंने दोषपूर्ण उत्पादन खरीदा",
    "मेरे पिता की मृत्यु हो गई और भाई-बहन सम्पत्ति पर लड़ रहे हैं",
    "किसी ने मेरा बैंक अकाउंट हैक कर लिया",
    "मुझे वकील चाहिए लेकिन खर्च उठाने में असमर्थ हूँ",
  ],
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

export default function IssuesPage() {
  const { locale, country, translate } = useI18n();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IssueResult | null>(null);
  const [modalResult, setModalResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState("");
  const [pendingResultId, setPendingResultId] = useState<string | null>(null);

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 3) return;
    setLoading(true);
    setError("");
    try {
      const lang = locale || "en";
      const countryParam = country && country !== "all" ? `&country=${country}` : "";
      const data = await api<IssueResult>(`/api/v1/issues/find?q=${encodeURIComponent(q)}&lang=${lang}${countryParam}`, { noAuth: true });
      setResult(data);
      window.history.replaceState({}, "", `/issues?q=${encodeURIComponent(q)}`);
    } catch {
      setError(translate("issues_page.search_failed"));
    }
    setLoading(false);
  }, [locale, country, translate]);

  // Read URL params on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");
    const rId = params.get("resultId");
    if (q) {
      setQuery(q);
      if (rId) setPendingResultId(rId);
      doSearch(q);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-open modal when resultId is in URL and search results are loaded
  useEffect(() => {
    if (!pendingResultId || !result) return;
    // Try to find it in search results
    const found = result.search_results.find(r => r.id === pendingResultId);
    if (found) {
      setModalResult(found);
      setPendingResultId(null);
      return;
    }
    // Otherwise fetch from API
    const fetchResult = async () => {
      try {
        const data = await api<SearchResult>(`/api/v1/laws/${pendingResultId}`, { noAuth: true });
        setModalResult({
          id: data.id || pendingResultId,
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
      setPendingResultId(null);
    };
    fetchResult();
  }, [pendingResultId, result]);

  const samples = SAMPLE_ISSUES[locale as keyof typeof SAMPLE_ISSUES] || SAMPLE_ISSUES.en;

  return (
    <div className="min-h-screen bg-gray-50 pb-20 md:pb-0">
      <Navbar />

      {/* Hero — Bright Red */}
      <div className="bg-gradient-to-br from-red-600 via-rose-600 to-red-700 text-white py-12 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/15 border border-white/25 mb-4">
            <svg className="w-4 h-4 text-red-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-[11px] font-bold uppercase tracking-wider text-red-100">{translate("issues_page.issue_finder")}</span>
          </div>
          <h1 className="text-2xl font-bold mb-2">{translate("issues_page.find_laws_for_issue")}</h1>
          <p className="text-red-100 text-sm max-w-lg mx-auto mb-6">{translate("issues_page.describe_situation")}</p>

          <div className="flex gap-2 max-w-xl mx-auto">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && doSearch(query)}
              placeholder={translate("issues_page.search_placeholder")}
              className="flex-1 text-sm px-4 py-2.5 rounded-xl bg-white/15 border border-white/25 text-white placeholder-white/50 focus:outline-none focus:bg-white/25 transition-colors"
            />
            <button
              onClick={() => doSearch(query)}
              disabled={loading || query.length < 3}
              className="px-5 py-2.5 rounded-xl bg-white text-red-600 text-sm font-semibold hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              {loading ? translate("issues_page.searching") : translate("issues_page.search")}
            </button>
          </div>

          {!result && !loading && (
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {samples.map((s, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(s); doSearch(s); }}
                  className="text-[11px] px-3 py-1.5 rounded-full bg-white/15 text-white/90 hover:bg-white/25 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6">
        <DisclaimerBanner />

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-3 mt-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 p-4 animate-pulse">
                <div className="flex items-center gap-1.5 mb-2">
                  <div className="h-5 w-20 bg-red-100 rounded-full" />
                  <div className="h-5 w-12 bg-gray-100 rounded-full" />
                </div>
                <div className="h-4 w-3/4 bg-gray-200 rounded mb-2" />
                <div className="h-3 w-full bg-gray-100 rounded" />
              </div>
            ))}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 mt-6">{error}</div>
        )}

        {result && (
          <div className="space-y-5 mt-6">
            {/* Identified Issue */}
            {result.issue_identified && (
              <div className="bg-red-50 rounded-2xl border border-red-200 p-5">
                <div className="flex items-center gap-2 mb-1">
                  <span className="w-7 h-7 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                    <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </span>
                  <h2 className="text-sm font-bold text-red-800">{translate("issues_page.identified_issue")} {result.title}</h2>
                  <button
                    onClick={() => navigator.clipboard.writeText(window.location.href)}
                    className="ml-auto text-[10px] px-2.5 py-1 rounded-lg bg-white text-red-600 hover:bg-red-100 transition-colors border border-red-200 inline-flex items-center gap-1"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    {translate("issues_page.share")}
                  </button>
                </div>
              </div>
            )}

            {/* Guidance */}
            {result.guidance && (
              <div className="bg-red-50/60 rounded-2xl border border-red-100 p-5">
                <h3 className="text-sm font-bold text-red-800 mb-2 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {translate("issues_page.what_to_do")}
                </h3>
                <p className="text-sm text-red-900/80 leading-relaxed">{result.guidance}</p>
              </div>
            )}

            {/* Key Provisions */}
            {result.provisions && result.provisions.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">{translate("issues_page.key_provisions")}</h3>
                <div className="space-y-3">
                  {result.provisions
                    .filter((p: { country: string }) => !country || country === "all" || p.country === country)
                    .map((p, i) => (
                    <div key={i}>
                      <div className="text-xs font-semibold text-gray-500 mb-1.5 flex items-center gap-1.5">
                        <span>{p.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                        <span>{translate(`issues_page.country_${p.country}`)}</span>
                      </div>
                      <div className="space-y-1">
                        {p.articles.map((a, j) => (
                          <button
                            key={j}
                            onClick={() => {
                              const full = result.search_results.find(r => r.id === a.id);
                              if (full) setModalResult(full);
                            }}
                            className="w-full flex items-center gap-2 text-xs p-2.5 rounded-xl bg-gray-50 hover:bg-red-50 hover:border-red-100 border border-transparent transition-all group text-left"
                          >
                            <span className="font-medium text-gray-700 group-hover:text-red-700 transition-colors">{a.title}</span>
                            {a.article_number && (
                              <span className="text-gray-400 font-mono ml-auto shrink-0">#{a.article_number}</span>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* All Search Results */}
            {result.search_results.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
                  {translate("issues_page.all_results")} ({result.search_results.length})
                </h3>
                <div className="space-y-2">
                  {result.search_results.map((r, i) => (
                    <button
                      key={i}
                      onClick={() => setModalResult(r)}
                      className="w-full bg-white rounded-2xl border border-gray-100 p-4 text-left hover:border-red-200 hover:shadow-md transition-all duration-200 group"
                    >
                      <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-red-50 text-red-600 border border-red-100">
                          {CAT_LABELS[r.category]?.[locale] || r.category?.replace(/_/g, " ")}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                          {r.country === "nepal" ? "🇳🇵" : "🇮🇳"}
                        </span>
                        {r.article_number && (
                          <span className="text-[10px] text-gray-400 font-mono">{translate("issues_page.article_prefix")} {r.article_number}</span>
                        )}
                        {r.score != null && (
                          <span className="ml-auto"><RelevanceBadge score={r.score} size="sm" /></span>
                        )}
                      </div>
                      <h4 className="text-xs font-semibold text-gray-900 group-hover:text-red-700 transition-colors">{r.title}</h4>
                      <p className="text-[11px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">{r.full_text}</p>
                      <p className="text-[10px] text-gray-400 mt-1.5">
                        {r.source_document?.replace(/_/g, " ")}
                        {r.enactment_year > 0 && <span className="ml-1 text-red-500 font-medium">({r.enactment_year})</span>}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {result.search_results.length === 0 && !loading && (
              <div className="text-center py-16">
                <div className="text-4xl mb-3">🔍</div>
                <p className="text-sm text-gray-500">{translate("issues_page.no_results")}</p>
              </div>
            )}
          </div>
        )}

        {!result && !loading && !error && (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">⚖️</div>
            <p className="text-sm text-gray-500">{translate("issues_page.describe_issue")}</p>
          </div>
        )}
      </div>

      {modalResult && (
        <SearchResultModal result={modalResult} onClose={() => setModalResult(null)} context="issues" />
      )}
    </div>
  );
}
