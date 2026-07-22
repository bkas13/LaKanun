"use client";

import { useState, useEffect } from "react";
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

interface PlainLanguageSummary {
  available: boolean;
  summary?: string;
}

interface RelatedProvision {
  id: string;
  title: string;
  article_number: string;
  country: string;
  category: string;
  source_document: string;
  score: number;
}

const CAT_LABELS: Record<string, { en: string; ne: string; hi: string }> = {
  criminal: { en: "Criminal Law", ne: "फौजदारी कानुन", hi: "आपराधिक कानून" },
  civil_procedure_general: { en: "Civil Procedure", ne: "दीवानी प्रक्रिया", hi: "दीवानी प्रक्रिया" },
  constitutional: { en: "Constitutional Law", ne: "संवैधानिक कानुन", hi: "संवैधानिक कानून" },
  civil: { en: "Civil Law", ne: "दीवानी कानुन", hi: "दीवानी कानून" },
  property_law: { en: "Property Law", ne: "सम्पत्ति कानुन", hi: "संपत्ति कानून" },
  civil_law_general: { en: "Civil Law", ne: "दीवानी कानुन", hi: "दीवानी कानून" },
  consumer_protection_general: { en: "Consumer Protection", ne: "उपभोक्ता संरक्षण", hi: "उपभोक्ता संरक्षण" },
  punishment_provisions: { en: "Penalties", ne: "सजाय व्यवस्था", hi: "दंड व्यवस्था" },
  labor: { en: "Labor Law", ne: "श्रम कानुन", hi: "श्रम कानून" },
  family: { en: "Family Law", ne: "पारिवारिक कानुन", hi: "पारिवारिक कानून" },
  tax: { en: "Tax Law", ne: "कर कानुन", hi: "कर कानून" },
  environmental: { en: "Environmental Law", ne: "वातावरण कानुन", hi: "पर्यावरण कानून" },
  commercial: { en: "Commercial Law", ne: "व्यापारिक कानुन", hi: "व्यापारिक कानून" },
  computer_offences: { en: "Computer Offences", ne: "कम्प्युटर अपराध", hi: "कम्प्यूटर अपराध" },
  evidence: { en: "Evidence", ne: "प्रमाण", hi: "साक्ष्य" },
  procedure: { en: "Procedure", ne: "प्रक्रिया", hi: "प्रक्रिया" },
};

const DOC_LABELS: Record<string, { en: string; ne: string; hi: string }> = {
  indian_penal_code: { en: "Indian Penal Code, 1860", ne: "भारतीय दण्ड संहिता, १८६०", hi: "भारतीय दंड संहिता, १८६०" },
  code_of_criminal_procedure: { en: "Code of Criminal Procedure, 1973", ne: "फौजदारी प्रक्रिया संहिता, १९७३", hi: "दंड प्रक्रिया संहिता, १९७३" },
  constitution_of_india: { en: "Constitution of India, 1950", ne: "भारतको संविधान, १९५०", hi: "भारत का संविधान, १९५०" },
  indian_contract_act: { en: "Indian Contract Act, 1872", ne: "भारतीय अनुबन्ध ऐन, १८७२", hi: "भारतीय अनुबंध अधिनियम, १८७२" },
  code_of_civil_procedure: { en: "Code of Civil Procedure, 1908", ne: "दीवानी प्रक्रिया संहिता, १९०८", hi: "दीवानी प्रक्रिया संहिता, १९०८" },
  minimum_wages_act: { en: "Minimum Wages Act, 1948", ne: "न्यूनतम ज्याला ऐन, १९४८", hi: "न्यूनतम वेतन अधिनियम, १९४८" },
  constitution_of_nepal_2072: { en: "Constitution of Nepal, 2072 (2015)", ne: "नेपालको संविधान, २०७२ (२०१५)", hi: "नेपाल का संविधान, २०७२ (२०१५)" },
  electronic_transactions: { en: "Electronic Transactions Act", ne: "इलेक्ट्रोनिक लेनदेन ऐन", hi: "इलेक्ट्रॉनिक लेनदेन अधिनियम" },
};

