"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import Navbar from "@/components/Navbar";
import { usePathname } from "next/navigation";

const ROLE_CONFIG = {
  public: {
    en: { label: "Public User", icon: "👤", color: "text-gray-500", bg: "bg-gray-50" },
    ne: { label: "सार्वजनिक प्रयोगकर्ता", icon: "👤", color: "text-gray-500", bg: "bg-gray-50" },
    hi: { label: "सार्वजनिक उपयोगकर्ता", icon: "👤", color: "text-gray-500", bg: "bg-gray-50" },
  },
  lawyer: {
    en: { label: "Legal Professional", icon: "⚖️", color: "text-cyan-600", bg: "bg-cyan-50" },
    ne: { label: "कानुनी पेशेवर", icon: "⚖️", color: "text-cyan-600", bg: "bg-cyan-50" },
    hi: { label: "कानूनी पेशेवर", icon: "⚖️", color: "text-cyan-600", bg: "bg-cyan-50" },
  },
  judge: {
    en: { label: "Judge", icon: "🔨", color: "text-violet-600", bg: "bg-violet-50" },
    ne: { label: "न्यायाधीश", icon: "🔨", color: "text-violet-600", bg: "bg-violet-50" },
    hi: { label: "न्यायाधीश", icon: "🔨", color: "text-violet-600", bg: "bg-violet-50" },
  },
  admin: {
    en: { label: "Administrator", icon: "⚙️", color: "text-amber-600", bg: "bg-amber-50" },
    ne: { label: "प्रशासक", icon: "⚙️", color: "text-amber-600", bg: "bg-amber-50" },
    hi: { label: "प्रशासक", icon: "⚙️", color: "text-amber-600", bg: "bg-amber-50" },
  },
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const { t, locale } = useI18n();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      // Skip redirect if logout is in progress (Navbar sets this flag)
      let loggingOut = false;
      try { loggingOut = sessionStorage.getItem("logging_out") === "1"; } catch {}
      if (loggingOut) {
        try { sessionStorage.removeItem("logging_out"); } catch {}
        return;
      }
      window.location.replace("/login");
    }
  }, [user, loading]);

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">Loading...</div>
      </>
    );
  }

  if (!user) return null;

  const isAdmin = user.role === "admin";
  const isPro = user.role === "lawyer" || user.role === "judge" || isAdmin;
  const roleConfig = ROLE_CONFIG[user.role as keyof typeof ROLE_CONFIG] || ROLE_CONFIG.public;
  const roleInfo = roleConfig[locale as keyof typeof roleConfig] || roleConfig.en;

  return (
    <>
      <Navbar />
      <div className="flex-1 flex min-h-0">
        {/* Sidebar */}
        <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0 hidden md:flex">
          {/* User Profile */}
          <div className={`p-4 border-b border-gray-100 ${roleInfo.bg}`}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shadow-sm shrink-0">
                <span className="text-sm font-bold text-white uppercase">{user.name?.charAt(0) || "U"}</span>
              </div>
              <div className="min-w-0">
                <div className="text-sm font-semibold text-gray-900 truncate">{user.name}</div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-xs">{roleInfo.icon}</span>
                  <span className={`text-[10px] font-medium ${roleInfo.color}`}>{roleInfo.label}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
            {/* Main Section */}
            <div className="mb-4">
              <div className="text-[9px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5 px-2">
                {locale === "ne" ? "मुख्य" : locale === "hi" ? "मुख्य" : "Main"}
              </div>
              <SideLink
                href="/dashboard"
                icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>}
                label={t.dashboard.overview}
                active={pathname === "/dashboard"}
              />
            </div>

            {/* Research Section (Pro users) */}
            {isPro && (
              <div className="mb-4">
                <div className="text-[9px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5 px-2">
                  {locale === "ne" ? "अनुसन्धान" : locale === "hi" ? "अनुसंधान" : "Research"}
                </div>
                <SideLink
                  href="/dashboard/bookmarks"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>}
                  label={locale === "ne" ? "बुकमार्क" : locale === "hi" ? "बुकमार्क" : "Bookmarks"}
                  active={pathname === "/dashboard/bookmarks"}
                />
                <SideLink
                  href="/dashboard/notes"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>}
                  label={locale === "ne" ? "केस नोट" : locale === "hi" ? "केस नोट" : "Case Notes"}
                  active={pathname === "/dashboard/notes"}
                />
                <SideLink
                  href="/dashboard/history"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                  label={locale === "ne" ? "खोज इतिहास" : locale === "hi" ? "खोज इतिहास" : "Search History"}
                  active={pathname === "/dashboard/history"}
                />
              </div>
            )}

            {/* AI Tools Section (Lawyers & Judges) */}
            {(user.role === "lawyer" || user.role === "judge") && (
              <div className="mb-4">
                <div className="text-[9px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5 px-2">
                  {locale === "ne" ? "AI उपकरण" : locale === "hi" ? "AI उपकरण" : "AI Tools"}
                </div>
                <SideLink
                  href="/dashboard/ai/brief"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
                  label={locale === "ne" ? "केस ब्रिफ" : locale === "hi" ? "केस ब्रीफ" : "Case Brief"}
                  active={pathname === "/dashboard/ai/brief"}
                  accent="cyan"
                />
                <SideLink
                  href="/dashboard/ai/precedent"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>}
                  label={locale === "ne" ? "पूर्वदृष्टान्त खोज" : locale === "hi" ? "पूर्वदृष्टान्त खोजें" : "Find Precedent"}
                  active={pathname === "/dashboard/ai/precedent"}
                  accent="cyan"
                />
                <SideLink
                  href="/dashboard/ai/analysis"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
                  label={locale === "ne" ? "तर्क विश्लेषण" : locale === "hi" ? "तर्क विश्लेषण" : "Argument Analysis"}
                  active={pathname === "/dashboard/ai/analysis"}
                  accent="cyan"
                />
              </div>
            )}

            {/* Admin Section */}
            {isAdmin && (
              <div className="mb-4">
                <div className="text-[9px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5 px-2">
                  {locale === "ne" ? "प्रशासन" : locale === "hi" ? "प्रशासन" : "Administration"}
                </div>
                <SideLink
                  href="/admin"
                  icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
                  label={locale === "ne" ? "प्रशासन प्यानल" : locale === "hi" ? "प्रशासन पैनल" : "Admin Panel"}
                  active={pathname === "/admin"}
                  accent="amber"
                />
              </div>
            )}
          </nav>

          {/* Help Link */}
          <div className="p-3 border-t border-gray-100">
            <SideLink
              href="/faq"
              icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
              label={locale === "ne" ? "सहायता" : locale === "hi" ? "सहायता" : "Help & FAQ"}
              active={pathname === "/faq"}
            />
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 pb-20 md:pb-6 overflow-auto">{children}</main>
      </div>
    </>
  );
}

function SideLink({
  href,
  icon,
  label,
  active,
  accent,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
  active: boolean;
  accent?: "cyan" | "amber" | "violet";
}) {
  const accentColors = {
    cyan: "text-cyan-600 bg-cyan-50",
    amber: "text-amber-600 bg-amber-50",
    violet: "text-violet-600 bg-violet-50",
  };

  return (
    <Link
      href={href}
      className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
        active
          ? accent
            ? accentColors[accent]
            : "text-cyan-700 bg-cyan-50"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
      }`}
    >
      <span className={active ? (accent ? accentColors[accent].split(" ")[0] : "text-cyan-600") : "text-gray-400"}>
        {icon}
      </span>
      {label}
    </Link>
  );
}
