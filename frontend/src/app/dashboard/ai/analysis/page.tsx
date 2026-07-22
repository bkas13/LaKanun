"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { api, rawFetch, ApiError } from "@/lib/api";
import RelevanceBadge from "@/components/RelevanceBadge";

interface ArgumentAnalysisResponse {
  strength_score: number;
  strength_level: string;
  supporting_laws: Array<{
    id?: string;
    title: string;
    article_number: string;
    source_document: string;
    country: string;
    relevance_score: number;
    key_text: string;
  }>;
  counterarguments: string[];
  recommendations: string[];
  risk_factors: string[];
}

interface UploadedDoc {
  filename: string;
  file_type: string;
  text: string;
  page_count?: number;
  char_count: number;
}

const EXAMPLES: Array<{ en: string; ne: string; hi: string }> = [
  { en: "Employer terminated without notice period", ne: "रोजगारदाताले सूचना अवधि बिना समाप्त गर्यो", hi: "नियोक्ता ने बिना नोटिस अवधि के समाप्त कर दिया" },
  { en: "Landlord refusing to return security deposit", ne: "मालिकले सुरक्षा जम्मा फिर्ता गर्न अस्वीकार गर्दै", hi: "मालिक सुरक्षा जमा वापस करने से इनकार कर रहा है" },
  { en: "Insurance claim denied after accident", ne: "दुर्घटनापछि बीमा दावी अस्वीकार", hi: "दुर्घटना के बाद बीमा दावा अस्वीकृत" },
  { en: "Neighbor encroaching on property boundary", ne: "छिमेकीले सम्पत्ति सीमा अतिक्रमण गर्दै", hi: "पड़ोसी संपत्ति सीमा का उल्लंघन कर रहा है" },
  { en: "Online seller delivered defective product", ne: "अनलाइन विक्रेताले दोषपूर्ण उत्पादन पठायो", hi: "ऑनलाइन विक्रेता ने दोषपूर्ण उत्पादन भेजा" },
  { en: "Wrongful arrest by police without warrant", ne: "वारेन्ट बिना प्रहरीद्वारा गलत गिरफ्तारी", hi: "वारंट के बिना पुलिस द्वारा गलत गिरफ्तारी" },
];

