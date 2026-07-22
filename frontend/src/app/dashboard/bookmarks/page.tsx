"use client";

import { useEffect, useState, useCallback } from "react";
import { api, ApiError } from "@/lib/api";
import { useI18n } from "@/contexts/I18nContext";
import { useToast } from "@/contexts/ToastContext";

interface Bookmark {
  id: number;
  provision_id: string;
  title: string;
  note: string;
  country: string;
  created_at: string;
}

export default function BookmarksPage() {
  const { t } = useI18n();
  const { addToast } = useToast();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api<Bookmark[]>("/api/v1/saved/bookmarks");
      setBookmarks(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError(t.bookmarks.access_error);
      } else {
        setError("Failed to load bookmarks.");
      }
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const remove = async (id: number) => {
    try {
      await api(`/api/v1/saved/bookmarks/${id}`, { method: "DELETE" });
      setBookmarks((prev) => prev.filter((b) => b.id !== id));
      addToast("Removed", "success");
    } catch {
      setError("Failed to delete.");
    }
  };

  return (
    <div>
      <h1 className="text-lg font-bold mb-3">{t.bookmarks.title}</h1>
      {error && <div className="mb-3 p-2 rounded-lg bg-red-50 border border-red-200 text-red-600 text-xs">{error}</div>}
      {loading && <p className="text-gray-400 text-sm">Loading...</p>}
      {!loading && bookmarks.length === 0 && <p className="text-gray-400 text-sm">{t.bookmarks.empty}</p>}
      <div className="space-y-2">
        {bookmarks.map((b) => (
          <div key={b.id} className="bg-white rounded-xl border border-gray-200 p-3 flex items-start justify-between">
            <div className="min-w-0">
              <h3 className="font-medium text-sm truncate">{b.title}</h3>
              <p className="text-xs text-gray-400">{b.provision_id}</p>
              {b.note && <p className="text-xs text-gray-500 mt-1 italic">{b.note}</p>}
            </div>
            <button onClick={() => remove(b.id)} className="text-xs text-red-500 hover:text-red-700 shrink-0 ml-3">
              {t.bookmarks.remove}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
