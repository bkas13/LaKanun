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
    setResult(null);
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

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");
    const rId = params.get("resultId");
    if (q) {
      setQuery(q);
      if (rId) setPendingResultId(rId);
      doSearch(q);
    }
  }, []);

  useEffect(() => {
    if (!pendingResultId || !result) return;
    const found = result.search_results.find(r => r.id === pendingResultId);
    if (found) {
      setModalResult(found);
      setPendingResultId(null);
      return;
    }
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

      {/* Hero — Red (distinct Issues theme) */}
      <div className="bg-gradient-to-br from-red-700 to-red-800 text-white py-10 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-red-200 bg-white/15 px-3 py-1 rounded-full">
              {translate("issues_page.issue_finder")}
            </span>
          </div>
          <h1 className="text-2xl font-bold mb-1">{translate("issues_page.find_laws_for_issue")}</h1>
          <p className="text-red-200 text-sm mb-5">{translate("issues_page.describe_situation")}</p>

          <div className="flex gap-2 max-w-2xl">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && doSearch(query)}
              placeholder={translate("issues_page.search_placeholder")}
              className="flex-1 text-sm px-4 py-2.5 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:bg-white/20 transition-colors"
            />
            <button
              onClick={() => doSearch(query)}
              disabled={loading || query.length < 3}
              className="px-5 py-2.5 rounded-xl bg-white text-red-600 text-sm font-semibold hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              {loading ? "..." : translate("issues_page.search")}
            </button>
          </div>

          {!result && !loading && (
            <div className="mt-5 flex flex-wrap gap-2">
              {samples.map((s, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(s); doSearch(s); }}
                  className="text-[11px] px-3 py-1.5 rounded-full bg-white/10 text-white/80 hover:bg-white/20 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-4 py-5 pb-20 md:pb-6">
        <DisclaimerBanner />

        {/* Query info banner */}
        {query.trim() && !loading && result && (
          <div className="mb-5 rounded-2xl border border-red-200 bg-white overflow-hidden">
            <div className="px-5 py-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-red-500">Issue results for</span>
                  </div>
                  <h2 className="text-lg font-bold leading-snug text-gray-900">&ldquo;{query}&rdquo;</h2>
                  <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                    {result.search_results.length > 0 && (
                      <span className="text-xs text-gray-500">{result.search_results.length} results found</span>
                    )}
                    {country && country !== "all" && (
                      <span className="text-xs text-gray-400">
                        {country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => { setQuery(""); setResult(null); window.history.pushState({}, "", "/issues"); }}
                  className="group shrink-0 flex items-center gap-1.5 text-[11px] font-medium px-3 py-1.5 rounded-lg text-red-500 hover:bg-red-50 hover:text-red-700 transition-all"
                >
                  <svg className="w-3.5 h-3.5 transition-transform group-hover:rotate-90 duration-200" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Clear
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
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

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
        )}

        {result && (
          <div className="space-y-5 mt-4">
            {/* Issue guidance banner — red theme */}
            {result.issue_identified && result.guidance && (
              <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 rounded-xl border border-red-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-7 h-7 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                    <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </span>
                  <h3 className="font-semibold text-sm text-red-800">{result.title}</h3>
                  <button
                    onClick={() => navigator.clipboard.writeText(window.location.href)}
                    className="ml-auto text-[10px] px-2.5 py-1 rounded-lg bg-white text-red-600 hover:bg-red-100 transition-colors border border-red-200 inline-flex items-center gap-1"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    Share
                  </button>
                </div>
                <p className="text-[11px] text-red-700 leading-relaxed">{result.guidance}</p>
                {result.provisions && result.provisions.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {result.provisions.map((prov) => (
                      <div key={prov.country} className="flex items-start gap-2">
                        <span className="text-xs font-semibold text-red-600 shrink-0 mt-0.5">
                          {prov.country === "nepal" ? "🇳🇵" : "🇮🇳"} {prov.country === "nepal" ? "Nepal" : "India"}:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {prov.articles.slice(0, 5).map((a) => (
                            <span key={a.id} className="text-[10px] px-2 py-0.5 bg-white rounded-full border border-red-200 text-red-700">
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

            {/* Search results — same cards as laws page */}
            {result.search_results.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
                  {translate("issues_page.all_results")} ({result.search_results.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {result.search_results.map((r, i) => {
                    const catColor = CAT_COLORS[r.category] || "bg-gray-50 text-gray-600 border-gray-100";
                    return (
                      <button
                        key={r.id || i}
                        onClick={() => setModalResult(r)}
                        className="w-full text-left bg-white rounded-2xl border border-gray-100 p-4 hover:shadow-md hover:border-red-200 active:scale-[0.99] transition-all duration-150 group"
                      >
                        <div className="flex items-center gap-1.5 mb-2 flex-wrap">
                          <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${catColor}`}>
                            {CAT_LABELS[r.category]?.[locale] || r.category?.replace(/_/g, " ")}
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
                        <h3 className="font-semibold text-sm text-gray-900 group-hover:text-red-700 transition-colors">{r.title}</h3>
                        <p className="text-[11px] text-gray-500 mt-1.5 line-clamp-2 leading-relaxed">{r.full_text}</p>
                        <div className="flex items-center justify-between mt-2">
                          <p className="text-[10px] text-gray-400">
                            {getSourceName(r.source_document)}
                            {r.enactment_year > 0 && <span className="ml-1 text-red-500 font-medium">({r.enactment_year})</span>}
                          </p>
                          <span className="text-[9px] text-red-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                            View details
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                          </span>
                        </div>
                      </button>
                    );
                  })}
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

        {!result && !loading && !error && !query.trim() && (
          <div className="text-center py-16">
            <div className="text-4xl mb-3">⚖️</div>
            <p className="text-sm text-gray-500">{translate("issues_page.describe_issue")}</p>
          </div>
        )}
      </main>

      {modalResult && (
        <SearchResultModal result={modalResult} onClose={() => setModalResult(null)} context="issues" />
      )}
    </div>
  );
}
