"use client";

import { useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import Navbar from "@/components/Navbar";

function CollapsibleItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="text-sm font-medium text-gray-800 pr-3">{q}</span>
        <svg
          className={`w-4 h-4 text-gray-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-4 pb-3 text-xs text-gray-600 leading-relaxed border-t border-gray-100 pt-2">
          {a}
        </div>
      )}
    </div>
  );
}

function CollapsibleSection({ title, desc, items }: { title: string; desc?: string; items: { q: string; a: string }[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div>
          <h3 className="text-sm font-bold text-gray-900">{title}</h3>
          {desc && <p className="text-[11px] text-gray-500 mt-0.5">{desc}</p>}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-5 pb-4 space-y-2 border-t border-gray-100 pt-3">
          {items.map((item, i) => (
            <CollapsibleItem key={i} q={item.q} a={item.a} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function FAQPage() {
  const { t, translate } = useI18n();
  const faq = t.faq_page;

  return (
    <>
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-8 pb-20 md:pb-8">
        <div className="text-center mb-8">
          <h1 className="text-xl font-bold text-gray-900">{translate("faq_page.title")}</h1>
          <p className="text-xs text-gray-500 mt-1">{translate("faq_page.subtitle")}</p>
        </div>

        <div className="space-y-4">
          <CollapsibleSection
            title={translate("faq_page.how_to_use.title")}
            items={faq.how_to_use.items}
          />
          <CollapsibleSection
            title={translate("faq_page.layman.title")}
            desc={translate("faq_page.layman.desc")}
            items={faq.layman.items}
          />
          <CollapsibleSection
            title={translate("faq_page.expert.title")}
            desc={translate("faq_page.expert.desc")}
            items={faq.expert.items}
          />
        </div>

        <div className="mt-8 text-center">
          <p className="text-[11px] text-gray-400">{translate("faq_page.still_have_questions")}</p>
        </div>
      </div>
    </>
  );
}