export default function SearchResultModal({
  result,
  onClose,
  context = "laws",
}: {
  result: SearchResult;
  onClose: () => void;
  context?: "laws" | "issues";
}) {
  const { locale, country, translate, t } = useI18n();
  const router = useRouter();
  const [plainSummary, setPlainSummary] = useState<PlainLanguageSummary | null>(null);
  const [related, setRelated] = useState<RelatedProvision[]>([]);
  const [activeTab, setActiveTab] = useState<"legal" | "plain">("legal");
  const [reported, setReported] = useState(false);
  const [relatedLoading, setRelatedLoading] = useState(true);
  const [bookmarked, setBookmarked] = useState(false);
  const [bookmarkId, setBookmarkId] = useState<number | null>(null);

  const isIssues = context === "issues";
  const th = {
    header: isIssues ? "from-red-600 via-rose-600 to-red-700" : "from-cyan-600 to-cyan-700",
    badge: isIssues ? "bg-red-50 text-red-600 border-red-100" : "bg-gray-50 text-gray-400 border-gray-100",
    enactment: isIssues ? "text-red-500" : "text-cyan-500",
    citationBg: isIssues ? "bg-red-50 border-red-100" : "bg-cyan-50 border-cyan-100",
    citationLabel: isIssues ? "text-red-500" : "text-cyan-500",
    citationText: isIssues ? "text-red-800" : "text-cyan-800",
    sourceLink: isIssues ? "text-red-600 hover:text-red-800" : "text-cyan-600 hover:text-cyan-800",
    tabActive: isIssues ? "bg-red-600 text-white" : "bg-cyan-600 text-white",
    relatedHover: isIssues
      ? "hover:bg-red-50 hover:border-red-100"
      : "hover:bg-cyan-50 hover:border-cyan-100",
    relatedText: isIssues ? "text-red-500 group-hover:text-red-700" : "text-cyan-500 group-hover:text-cyan-700",
    relatedArrow: isIssues ? "group-hover:text-red-500" : "group-hover:text-cyan-500",
    closeBtn: isIssues
      ? "bg-red-600 hover:bg-red-700"
      : "bg-cyan-600 hover:bg-cyan-700",
  };

  const handleReport = async () => {
    try {
      await api("/api/v1/feedback/report-citation", {
        method: "POST",
        body: {
          result_id: result.id,
          issue: "citation_inaccuracy",
          details: `User-reported citation issue for ${result.id}`,
        },
      });
      setReported(true);
    } catch {
      setReported(true);
    }
  };

  useEffect(() => {
    setRelatedLoading(true);
    setPlainSummary(null);
    setRelated([]);
    setBookmarked(false);
    setBookmarkId(null);
    if (!result.id) return;
    const lang = locale || "en";
    api<PlainLanguageSummary>(`/api/v1/plain-language/${result.id}?lang=${lang}`, { noAuth: true })
      .then(setPlainSummary)
      .catch(() => {});
    const countryParam = country && country !== "all" ? `&country=${country}` : "";
    api<{ related: RelatedProvision[] }>(`/api/v1/related/${result.id}?limit=5${countryParam}`, { noAuth: true })
      .then((data) => setRelated(data.related || []))
      .catch(() => {})
      .finally(() => setRelatedLoading(false));
    // Track view
    api(`/api/v1/laws/${result.id}/view`, { method: "POST", noAuth: true }).catch(() => {});
    // Check bookmark status
    api<{ bookmarked: boolean; id: number | null }>(`/api/v1/laws/bookmarks/check/${result.id}`)
      .then((data) => { setBookmarked(data.bookmarked); setBookmarkId(data.id); })
      .catch(() => {});
  }, [result.id, locale, country]);

  const handleBookmark = async () => {
    if (bookmarked && bookmarkId) {
      try {
        await api(`/api/v1/laws/bookmarks/${bookmarkId}`, { method: "DELETE" });
        setBookmarked(false);
        setBookmarkId(null);
      } catch {}
    } else {
      try {
        const data = await api<{ id: number }>("/api/v1/laws/bookmarks", {
          method: "POST",
          body: {
            provision_id: result.id,
            country: result.country,
            category: result.category,
            title: result.title,
          },
        });
        setBookmarked(true);
        setBookmarkId(data.id);
      } catch {}
    }
  };

  const handleRelatedClick = (relatedProvision: RelatedProvision) => {
    const params = new URLSearchParams({ q: relatedProvision.title, resultId: relatedProvision.id });
    if (country && country !== "all") params.set("country", country);
    router.push(`/laws?${params}`);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-[90] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto">
        {/* Gradient Header */}
        <div className={`sticky top-0 z-10 bg-gradient-to-br ${th.header} rounded-t-2xl px-5 py-4 flex items-start justify-between`}>
          <div className="min-w-0 pr-3">
            <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/20 text-white uppercase">
                {CAT_LABELS[result.category]?.[locale] || result.category}
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/15 text-white/80">
                {result.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
              </span>
              {result.article_number && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/15 text-white/80 font-mono">
                  Art. {result.article_number}
                </span>
              )}
              {result.confidence && (
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                  result.confidence === "high" ? "bg-emerald-400/20 text-emerald-100" :
                  result.confidence === "medium" ? "bg-amber-400/20 text-amber-100" :
                  "bg-red-400/20 text-red-100"
                }`}>
                  {result.confidence === "high" ? "✓ High" : result.confidence === "medium" ? "~ Medium" : "△ Low"} confidence
                </span>
              )}
            </div>
            <h2 className="text-sm font-bold text-white leading-snug">{result.title}</h2>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={handleBookmark}
              className={`w-7 h-7 rounded-full flex items-center justify-center transition-colors ${
                bookmarked
                  ? "bg-yellow-400 text-yellow-900"
                  : "bg-white/15 hover:bg-white/30 text-white"
              }`}
              title={bookmarked ? translate("laws.remove_bookmark") : translate("laws.bookmark")}
            >
              <svg className="w-3.5 h-3.5" fill={bookmarked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-white/15 hover:bg-white/30 flex items-center justify-center text-white shrink-0 transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="px-5 py-4 space-y-4">
          {/* Relevance */}
          <RelevanceBadge score={result.score} size="md" />

          {/* Source Document */}
          <div className="bg-gray-50 rounded-xl p-3">
            <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">{translate("search_modal.source_document")}</div>
            <div className="text-xs font-medium text-gray-700">
              {DOC_LABELS[result.source_document]?.[locale] || result.source_document?.replace(/_/g, " ") || "—"}
              {result.enactment_year > 0 && (
                <span className={`ml-1.5 ${th.enactment}`}>({result.enactment_year})</span>
              )}
            </div>
            {result.document_type && (
              <div className="text-[10px] text-gray-400 mt-0.5 capitalize">{result.document_type.replace(/_/g, " ")}</div>
            )}
          </div>

          {/* Citation */}
          {result.citation && (
            <div className={`${th.citationBg} rounded-xl p-3 border`}>
              <div className={`text-[10px] ${th.citationLabel} uppercase tracking-wider mb-1`}>{translate("search_modal.citation")}</div>
              <p className={`text-xs ${th.citationText} font-medium font-serif italic leading-relaxed`}>{result.citation}</p>
            </div>
          )}

          {/* Source URL */}
          {result.source_url && (
            <div className="flex items-center gap-2">
              <a
                href={result.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className={`text-[10px] ${th.sourceLink} underline font-medium flex items-center gap-1`}
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                {translate("search_modal.view_official_source")}
              </a>
              {result.last_verified && (
                <span className="text-[10px] text-gray-400">{translate("search_modal.last_verified")}: {result.last_verified}</span>
              )}
            </div>
          )}

          {/* Language & Source Attribution */}
          <div className="flex items-center gap-2 flex-wrap">
            {result.language && (
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                result.language === "hi" ? "bg-orange-50 text-orange-600 border border-orange-200" :
                result.language === "ne" ? "bg-red-50 text-red-600 border border-red-200" :
                "bg-blue-50 text-blue-600 border border-blue-200"
              }`}>
                {result.language === "hi" ? "हिन्दी" : result.language === "ne" ? "नेपाली" : "English"}
              </span>
            )}
            <span className="text-[10px] text-gray-400">{translate("search_modal.text_from_original")}</span>
          </div>

          {/* Full Text with tabs */}
          <div>
            <div className="flex items-center gap-1 mb-2">
              <button
                onClick={() => setActiveTab("legal")}
                className={`text-[10px] font-semibold px-2.5 py-1 rounded-full transition-colors ${
                  activeTab === "legal" ? th.tabActive : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                }`}
              >
                {translate("search_modal.legal_text")}
              </button>
              {plainSummary?.available && (
                <button
                  onClick={() => setActiveTab("plain")}
                  className={`text-[10px] font-semibold px-2.5 py-1 rounded-full transition-colors ${
                    activeTab === "plain" ? "bg-emerald-600 text-white" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                  }`}
                >
                  {translate("search_modal.plain_language")}
                </button>
              )}
            </div>
            {activeTab === "legal" ? (
              <>
                <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1.5">{translate("search_modal.full_text")}</div>
                <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">{result.full_text}</p>
              </>
            ) : (
              <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-200">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <svg className="w-3 h-3 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-[10px] font-semibold text-emerald-700 uppercase">{translate("search_modal.in_plain_language")}</span>
                </div>
                <p className="text-xs text-emerald-800 leading-relaxed">{plainSummary?.summary}</p>
              </div>
            )}
          </div>

          {/* Related Provisions */}
          <div>
            <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-2">{translate("search_modal.related_provisions")}</div>
            {relatedLoading ? (
              <div className="space-y-1.5">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse flex items-center gap-2 p-2 rounded-lg bg-gray-50">
                    <div className="w-5 h-5 bg-gray-200 rounded-full shrink-0" />
                    <div className="h-3 bg-gray-200 rounded flex-1" />
                    <div className="h-3 w-8 bg-gray-100 rounded shrink-0" />
                  </div>
                ))}
              </div>
            ) : related.length > 0 ? (
              <div className="space-y-1.5">
                {related.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => handleRelatedClick(r)}
                    className={`w-full flex items-center gap-2 text-xs p-2.5 rounded-xl bg-gray-50 ${th.relatedHover} border border-transparent transition-all group text-left`}
                  >
                    <span className={`${th.relatedText} shrink-0`}>{r.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                    <span className={`text-gray-700 font-medium truncate group-hover:transition-colors ${isIssues ? "group-hover:text-red-700" : "group-hover:text-cyan-700"}`}>{r.title}</span>
                    {r.article_number && (
                      <span className="text-[10px] text-gray-400 font-mono shrink-0">#{r.article_number}</span>
                    )}
                    <svg className={`w-3 h-3 text-gray-300 shrink-0 ml-auto opacity-0 group-hover:opacity-100 transition-opacity ${th.relatedArrow}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-[10px] text-gray-400 italic">{translate("search_modal.no_related")}</p>
            )}
          </div>

          {/* Provision ID */}
          <div className="flex items-center gap-2 text-[10px] text-gray-300 font-mono"><span>{result.id}</span></div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white rounded-b-2xl border-t border-gray-100 px-5 py-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-gray-400">{translate("search_modal.informational_only")}</span>
            <button
              onClick={handleReport}
              disabled={reported}
              className={`text-[10px] px-2 py-0.5 rounded-full border transition-colors ${
                reported
                  ? "bg-emerald-50 text-emerald-600 border-emerald-200 cursor-default"
                  : "bg-gray-50 text-gray-500 border-gray-200 hover:bg-red-50 hover:text-red-600 hover:border-red-200"
              }`}
            >
              {reported ? translate("search_modal.reported") : translate("search_modal.report")}
            </button>
          </div>
          <button
            onClick={onClose}
            className={`text-xs px-4 py-1.5 rounded-lg ${th.closeBtn} text-white transition-colors font-medium shrink-0`}
          >
            {translate("search_modal.close")}
          </button>
        </div>
      </div>
    </div>
  );
}