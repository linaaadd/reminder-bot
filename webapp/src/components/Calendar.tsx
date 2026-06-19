import { useMemo, type CSSProperties } from "react";
import {
  Calendar as BigCalendar,
  dateFnsLocalizer,
  type Event,
  type View,
} from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { enUS, ru, de, uk, es } from "date-fns/locale";
import type { Lang, Strings } from "../i18n";
import type { Reminder } from "../types";
import { CalendarToolbar } from "./CalendarToolbar";

const LOCALES = { en: enUS, ru, de, uk, es } as const;

// Distinct, accessible palette. Each reminder gets a stable color derived from
// its title, so the same task always shows the same color and different tasks
// are visually distinguishable ("sort by color").
const PALETTE = [
  "#2563EB", // blue
  "#059669", // green
  "#D97706", // amber
  "#DC2626", // red
  "#7C3AED", // violet
  "#0891B2", // cyan
  "#DB2777", // pink
  "#65A30D", // lime
];

function colorFor(r: Reminder): string {
  let h = 0;
  for (let i = 0; i < r.title.length; i++) h = (h * 31 + r.title.charCodeAt(i)) | 0;
  return PALETTE[Math.abs(h) % PALETTE.length];
}

export interface ReminderEvent extends Event {
  id: number;
  status: Reminder["status"];
  color: string;
}

/** Month view: render reminders as compact colored dots (no text). */
function MonthEvent({ event }: { event: ReminderEvent }) {
  const cls =
    event.status === "done"
      ? "evt-dot done"
      : event.status === "cancelled"
        ? "evt-dot cancelled"
        : "evt-dot";
  return (
    <span
      className={cls}
      style={{ ["--dot" as string]: event.color } as CSSProperties}
      title={event.title as string}
    />
  );
}

export function ReminderCalendar({
  reminders,
  lang,
  t,
  view,
  date,
  onView,
  onNavigate,
  onSelectEvent,
  onSelectSlot,
}: {
  reminders: Reminder[];
  lang: Lang;
  t: Strings;
  view: View;
  date: Date;
  onView: (v: View) => void;
  onNavigate: (d: Date) => void;
  onSelectEvent: (id: number) => void;
  onSelectSlot: (start: Date) => void;
}) {
  const localizer = useMemo(
    () =>
      dateFnsLocalizer({
        format,
        parse,
        startOfWeek: () => startOfWeek(new Date(), { locale: LOCALES[lang] }),
        getDay,
        locales: LOCALES,
      }),
    [lang],
  );

  const events: ReminderEvent[] = useMemo(
    () =>
      reminders.map((r) => {
        const start = new Date(r.remind_at);
        return {
          id: r.id,
          title: r.title,
          start,
          end: new Date(start.getTime() + 30 * 60 * 1000),
          status: r.status,
          color: colorFor(r),
        };
      }),
    [reminders],
  );

  const messages = useMemo(
    () => ({
      today: t.today,
      previous: t.previous,
      next: t.next,
      month: t.month,
      week: t.week,
      day: t.day,
      agenda: t.agenda,
      noEventsInRange: t.noEvents,
    }),
    [t],
  );

  return (
    <BigCalendar
      localizer={localizer}
      culture={lang}
      events={events}
      view={view}
      date={date}
      onView={onView}
      onNavigate={onNavigate}
      views={["month", "week", "day", "agenda"]}
      selectable
      popup
      messages={messages}
      components={{
        toolbar: (props) => <CalendarToolbar {...props} t={t} />,
        month: { event: MonthEvent },
      }}
      onSelectEvent={(e) => onSelectEvent((e as ReminderEvent).id)}
      onSelectSlot={(slot) => onSelectSlot(slot.start as Date)}
      eventPropGetter={(e) => {
        const ev = e as ReminderEvent;
        const cls =
          ev.status === "done"
            ? "rbc-event-done"
            : ev.status === "cancelled"
              ? "rbc-event-cancelled"
              : "";
        // Color the time-grid (week/day) and agenda bars by reminder color.
        // Month uses the dot component, where CSS clears this background.
        return { className: cls, style: { backgroundColor: ev.color } };
      }}
      style={{ height: "100%" }}
    />
  );
}
