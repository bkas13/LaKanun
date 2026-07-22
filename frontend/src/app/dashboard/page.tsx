"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";

interface DetailedStats {
  total_provisions: number;
  nepal: { total: number; documents: { name: string; count: number }[]; categories: { name: string; count: number }[] };
  india: { total: number; documents: { name: string; count: number }[]; categories: { name: string; count: number }[] };
}

const toDevanagari = (n: number, locale: string): string => {
  if (locale === "en") return n.toLocaleString();
  const digits = ["०","१","२","३","४","५","६","७","८","९"];
  return n.toLocaleString("en-IN").replace(/[0-9]/g, (d) => digits[parseInt(d)]);
};

const CAT_LABELS: Record<string, { en: string; ne: string; hi: string }> = {
  criminal: { en: "Criminal", ne: "फौजदारी", hi: "आपराधिक" },
  civil_procedure_general: { en: "Civil Procedure", ne: "दीवानी प्रक्रिया", hi: "दीवानी प्रक्रिया" },
  constitutional: { en: "Constitutional", ne: "संवैधानिक", hi: "संवैधानिक" },
  civil: { en: "Civil", ne: "दीवानी", hi: "दीवानी" },
  property_law: { en: "Property", ne: "सम्पत्ति", hi: "संपत्ति" },
  civil_law_general: { en: "Civil", ne: "दीवानी", hi: "दीवानी" },
  consumer_protection_general: { en: "Consumer", ne: "उपभोक्ता", hi: "उपभोक्ता" },
  punishment_provisions: { en: "Penalties", ne: "सजाय", hi: "सजा" },
  labor: { en: "Labor", ne: "श्रम", hi: "श्रम" },
  family: { en: "Family", ne: "पारिवारिक", hi: "पारिवारिक" },
  tax: { en: "Tax", ne: "कर", hi: "कर" },
  environmental: { en: "Environment", ne: "वातावरण", hi: "पर्यावरण" },
  commercial: { en: "Commercial", ne: "व्यापारिक", hi: "व्यापारिक" },
};

interface SourceInfo {
  title: { en: string; ne: string; hi: string };
  desc: { en: string; ne: string; hi: string };
  icon: string;
}

