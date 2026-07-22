"use client";

import { useState, useEffect } from "react";
import { useI18n } from "@/contexts/I18nContext";

interface UseCaseBannerProps {
  onDismiss?: () => void;
  forceShow?: boolean;
}

export default function UseCaseBanner({ onDismiss, forceShow }: UseCaseBannerProps) {
  const { t, locale } = useI18n();
  const [visible, setVisible] = useState(false);
  const [privacy, setPrivacy] = useState({
    search_history: true,
    personalized: true,
    analytics: false,
    cloud_sync: true,
    legal_updates: false,
  });

  useEffect(() => {
    if (forceShow) {
      setVisible(true);
      return;
    }
    const dismissed = localStorage.getItem("kanun_usecase_dismissed");
    if (!dismissed) setVisible(true);
  }, [forceShow]);

  const dismiss = () => {
    setVisible(false);
    localStorage.setItem("kanun_usecase_dismissed", "1");
    onDismiss?.();
  };

  if (!visible) return null;

  const togglePrivacy = (key: keyof typeof privacy) => {
    setPrivacy((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const tryPrompt = (prompt: string) => {
    dismiss();
    const input = document.querySelector('input[type="text"]') as HTMLInputElement;
    if (input) {
      input.value = prompt;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      const form = document.querySelector("form");
      if (form) form.requestSubmit();
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) dismiss();
      }}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white rounded-t-2xl border-b border-gray-100 px-5 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-gray-900">{t.usecase_banner.title}</h2>
            <p className="text-[11px] text-gray-500">{t.usecase_banner.subtitle}</p>
          </div>
          <button
            onClick={dismiss}
            className="w-7 h-7 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-5 py-4 space-y-5">
          {/* Features */}
          <div>
            <h3 className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">
              {t.usecase_banner.features_title}
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {t.usecase_banner.features.map((f: { icon: string; title: string; desc: string }, i: number) => (
                <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
                  <span className="text-base mt-0.5">{f.icon}</span>
                  <div>
                    <div className="text-[11px] font-semibold text-gray-800">{f.title}</div>
                    <div className="text-[10px] text-gray-500 leading-relaxed">{f.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sample Prompts */}
          <div>
            <h3 className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">
              {t.usecase_banner.prompts_title}
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {t.usecase_banner.sample_prompts.map((prompt: string, i: number) => (
                <button
                  key={i}
                  onClick={() => tryPrompt(prompt)}
                  className="text-[10px] px-2.5 py-1.5 rounded-full bg-cyan-50 text-cyan-700 hover:bg-cyan-100 transition-colors text-left"
                >
                  &ldquo;{prompt}&rdquo;
                </button>
              ))}
            </div>
          </div>

          {/* Privacy */}
          <div>
            <h3 className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">
              {t.usecase_banner.privacy_title}
            </h3>
            <p className="text-[10px] text-gray-400 mb-2">{t.usecase_banner.privacy_desc}</p>
            <div className="space-y-2">
              {t.usecase_banner.privacy_items.map((item: { key: string; label: string; desc: string }, i: number) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="min-w-0 mr-3">
                    <div className="text-[11px] font-medium text-gray-700">{item.label}</div>
                    <div className="text-[10px] text-gray-400">{item.desc}</div>
                  </div>
                  <button
                    onClick={() => togglePrivacy(item.key as keyof typeof privacy)}
                    className={`relative w-9 h-5 rounded-full transition-colors shrink-0 ${
                      privacy[item.key as keyof typeof privacy] ? "bg-cyan-500" : "bg-gray-300"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
                        privacy[item.key as keyof typeof privacy] ? "translate-x-4" : ""
                      }`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 bg-white rounded-b-2xl border-t border-gray-100 px-5 py-3">
          <button
            onClick={dismiss}
            className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-semibold transition-colors"
          >
            {t.usecase_banner.dismiss}
          </button>
        </div>
      </div>
    </div>
  );
}
