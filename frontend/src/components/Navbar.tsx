"use client";

import Link from "next/link";
import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { usePathname, useRouter } from "next/navigation";
import LanguageSwitcher from "./LanguageSwitcher";
import CountrySwitcher from "./CountrySwitcher";
import SearchModal from "./SearchModal";

const NAV_ITEMS = [
  {
    href: "/laws",
    labelKey: "nav.browse_laws",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
  },
  {
    href: "/rights",
    labelKey: "nav.rights",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
  },
  {
    href: "/issues",
    labelKey: "nav.issues",
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    accent: true,
  },
];

const COUNTRY_STRIPE: Record<string, string> = {
  all: "from-slate-500 via-slate-400 to-slate-500",
  nepal: "from-red-500 via-cyan-500 to-white",
  india: "from-orange-500 via-white to-green-500",
};

const ROLE_BADGE: Record<string, { en: string; ne: string; hi: string; color: string }> = {
  public:  { en: "Public",  ne: "सार्वजनिक", hi: "सार्वजनिक", color: "bg-gray-100 text-gray-600" },
  lawyer:  { en: "Lawyer",  ne: "वकील",      hi: "वकील",      color: "bg-cyan-50 text-cyan-600" },
  judge:   { en: "Judge",   ne: "न्यायाधीश",  hi: "न्यायाधीश",  color: "bg-violet-50 text-violet-600" },
  admin:   { en: "Admin",   ne: "प्रशासक",    hi: "प्रशासक",    color: "bg-amber-50 text-amber-600" },
};