const SOURCE_INFO: Record<string, SourceInfo> = {
  constitution_of_nepal_2072: {
    title: { en: "Constitution of Nepal 2072", ne: "नेपालको संविधान २०७२", hi: "नेपाल संविधान २०७२" },
    desc: { en: "Supreme law — fundamental rights & duties", ne: "सर्वोच्च कानुन — मौलिक अधिकार र कर्तव्य", hi: "सर्वोच्च कानून — मौलिक अधिकार और कर्तव्य" },
    icon: "📜",
  },
  nepal_civil_code: {
    title: { en: "Nepal Civil Code", ne: "नेपाल नागरिक संहिता", hi: "नेपाल नागरिक संहिता" },
    desc: { en: "Property, contracts, family & civil obligations", ne: "सम्पत्ति, अनुबन्ध, परिवार र दीवानी दायित्व", hi: "संपत्ति, अनुबंध, परिवार और नागरिक दायित्व" },
    icon: "🏠",
  },
  nepal_civil_procedure: {
    title: { en: "Nepal Civil Procedure", ne: "नेपाल दीवानी प्रक्रिया", hi: "नेपाल दीवानी प्रक्रिया" },
    desc: { en: "How civil cases are filed and tried", ne: "दीवानी मुद्दा कसरी दायर र सुनुवाइ हुन्छ", hi: "दीवानी मामले कैसे दायर और सुनवाई होती है" },
    icon: "⚖️",
  },
  nepal_penal_code: {
    title: { en: "Nepal Penal Code", ne: "नेपाल दण्ड संहिता", hi: "नेपाल दंड संहिता" },
    desc: { en: "Criminal offences & punishments", ne: "फौजदारी अपराध र सजाय", hi: "आपराधिक अपराध और सजा" },
    icon: "🔒",
  },
  nepal_criminal_procedure: {
    title: { en: "Nepal Criminal Procedure", ne: "नेपाल फौजदारी प्रक्रिया", hi: "नेपाल दंड प्रक्रिया" },
    desc: { en: "How criminal cases are investigated & prosecuted", ne: "फौजदारी मुद्दा कसरी छानबिनी र मुद्दा चलिन्छ", hi: "आपराधिक मामले कैसे जांच और अभियोजन होते हैं" },
    icon: "🔍",
  },
  nepal_labor_act: {
    title: { en: "Nepal Labor Act", ne: "नेपाल श्रम ऐन", hi: "नेपाल श्रम अधिनियम" },
    desc: { en: "Worker rights, wages & workplace safety", ne: "श्रमिक अधिकार, ज्याला र कार्यस्थल सुरक्षा", hi: "श्रमिक अधिकार, वेतन और कार्यस्थल सुरक्षा" },
    icon: "💼",
  },
  nepal_electronic_transactions: {
    title: { en: "Electronic Transactions Act", ne: "इलेक्ट्रोनिक लेनदेन ऐन", hi: "इलेक्ट्रॉनिक लेनदेन अधिनियम" },
    desc: { en: "Digital signatures, e-commerce & cyber law", ne: "डिजिटल सही, ई-कमर्स र साइबर कानुन", hi: "डिजिटल हस्ताक्षर, ई-कॉमर्स और साइबर कानून" },
    icon: "💻",
  },
  nepal_right_to_information: {
    title: { en: "Right to Information Act", ne: "सूचना अधिकार ऐन", hi: "सूचना का अधिकार अधिनियम" },
    desc: { en: "Citizens' right to access government information", ne: "सरकारी सूचना प्राप्त गर्ने नागरिकको अधिकार", hi: "सरकारी जानकारी तक पहुंचने का नागरिक अधिकार" },
    icon: "📰",
  },
  constitution_of_india: {
    title: { en: "Constitution of India 1950", ne: "भारतको संविधान १९५०", hi: "भारत संविधान १९५०" },
    desc: { en: "Supreme law — fundamental rights & duties", ne: "सर्वोच्च कानुन — मौलिक अधिकार र कर्तव्य", hi: "सर्वोच्च कानून — मौलिक अधिकार और कर्तव्य" },
    icon: "📜",
  },
  indian_penal_code: {
    title: { en: "Indian Penal Code 1860", ne: "भारतीय दण्ड संहिता १८६०", hi: "भारतीय दंड संहिता १८६०" },
    desc: { en: "Criminal offences & punishments in India", ne: "भारतमा फौजदारी अपराध र सजाय", hi: "भारत में आपराधिक अपराध और सजा" },
    icon: "🔒",
  },
  code_of_criminal_procedure: {
    title: { en: "Code of Criminal Procedure 1973", ne: "फौजदारी प्रक्रिया संहिता १९७३", hi: "दंड प्रक्रिया संहिता १९७३" },
    desc: { en: "How criminal cases are investigated & prosecuted", ne: "फौजदारी मुद्दा कसरी छानबिनी र मुद्दा चलिन्छ", hi: "आपराधिक मामले कैसे जांच और अभियोजन होते हैं" },
    icon: "🔍",
  },
  code_of_civil_procedure: {
    title: { en: "Code of Civil Procedure 1908", ne: "दीवानी प्रक्रिया संहिता १९०८", hi: "दीवानी प्रक्रिया संहिता १९०८" },
    desc: { en: "How civil cases are filed and tried", ne: "दीवानी मुद्दा कसरी दायर र सुनुवाइ हुन्छ", hi: "दीवानी मामले कैसे दायर और सुनवाई होती है" },
    icon: "⚖️",
  },
  indian_contract_act: {
    title: { en: "Indian Contract Act 1872", ne: "भारतीय अनुबन्ध ऐन १८७२", hi: "भारतीय अनुबंध अधिनियम १८७२" },
    desc: { en: "Contracts, agreements & obligations", ne: "अनुबन्ध, सम्झौता र दायित्व", hi: "अनुबंध, समझौता और दायित्व" },
    icon: "📝",
  },
  minimum_wages_act: {
    title: { en: "Minimum Wages Act 1948", ne: "न्यूनतम ज्याला ऐन १९४८", hi: "न्यूनतम वेतन अधिनियम १९४८" },
    desc: { en: "Minimum wage standards & worker protections", ne: "न्यूनतम ज्याला मापदण्ड र श्रमिक सुरक्षा", hi: "न्यूनतम वेतन मानक और श्रमिक सुरक्षा" },
    icon: "💰",
  },
};

