"use client";

import { useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import FeedbackModal from "./FeedbackModal";

export default function FeedbackCTA({ prefillType }: { prefillType?: string } = {}) {
  const { translate } = useI18n();
  const [open, setOpen] = useState(false);

  const label = translate("feedback.give_feedback");

  return (
    <>
      {/* Floating button — bottom right */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-5 right-5 z-[80] flex items-center gap-2 px-4 py-2.5 bg-cyan-600 text-white text-xs font-semibold rounded-full shadow-lg hover:bg-cyan-700 hover:shadow-xl transition-all group"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <span className="hidden sm:inline">{label}</span>
      </button>

      <FeedbackModal open={open} onClose={() => setOpen(false)} prefillType={prefillType} />
    </>
  );
}
