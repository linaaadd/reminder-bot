/**
 * Localization for the WebApp UI.
 *
 * Language is auto-detected from Telegram's language_code with an English
 * fallback, and can be overridden manually (persisted in localStorage).
 * Minimum set: en / ru / de / uk / es — add a language by extending STRINGS.
 */
import { tgLanguage } from "./telegram";

export type Lang = "en" | "ru" | "de" | "uk" | "es";

export interface Strings {
  appTitle: string;
  newReminder: string;
  editReminder: string;
  titleLabel: string;
  titlePlaceholder: string;
  whenLabel: string;
  save: string;
  cancel: string;
  delete: string;
  markDone: string;
  done: string;
  pending: string;
  cancelled: string;
  empty: string;
  loadError: string;
  // react-big-calendar toolbar/messages
  today: string;
  previous: string;
  next: string;
  month: string;
  week: string;
  day: string;
  agenda: string;
  noEvents: string;
}

const STRINGS: Record<Lang, Strings> = {
  en: {
    appTitle: "My reminders",
    newReminder: "New reminder",
    editReminder: "Edit reminder",
    titleLabel: "What",
    titlePlaceholder: "e.g. Buy milk",
    whenLabel: "When",
    save: "Save",
    cancel: "Cancel",
    delete: "Delete",
    markDone: "Mark done",
    done: "Done",
    pending: "Pending",
    cancelled: "Cancelled",
    empty: "No reminders yet. Tap + to add one.",
    loadError: "Couldn't load your reminders.",
    today: "Today",
    previous: "Back",
    next: "Next",
    month: "Month",
    week: "Week",
    day: "Day",
    agenda: "List",
    noEvents: "No reminders in this range.",
  },
  ru: {
    appTitle: "Мои напоминания",
    newReminder: "Новое напоминание",
    editReminder: "Изменить напоминание",
    titleLabel: "Что",
    titlePlaceholder: "напр. Купить молоко",
    whenLabel: "Когда",
    save: "Сохранить",
    cancel: "Отмена",
    delete: "Удалить",
    markDone: "Выполнено",
    done: "Готово",
    pending: "Активно",
    cancelled: "Отменено",
    empty: "Пока нет напоминаний. Нажми +, чтобы добавить.",
    loadError: "Не удалось загрузить напоминания.",
    today: "Сегодня",
    previous: "Назад",
    next: "Вперёд",
    month: "Месяц",
    week: "Неделя",
    day: "День",
    agenda: "Список",
    noEvents: "Нет напоминаний в этом диапазоне.",
  },
  de: {
    appTitle: "Meine Erinnerungen",
    newReminder: "Neue Erinnerung",
    editReminder: "Erinnerung bearbeiten",
    titleLabel: "Was",
    titlePlaceholder: "z. B. Milch kaufen",
    whenLabel: "Wann",
    save: "Speichern",
    cancel: "Abbrechen",
    delete: "Löschen",
    markDone: "Erledigt",
    done: "Erledigt",
    pending: "Offen",
    cancelled: "Abgebrochen",
    empty: "Noch keine Erinnerungen. Tippe auf +.",
    loadError: "Erinnerungen konnten nicht geladen werden.",
    today: "Heute",
    previous: "Zurück",
    next: "Weiter",
    month: "Monat",
    week: "Woche",
    day: "Tag",
    agenda: "Liste",
    noEvents: "Keine Erinnerungen in diesem Zeitraum.",
  },
  uk: {
    appTitle: "Мої нагадування",
    newReminder: "Нове нагадування",
    editReminder: "Редагувати нагадування",
    titleLabel: "Що",
    titlePlaceholder: "напр. Купити молоко",
    whenLabel: "Коли",
    save: "Зберегти",
    cancel: "Скасувати",
    delete: "Видалити",
    markDone: "Виконано",
    done: "Готово",
    pending: "Активне",
    cancelled: "Скасовано",
    empty: "Поки немає нагадувань. Натисни +, щоб додати.",
    loadError: "Не вдалося завантажити нагадування.",
    today: "Сьогодні",
    previous: "Назад",
    next: "Далі",
    month: "Місяць",
    week: "Тиждень",
    day: "День",
    agenda: "Список",
    noEvents: "Немає нагадувань у цьому діапазоні.",
  },
  es: {
    appTitle: "Mis recordatorios",
    newReminder: "Nuevo recordatorio",
    editReminder: "Editar recordatorio",
    titleLabel: "Qué",
    titlePlaceholder: "p. ej. Comprar leche",
    whenLabel: "Cuándo",
    save: "Guardar",
    cancel: "Cancelar",
    delete: "Eliminar",
    markDone: "Hecho",
    done: "Hecho",
    pending: "Pendiente",
    cancelled: "Cancelado",
    empty: "Aún no hay recordatorios. Pulsa + para añadir.",
    loadError: "No se pudieron cargar los recordatorios.",
    today: "Hoy",
    previous: "Atrás",
    next: "Siguiente",
    month: "Mes",
    week: "Semana",
    day: "Día",
    agenda: "Lista",
    noEvents: "No hay recordatorios en este rango.",
  },
};

export const SUPPORTED_LANGS = Object.keys(STRINGS) as Lang[];

const STORAGE_KEY = "reminder_lang";

export function detectLang(): Lang {
  const saved = localStorage.getItem(STORAGE_KEY) as Lang | null;
  if (saved && saved in STRINGS) return saved;
  const short = (tgLanguage ?? "en").split("-")[0] as Lang;
  return short in STRINGS ? short : "en";
}

export function saveLang(lang: Lang): void {
  localStorage.setItem(STORAGE_KEY, lang);
}

export function strings(lang: Lang): Strings {
  return STRINGS[lang];
}