function getGreeting(locale: string): string {
  const h = new Date().getHours();
  if (locale === "ne") return h < 12 ? "शुभ प्रभात" : h < 17 ? "शुभ दिन" : "शुभ साँझ";
  if (locale === "hi") return h < 12 ? "शुभ प्रभात" : h < 17 ? "शुभ दोपहर" : "शुभ संध्या";
  return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
}

function StatSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-xl border border-gray-100 p-3 animate-pulse">
          <div className="h-2 w-12 bg-gray-200 rounded mb-2" />
          <div className="h-5 w-16 bg-gray-200 rounded" />
        </div>
      ))}
    </div>
  );
}

function CorpusSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="h-3 w-20 bg-gray-200 rounded" />
        <div className="h-2 w-16 bg-gray-200 rounded" />
      </div>
      <div className="flex flex-wrap gap-1.5">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-6 w-20 bg-gray-100 rounded-full" />
        ))}
      </div>
    </div>
  );
}

export default function DashboardOverview() {
  const { user } = useAuth();
  const { translate, locale, country } = useI18n();
  const [stats, setStats] = useState<DetailedStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showNepal, setShowNepal] = useState(true);

  useEffect(() => {
    if (country === "nepal") setShowNepal(true);
    else if (country === "india") setShowNepal(false);
  }, [country]);

  useEffect(() => {
    setLoading(true);
    api<DetailedStats>("/api/v1/laws/stats/detailed", { noAuth: true })
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const isPro = user?.role === "lawyer" || user?.role === "judge";
  const isAdmin = user?.role === "admin";
  const active = showNepal ? stats?.nepal : stats?.india;
  const countryLabel = showNepal ? translate("nepal") : translate("india");

  const roleLabel: Record<string, { en: string; ne: string; hi: string }> = {
    public: { en: "Public User", ne: "सार्वजनिक प्रयोगकर्ता", hi: "सार्वजनिक उपयोगकर्ता" },
    lawyer: { en: "Legal Professional", ne: "कानुनी पेशेवर", hi: "कानूनी पेशेवर" },
    judge: { en: "Judge", ne: "न्यायाधीश", hi: "न्यायाधीश" },
    admin: { en: "Administrator", ne: "प्रशासक", hi: "प्रशासक" },
  };

  const roleColor: Record<string, string> = {
    public: "bg-gray-100 text-gray-600",
    lawyer: "bg-cyan-50 text-cyan-700",
    judge: "bg-violet-50 text-violet-700",
    admin: "bg-amber-50 text-amber-700",
  };

  const quickActions = [
    { href: "/", icon: "search", label: translate("dashboard.search_laws_action"), color: "from-cyan-500 to-cyan-600" },
    { href: "/laws", icon: "browse", label: translate("dashboard.browse_laws_action"), color: "from-blue-500 to-blue-600" },
    ...(isPro ? [
      { href: "/dashboard/bookmarks", icon: "bookmark", label: translate("dashboard.bookmarks_action"), color: "from-amber-500 to-amber-600" },
      { href: "/dashboard/notes", icon: "note", label: translate("dashboard.case_notes_action_label"), color: "from-emerald-500 to-emerald-600" },
      { href: "/dashboard/history", icon: "history", label: translate("dashboard.search_history_action"), color: "from-purple-500 to-purple-600" },
    ] : []),
    ...(isAdmin ? [
      { href: "/admin", icon: "admin", label: translate("dashboard.admin_panel_action"), color: "from-rose-500 to-rose-600" },
    ] : []),
  ];

  const aiTools = (user?.role === "lawyer" || user?.role === "judge") ? [
    {
      href: "/dashboard/ai/brief",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>,
      title: translate("ai_tools.case_brief.title"),
      description: translate("ai_tools.case_brief.description"),
      color: "from-cyan-500 to-blue-600",
    },
    {
      href: "/dashboard/ai/precedent",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
      title: translate("ai_tools.precedent.title"),
      description: translate("ai_tools.precedent.description"),
      color: "from-violet-500 to-purple-600",
    },
    {
      href: "/dashboard/ai/analysis",
      icon: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>,
      title: translate("ai_tools.analysis.title"),
      description: translate("ai_tools.analysis.description"),
      color: "from-emerald-500 to-teal-600",
    },
  ] : [];

  const QUICK_ICON: Record<string, React.ReactNode> = {
    search: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
    browse: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>,
    bookmark: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>,
    note: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>,
    history: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
    admin: <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94 1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>,
  };

  return (
    <div className="max-w-2xl">
      {/* ─── Welcome Hero ────────────────────────────────── */}
      <div className="bg-gradient-to-br from-cyan-600 via-cyan-700 to-blue-800 rounded-2xl p-5 mb-5 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
        <div className="relative">
          <p className="text-cyan-100 text-[11px] font-medium mb-1">{getGreeting(locale)}</p>
          <h1 className="text-xl font-bold mb-1.5">{user?.name || user?.email}</h1>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] px-2.5 py-1 rounded-full font-semibold ${roleColor[user?.role || "public"]} bg-white/20 text-white`}>
              {roleLabel[user?.role || "public"]?.[locale] || user?.role}
            </span>
            {stats && (
              <span className="text-[10px] text-cyan-200">
                {toDevanagari(stats.total_provisions, locale)} {translate("dashboard.provisions")}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ─── Quick Stats ─────────────────────────────────── */}
      {loading ? (
        <div className="mb-5"><StatSkeleton /></div>
      ) : stats ? (
        <div className="grid grid-cols-3 gap-2 mb-5">
          <div className="bg-white rounded-xl border border-gray-100 p-3 text-center">
            <div className="text-[10px] text-gray-400 uppercase font-medium mb-1">{translate("nepal")}</div>
            <div className="text-lg font-bold text-gray-900">{toDevanagari(stats.nepal.total, locale)}</div>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 p-3 text-center">
            <div className="text-[10px] text-gray-400 uppercase font-medium mb-1">{translate("india")}</div>
            <div className="text-lg font-bold text-gray-900">{toDevanagari(stats.india.total, locale)}</div>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 p-3 text-center">
            <div className="text-[10px] text-gray-400 uppercase font-medium mb-1">{translate("dashboard.categories")}</div>
            <div className="text-lg font-bold text-gray-900">
              {toDevanagari(
                new Set([
                  ...stats.nepal.categories.map((c) => c.name),
                  ...stats.india.categories.map((c) => c.name),
                ]).size,
                locale
              )}
            </div>
          </div>
        </div>
      ) : null}

      {/* ─── Quick Actions ───────────────────────────────── */}
      <div className="mb-5">
        <h2 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2.5">{translate("dashboard.quick_access")}</h2>
        <div className="grid grid-cols-2 gap-2">
          {quickActions.map((action) => (
            <Link
              key={action.href}
              href={action.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white border border-gray-100 hover:border-cyan-200 hover:shadow-sm transition-all group"
            >
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center shadow-sm shrink-0`}>
                {QUICK_ICON[action.icon]}
              </div>
              <span className="text-xs font-medium text-gray-700 group-hover:text-cyan-700">{action.label}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* ─── AI Tools (Lawyers & Judges) ────────────────── */}
      {aiTools.length > 0 && (
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-2.5">
            <h2 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              {locale === "ne" ? "AI उपकरण" : locale === "hi" ? "AI उपकरण" : "AI Tools"}
            </h2>
            <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold">
              {user?.role === "judge" ? (locale === "ne" ? "न्यायाधीश" : locale === "hi" ? "न्यायाधीश" : "Judge") : (locale === "ne" ? "वकील" : locale === "hi" ? "वकील" : "Lawyer")}
            </span>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {aiTools.map((tool) => (
              <Link
                key={tool.href}
                href={tool.href}
                className="flex items-start gap-4 px-4 py-4 rounded-xl bg-gradient-to-br from-white to-gray-50 border border-gray-200 hover:border-cyan-300 hover:shadow-md transition-all group"
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${tool.color} flex items-center justify-center shadow-md shrink-0 text-white group-hover:scale-105 transition-transform`}>
                  {tool.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900 group-hover:text-cyan-700 transition-colors mb-0.5">
                    {tool.title}
                  </h3>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    {tool.description}
                  </p>
                </div>
                <svg className="w-4 h-4 text-gray-300 group-hover:text-cyan-500 mt-1 shrink-0 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ─── Corpus by Country ───────────────────────────── */}
      <div className="mb-5">
        <h2 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2.5">{translate("dashboard.legal_corpus")}</h2>
        {loading ? (
          <CorpusSkeleton />
        ) : stats ? (
          <>
            {(country as string) === "all" && (
              <div className="flex gap-2 mb-3">
                <button
                  onClick={() => setShowNepal(true)}
                  className={`flex-1 py-2 rounded-xl text-xs font-medium transition-all ${
                    showNepal ? "bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-sm" : "bg-white text-gray-500 border border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  🇳🇵 {translate("nepal")} — {toDevanagari(stats.nepal.total, locale)}
                </button>
                <button
                  onClick={() => setShowNepal(false)}
                  className={`flex-1 py-2 rounded-xl text-xs font-medium transition-all ${
                    !showNepal ? "bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-sm" : "bg-white text-gray-500 border border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  🇮🇳 {translate("india")} — {toDevanagari(stats.india.total, locale)}
                </button>
              </div>
            )}
            {active && (
              <div className="bg-white rounded-xl border border-gray-100 p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-semibold text-gray-700">
                    {showNepal ? "🇳🇵" : "🇮🇳"} {countryLabel}
                  </h3>
                  <span className="text-[10px] text-gray-400">
                    {active.categories.length} {translate("dashboard.categories")}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {active.categories.slice(0, 10).map((cat) => (
                    <span key={cat.name} className="text-[10px] px-2 py-1 rounded-full bg-gray-50 text-gray-600 border border-gray-100">
                      {CAT_LABELS[cat.name]?.[locale] || cat.name}
                      <span className="ml-1 font-semibold text-cyan-600">{toDevanagari(cat.count, locale)}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : null}
      </div>

      {/* ─── Trusted Sources ──────────────────────────────── */}
      {stats && (
        <div className="mb-5">
          <h2 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2.5">{translate("dashboard.trusted_sources")}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(country === "all"
              ? [
                  ...(stats.nepal.documents?.filter((d) => d.count > 0).map((d) => ({ ...d, country: "nepal" })) || []),
                  ...(stats.india.documents?.filter((d) => d.count > 0).map((d) => ({ ...d, country: "india" })) || []),
                ]
              : (showNepal ? stats.nepal : stats.india).documents?.filter((d) => d.count > 0).map((d) => ({ ...d, country: showNepal ? "nepal" : "india" })) || []
            ).slice(0, 8).map((doc) => {
              const info = SOURCE_INFO[doc.name];
              const localeKey = locale as keyof typeof info.title;
              return (
                <Link
                  key={doc.name}
                  href={`/laws?q=${encodeURIComponent(info?.title?.[localeKey] || doc.name)}`}
                  className="flex items-start gap-3 bg-white rounded-xl border border-gray-100 p-3.5 hover:border-cyan-200 hover:shadow-sm transition-all group"
                >
                  <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-50 to-cyan-100 flex items-center justify-center text-lg shrink-0 group-hover:from-cyan-100 group-hover:to-cyan-200 transition-colors">
                    {info?.icon || "📄"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px]">{doc.country === "nepal" ? "🇳🇵" : "🇮🇳"}</span>
                      <h3 className="text-xs font-semibold text-gray-800 truncate group-hover:text-cyan-700 transition-colors">
                        {info?.title?.[localeKey] || doc.name.replace(/_/g, " ")}
                      </h3>
                    </div>
                    {info && (
                      <p className="text-[10px] text-gray-400 mt-0.5 leading-relaxed line-clamp-1">
                        {info.desc[localeKey] || info.desc.en}
                      </p>
                    )}
                    <div className="flex items-center gap-1.5 mt-1.5">
                      <span className="text-[10px] font-semibold text-cyan-600">
                        {toDevanagari(doc.count, locale)}
                      </span>
                      <span className="text-[10px] text-gray-400">{translate("dashboard.provisions")}</span>
                      <svg className="w-3 h-3 text-gray-300 group-hover:text-cyan-500 ml-auto transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
