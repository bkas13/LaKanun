"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import { useI18n } from "@/contexts/I18nContext";
import { useToast } from "@/contexts/ToastContext";

interface CaseNote {
  id: number;
  title: string;
  content: string;
  tags: string[];
  linked_provisions: string[];
  created_at: string;
  updated_at: string;
}

export default function NotesPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", tags: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<CaseNote[]>("/api/v1/saved/notes");
      setNotes(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError(t.notes.access_error);
      } else {
        setError("Failed to load notes.");
      }
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const note = await api<CaseNote>("/api/v1/saved/notes", {
        method: "POST",
        body: {
          title: form.title,
          content: form.content,
          tags: form.tags ? form.tags.split(",").map((t) => t.trim()).filter(Boolean) : [],
          linked_provisions: [],
        },
      });
      setNotes((prev) => [note, ...prev]);
      setForm({ title: "", content: "", tags: "" });
      setShowForm(false);
      addToast("Note saved", "success");
    } catch {
      setError("Failed to create note.");
    }
  };

  const remove = async (id: number) => {
    try {
      await api(`/api/v1/saved/notes/${id}`, { method: "DELETE" });
      setNotes((prev) => prev.filter((n) => n.id !== id));
      addToast("Deleted", "success");
    } catch {
      setError("Failed to delete.");
    }
  };

  const inputClass = "w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-cyan-500 outline-none bg-gray-50 focus:bg-white";

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-lg font-bold">{t.notes.title}</h1>
        <button onClick={() => setShowForm(!showForm)} className="text-xs px-3 py-1.5 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 transition-colors">
          {showForm ? t.notes.cancel : t.notes.new_note}
        </button>
      </div>
      {error && <div className="mb-3 p-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-xs">{error}</div>}
      {showForm && (
        <form onSubmit={create} className="bg-white rounded-xl border border-gray-200 p-4 mb-4 space-y-2">
          <input type="text" placeholder={t.notes.title_placeholder} required value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} className={inputClass} />
          <textarea placeholder={t.notes.content_placeholder} required rows={3} value={form.content} onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))} className={inputClass} />
          <input type="text" placeholder={t.notes.tags_placeholder} value={form.tags} onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))} className={inputClass} />
          <button type="submit" className="px-4 py-2 rounded-xl bg-cyan-600 text-white text-sm font-medium hover:bg-cyan-700">
            {t.notes.save}
          </button>
        </form>
      )}
      {loading && <p className="text-gray-400 text-sm">Loading...</p>}
      {!loading && notes.length === 0 && <p className="text-gray-400 text-sm">{t.notes.empty}</p>}
      <div className="space-y-2">
        {notes.map((n) => (
          <div key={n.id} className="bg-white rounded-xl border border-gray-200 p-3">
            <div className="flex items-start justify-between">
              <div className="min-w-0 flex-1">
                <h3 className="font-medium text-sm">{n.title}</h3>
                <p className="text-xs text-gray-600 mt-1 whitespace-pre-wrap line-clamp-3">{n.content}</p>
                {n.tags && n.tags.length > 0 && (
                  <div className="flex gap-1 mt-1.5 flex-wrap">
                    {(Array.isArray(n.tags) ? n.tags : []).filter(Boolean).map((tag, i) => (
                      <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-100 text-cyan-700">{typeof tag === "string" ? tag.trim() : String(tag)}</span>
                    ))}
                  </div>
                )}
              </div>
              <button onClick={() => remove(n.id)} className="text-xs text-red-500 hover:text-red-700 shrink-0 ml-3">
                {t.notes.delete}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
