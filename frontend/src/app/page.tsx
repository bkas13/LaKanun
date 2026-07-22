"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useI18n } from "@/contexts/I18nContext";
import Navbar from "@/components/Navbar";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import { useAuth } from "@/contexts/AuthContext";

const RIGHTS_CARD_CATEGORIES = [
  { key: "constitutional", icon: "📜", i18nTitle: "know_your_rights.rights[0].title", i18nDesc: "know_your_rights.rights[0].desc" },
  { key: "criminal", icon: "⚖️", i18nTitle: "know_your_rights.rights[1].title", i18nDesc: "know_your_rights.rights[1].desc" },
  { key: "family", icon: "👨‍👩‍👧", i18nTitle: "know_your_rights.rights[2].title", i18nDesc: "know_your_rights.rights[2].desc" },
  { key: "property", icon: "🏠", i18nTitle: "know_your_rights.rights[3].title", i18nDesc: "know_your_rights.rights[3].desc" },
  { key: "labor", icon: "💼", i18nTitle: "know_your_issues.samples[3].title", i18nDesc: "know_your_issues.samples[3].query" },
  { key: "consumer", icon: "🛡️", i18nTitle: "know_your_issues.samples[4].title", i18nDesc: "know_your_issues.samples[4].query" },
  { key: "child", icon: "👶", i18nTitle: "know_your_issues.samples[5].title", i18nDesc: "know_your_issues.samples[5].query" },
  { key: "cyber", icon: "💻", i18nTitle: "know_your_issues.samples[6].title", i18nDesc: "know_your_issues.samples[6].query" },
];

const ISSUE_CARD_SAMPLES = [
  { icon: "🚔", i18nTitle: "know_your_issues.samples[0].title", i18nQuery: "know_your_issues.samples[0].query" },
  { icon: "🏠", i18nTitle: "know_your_issues.samples[1].title", i18nQuery: "know_your_issues.samples[1].query" },
  { icon: "🔑", i18nTitle: "know_your_issues.samples[2].title", i18nQuery: "know_your_issues.samples[2].query" },
  { icon: "💼", i18nTitle: "know_your_issues.samples[3].title", i18nQuery: "know_your_issues.samples[3].query" },
  { icon: "🛡️", i18nTitle: "know_your_issues.samples[4].title", i18nQuery: "know_your_issues.samples[4].query" },
  { icon: "⚖️", i18nTitle: "know_your_issues.samples[5].title", i18nQuery: "know_your_issues.samples[5].query" },
  { icon: "💻", i18nTitle: "know_your_issues.samples[6].title", i18nQuery: "know_your_issues.samples[6].query" },
  { icon: "🆓", i18nTitle: "know_your_issues.samples[7].title", i18nQuery: "know_your_issues.samples[7].query" },
];

