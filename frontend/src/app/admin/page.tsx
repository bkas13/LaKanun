"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useI18n } from "@/contexts/I18nContext";
import Navbar from "@/components/Navbar";
import { api } from "@/lib/api";

interface AdminUser {
  id: number;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  ai_tier?: string;
}

interface TierUser {
  id: number;
  email: string;
  name: string;
  role: string;
  ai_tier: string;
  daily_limit: number;
  is_active: boolean;
}

interface TierStats {
  total: number;
  by_tier: Record<string, number>;
}

interface CorpusStats {
  total_documents: number;
  total_provisions: number;
  documents: Record<string, number>;
}

const TIER_COLORS: Record<string, string> = {
  free: "bg-gray-100 text-gray-600 border-gray-200",
  basic: "bg-blue-50 text-blue-600 border-blue-200",
  pro: "bg-violet-50 text-violet-600 border-violet-200",
  enterprise: "bg-amber-50 text-amber-600 border-amber-200",
};

const TIER_LABELS: Record<string, string> = {
  free: "Free",
  basic: "Basic",
  pro: "Pro",
  enterprise: "Enterprise",
};

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const { t } = useI18n();
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [tierUsers, setTierUsers] = useState<TierUser[]>([]);
  const [tierStats, setTierStats] = useState<TierStats | null>(null);
  const [stats, setStats] = useState<CorpusStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [tierFilter, setTierFilter] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"users" | "tiers">("users");

  useEffect(() => {
    if (!authLoading && (!user || user.role !== "admin")) router.push("/dashboard");
  }, [user, authLoading, router]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [u, s, ts, tu] = await Promise.all([
        api<AdminUser[]>("/api/v1/admin/users"),
        api<CorpusStats>("/api/v1/admin/stats"),
        api<TierStats>("/api/v1/admin/ai-tiers/stats"),
        api<TierUser[]>(`/api/v1/admin/ai-tiers${tierFilter ? `?tier=${tierFilter}` : ""}`),
      ]);
      setUsers(u);
      setStats(s);
      setTierStats(ts);
      setTierUsers(tu);
    } catch { /* */ } finally { setLoading(false); }
  }, [tierFilter]);

  useEffect(() => { if (user?.role === "admin") load(); }, [user, load]);

  const updateRole = async (userId: number, role: string) => {
    try {
      await api(`/api/v1/admin/users/${userId}`, { method: "PATCH", body: { role } });
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, role } : u)));
    } catch { /* */ }
  };

  const updateTier = async (userId: number, ai_tier: string) => {
    try {
      await api(`/api/v1/admin/ai-tiers/${userId}`, { method: "PATCH", body: { ai_tier } });
      setTierUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, ai_tier } : u)));
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, ai_tier } : u)));
    } catch { /* */ }
  };

  if (authLoading || !user || user.role !== "admin") return null;

  return (
    <>
      <Navbar />
      <div className="flex-1 flex">
        <aside className="w-48 bg-white border-r border-gray-200 p-3 shrink-0 hidden md:block">
          <a href="/dashboard" className="block px-2.5 py-1.5 rounded-lg text-xs text-gray-600 hover:bg-gray-100">
            ← {t.dashboard.back_to_dashboard}
          </a>
        </aside>
        <main className="flex-1 p-4 pb-20 md:pb-6 overflow-auto">
          <h1 className="text-lg font-bold mb-4">{t.admin.title}</h1>

          {loading && <p className="text-gray-400 text-sm">Loading...</p>}

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
              <Stat label={t.admin.documents} value={String(stats.total_documents)} />
              <Stat label={t.admin.provisions} value={stats.total_provisions.toLocaleString()} />
              <Stat label={t.admin.users} value={String(users.length)} />
              {tierStats && (
                <Stat
                  label="AI Users"
                  value={String(tierStats.total - (tierStats.by_tier.free || 0))}
                  accent
                />
              )}
            </div>
          )}

          {/* Tier Distribution Bar */}
          {tierStats && (
            <div className="bg-white rounded-xl border border-gray-200 p-4 mb-5">
              <h2 className="text-xs font-semibold text-gray-500 uppercase mb-3">AI Tier Distribution</h2>
              <div className="flex rounded-lg overflow-hidden h-5 mb-2">
                {(["free", "basic", "pro", "enterprise"] as const).map((tier) => {
                  const count = tierStats.by_tier[tier] || 0;
                  const pct = tierStats.total > 0 ? (count / tierStats.total) * 100 : 0;
                  if (pct === 0) return null;
                  const colors: Record<string, string> = {
                    free: "bg-gray-200",
                    basic: "bg-blue-400",
                    pro: "bg-violet-500",
                    enterprise: "bg-amber-400",
                  };
                  return (
                    <div
                      key={tier}
                      className={`${colors[tier]} transition-all`}
                      style={{ width: `${pct}%` }}
                      title={`${TIER_LABELS[tier]}: ${count}`}
                    />
                  );
                })}
              </div>
              <div className="flex gap-4 text-[10px] text-gray-400">
                {(["free", "basic", "pro", "enterprise"] as const).map((tier) => (
                  <div key={tier} className="flex items-center gap-1">
                    <div className={`w-2 h-2 rounded-full ${
                      tier === "free" ? "bg-gray-300" :
                      tier === "basic" ? "bg-blue-400" :
                      tier === "pro" ? "bg-violet-500" : "bg-amber-400"
                    }`} />
                    {TIER_LABELS[tier]}: {tierStats.by_tier[tier] || 0}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-1 mb-4 bg-gray-100 rounded-lg p-0.5 w-fit">
            <button
              onClick={() => setActiveTab("users")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === "users" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              User Management
            </button>
            <button
              onClick={() => setActiveTab("tiers")}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === "tiers" ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              AI Tier Management
            </button>
          </div>

          {/* User Management Tab */}
          {activeTab === "users" && (
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h2 className="text-sm font-semibold mb-3">{t.admin.user_management}</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-left text-gray-400 border-b">
                      <th className="pb-1.5">{t.admin.email}</th>
                      <th className="pb-1.5">{t.admin.name}</th>
                      <th className="pb-1.5">{t.admin.role}</th>
                      <th className="pb-1.5">Tier</th>
                      <th className="pb-1.5">{t.admin.active}</th>
                      <th className="pb-1.5">{t.admin.joined}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-b last:border-0">
                        <td className="py-1.5">{u.email}</td>
                        <td className="py-1.5">{u.name}</td>
                        <td className="py-1.5">
                          <select value={u.role} onChange={(e) => updateRole(u.id, e.target.value)} className="px-1.5 py-0.5 border rounded text-[10px]">
                            {["public", "lawyer", "judge", "admin"].map((r) => <option key={r} value={r}>{r}</option>)}
                          </select>
                        </td>
                        <td className="py-1.5">
                          <span className={`inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded-full border ${TIER_COLORS[u.ai_tier || "free"]}`}>
                            {TIER_LABELS[u.ai_tier || "free"]}
                          </span>
                        </td>
                        <td className="py-1.5">
                          <span className={u.is_active ? "text-green-600" : "text-red-500"}>
                            {u.is_active ? t.admin.yes : t.admin.no}
                          </span>
                        </td>
                        <td className="py-1.5 text-gray-400">{new Date(u.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* AI Tier Management Tab */}
          {activeTab === "tiers" && (
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">AI Tier Management</h2>
                <div className="flex gap-1">
                  {["", "free", "basic", "pro", "enterprise"].map((tier) => (
                    <button
                      key={tier}
                      onClick={() => setTierFilter(tier)}
                      className={`px-2 py-1 rounded-md text-[10px] font-medium transition-colors ${
                        tierFilter === tier
                          ? "bg-cyan-600 text-white"
                          : "bg-gray-100 text-gray-500 hover:bg-gray-200"
                      }`}
                    >
                      {tier ? TIER_LABELS[tier] : "All"}
                    </button>
                  ))}
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-left text-gray-400 border-b">
                      <th className="pb-1.5">User</th>
                      <th className="pb-1.5">Role</th>
                      <th className="pb-1.5">Current Tier</th>
                      <th className="pb-1.5">Daily Limit</th>
                      <th className="pb-1.5">Change Tier</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tierUsers.map((u) => (
                      <tr key={u.id} className="border-b last:border-0 hover:bg-gray-50">
                        <td className="py-2">
                          <div className="font-medium">{u.name}</div>
                          <div className="text-[10px] text-gray-400">{u.email}</div>
                        </td>
                        <td className="py-2">
                          <span className="text-[10px] text-gray-500">{u.role}</span>
                        </td>
                        <td className="py-2">
                          <span className={`inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded-full border ${TIER_COLORS[u.ai_tier]}`}>
                            {TIER_LABELS[u.ai_tier]}
                          </span>
                        </td>
                        <td className="py-2 text-[10px] text-gray-500">
                          {u.daily_limit === -1 ? "Unlimited" : u.daily_limit === 0 ? "None" : `${u.daily_limit}/day`}
                        </td>
                        <td className="py-2">
                          <select
                            value={u.ai_tier}
                            onChange={(e) => updateTier(u.id, e.target.value)}
                            className="px-2 py-1 border rounded text-[10px] bg-white"
                          >
                            {["free", "basic", "pro", "enterprise"].map((tier) => (
                              <option key={tier} value={tier}>{TIER_LABELS[tier]}</option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {tierUsers.length === 0 && (
                  <p className="text-center text-gray-400 text-xs py-6">No users found</p>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className={`rounded-xl border p-3 ${accent ? "bg-cyan-50 border-cyan-200" : "bg-white border-gray-200"}`}>
      <div className={`text-[10px] uppercase ${accent ? "text-cyan-500" : "text-gray-400"}`}>{label}</div>
      <div className={`text-lg font-bold mt-0.5 ${accent ? "text-cyan-700" : ""}`}>{value}</div>
    </div>
  );
}
