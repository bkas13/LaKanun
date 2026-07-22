"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { useI18n } from "@/contexts/I18nContext";

interface HistoryEntry {
  id: number;
  query: string;
  country: string | null;
  results_count: number;
  timestamp: string;
}

export default function SearchHistoryPage() {
  const { t } = useI18n();
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setEntries(await api<HistoryEntry[]>("/api/v1/saved/search-history?limit=50"));
    } catch { /* */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const remove = async (id: number) => {
    try {
      await api(`/api/v1/saved/search-history/${id}`, { method: "DELETE" });
      setEntries((prev) => prev.filter((e) => e.id !== id));
    } catch { /* */ }
  };

  return (
    <div>
      <h1 className="text-lg font-bold mb-3">{t.history.title}</h1>
      {loading && <p className="text-gray-400 text-sm">Loading...</p>}
      {!loading && entries.length === 0 && <p className="text-gray-400 text-sm">{t.history.empty}</p>}
      <div className="space-y-1">
        {entries.map((e) => (
          <div key={e.id} className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white border border-transparent hover:border-gray-200 transition-colors">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm font-medium truncate">{e.query}</span>
              {e.country && <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 shrink-0">{e.country}</span>}
              <span className="text-[10px] text-gray-400 shrink-0">{e.results_count} {t.history.results}</span>
            </div>
            <div className="flex items-center gap-2 shrink-0 ml-2">
              <span className="text-[10px] text-gray-300 hidden sm:block">{new Date(e.timestamp).toLocaleString()}</span>
              <button onClick={() => remove(e.id)} className="text-[10px] text-red-400 hover:text-red-600">{t.history.remove}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