export default function HomePage() {
  const { t, translate, country } = useI18n();
  const { user } = useAuth();
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    const seen = localStorage.getItem("welcome_seen");
    if (!seen) setShowWelcome(true);
  }, []);

  return (
    <>
      <Navbar />
      <DisclaimerBanner />

      {/* Welcome Banner */}
      {showWelcome && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/30 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto">
            <div className="bg-gradient-to-br from-cyan-600 to-cyan-700 rounded-t-2xl px-5 py-4 text-white">
              <h2 className="text-lg font-bold">🙏 {translate("usecase_banner.title")}</h2>
              <p className="text-cyan-100 text-sm mt-1">{translate("usecase_banner.subtitle")}</p>
            </div>
            <div className="p-5 space-y-4">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">{translate("usecase_banner.features_title")}</h3>
              <div className="space-y-3">
                {t.usecase_banner.features.map((f: any, i: number) => (
                  <div key={`feat-${i}`} className="flex items-start gap-3">
                    <span className="text-xl shrink-0">{f.icon}</span>
                    <div>
                      <div className="font-medium text-gray-900">{f.title}</div>
                      <div className="text-xs text-gray-500">{f.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="border-t border-gray-100 pt-3">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">{translate("usecase_banner.privacy_title")}</h3>
                <p className="text-xs text-gray-500 mb-3">{translate("usecase_banner.privacy_desc")}</p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {t.usecase_banner.privacy_items.map((item: any, i: number) => (
                    <label key={`priv-${i}`} className="flex items-start gap-2 cursor-pointer">
                      <input type="checkbox" defaultChecked={item.key !== "analytics" && item.key !== "legal_updates"} className="mt-1 w-4 h-4 text-cyan-600 border-gray-300 rounded focus:ring-cyan-500" />
                      <div>
                        <div className="text-xs font-medium text-gray-800">{item.label}</div>
                        <div className="text-[10px] text-gray-400">{item.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
                <button onClick={() => { localStorage.setItem("welcome_seen", "true"); setShowWelcome(false); }} className="w-full mt-4 py-2.5 bg-cyan-600 text-white text-sm font-semibold rounded-xl hover:bg-cyan-700 transition-colors">{translate("usecase_banner.dismiss")}</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hero */}
      <section className="relative bg-gradient-to-br from-cyan-700 via-cyan-800 to-cyan-900 text-white">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
        <div className="relative max-w-4xl mx-auto px-4 py-14 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 border border-white/20 mb-4">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-100">{translate("app_name")}</span>
          </div>
          <h1 className="text-3xl font-bold mb-2 tracking-tight">{translate("tagline")}</h1>
          <p className="text-cyan-100 text-sm max-w-xl mx-auto mb-6 leading-relaxed">{translate("quote")}</p>
          <div className="flex items-center gap-3 justify-center flex-wrap">
            <Link href="/laws" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white text-cyan-700 text-sm font-semibold hover:bg-cyan-50 transition-colors shadow-lg">
              {translate("nav.browse_laws")}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
            </Link>
            <Link href="/rights" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border-2 border-white/30 text-white text-sm font-semibold hover:bg-white/10 transition-colors">
              {translate("nav.rights")}
            </Link>
          </div>
        </div>
      </section>

      <main className="max-w-4xl mx-auto px-4 py-6 pb-20 md:pb-6">

        {/* Know Your Rights section */}
        <section className="mt-8" aria-labelledby="rights-heading">
          <div className="flex items-center gap-3 mb-5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-violet-600 to-purple-600 text-white">
              <span className="text-lg">⚖️</span>
              <span className="text-[11px] font-bold uppercase tracking-wider">{translate("homepage.know_your_rights_badge")}</span>
            </div>
            <h2 id="rights-heading" className="text-xl font-bold text-gray-900">{translate("know_your_rights.title")}</h2>
          </div>
          <p className="text-sm text-gray-500 mb-5 max-w-2xl">
            {country === "nepal" ? translate("homepage.know_your_rights_desc_nepal") : translate("homepage.know_your_rights_desc_india")}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
            {RIGHTS_CARD_CATEGORIES.map((cat, i) => (
              <Link
                key={`rights-${i}`}
                href={`/rights?category=${cat.key}`}
                className="group bg-white rounded-2xl border border-gray-100 p-5 hover:border-violet-300 hover:shadow-lg transition-all"
              >
                <div className="text-4xl mb-3">{cat.icon}</div>
                <h3 className="font-semibold text-sm text-gray-900 group-hover:text-violet-700 transition-colors mb-1.5">
                  {translate(cat.i18nTitle)}
                </h3>
                <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
                  {translate(cat.i18nDesc)}
                </p>
                <div className="mt-3 flex items-center gap-1 text-violet-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-[10px] font-medium">{translate("homepage.explore_all_rights")}</span>
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
          <div className="text-center">
            <Link href="/rights" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white font-semibold hover:from-violet-700 hover:to-purple-700 transition-all shadow-lg">
              {translate("homepage.explore_all_rights")}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </section>

        {/* Know Your Issues section */}
        <section className="mt-14" aria-labelledby="issues-heading">
          <div className="flex items-center gap-3 mb-5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-600 to-orange-600 text-white">
              <span className="text-lg">⚖️</span>
              <span className="text-[11px] font-bold uppercase tracking-wider">{translate("homepage.know_your_issues_badge")}</span>
            </div>
            <h2 id="issues-heading" className="text-xl font-bold text-gray-900">{translate("know_your_issues.title")}</h2>
          </div>
          <p className="text-sm text-gray-500 mb-5 max-w-2xl">{translate("know_your_issues.subtitle")}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
            {ISSUE_CARD_SAMPLES.map((cat, i) => {
              const issueQuery = translate(cat.i18nQuery);
              return (
                <Link
                  key={`issue-${i}`}
                  href={`/issues?q=${encodeURIComponent(issueQuery)}`}
                  className="group bg-white rounded-2xl border border-gray-100 p-5 hover:border-amber-300 hover:shadow-lg transition-all text-left"
                >
                  <div className="text-4xl mb-3">{cat.icon}</div>
                  <h3 className="font-semibold text-sm text-gray-900 group-hover:text-amber-700 transition-colors mb-1.5">
                    {translate(cat.i18nTitle)}
                  </h3>
                  <p className="text-[11px] text-gray-500 leading-relaxed line-clamp-2">
                    {issueQuery}
                  </p>
                  <div className="mt-3 flex items-center gap-1 text-amber-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] font-medium">{translate("homepage.find_laws_cta")}</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </Link>
              );
            })}
          </div>
          <div className="text-center">
            <Link href="/issues" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-orange-600 text-white font-semibold hover:from-amber-700 hover:to-orange-700 transition-all shadow-lg">
              {translate("know_your_issues.cta")}
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </section>

        {/* How it works */}
        <section className="mt-14" aria-labelledby="how-heading">
          <h2 id="how-heading" className="text-xl font-bold text-gray-900 text-center mb-8">{translate("how_it_works.title")}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: "🌐", title: translate("how_it_works.step1_title"), desc: translate("how_it_works.step1_desc") },
              { icon: "📊", title: translate("how_it_works.step2_title"), desc: translate("how_it_works.step2_desc") },
              { icon: "💾", title: translate("how_it_works.step3_title"), desc: translate("how_it_works.step3_desc") },
            ].map((step, i) => (
              <div key={`step-${i}`} className="bg-white rounded-2xl border border-gray-100 p-6 text-center">
                <div className="text-4xl mb-3">{step.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1.5">{step.title}</h3>
                <p className="text-sm text-gray-500">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ section */}
        <section className="mt-14" aria-labelledby="faq-heading">
          <div className="flex items-center gap-3 mb-5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 text-slate-700">
              <span className="text-lg">❓</span>
              <span className="text-[11px] font-bold uppercase tracking-wider">{translate("homepage.faq_badge")}</span>
            </div>
            <h2 id="faq-heading" className="text-xl font-bold text-gray-900">{translate("faq_page.title")}</h2>
          </div>
          <div className="space-y-3 max-w-2xl">
            {t.faq_page.how_to_use.items.slice(0, 3).map((item: any, i: number) => (
              <details key={`faq-${i}`} className="group bg-white rounded-xl border border-gray-200 overflow-hidden">
                <summary className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 cursor-pointer list-none">
                  <span className="text-sm font-medium text-gray-800 pr-3">{item.q}</span>
                  <svg className="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <div className="px-4 pb-3 text-xs text-gray-600 leading-relaxed border-t border-gray-100 pt-2">{item.a}</div>
              </details>
            ))}
          </div>
          <div className="text-center mt-4">
            <Link href="/faq" className="text-sm text-cyan-600 hover:text-cyan-700 font-medium">{translate("faq_page.title")} →</Link>
          </div>
        </section>

        {/* CTA for new users */}
        {!user && (
          <section className="mt-14 bg-gradient-to-br from-cyan-600 to-cyan-700 rounded-2xl p-8 text-white text-center">
            <h2 className="text-xl font-bold mb-2">{translate("cta.title")}</h2>
            <p className="text-cyan-100 text-sm mb-6 max-w-lg mx-auto">{translate("cta.desc")}</p>
            <div className="flex gap-3 justify-center">
              <Link href="/register" className="px-6 py-2.5 bg-white text-cyan-700 text-sm font-semibold rounded-xl hover:bg-cyan-50 transition-colors">{translate("cta.get_started")}</Link>
              <Link href="/login" className="px-6 py-2.5 border-2 border-white/30 text-white text-sm font-semibold rounded-xl hover:bg-white/10 transition-colors">{translate("cta.sign_in")}</Link>
            </div>
          </section>
        )}

        {/* Signed in user info */}
        {user && (
          <section className="mt-10 p-6 bg-white rounded-2xl border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400 mb-1">{translate("homepage.new_here")}</p>
                <h3 className="font-semibold text-gray-900">{translate("homepage.signed_in_as")} {user.name || user.email}</h3>
              </div>
              <Link href="/dashboard" className="px-4 py-2 bg-cyan-600 text-white text-sm font-medium rounded-xl hover:bg-cyan-700 transition-colors">{translate("homepage.go_to_dashboard")}</Link>
            </div>
          </section>
        )}

        {/* Footer stats */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          {[
            { icon: "📜", value: "6,242+", label: translate("stats.provisions") },
            { icon: "🇳🇵", value: "2,655+", label: translate("stats.nepal_laws") },
            { icon: "🇮🇳", value: "4,001+", label: translate("stats.india_laws") },
            { icon: "📂", value: "12", label: translate("stats.categories") },
          ].map((stat, i) => (
            <div key={`stat-${i}`} className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="text-3xl mb-1">{stat.icon}</div>
              <div className="text-2xl font-bold text-cyan-600">{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </main>

      <footer className="border-t border-gray-100 py-6 px-4 mt-12">
        <p className="text-center text-xs text-gray-400">{translate("footer.copyright")}</p>
        <p className="text-center text-[10px] text-gray-400 mt-1">{translate("footer.disclaimer")}</p>
      </footer>
    </>
  );
}
