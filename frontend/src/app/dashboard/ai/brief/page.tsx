"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { api, ApiError } from "@/lib/api";
import RelevanceBadge from "@/components/RelevanceBadge";

interface CaseBriefResponse {
  summary: string;
  key_issues: string[];
  relevant_laws: Array<{
    id?: string;
    title: string;
    article_number: string;
    source_document: string;
    country: string;
    category: string;
    relevance_score: number;
    key_text: string;
  }>;
  recommended_actions: string[];
  strengths: string[];
  weaknesses: string[];
  precedents: Array<{
    id?: string;
    title: string;
    article_number: string;
    relationship: string;
    country: string;
  }>;
}

const EXAMPLES: Array<{ en: string; ne: string; hi: string }> = [
  { en: "Property dispute between siblings after father's death", ne: "बुबाको मृत्युपछि दाजुभाइबीच सम्पत्ति विवाद", hi: "पिता की मृत्यु के बाद भाइयों के बीच संपत्ति विवाद" },
  { en: "Wrongful termination from employment without notice", ne: "सूचना बिना रोजगारबाट गलत समाप्ति", hi: "बिना नोटिस के रोजगार से गलत समाप्ति" },
  { en: "Domestic violence and protection order", ne: "घरेलु हिंसा र सुरक्षा आदेश", hi: "घरेलू हिंसा और सुरक्षा आदेश" },
  { en: "Consumer fraud in online transaction", ne: "अनलाइन लेनदेनमा उपभोक्ता धोका", hi: "ऑनलाइन लेनदेन में उपभोक्ता धोखा" },
  { en: "Breach of contract by vendor", ne: "विक्रेताद्वारा अनुबन्ध उल्लंघन", hi: "विक्रेता द्वारा अनुबंध का उल्लंघन" },
  { en: "Motor vehicle accident liability", ne: "सवारी साधन दुर्घटना दायित्व", hi: "मोटर वाहन दुर्घटना दायित्व" },
];

