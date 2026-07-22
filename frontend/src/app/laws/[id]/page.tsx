"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import SearchResultModal from "@/components/SearchResultModal";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";

interface LawDetail {
  id: string;
  title: string;
  full_text: string;
  country: string;
  category: string;
  document_type: string;
  article_number: string;
  source_document: string;
  language?: string;
  citation?: string;
  last_verified?: string;
  source_url?: string;
  effective_date?: string;
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

export default function LawDetailPage() {
  const { id } = useParams();
  const { translate, locale } = useI18n();
  const [law, setLaw] = useState<LawDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bookmarked, setBookmarked] = useState(false);
  const [bookmarkId, setBookmarkId] = useState<number | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchLaw = async () => {
      try {
        const data = await api<LawDetail>(`/api/v1/laws/${id}`, { noAuth: true });
        setLaw(data);
        api(`/api/v1/laws/${id}/view`, { method: "POST" }).catch(() => {});
        api(`/api/v1/laws/bookmarks/check/${id}`)
          .then((data: any) => { setBookmarked(data.bookmarked); setBookmarkId(data.id); })
          .catch(() => {});
      } catch (e) {
        setError("Law not found");
      } finally {
        setLoading(false);
      }
    };
    fetchLaw();
  }, [id]);

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
            provision_id: law?.id,
            country: law?.country,
            category: law?.category,
            title: law?.title,
          },
        });
        setBookmarked(true);
        setBookmarkId(data.id);
      } catch {}
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-3/4 bg-gray-200 rounded" />
            <div className="h-4 w-1/2 bg-gray-100 rounded" />
            <div className="h-32 bg-gray-100 rounded-xl" />
          </div>
        </div>
      </>
    );
  }

  if (error || !law) {
    return (
      <>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <div className="text-4xl mb-3">📚</div>
          <p className="text-sm text-gray-500">{error || "Law not found"}</p>
        </div>
      </>
    );
  }

  const catColor = CAT_COLORS[law.category] || "bg-gray-50 text-gray-600 border-gray-100";

  return (
    <>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-6 pb-20 md:pb-6">
        <DisclaimerBanner />

        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${catColor}`}>
                  {CAT_LABELS[law.category]?.[locale] || law.category}
                </span>
                <span className="text-xs px-3 py-1 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                  {law.country === "nepal" ? "🇳🇵 Nepal" : "🇮🇳 India"}
                </span>
                {law.article_number && (
                  <span className="text-xs text-gray-400 font-mono">Art. {law.article_number}</span>
                )}
              </div>
              <h1 className="text-xl font-bold text-gray-900 mb-2">{law.title}</h1>
              <p className="text-sm text-gray-500">
                {law.source_document?.replace(/_/g, " ")}
              </p>
            </div>
            <button
              onClick={handleBookmark}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                bookmarked
                  ? "bg-yellow-100 text-yellow-700 border border-yellow-200"
                  : "bg-gray-100 text-gray-600 border border-gray-200 hover:bg-yellow-50 hover:text-yellow-600 hover:border-yellow-200"
              }`}
            >
              {bookmarked ? translate("laws.bookmarked") : translate("laws.bookmark")}
            </button>
          </div>
        </div>

        {/* Citation */}
        {law.citation && (
          <div className="bg-cyan-50 rounded-2xl border border-cyan-100 p-4 mb-4">
            <div className="text-[10px] text-cyan-500 uppercase tracking-wider mb-1">{translate("search_modal.citation")}</div>
            <p className="text-sm text-cyan-800 font-medium font-serif italic">{law.citation}</p>
          </div>
        )}

        {/* Source URL */}
        {law.source_url && (
          <div className="mb-4">
            <a
              href={law.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-cyan-600 hover:text-cyan-800 underline font-medium flex items-center gap-1"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              {translate("search_modal.view_official_source")}
            </a>
          </div>
        )}

        {/* Full Text */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6">
          <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-3">{translate("search_modal.full_text")}</div>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{law.full_text}</p>
        </div>

        {/* Metadata */}
        <div className="mt-4 flex items-center gap-4 text-[10px] text-gray-400">
          <span>{translate("search_modal.last_verified")}: {law.last_verified}</span>
          <span>{law.language === "ne" ? "नेपाली" : law.language === "hi" ? "हिन्दी" : "English"}</span>
        </div>
      </div>
    </>
  );
}