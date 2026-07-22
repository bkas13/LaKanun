"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import { useToast } from "@/contexts/ToastContext";

const PRIVACY_KEYS = [
  { key: "search", icon: "🔍", defaultOn: true },
  { key: "personalized", icon: "🎯", defaultOn: true },
  { key: "analytics", icon: "📊", defaultOn: false },
  { key: "sync", icon: "☁️", defaultOn: true },
  { key: "updates", icon: "📧", defaultOn: false },
] as const;

export default function RegisterPage() {
  const { register } = useAuth();
  const { translate } = useI18n();
  const { addToast } = useToast();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<1 | 2>(1);
  const [privacy, setPrivacy] = useState<Record<string, boolean>>(
    Object.fromEntries(PRIVACY_KEYS.map((p) => [p.key, p.defaultOn]))
  );

  const togglePrivacy = (key: string) => {
    setPrivacy((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleStep1 = (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) {
      setError(translate("auth.password_min"));
      return;
    }
    setError("");
    setStep(2);
  };

  const handleStep2 = async () => {
    setError("");
    setLoading(true);
    try {
      await register(name, email, password);
      localStorage.setItem("privacy_settings", JSON.stringify(privacy));
      addToast(translate("auth.welcome_new"), "success");
      router.push("/dashboard");
    } catch (err: unknown) {
      try {
        const parsed = JSON.parse(err instanceof Error ? err.message : "{}");
        setError(parsed.detail || translate("auth.registration_failed"));
      } catch {
        setError(translate("auth.registration_failed"));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 relative overflow-hidden bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900">
      {/* Decorative blobs */}
      <div className="absolute top-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-500/10 blur-[120px]" />
      <div className="absolute bottom-[-20%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:shadow-cyan-500/50 transition-shadow">
              <span className="text-lg font-black text-white">ल</span>
            </div>
            <span className="text-xl font-bold text-white tracking-tight">Kanun</span>
          </Link>
          <h1 className="text-xl font-semibold text-white/90">{translate("auth.register_title")}</h1>
          <p className="text-sm text-cyan-200/70 mt-1">Create your account to get started</p>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-6">
          <div className={`flex-1 h-1.5 rounded-full transition-all duration-500 ${step >= 1 ? "bg-gradient-to-r from-cyan-400 to-cyan-500 shadow-sm shadow-cyan-500/30" : "bg-white/10"}`} />
          <div className={`flex-1 h-1.5 rounded-full transition-all duration-500 ${step >= 2 ? "bg-gradient-to-r from-cyan-400 to-cyan-500 shadow-sm shadow-cyan-500/30" : "bg-white/10"}`} />
        </div>

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl">
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs flex items-center gap-2.5">
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          )}

          {step === 1 && (
            <form onSubmit={handleStep1} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-cyan-200/80 mb-1.5">{translate("auth.full_name")}</label>
                <div className="relative">
                  <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <input type="text" required value={name} onChange={(e) => setName(e.target.value)}
                    className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/30 focus:outline-none focus:bg-white/10 focus:border-cyan-400/50 transition-all"
                    placeholder={translate("auth.placeholder_name")} />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-cyan-200/80 mb-1.5">{translate("auth.email")}</label>
                <div className="relative">
                  <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/30 focus:outline-none focus:bg-white/10 focus:border-cyan-400/50 transition-all"
                    placeholder={translate("auth.placeholder_email")} />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-cyan-200/80 mb-1.5">{translate("auth.password")}</label>
                <div className="relative">
                  <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/30 focus:outline-none focus:bg-white/10 focus:border-cyan-400/50 transition-all"
                    placeholder={translate("auth.placeholder_password")} />
                </div>
              </div>
              <button type="submit" disabled={!name || !email || !password}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-white text-sm font-semibold transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 disabled:opacity-30 disabled:cursor-not-allowed">
                {translate("auth.continue")}
              </button>
            </form>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-sm font-semibold text-white/90 mb-1">{translate("auth.privacy_title")}</h2>
              <p className="text-xs text-white/50 mb-5">{translate("auth.privacy_desc")}</p>

              <div className="space-y-2.5">
                {PRIVACY_KEYS.map((item) => (
                  <div
                    key={item.key}
                    className={`flex items-center gap-3 p-3.5 rounded-xl border transition-all ${
                      privacy[item.key]
                        ? "border-cyan-500/30 bg-cyan-500/10"
                        : "border-white/10 bg-white/5"
                    }`}
                  >
                    <span className="text-lg shrink-0">{item.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-white/80">{translate(`auth.privacy_${item.key}`)}</div>
                      <div className="text-[11px] text-white/40">{translate(`auth.privacy_${item.key}_desc`)}</div>
                    </div>
                    <button
                      onClick={() => togglePrivacy(item.key)}
                      className={`relative w-10 h-5 rounded-full transition-colors shrink-0 ${
                        privacy[item.key] ? "bg-cyan-500" : "bg-white/20"
                      }`}
                    >
                      <div
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all duration-200 ${
                          privacy[item.key] ? "left-[22px]" : "left-0.5"
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setStep(1)}
                  className="flex-1 py-2.5 rounded-xl border border-white/10 text-white/60 text-sm font-medium hover:bg-white/5 hover:text-white/80 transition-all">
                  {translate("auth.back")}
                </button>
                <button onClick={handleStep2} disabled={loading}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-white text-sm font-semibold transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 disabled:opacity-30">
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      {translate("auth.creating_account")}
                    </span>
                  ) : translate("auth.create_account")}
                </button>
              </div>
            </div>
          )}
        </div>

        <p className="mt-5 text-center text-xs text-white/40">
          {translate("auth.has_account")}{" "}
          <Link href="/login" className="text-cyan-400 font-medium hover:text-cyan-300 transition-colors">
            {translate("auth.login_link")}
          </Link>
        </p>
      </div>
    </div>
  );
}
