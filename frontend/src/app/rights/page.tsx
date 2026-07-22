"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";

interface RightsScenario {
  id: string;
  category: string;
  title: string;
  description: string;
}

interface RightsDetail {
  id: string;
  category: string;
  title: string;
  description: string;
  your_rights: string[];
  what_authorities_must_do: string[];
  deadlines: string;
  where_to_go: string;
  provisions: { country: string; article_id: string; title: string }[];
}

const CATEGORY_ICONS: Record<string, string> = {
  criminal: "⚖️",
  family: "👨‍👩‍👧",
  property: "🏠",
  labor: "💼",
  consumer: "🛒",
  child: "👶",
  cyber: "💻",
  constitutional: "📜",
  civil: "🏘️",
};

export default function RightsPage() {
  const { locale, country, translate } = useI18n();
  const [scenarios, setScenarios] = useState<RightsScenario[]>([]);
  const [selected, setSelected] = useState<RightsDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const lang = locale || "en";
    api<{ scenarios: RightsScenario[] }>(`/api/v1/rights?lang=${lang}`, { noAuth: true })
      .then((data) => {
        setScenarios(data.scenarios || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [locale]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (id) loadDetail(id);
  }, []);

  const loadDetail = async (id: string) => {
    setDetailLoading(true);
    try {
      const lang = locale || "en";
      const data = await api<RightsDetail>(`/api/v1/rights/${id}?lang=${lang}`, { noAuth: true });
      setSelected(data);
    } catch {
      // ignore
    }
    setDetailLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 md:pb-0">
      <Navbar />

      {selected ? (
        /* ─── Detail View ──────────────────────────────────────── */
        <div className="max-w-2xl mx-auto px-4 py-8">
          <button
            onClick={() => setSelected(null)}
            className="text-sm text-cyan-600 hover:text-cyan-700 mb-6 flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            {translate("rights_page.back")}
          </button>

          <DisclaimerBanner />

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
            <div className="text-3xl mb-3">{CATEGORY_ICONS[selected.category] || "📋"}</div>
            <h1 className="text-xl font-bold text-gray-900 mb-2">{selected.title}</h1>
            <p className="text-sm text-gray-600 leading-relaxed">{selected.description}</p>
          </div>

          {/* Your Rights */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
            <h2 className="text-sm font-bold text-cyan-700 uppercase tracking-wider mb-3">
              {translate("rights_page.your_rights")}
            </h2>
            <ul className="space-y-2.5">
              {(selected.your_rights || []).map((right: string, i: number) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="text-cyan-500 mt-0.5 shrink-0">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </span>
                  <span className="text-sm text-gray-700">{right}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* What Authorities Must Do */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
            <h2 className="text-sm font-bold text-orange-600 uppercase tracking-wider mb-3">
              {translate("rights_page.authorities_must")}
            </h2>
            <ul className="space-y-2.5">
              {(selected.what_authorities_must_do || []).map((item: string, i: number) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="text-orange-500 mt-0.5 shrink-0">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </span>
                  <span className="text-sm text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Deadlines */}
          <div className="bg-amber-50 rounded-2xl border border-amber-200 p-6 mb-4">
            <h2 className="text-sm font-bold text-amber-700 uppercase tracking-wider mb-2">
              {translate("rights_page.deadlines")}
            </h2>
            <p className="text-sm text-amber-800">{selected.deadlines}</p>
          </div>

          {/* Where to Go */}
          <div className="bg-blue-50 rounded-2xl border border-blue-200 p-6 mb-4">
            <h2 className="text-sm font-bold text-blue-700 uppercase tracking-wider mb-2">
              {translate("rights_page.where_to_go")}
            </h2>
            <p className="text-sm text-blue-800">{selected.where_to_go}</p>
          </div>

          {/* Legal Provisions */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
              {translate("rights_page.linked_provisions")}
            </h2>
            <div className="space-y-2">
              {(selected.provisions || [])
                .filter((p: { country: string }) => !country || country === "all" || p.country === country)
                .map((p: { country: string; article_id: string; title: string }, i: number) => (
                <div key={i} className="flex items-center gap-2 text-xs p-2 rounded-lg bg-gray-50">
                  <span>{p.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                  <span className="font-medium text-gray-700">{p.title}</span>
                  <span className="text-gray-400 ml-auto">({p.article_id})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-center print:hidden">
            <p className="text-xs text-gray-400 mb-3">{translate("rights_page.disclaimer")}</p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => window.print()}
                className="text-xs px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors font-medium inline-flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                {translate("rights_page.print")}
              </button>
              <button
                onClick={() => {
                  const url = `${window.location.origin}/rights?id=${selected.id}`;
                  navigator.clipboard.writeText(url);
                }}
                className="text-xs px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors font-medium inline-flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                {translate("rights_page.share")}
              </button>
              <button
                onClick={() => setSelected(null)}
                className="text-xs px-4 py-2 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 transition-colors"
              >
                {translate("rights_page.view_another")}
              </button>
            </div>
          </div>

          {/* Print-only rights card */}
          <style>{`@media print { body * { visibility: hidden; } .print-rights-card, .print-rights-card * { visibility: visible; } .print-rights-card { position: absolute; left: 0; top: 0; width: 100%; padding: 20px; } }`}</style>
          <div className="print-rights-card hidden print:block">
            <h1 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>⚖️ {selected.title}</h1>
            <p style={{ fontSize: '12px', marginBottom: '16px' }}>{selected.description}</p>
            <h2 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>{translate("rights_page.your_rights")}:</h2>
            <ul style={{ fontSize: '11px', marginBottom: '12px', paddingLeft: '20px' }}>
              {(selected.your_rights || []).map((r: string, i: number) => <li key={i} style={{ marginBottom: '4px' }}>{r}</li>)}
            </ul>
            <h2 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>{translate("rights_page.deadlines")}:</h2>
            <p style={{ fontSize: '11px', marginBottom: '12px' }}>{selected.deadlines}</p>
            <h2 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>{translate("rights_page.where_to_go")}:</h2>
            <p style={{ fontSize: '11px', marginBottom: '12px' }}>{selected.where_to_go}</p>
            <p style={{ fontSize: '9px', color: '#999', marginTop: '16px' }}>{translate("rights_page.print_disclaimer")} {window.location.origin}</p>
          </div>
        </div>
      ) : (
        /* ─── List View ────────────────────────────────────────── */
        <>
          <div className="bg-gradient-to-br from-cyan-700 to-cyan-800 text-white py-12 px-4">
            <div className="max-w-4xl mx-auto text-center">
              <div className="text-4xl mb-4">⚖️</div>
              <h1 className="text-2xl font-bold mb-2">{translate("rights_page.title")}</h1>
              <p className="text-cyan-100 text-sm max-w-lg mx-auto">{translate("rights_page.subtitle")}</p>
            </div>
          </div>

          <div className="max-w-4xl mx-auto px-4 py-8">
            <DisclaimerBanner />
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="bg-white rounded-2xl p-5 animate-pulse">
                    <div className="w-10 h-10 bg-gray-200 rounded-xl mb-3" />
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                    <div className="h-3 bg-gray-100 rounded w-full" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {scenarios.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => loadDetail(s.id)}
                    disabled={detailLoading}
                    className="bg-white rounded-2xl overflow-hidden text-left border border-gray-100 hover:border-cyan-300 hover:shadow-md transition-all group"
                  >
                    <div className="h-1 bg-gradient-to-r from-cyan-400 to-cyan-600" />
                    <div className="p-5">
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-3xl">{CATEGORY_ICONS[s.category] || "📋"}</div>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-600 border border-cyan-100 capitalize">
                          {translate(`rights_page.categories.${s.category}`) || s.category}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-gray-900 group-hover:text-cyan-700 transition-colors mb-1.5">
                        {s.title}
                      </h3>
                      <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
                        {s.description}
                      </p>
                      <div className="mt-3 flex items-center gap-1 text-cyan-600 opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="text-[10px] font-medium">{translate("rights_page.learn_more")}</span>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            <div className="mt-12 text-center">
              <p className="text-xs text-gray-400 mb-4">{translate("rights_page.disclaimer")}</p>
              <Link
                href="/issues"
                className="inline-flex items-center gap-2 text-sm text-cyan-600 hover:text-cyan-700 font-medium"
              >
                {translate("rights_page.describe_issue")}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}