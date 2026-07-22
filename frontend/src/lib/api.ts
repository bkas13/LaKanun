const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiOptions {
  method?: string;
  body?: unknown;
  token?: string;
  noAuth?: boolean;
  signal?: AbortSignal;
}

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(JSON.stringify(data));
    this.status = status;
    this.data = data;
  }
}

export async function api<T = unknown>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const { method = "GET", body, token, noAuth, signal } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  } else if (!noAuth) {
    const stored = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (stored) {
      headers["Authorization"] = `Bearer ${stored}`;
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(res.status, data);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export function setTokens(access: string, refresh: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }
}

export function getAccessToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("access_token");
  }
  return null;
}

export function clearTokens() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
}

export async function rawFetch<T = unknown>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  const stored = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (stored) headers["Authorization"] = `Bearer ${stored}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...headers, ...Object.fromEntries(new Headers(init.headers)) },
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new ApiError(res.status, data);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function refreshAccessToken(): Promise<string | null> {
  const refresh = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
  if (!refresh) return null;

  try {
    const data = await api<{ access_token: string }>("/api/v1/auth/refresh", {
      method: "POST",
      body: { refresh_token: refresh },
      noAuth: true,
    });
    setTokens(data.access_token, refresh);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}
