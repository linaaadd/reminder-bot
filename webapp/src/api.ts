/** Backend API client. Every request carries the signed Telegram initData. */
import { initData } from "./telegram";
import type { Me, Reminder } from "./types";

// Trim stray whitespace/newline and any trailing slash: a trailing space in
// the VITE_API_URL env var produces a malformed fetch URL ("…app /api/…") that
// fails with a misleading "Failed to fetch".
const BASE = (import.meta.env.VITE_API_URL ?? "").trim().replace(/\/+$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData,
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  // 204 No Content
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  me: () => request<Me>("/api/me"),

  list: () => request<Reminder[]>("/api/reminders"),

  create: (title: string, remindAt: Date) =>
    request<Reminder>("/api/reminders", {
      method: "POST",
      body: JSON.stringify({ title, remind_at: remindAt.toISOString() }),
    }),

  update: (
    id: number,
    patch: { title?: string; remind_at?: Date; status?: string },
  ) =>
    request<Reminder>(`/api/reminders/${id}`, {
      method: "PATCH",
      body: JSON.stringify({
        ...patch,
        remind_at: patch.remind_at ? patch.remind_at.toISOString() : undefined,
      }),
    }),

  remove: (id: number) =>
    request<void>(`/api/reminders/${id}`, { method: "DELETE" }),
};
