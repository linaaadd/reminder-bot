export type ReminderStatus = "pending" | "done" | "cancelled";

export interface Reminder {
  id: number;
  title: string;
  remind_at: string; // ISO 8601 UTC instant
  status: ReminderStatus;
  source: "voice" | "text" | "manual";
  created_at: string;
}

export interface Me {
  telegram_id: number;
  first_name: string | null;
  timezone: string;
  language: string | null;
}
