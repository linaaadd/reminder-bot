import { useMemo } from "react";
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

export interface ReminderEvent extends Event {
  id: number;
  status: Reminder["status"];
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
        return { className: cls };
      }}
      style={{ height: "100%" }}
    />
  );
}
