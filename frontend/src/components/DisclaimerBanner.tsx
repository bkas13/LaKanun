"use client";

import { useI18n } from "@/contexts/I18nContext";

export default function DisclaimerBanner() {
  const { translate } = useI18n();

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 flex items-start gap-2.5">
      <svg className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <div>
        <p className="text-xs font-medium text-amber-800">{translate("disclaimer_banner.main")}</p>
        <p className="text-[11px] text-amber-600 mt-0.5">{translate("disclaimer_banner.sub")}</p>
      </div>
    </div>
  );
}