export default function Navbar() {
  const { user, logout } = useAuth();
  const { translate, locale, country } = useI18n();
  const pathname = usePathname();
  const router = useRouter();
  const [moreOpen, setMoreOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [registerHover, setRegisterHover] = useState(false);
  const accountRef = useRef<HTMLDivElement>(null);
  const registerRef = useRef<HTMLDivElement>(null);
  const registerTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  const dashboardHref = user?.role === "admin" ? "/admin" : "/dashboard";
  const roleBadge = user ? ROLE_BADGE[user.role] || ROLE_BADGE.public : null;

  useEffect(() => {
    if (!accountOpen) return;
    const handler = (e: MouseEvent) => {
      if (accountRef.current && !accountRef.current.contains(e.target as Node)) {
        setAccountOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [accountOpen]);

  const handleLogout = useCallback(() => {
    setAccountOpen(false);
    setMoreOpen(false);
    try { sessionStorage.setItem("logging_out", "1"); } catch {}
    logout();
    window.location.replace("/");
  }, [logout]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const tag = (e.target as HTMLElement)?.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const handleRegisterEnter = () => {
    if (registerTimeout.current) clearTimeout(registerTimeout.current);
    setRegisterHover(true);
  };

  const handleRegisterLeave = () => {
    registerTimeout.current = setTimeout(() => setRegisterHover(false), 200);
  };

  const countryLabel =
    country === "nepal" ? translate("country_switcher.country_label_nepal") :
    country === "india" ? translate("country_switcher.country_label_india") :
    translate("country_switcher.country_label_all");

  return (
    <>
      {/* ═══════ DESKTOP HEADER ═══════ */}
      <header className="hidden sm:block sticky top-0 z-50">
        <div className="bg-slate-900 border-b border-slate-700/50">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center h-12 gap-3">
              {/* Logo */}
              <Link href="/" className="flex items-center gap-2 shrink-0 group">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-400 to-cyan-500 flex items-center justify-center shadow-sm shadow-cyan-500/30 group-hover:shadow-cyan-500/50 transition-shadow">
                  <span className="text-xs font-black text-white">ल</span>
                </div>
                <span className="font-bold text-sm text-white/90 tracking-tight group-hover:text-white transition-colors">Kanun</span>
              </Link>

              {/* Search — compact inline */}
              <button
                onClick={() => setSearchOpen(true)}
                className="flex items-center gap-2 bg-white/10 hover:bg-white/15 rounded-lg px-3 py-1.5 text-[11px] text-white/50 hover:text-white/70 transition-all cursor-text min-w-0 max-w-xs shrink-0"
              >
                <svg className="w-3.5 h-3.5 text-white/40 shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="truncate">{translate("search.placeholder")}</span>
                <kbd className="hidden lg:inline text-[9px] px-1.5 py-0.5 rounded bg-white/10 text-white/30 font-mono shrink-0">/</kbd>
              </button>

              {/* Nav CTAs */}
              <nav className="flex items-center gap-0.5">
                {NAV_ITEMS.map((item) => {
                  const active = isActive(item.href);
                  const isAccent = "accent" in item && item.accent;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-medium transition-all whitespace-nowrap ${
                        active
                          ? "bg-white/15 text-white"
                          : isAccent
                            ? "text-red-300 hover:bg-red-500/15 hover:text-red-200"
                            : "text-white/50 hover:bg-white/10 hover:text-white/80"
                      }`}
                    >
                      <span className={active ? "text-cyan-300" : isAccent ? "text-red-400/70" : "text-white/40"}>
                        {item.icon}
                      </span>
                      <span className="hidden lg:inline">{translate(item.labelKey)}</span>
                    </Link>
                  );
                })}
              </nav>

              <div className="flex-1" />

              {/* Switchers + Account */}
              <div className="flex items-center gap-1.5">
                <CountrySwitcher />
                <LanguageSwitcher variant="light" />
                <div className="w-px h-4 bg-white/15 mx-0.5" />
                {user ? (
                  <div className="relative" ref={accountRef}>
                    <button
                      onClick={() => setAccountOpen((v) => !v)}
                      className="flex items-center gap-1.5 pl-1 pr-1.5 py-1 rounded-lg hover:bg-white/10 transition-colors"
                    >
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-500 flex items-center justify-center shadow-sm">
                        <span className="text-[9px] font-bold text-white uppercase">{user.name?.charAt(0) || "U"}</span>
                      </div>
                      <svg className={`w-3 h-3 text-white/40 transition-transform ${accountOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {accountOpen && (
                      <div onMouseDown={(e) => e.stopPropagation()} className="absolute right-0 top-full mt-1.5 w-52 bg-white rounded-xl border border-gray-200 shadow-xl z-50 overflow-hidden">
                        <div className="px-3.5 pt-3 pb-2.5 border-b border-gray-100">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shadow-sm shrink-0">
                              <span className="text-[10px] font-bold text-white uppercase">{user.name?.charAt(0) || "U"}</span>
                            </div>
                            <div className="min-w-0">
                              <div className="text-[13px] font-semibold text-gray-900 truncate">{user.name}</div>
                              <div className="text-[10px] text-gray-400 truncate">{user.email}</div>
                            </div>
                          </div>
                          {roleBadge && <span className={`inline-block mt-1.5 text-[9px] font-semibold px-2 py-0.5 rounded-full ${roleBadge.color}`}>{roleBadge[locale as keyof typeof roleBadge] || roleBadge.en}</span>}
                        </div>
                        <div className="py-1">
                          <Link href={dashboardHref} onClick={() => setAccountOpen(false)} className="flex items-center gap-2 px-3.5 py-2 text-[11px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                            {translate("navbar.my_dashboard")}
                          </Link>
                          {user.role === "admin" && (
                            <Link href="/admin" onClick={() => setAccountOpen(false)} className="flex items-center gap-2 px-3.5 py-2 text-[11px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                              {translate("navbar.admin_panel")}
                            </Link>
                          )}
                          <Link href="/faq" onClick={() => setAccountOpen(false)} className="flex items-center gap-2 px-3.5 py-2 text-[11px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                            <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            {translate("navbar.faq_help")}
                          </Link>
                        </div>
                        <div className="border-t border-gray-100 py-1">
                          <button onClick={handleLogout} className="flex items-center gap-2 w-full px-3.5 py-2 text-[11px] font-medium text-red-600 hover:bg-red-50 transition-colors">
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                            {translate("navbar.sign_out")}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div
                    ref={registerRef}
                    className="relative"
                    onMouseEnter={handleRegisterEnter}
                    onMouseLeave={handleRegisterLeave}
                  >
                    <Link
                      href="/login"
                      className="flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-md text-white/60 hover:text-white hover:bg-white/10 transition-colors font-medium"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                      </svg>
                      {translate("nav.login")}
                    </Link>
                    {registerHover && (
                      <div className="absolute right-0 top-full mt-1 w-64 bg-white rounded-xl border border-gray-200 shadow-xl z-50 overflow-hidden">
                        <div className="p-4 text-center">
                          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-600 to-cyan-700 flex items-center justify-center mx-auto mb-2.5 shadow-md shadow-cyan-600/20">
                            <span className="text-base font-black text-white">ल</span>
                          </div>
                          <div className="text-sm font-semibold text-gray-900 mb-1">{translate("navbar.register_title")}</div>
                          <p className="text-[11px] text-gray-500 leading-relaxed mb-3">{translate("navbar.register_subtitle")}</p>
                          <Link
                            href="/register"
                            className="inline-flex items-center justify-center w-full text-[12px] font-semibold px-4 py-2 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 transition-colors shadow-sm"
                          >
                            {translate("navbar.register_cta")}
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        {/* Country stripe */}
        <div className={`h-[3px] bg-gradient-to-r ${COUNTRY_STRIPE[country]}`} />
      </header>

      {/* ═══════ MOBILE: TOP BAR ═══════ */}
      <div className="sm:hidden sticky top-0 z-50 bg-slate-900">
        <div className="flex items-center h-12 px-3">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-400 to-cyan-500 flex items-center justify-center shadow-sm shadow-cyan-500/30">
              <span className="text-xs font-black text-white">ल</span>
            </div>
            <span className="font-bold text-sm text-white/90">Kanun</span>
          </Link>
          <div className="flex-1" />
          <button onClick={() => setSearchOpen(true)} className="w-9 h-9 flex items-center justify-center rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors mr-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
          <span className="text-sm mr-2">
            {country === "nepal" ? "🇳🇵" : country === "india" ? "🇮🇳" : "🌐"}
          </span>
          {user ? (
            <div className="relative" ref={accountRef}>
              <button onClick={() => setAccountOpen((v) => !v)} className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-500 flex items-center justify-center shadow-sm">
                <span className="text-[9px] font-bold text-white uppercase">{user.name?.charAt(0) || "U"}</span>
              </button>
              {accountOpen && (
                <div onMouseDown={(e) => e.stopPropagation()} className="absolute right-0 top-full mt-1.5 w-52 bg-white rounded-xl border border-gray-200 shadow-xl z-50 overflow-hidden">
                  <div className="px-4 pt-3 pb-2 border-b border-gray-100">
                    <div className="text-sm font-semibold text-gray-900 truncate">{user.name}</div>
                    <div className="text-[10px] text-gray-400 truncate">{user.email}</div>
                    {roleBadge && <span className={`inline-block mt-1.5 text-[10px] font-semibold px-2 py-0.5 rounded-full ${roleBadge.color}`}>{roleBadge[locale as keyof typeof roleBadge] || roleBadge.en}</span>}
                  </div>
                  <div className="py-1.5">
                    <Link href={dashboardHref} onClick={() => setAccountOpen(false)} className="flex items-center gap-2.5 px-4 py-2 text-[12px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                      {translate("navbar.my_dashboard")}
                    </Link>
                    {user.role === "admin" && (
                      <Link href="/admin" onClick={() => setAccountOpen(false)} className="flex items-center gap-2.5 px-4 py-2 text-[12px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        {translate("navbar.admin_panel")}
                      </Link>
                    )}
                    <Link href="/faq" onClick={() => setAccountOpen(false)} className="flex items-center gap-2.5 px-4 py-2 text-[12px] font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      {translate("navbar.faq_help")}
                    </Link>
                  </div>
                  <div className="border-t border-gray-100 py-1.5">
                    <button onClick={handleLogout} className="flex items-center gap-2.5 w-full px-4 py-2 text-[12px] font-medium text-red-600 hover:bg-red-50 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                      {translate("navbar.sign_out")}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link href="/login" className="text-[10px] px-2.5 py-1 rounded-md bg-white/15 text-white/80 font-semibold">
              {translate("nav.login")}
            </Link>
          )}
        </div>
        {/* Country stripe */}
        <div className={`h-[3px] bg-gradient-to-r ${COUNTRY_STRIPE[country]}`} />
      </div>

      {/* ═══════ MOBILE: BOTTOM TAB BAR ═══════ */}
      <nav className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-[0_-2px_12px_rgba(0,0,0,0.06)]">
        <div className="flex items-center h-14 px-1">
          <Link href="/" className={`flex-1 flex flex-col items-center justify-center gap-0.5 py-1 transition-colors duration-150 ${pathname === "/" ? "text-cyan-600" : "text-gray-400"}`}>
            <span className={`transition-transform duration-150 ${pathname === "/" ? "scale-110" : ""}`}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1" /></svg>
            </span>
            <span className="text-[9px] font-semibold leading-none">{translate("nav.home")}</span>
            {pathname === "/" && <span className="w-5 h-[2.5px] bg-cyan-600 rounded-full mt-0.5" />}
          </Link>
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            const isAccent = "accent" in item && item.accent;
            return (
              <Link key={item.href} href={item.href} className={`flex-1 flex flex-col items-center justify-center gap-0.5 py-1 transition-colors duration-150 ${active ? "text-cyan-600" : isAccent ? "text-red-400" : "text-gray-400"}`}>
                <span className={`transition-transform duration-150 ${active ? "scale-110" : ""}`}>{item.icon}</span>
                <span className="text-[9px] font-semibold leading-none">{translate(item.labelKey)?.split(" ").slice(-1)}</span>
                {active && <span className="w-5 h-[2.5px] bg-cyan-600 rounded-full mt-0.5" />}
              </Link>
            );
          })}
          <button onClick={() => setMoreOpen(true)} className="flex-1 flex flex-col items-center justify-center gap-0.5 py-1 text-gray-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
            <span className="text-[9px] font-semibold leading-none">{translate("navbar.more")}</span>
          </button>
        </div>
      </nav>

      {/* ═══════ MOBILE: MORE DRAWER ═══════ */}
      {moreOpen && (
        <div className="sm:hidden fixed inset-0 z-[60]">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setMoreOpen(false)} />
          <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-center pt-3 pb-2"><div className="w-10 h-1 rounded-full bg-gray-300" /></div>
            <div className="px-4 pb-8 space-y-4">
              <div className="space-y-3">
                <div>
                  <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{translate("navbar.country")}</span>
                  <div className="mt-1.5"><CountrySwitcher /></div>
                </div>
                <div>
                  <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{translate("navbar.language")}</span>
                  <div className="mt-1.5"><LanguageSwitcher variant="light" /></div>
                </div>
              </div>
              <div className="border-t border-gray-100" />
              {user && (
                <div className="flex items-center gap-3 px-1">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center shadow-sm shrink-0">
                    <span className="text-sm font-bold text-white uppercase">{user.name?.charAt(0) || "U"}</span>
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-gray-900 truncate">{user.name}</div>
                    <div className="text-[10px] text-gray-400 truncate">{user.email}</div>
                    {roleBadge && <span className={`inline-block mt-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${roleBadge.color}`}>{roleBadge[locale as keyof typeof roleBadge] || roleBadge.en}</span>}
                  </div>
                </div>
              )}
              <div className="border-t border-gray-100" />
              {/* CTA tiles in drawer */}
              <div className="grid grid-cols-2 gap-2">
                <Link href="/rights" onClick={() => setMoreOpen(false)} className="flex items-center gap-2 p-3 rounded-xl bg-violet-50 border border-violet-100 text-violet-700 text-xs font-semibold hover:bg-violet-100 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                  {translate("nav.rights")}
                </Link>
                <Link href="/issues" onClick={() => setMoreOpen(false)} className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100 text-red-700 text-xs font-semibold hover:bg-red-100 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
                  {translate("nav.issues")}
                </Link>
              </div>
              <div className="space-y-1">
                <button onClick={() => { setMoreOpen(false); setSearchOpen(true); }} className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                  {translate("nav.search")}
                </button>
                {user && (
                  <Link href={dashboardHref} onClick={() => setMoreOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${isActive(dashboardHref) ? "bg-cyan-50 text-cyan-700" : "text-gray-700 hover:bg-gray-50"}`}>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                    {translate("navbar.my_dashboard")}
                  </Link>
                )}
                {user?.role === "admin" && (
                  <Link href="/admin" onClick={() => setMoreOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${isActive("/admin") ? "bg-cyan-50 text-cyan-700" : "text-gray-700 hover:bg-gray-50"}`}>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    {translate("navbar.admin_panel")}
                  </Link>
                )}
                <Link href="/faq" onClick={() => setMoreOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {translate("navbar.faq_help")}
                </Link>
              </div>
              <div className="border-t border-gray-100" />
              {user ? (
                <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 text-sm px-4 py-2.5 rounded-xl bg-red-50 text-red-600 font-medium hover:bg-red-100 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                  {translate("navbar.sign_out")}
                </button>
              ) : (
                <div className="flex gap-2">
                  <Link href="/login" onClick={() => setMoreOpen(false)} className="flex-1 text-center text-sm px-4 py-2.5 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors">{translate("nav.login")}</Link>
                  <Link href="/register" onClick={() => setMoreOpen(false)} className="flex-1 text-center text-sm px-4 py-2.5 rounded-xl bg-cyan-600 text-white font-semibold hover:bg-cyan-700 transition-colors shadow-sm">{translate("nav.register")}</Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ═══════ SEARCH MODAL ═══════ */}
      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
