"use client";

import { useState } from "react";
import { useI18n } from "@/contexts/I18nContext";
import { api } from "@/lib/api";

const FEEDBACK_TYPES = [
  { value: "suggestion", icon: "💡" },
  { value: "ui", icon: "🎨" },
  { value: "bug", icon: "🐛" },
  { value: "general", icon: "💬" },
  { value: "objection", icon: "📢" },
];

const TYPE_LABELS: Record<string, { en: string; ne: string; hi: string }> = {
  suggestion: { en: "Suggestion", ne: "सुझाव", hi: "सुझाव" },
  ui: { en: "UI Feedback", ne: "UI प्रतिक्रिया", hi: "UI प्रतिक्रिया" },
  bug: { en: "Bug Report", ne: "बग रिपोर्ट", hi: "बग रिपोर्ट" },
  general: { en: "General", ne: "सामान्य", hi: "सामान्य" },
  objection: { en: "Objection to Admin", ne: "प्रशासकलाई आपत्ति", hi: "प्रशासक को आपत्ति" },
};

const TYPE_DESCRIPTIONS: Record<string, { en: string; ne: string; hi: string }> = {
  suggestion: { en: "Help us improve with your ideas", ne: "आफ्ना विचारहरूले हामीलाई सुधार गर्न सहयोग गर्नुहोस्", hi: "अपने विचारों से हमें बेहतर बनाने में मदद करें" },
  ui: { en: "Report design or usability issues", ne: "डिजाइन वा प्रयोगिता समस्या रिपोर्ट गर्नुहोस्", hi: "डिज़ाइन या उपयोगिता समस्याओं की रिपोर्ट करें" },
  bug: { en: "Something not working? Tell us", ne: "केही काम गर्दैन? हामीलाई भन्नुहोस्", hi: "कुछ काम नहीं कर रहा? हमें बताएं" },
  general: { en: "Any thoughts or feedback", ne: "कुनै विचार वा प्रतिक्रिया", hi: "कोई विचार या प्रतिक्रिया" },
  objection: { en: "Raise a concern to administrators", ne: "प्रशासकहरूलाई चिन्ता उठाउनुहोस्", hi: "प्रशासकों को चिंता उठाएं" },
};

