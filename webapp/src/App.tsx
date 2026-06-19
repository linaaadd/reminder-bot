import { useCallback, useEffect, useMemo, useState } from "react";
import type { View } from "react-big-calendar";
import { api } from "./api";
import { ReminderCalendar } from "./components/Calendar";
import { LangSwitch } from "./components/LangSwitch";
import { ReminderModal } from "./components/ReminderModal";
import { detectLang, saveLang, strings, type Lang } from "./i18n";
import { PlusIcon } from "./components/icons";
import type { Reminder } from "./types";

export default function App() {
  const [lang, setLang] = useState<Lang>(detectLang());
  const t = useMemo(() => strings(lang), [lang]);

  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [view, setView] = useState<View>("month");
  const [date, setDate] = useState<Date>(new Date());

  // Modal state: undefined = closed; null = create; Reminder = edit.
  const [editing, setEditing] = useState<Reminder | null | undefined>(undefined);
  const [slotDate, setSlotDate] = useState<Date>(new Date());

  const load = useCallback(async () => {
    try {
      setError(null);
      setReminders(await api.list());
    } catch (e) {
      console.error(e);
      // TEMP: show the real error to pin down intermittent load failures.
      const detail = e instanceof Error ? e.message : String(e);
      setError(`${t.loadError}\n\n🧪 ${detail}`);
    }
  }, [t.loadError]);

  useEffect(() => {
    void load();
  }, [load]);

  const changeLang = (l: Lang) => {
    setLang(l);
    saveLang(l);
  };

  const handleSave = async (title: string, when: Date) => {
    try {
      if (editing) {
        await api.update(editing.id, { title, remind_at: when });
      } else {
        await api.create(title, when);
      }
      setEditing(undefined);
      await load();
    } catch (e) {
      console.error(e);
      setError(t.loadError);
    }
  };

  const handleDelete = async (id: number) => {
    await api.remove(id);
    setEditing(undefined);
    await load();
  };

  const handleMarkDone = async (id: number) => {
    await api.update(id, { status: "done" });
    setEditing(undefined);
    await load();
  };

  const openForEvent = (id: number) => {
    const r = reminders.find((x) => x.id === id);
    if (r) setEditing(r);
  };

  const openForSlot = (start: Date) => {
    setSlotDate(start);
    setEditing(null);
  };

  const openNew = () => {
    setSlotDate(new Date());
    setEditing(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>{t.appTitle}</h1>
        <LangSwitch lang={lang} onChange={changeLang} />
      </header>

      {error && <div className="banner error">{error}</div>}

      {reminders.length === 0 && !error && (
        <div className="banner empty">{t.empty}</div>
      )}

      <div className="calendar-wrap">
        <ReminderCalendar
          reminders={reminders}
          lang={lang}
          t={t}
          view={view}
          date={date}
          onView={setView}
          onNavigate={setDate}
          onSelectEvent={openForEvent}
          onSelectSlot={openForSlot}
        />
      </div>

      <button className="fab" onClick={openNew} aria-label={t.newReminder}>
        <PlusIcon size={26} />
      </button>

      {editing !== undefined && (
        <ReminderModal
          reminder={editing}
          initialDate={slotDate}
          t={t}
          onSave={handleSave}
          onDelete={handleDelete}
          onMarkDone={handleMarkDone}
          onClose={() => setEditing(undefined)}
        />
      )}
    </div>
  );
}