export default function CaseBriefPage() {
  const { user } = useAuth();
  const { t, locale } = useI18n();
  const router = useRouter();
  const [description, setDescription] = useState("");
  const [country, setCountry] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CaseBriefResponse | null>(null);
  const [error, setError] = useState("");
  const [showIssues, setShowIssues] = useState(true);
  const [showActions, setShowActions] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(async () => {
    if (!description.trim() || description.length < 10) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api<CaseBriefResponse>("/api/v1/ai/case-brief", {
        method: "POST",
        body: {
          case_description: description.trim(),
          country: country || undefined,
        },
      });
      setResult(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 401) { router.push("/login"); return; }
      setError(err instanceof ApiError ? (err.data as any)?.detail || err.message : err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  }, [description, country, router]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleExampleClick = (ex: { en: string; ne: string; hi: string }) => {
    setDescription(ex[locale as keyof typeof ex] || ex.en);
    textareaRef.current?.focus();
  };

  const handleLawClick = (law: { id?: string; title: string; article_number: string }) => {
    const q = law.title || law.article_number;
    router.push(`/laws?q=${encodeURIComponent(q)}${law.id ? `&resultId=${law.id}` : ""}`);
  };

  if (user?.role !== "lawyer" && user?.role !== "judge") {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="text-4xl mb-4">🔒</div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">{t.ai_tools?.locked_title || "Access Restricted"}</h1>
        <p className="text-sm text-gray-500">{t.ai_tools?.locked_desc || "This feature is available to lawyers and judges only."}</p>
      </div>
    );
  }

  const nepalCount = result?.relevant_laws.filter(l => l.country === "nepal").length || 0;
  const indiaCount = result?.relevant_laws.filter(l => l.country === "india").length || 0;
  const categories = [...new Set(result?.relevant_laws.map(l => l.category).filter(Boolean))];

  return (
    <div className="max-w-4xl">
      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-cyan-600 via-teal-600 to-emerald-700 text-white rounded-xl p-6 sm:p-8 mb-6">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-48 h-48 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-0 w-64 h-64 bg-emerald-300 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold">{t.ai_tools?.case_brief?.title || "Case Brief Generator"}</h1>
          </div>
          <p className="text-cyan-100 text-sm max-w-xl">{t.ai_tools?.case_brief?.description || "Generate a structured case brief with relevant laws and analysis"}</p>
        </div>
      </div>

      {/* Examples */}
      <div className="mb-4">
        <div className="text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-2">
          {t.ai_tools?.precedent?.examples_title || "Try these examples"}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => handleExampleClick(ex)}
              className="text-[11px] px-2.5 py-1 rounded-full border border-cyan-200 text-cyan-700 bg-white hover:bg-cyan-50 hover:border-cyan-300 transition-colors cursor-pointer"
            >
              {ex[locale as keyof typeof ex] || ex.en}
            </button>
          ))}
        </div>
      </div>

      {/* Input form */}
      <div className="bg-white rounded-xl border border-cyan-100 shadow-sm p-4 mb-4">
        <textarea
          ref={textareaRef}
          value={description}
          onChange={e => setDescription(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t.ai_tools?.case_brief?.case_placeholder || "Describe the case, legal situation, or legal question in detail..."}
          className="w-full h-28 text-sm border border-cyan-200 rounded-lg p-3 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 resize-none"
        />
        <div className="flex items-center gap-2 mt-3">
          <select
            value={country}
            onChange={e => setCountry(e.target.value)}
            className="text-xs border border-cyan-200 rounded-lg px-3 py-2 focus:outline-none focus:border-cyan-400 text-gray-700"
          >
            <option value="">{t.ai_tools?.case_brief?.country || "Country (Optional)"}</option>
            <option value="nepal">🇳🇵 Nepal</option>
            <option value="india">🇮🇳 India</option>
          </select>
          <div className="flex-1" />
          <span className="text-[10px] text-gray-400 hidden sm:block">⌘ + Enter to generate</span>
          <button
            onClick={handleSubmit}
            disabled={loading || description.length < 10}
            className="bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700 disabled:opacity-40 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all shadow-sm cursor-pointer"
          >
            {loading ? `⏳ ${t.ai_tools?.case_brief?.generating || "Generating..."}` : `📄 ${t.ai_tools?.case_brief?.generate || "Generate Brief"}`}
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
          <div className="w-10 h-10 border-3 border-cyan-200 border-t-cyan-600 rounded-full animate-spin" />
          <p className="text-sm text-gray-500">{t.ai_tools?.case_brief?.generating || "Generating case brief..."}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl border border-cyan-200 p-5">
            <h2 className="text-[10px] font-semibold text-cyan-600 uppercase tracking-wider mb-2">{t.ai_tools?.case_brief?.summary || "Case Summary"}</h2>
            <p className="text-sm text-gray-700 leading-relaxed">{result.summary}</p>
          </div>

          {/* Summary bar */}
          <div className="flex flex-wrap items-center gap-3 bg-white rounded-lg border border-cyan-100 px-4 py-2.5">
            <span className="text-sm font-semibold text-cyan-700">
              {result.relevant_laws.length} {t.ai_tools?.precedent?.precedents || "laws"} found
            </span>
            {categories.length > 0 && (
              <span className="text-[11px] text-gray-500">
                across {categories.length} areas
              </span>
            )}
            {nepalCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-50 text-red-600 font-medium">🇳🇵 {nepalCount} Nepal</span>
            )}
            {indiaCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 font-medium">🇮🇳 {indiaCount} India</span>
            )}
          </div>

          {/* Key Issues */}
          {result.key_issues.length > 0 && (
            <div className="bg-white rounded-xl border border-cyan-100 overflow-hidden">
              <button
                onClick={() => setShowIssues(!showIssues)}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm font-semibold text-cyan-700 hover:bg-cyan-50 transition-colors cursor-pointer"
              >
                <span className={`transition-transform text-xs ${showIssues ? "rotate-90" : ""}`}>▶</span>
                {t.ai_tools?.case_brief?.key_issues || "Key Issues"}
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-600">{result.key_issues.length}</span>
              </button>
              {showIssues && (
                <div className="px-4 pb-3 space-y-1.5">
                  {result.key_issues.map((issue, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0 mt-1" />
                      {issue}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Relevant Laws */}
          {result.relevant_laws.length > 0 && (
            <div className="bg-white rounded-xl border border-cyan-100 p-4">
              <h3 className="text-sm font-semibold text-cyan-700 mb-3">
                📚 {t.ai_tools?.case_brief?.relevant_laws || "Relevant Laws"} ({result.relevant_laws.length})
              </h3>
              <div className="space-y-2">
                {result.relevant_laws.slice(0, 8).map((law, i) => (
                  <button
                    key={i}
                    onClick={() => handleLawClick(law)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-cyan-50 rounded-lg border border-gray-100 hover:border-cyan-200 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs">{law.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                        <span className="text-sm font-medium text-gray-800 group-hover:text-cyan-700 transition-colors">{law.title}</span>
                      </div>
                      <RelevanceBadge score={law.relevance_score} size="sm" />
                    </div>
                    <div className="text-xs text-gray-500 mb-1">
                      {law.article_number} • {law.source_document?.replace(/_/g, " ")}
                    </div>
                    <p className="text-xs text-gray-600 line-clamp-2">{law.key_text}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-green-100 p-4">
              <h3 className="text-sm font-semibold text-green-700 mb-3">💪 {t.ai_tools?.case_brief?.strengths || "Strengths"}</h3>
              <div className="space-y-1.5">
                {result.strengths.map((s, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                    <span className="text-green-500 shrink-0">✓</span>
                    {s}
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-amber-100 p-4">
              <h3 className="text-sm font-semibold text-amber-700 mb-3">⚠️ {t.ai_tools?.case_brief?.weaknesses || "Weaknesses"}</h3>
              <div className="space-y-1.5">
                {result.weaknesses.map((w, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                    <span className="text-amber-500 shrink-0">!</span>
                    {w}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Actions */}
          {result.recommended_actions.length > 0 && (
            <div className="bg-white rounded-xl border border-cyan-100 overflow-hidden">
              <button
                onClick={() => setShowActions(!showActions)}
                className="w-full flex items-center gap-2 px-4 py-3 text-sm font-semibold text-cyan-700 hover:bg-cyan-50 transition-colors cursor-pointer"
              >
                <span className={`transition-transform text-xs ${showActions ? "rotate-90" : ""}`}>▶</span>
                {t.ai_tools?.case_brief?.recommended_actions || "Recommended Actions"}
                <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-cyan-100 text-cyan-600">{result.recommended_actions.length}</span>
              </button>
              {showActions && (
                <div className="px-4 pb-3 space-y-1.5">
                  {result.recommended_actions.map((action, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                      <span className="w-4 h-4 rounded-full bg-cyan-100 text-cyan-600 flex items-center justify-center shrink-0 text-[9px] font-bold">{i + 1}</span>
                      {action}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Related Precedents */}
          {result.precedents.length > 0 && (
            <div className="bg-white rounded-xl border border-cyan-100 p-4">
              <h3 className="text-sm font-semibold text-cyan-700 mb-3">🔗 {t.ai_tools?.case_brief?.precedents || "Related Precedents"}</h3>
              <div className="space-y-2">
                {result.precedents.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      const q = p.title || p.article_number;
                      router.push(`/laws?q=${encodeURIComponent(q)}${p.id ? `&resultId=${p.id}` : ""}`);
                    }}
                    className="w-full text-left flex items-center gap-3 p-2.5 bg-gray-50 hover:bg-cyan-50 rounded-lg transition-colors cursor-pointer group"
                  >
                    <span className="text-xs">{p.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-800 group-hover:text-cyan-700 transition-colors truncate">{p.title}</div>
                      <div className="text-[10px] text-gray-500">{p.article_number}</div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 shrink-0">
                      {p.relationship}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}