export default function FeedbackModal({
  open,
  onClose,
  prefillType,
}: {
  open: boolean;
  onClose: () => void;
  prefillType?: string;
}) {
  const { t, locale } = useI18n();
  const [type, setType] = useState(prefillType || "suggestion");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const reset = () => {
    setType(prefillType || "suggestion");
    setSubject("");
    setMessage("");
    setEmail("");
    setSubmitting(false);
    setSubmitted(false);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async () => {
    if (!subject.trim() || message.trim().length < 10) return;
    setSubmitting(true);
    try {
      const sessionId = localStorage.getItem("kanun_session_id") || "";
      await api("/api/v1/feedback/submit", {
        method: "POST",
        body: {
          feedback_type: type,
          subject: subject.trim(),
          message: message.trim(),
          email: email.trim() || null,
          page_url: window.location.href,
          locale,
          session_id: sessionId || null,
        },
        noAuth: true,
      });
      setSubmitted(true);
    } catch {}
    setSubmitting(false);
  };

  if (!open) return null;

  const labels = {
    title: locale === "ne" ? "तपाईंको प्रतिक्रिया" : locale === "hi" ? "आपकी प्रतिक्रिया" : "Your Feedback",
    subtitle: locale === "ne"
      ? "हामी तपाईंको विचारहरू महत्त्वपूर्ण मान्छौं। यसले हामीलाई राम्रो बन्न सहयोग गर्छ।"
      : locale === "hi"
        ? "हम आपके विचारों को महत्व देते हैं। यह हमें बेहतर बनने में मदद करता है।"
        : "We value your thoughts. It helps us serve you better.",
    type_label: locale === "ne" ? "प्रतिक्रियाको प्रकार" : locale === "hi" ? "प्रतिक्रिया का प्रकार" : "Feedback Type",
    subject_label: locale === "ne" ? "विषय" : locale === "hi" ? "विषय" : "Subject",
    subject_placeholder: locale === "ne" ? "छोटो विषय लेख्नुहोस्" : locale === "hi" ? "संक्षिप्त विषय लिखें" : "Brief subject line",
    message_label: locale === "ne" ? "विवरण" : locale === "hi" ? "विवरण" : "Message",
    message_placeholder: locale === "ne"
      ? "तपाईंको विस्तृत प्रतिक्रिया लेख्नुहोस्..."
      : locale === "hi"
        ? "अपनी विस्तृत प्रतिक्रिया लिखें..."
        : "Write your detailed feedback...",
    email_label: locale === "ne" ? "इमेल (ऐच्छिक)" : locale === "hi" ? "ईमेल (वैकल्पिक)" : "Email (optional)",
    email_placeholder: locale === "ne" ? "हामी तपाईंलाई सम्पर्क गर्न सकौं" : locale === "hi" ? "हम आपसे संपर्क कर सकें" : "So we can get back to you",
    submit: locale === "ne" ? "पठाउनुहोस्" : locale === "hi" ? "भेजें" : "Submit Feedback",
    submitting: locale === "ne" ? "पठाउँदै..." : locale === "hi" ? "भेज रहे हैं..." : "Submitting...",
    close: locale === "ne" ? "बन्द गर्नुहोस्" : locale === "hi" ? "बंद करें" : "Close",
    thank_title: locale === "ne" ? "धन्यवाद!" : locale === "hi" ? "धन्यवाद!" : "Thank You!",
    thank_msg: locale === "ne"
      ? "तपाईंको प्रतिक्रिया सफलतापूर्वक पठाइयो। हामी यसलाई गम्भीरतापूर्वक विचार गर्छौं।"
      : locale === "hi"
        ? "आपकी प्रतिक्रिया सफलतापूर्वक भेज दी गई। हम इसे गंभीरता से विचार करेंगे।"
        : "Your feedback has been submitted successfully. We take every piece of feedback seriously.",
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4"
      onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {submitted ? (
          <div className="px-6 py-12 text-center">
            <div className="w-14 h-14 rounded-full bg-cyan-100 flex items-center justify-center mx-auto mb-4">
              <svg className="w-7 h-7 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">{labels.thank_title}</h3>
            <p className="text-sm text-gray-500 mb-6">{labels.thank_msg}</p>
            <button
              onClick={handleClose}
              className="text-sm px-6 py-2 rounded-xl bg-cyan-600 text-white hover:bg-cyan-700 transition-colors font-medium"
            >
              {labels.close}
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="sticky top-0 bg-white rounded-t-2xl border-b border-gray-100 px-5 py-4 flex items-start justify-between">
              <div>
                <h2 className="text-base font-bold text-gray-900">{labels.title}</h2>
                <p className="text-[11px] text-gray-400 mt-0.5">{labels.subtitle}</p>
              </div>
              <button
                onClick={handleClose}
                className="w-7 h-7 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-400 shrink-0 transition-colors"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="px-5 py-4 space-y-4">
              {/* Type selector */}
              <div>
                <label className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2 block">
                  {labels.type_label}
                </label>
                <div className="grid grid-cols-5 gap-1.5">
                  {FEEDBACK_TYPES.map((ft) => (
                    <button
                      key={ft.value}
                      onClick={() => setType(ft.value)}
                      className={`flex flex-col items-center gap-1 py-2 rounded-xl text-[10px] font-medium transition-all ${
                        type === ft.value
                          ? "bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-sm"
                          : "bg-gray-50 text-gray-500 border border-gray-200 hover:bg-gray-100"
                      }`}
                    >
                      <span className="text-base">{ft.icon}</span>
                      <span className="leading-tight text-center">{TYPE_LABELS[ft.value][locale]}</span>
                    </button>
                  ))}
                </div>
                <p className="text-[10px] text-gray-400 mt-1.5">
                  {TYPE_DESCRIPTIONS[type]?.[locale]}
                </p>
              </div>

              {/* Subject */}
              <div>
                <label className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">
                  {labels.subject_label}
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder={labels.subject_placeholder}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 outline-none"
                  maxLength={200}
                />
              </div>

              {/* Message */}
              <div>
                <label className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">
                  {labels.message_label}
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={labels.message_placeholder}
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 outline-none resize-none"
                  maxLength={5000}
                />
                <div className="flex justify-between mt-1">
                  <span className={`text-[10px] ${message.length > 0 && message.length < 10 ? "text-red-400" : "text-gray-300"}`}>
                    {message.length < 10 ? `${10 - message.length} ${locale === "ne" ? "अक्षर बाँकी" : locale === "hi" ? "अक्षर शेष" : "more characters needed"}` : ""}
                  </span>
                  <span className="text-[10px] text-gray-300">{message.length}/5000</span>
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">
                  {labels.email_label}
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={labels.email_placeholder}
                  className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 outline-none"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-white rounded-b-2xl border-t border-gray-100 px-5 py-3 flex items-center justify-between">
              <span className="text-[10px] text-gray-400">
                {locale === "ne" ? "तपाईंको जानकारी सुरक्षित छ" : locale === "hi" ? "आपकी जानकारी सुरक्षित है" : "Your information is safe"}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={handleClose}
                  className="text-xs px-4 py-1.5 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors font-medium"
                >
                  {labels.close}
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={submitting || !subject.trim() || message.trim().length < 10}
                  className="text-xs px-4 py-1.5 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-medium"
                >
                  {submitting ? labels.submitting : labels.submit}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