export default function ArgumentAnalysisPage() {
  const { user } = useAuth();
  const { t, locale } = useI18n();
  const router = useRouter();
  const [argument, setArgument] = useState("");
  const [opposingView, setOpposingView] = useState("");
  const [country, setCountry] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ArgumentAnalysisResponse | null>(null);
  const [error, setError] = useState("");

  // Document upload state
  const [uploadedDoc, setUploadedDoc] = useState<UploadedDoc | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleUpload = useCallback(async (file: File) => {
    setUploading(true);
    setUploadError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const doc: UploadedDoc = await rawFetch("/api/v1/ai/upload-document", {
        method: "POST",
        body: formData,
      });
      setUploadedDoc(doc);
      // Auto-populate argument from document if empty
      if (!argument.trim() && doc.file_type !== "image") {
        const preview = doc.text.slice(0, 500);
        setArgument(preview);
      }
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 401) { router.push("/login"); return; }
      setUploadError(err instanceof ApiError ? (err.data as any)?.detail || err.message : err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [argument, router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleSubmit = useCallback(async () => {
    if (!argument.trim() || argument.length < 10) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api<ArgumentAnalysisResponse>("/api/v1/ai/analyze-argument", {
        method: "POST",
        body: {
          argument: argument.trim(),
          country: country || undefined,
          opposing_view: opposingView || undefined,
          document_text: uploadedDoc?.text || undefined,
        },
      });
      setResult(data);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 401) { router.push("/login"); return; }
      setError(err instanceof ApiError ? (err.data as any)?.detail || err.message : err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  }, [argument, country, opposingView, uploadedDoc, router]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleExampleClick = (ex: { en: string; ne: string; hi: string }) => {
    setArgument(ex[locale as keyof typeof ex] || ex.en);
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

  const nepalCount = result?.supporting_laws.filter(l => l.country === "nepal").length || 0;
  const indiaCount = result?.supporting_laws.filter(l => l.country === "india").length || 0;

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
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold">{t.ai_tools?.analysis?.title || "Argument Analysis"}</h1>
          </div>
          <p className="text-purple-100 text-sm max-w-xl">{t.ai_tools?.analysis?.description || "Analyze the strength of a legal argument with supporting laws"}</p>
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
              className="text-[11px] px-2.5 py-1 rounded-full border border-purple-200 text-purple-700 bg-white hover:bg-purple-50 hover:border-purple-300 transition-colors cursor-pointer"
            >
              {ex[locale as keyof typeof ex] || ex.en}
            </button>
          ))}
        </div>
      </div>

      {/* Input form */}
      <div className="bg-white rounded-xl border border-purple-100 shadow-sm p-4 mb-4">
        {/* Document upload zone */}
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`mb-3 border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all ${
            dragOver
              ? "border-purple-400 bg-purple-50"
              : uploadedDoc
                ? "border-green-200 bg-green-50"
                : "border-gray-200 hover:border-purple-300 hover:bg-purple-50/50"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md,.png,.jpg,.jpeg,.webp"
            onChange={handleFileChange}
            className="hidden"
          />
          {uploading ? (
            <div className="flex items-center justify-center gap-2 py-2">
              <div className="w-4 h-4 border-2 border-purple-300 border-t-purple-600 rounded-full animate-spin" />
              <span className="text-xs text-gray-500">Uploading...</span>
            </div>
          ) : uploadedDoc ? (
            <div className="flex items-center justify-between py-1">
              <div className="flex items-center gap-2">
                <span className="text-lg">
                  {uploadedDoc.file_type === "pdf" ? "📄" : uploadedDoc.file_type === "image" ? "🖼️" : "📝"}
                </span>
                <div className="text-left">
                  <div className="text-xs font-medium text-green-700">{uploadedDoc.filename}</div>
                  <div className="text-[10px] text-gray-500">
                    {uploadedDoc.char_count.toLocaleString()} chars
                    {uploadedDoc.page_count ? ` • ${uploadedDoc.page_count} pages` : ""}
                  </div>
                </div>
              </div>
              <button
                onClick={e => { e.stopPropagation(); setUploadedDoc(null); setArgument(""); }}
                className="text-[10px] text-gray-400 hover:text-red-500 transition-colors px-2 py-1"
              >
                ✕ Remove
              </button>
            </div>
          ) : (
            <div className="py-1">
              <div className="text-lg mb-1">📎</div>
              <p className="text-xs text-gray-500">
                Drop a document here or <span className="text-purple-600 font-medium">browse</span>
              </p>
              <p className="text-[10px] text-gray-400 mt-0.5">PDF, TXT, PNG, JPG — up to 20MB</p>
            </div>
          )}
        </div>
        {uploadError && <div className="text-xs text-red-600 mb-2">{uploadError}</div>}

        <textarea
          ref={textareaRef}
          value={argument}
          onChange={e => setArgument(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t.ai_tools?.analysis?.argument_placeholder || "Present your legal argument or position..."}
          className="w-full h-24 text-sm border border-purple-200 rounded-lg p-3 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100 resize-none"
        />
        <div className="text-[10px] text-gray-400 mt-1">{argument.length}/5000 characters</div>

        <div className="mt-2">
          <label className="block text-[10px] font-medium text-gray-500 uppercase tracking-wider mb-1">
            {t.ai_tools?.analysis?.opposing_view || "Opposing View (Optional)"}
          </label>
          <textarea
            value={opposingView}
            onChange={e => setOpposingView(e.target.value)}
            placeholder={t.ai_tools?.analysis?.opposing_placeholder || "If you know the opposing argument, enter it here..."}
            className="w-full h-16 text-xs border border-purple-200 rounded-lg p-3 focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100 resize-none"
          />
        </div>

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
          <span className="text-[10px] text-gray-400 hidden sm:block">⌘ + Enter to analyze</span>
          <button
            onClick={handleSubmit}
            disabled={loading || argument.length < 10}
            className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 disabled:opacity-40 text-white px-5 py-2 rounded-lg text-sm font-medium transition-all shadow-sm cursor-pointer"
          >
            {loading ? `⏳ ${t.ai_tools?.analysis?.analyzing || "Analyzing..."}` : `🔍 ${t.ai_tools?.analysis?.analyze || "Analyze Argument"}`}
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
          <p className="text-sm text-gray-500">{t.ai_tools?.analysis?.analyzing || "Analyzing argument strength..."}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-4">
          {/* Strength Score */}
          <RelevanceBadge score={result.strength_score} size="lg" showLabel />

          {/* Summary bar */}
          <div className="flex flex-wrap items-center gap-3 bg-white rounded-lg border border-purple-100 px-4 py-2.5">
            <span className="text-sm font-semibold text-purple-700">
              {result.supporting_laws.length} {t.ai_tools?.precedent?.precedents || "supporting laws"}
            </span>
            {nepalCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-red-50 text-red-600 font-medium">🇳🇵 {nepalCount} Nepal</span>
            )}
            {indiaCount > 0 && (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 font-medium">🇮🇳 {indiaCount} India</span>
            )}
          </div>

          {/* Supporting Laws */}
          {result.supporting_laws.length > 0 && (
            <div className="bg-white rounded-xl border border-purple-100 p-4">
              <h3 className="text-sm font-semibold text-purple-700 mb-3">
                📚 {t.ai_tools?.analysis?.supporting_laws || "Supporting Laws"} ({result.supporting_laws.length})
              </h3>
              <div className="space-y-2">
                {result.supporting_laws.slice(0, 8).map((law, i) => (
                  <button
                    key={i}
                    onClick={() => handleLawClick(law)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-purple-50 rounded-lg border border-gray-100 hover:border-purple-200 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs">{law.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                        <span className="text-sm font-medium text-gray-800 group-hover:text-purple-700 transition-colors">{law.title}</span>
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

          {/* Counterarguments & Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border border-purple-100 p-4">
              <h3 className="text-sm font-semibold text-amber-700 mb-3">🛡️ {t.ai_tools?.analysis?.counterarguments || "Counterarguments"}</h3>
              <div className="space-y-1.5">
                {result.counterarguments.map((c, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-1" />
                    {c}
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-purple-100 p-4">
              <h3 className="text-sm font-semibold text-cyan-700 mb-3">💡 {t.ai_tools?.analysis?.recommendations || "Recommendations"}</h3>
              <div className="space-y-1.5">
                {result.recommendations.map((r, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-gray-600 py-1">
                    <span className="w-4 h-4 rounded-full bg-cyan-100 text-cyan-600 flex items-center justify-center shrink-0 text-[9px] font-bold">{i + 1}</span>
                    {r}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Risk Factors */}
          {result.risk_factors.length > 0 && (
            <div className="bg-white rounded-xl border border-purple-100 p-4">
              <h3 className="text-sm font-semibold text-red-700 mb-3">⚠️ {t.ai_tools?.analysis?.risk_factors || "Risk Factors"}</h3>
              <div className="flex flex-wrap gap-2">
                {result.risk_factors.map((risk, i) => (
                  <span key={i} className="text-xs px-3 py-1.5 rounded-full bg-red-50 text-red-700 border border-red-200">
                    {risk}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}