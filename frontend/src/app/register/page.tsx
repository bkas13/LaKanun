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

  const inputClass =
    "w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none bg-gray-50 focus:bg-white transition-colors";

  return (
    <div className="min-h-[calc(100vh-40px)] flex items-center justify-center px-4 bg-gradient-to-br from-cyan-50 to-cyan-50 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-5">
          <Link href="/" className="inline-flex items-center gap-1 text-cyan-700 font-bold text-xl mb-2">
            <span className="text-2xl">ल</span> Kanun
          </Link>
          <h1 className="text-lg font-semibold text-gray-800">{translate("auth.register_title")}</h1>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-5">
          <div className={`flex-1 h-1 rounded-full transition-colors ${step >= 1 ? "bg-cyan-500" : "bg-gray-200"}`} />
          <div className={`flex-1 h-1 rounded-full transition-colors ${step >= 2 ? "bg-cyan-500" : "bg-gray-200"}`} />
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-xs">
              {error}
            </div>
          )}

          {step === 1 && (
            <form onSubmit={handleStep1} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">{translate("auth.full_name")}</label>
                <input type="text" required value={name} onChange={(e) => setName(e.target.value)} className={inputClass} placeholder={translate("auth.placeholder_name")} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">{translate("auth.email")}</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} placeholder={translate("auth.placeholder_email")} />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">{translate("auth.password")}</label>
                <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} placeholder={translate("auth.placeholder_password")} />
              </div>
              <button type="submit" disabled={!name || !email || !password} className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
                {translate("auth.continue")}
              </button>
            </form>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-sm font-semibold text-gray-800 mb-1">{translate("auth.privacy_title")}</h2>
              <p className="text-xs text-gray-500 mb-4">{translate("auth.privacy_desc")}</p>

              <div className="space-y-2">
                {PRIVACY_KEYS.map((item) => (
                  <div
                    key={item.key}
                    className={`flex items-center gap-3 p-3 rounded-xl border transition-colors ${
                      privacy[item.key] ? "border-cyan-200 bg-cyan-50" : "border-gray-200 bg-gray-50"
                    }`}
                  >
                    <span className="text-lg shrink-0">{item.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-800">{translate(`auth.privacy_${item.key}`)}</div>
                      <div className="text-[11px] text-gray-400">{translate(`auth.privacy_${item.key}_desc`)}</div>
                    </div>
                    <button
                      onClick={() => togglePrivacy(item.key)}
                      className={`relative w-10 h-5 rounded-full transition-colors shrink-0 ${
                        privacy[item.key] ? "bg-cyan-500" : "bg-gray-300"
                      }`}
                    >
                      <div
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                          privacy[item.key] ? "left-[22px]" : "left-0.5"
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>

              <div className="flex gap-2 mt-5">
                <button onClick={() => setStep(1)} className="flex-1 py-2.5 rounded-xl border border-gray-200 text-gray-600 text-sm font-medium hover:bg-gray-50 transition-colors">
                  {translate("auth.back")}
                </button>
                <button onClick={handleStep2} disabled={loading} className="flex-1 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium transition-colors disabled:opacity-40">
                  {loading ? translate("auth.creating_account") : translate("auth.create_account")}
                </button>
              </div>
            </div>
          )}
        </div>

        <p className="mt-4 text-center text-xs text-gray-500">
          {translate("auth.has_account")}{" "}
          <Link href="/login" className="text-cyan-600 font-medium hover:underline">
            {translate("auth.login_link")}
          </Link>
        </p>
      </div>
    </div>
  );
}