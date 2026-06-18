"""Translation tables. Add a language by adding one more dict.

Minimum set: en, ru, de, uk, es. English is the fallback and the source of
truth for which keys must exist.
"""
from __future__ import annotations

LOCALES: dict[str, dict[str, str]] = {
    "en": {
        "btn_webapp": "📅 My reminders",
        "btn_save": "✅ Save",
        "btn_edit": "✏️ Edit",
        "btn_cancel": "❌ Cancel",
        "btn_done": "✅ Done",
        "btn_snooze": "⏰ Snooze 1h",
        "start_greeting": (
            "👋 Hi, {name}!\n\n"
            "I'm your reminder bot. Just send me a voice message or text — tell "
            "me *what* to remind you about and *when*. For example:\n"
            "• “remind me tomorrow at 6pm to buy milk”\n"
            "• “call mom in 2 hours”\n\n"
            "I understand many languages and reply in yours."
        ),
        "start_tz_hint": (
            "🌍 Your timezone is set to *{tz}*. If that's wrong, set it with "
            "/timezone so reminders fire at the right moment."
        ),
        "help": (
            "🤖 *How to use me*\n\n"
            "Send a voice message or text describing a reminder — what and when.\n\n"
            "*Commands*\n"
            "/list — your upcoming reminders\n"
            "/timezone — set your timezone\n"
            "/help — this message\n\n"
            "Open 📅 *My reminders* for the calendar."
        ),
        "list_empty": "You have no upcoming reminders. 🎉",
        "list_header": "🗓 *Your upcoming reminders:*",
        "list_item": "• *{title}* — {when}",
        "recognized": "🎙 I heard: _{text}_",
        "confirm": "📝 Remind you: *{title}*\n🕒 When: *{when}*",
        "saved_ok": "✅ Saved! I'll remind you on *{when}*.",
        "cancelled": "❌ Cancelled.",
        "edit_prompt": "✏️ Okay, send the reminder again (what and when).",
        "needs_time": (
            "🤔 I couldn't figure out the time. {message}"
        ),
        "needs_time_generic": (
            "🤔 When should I remind you? Try “tomorrow at 6pm” or “in 2 hours”."
        ),
        "tz_current": "🌍 Your current timezone: *{tz}*.",
        "tz_usage": (
            "Send your timezone as an IANA name, e.g. `/timezone Europe/Berlin` "
            "or `/timezone America/New_York`."
        ),
        "tz_set_ok": "✅ Timezone set to *{tz}*.",
        "tz_invalid": "⚠️ Unknown timezone. Use an IANA name like `Europe/Berlin`.",
        "reminder_fire": "🔔 *Reminder:* {title}",
        "done_ok": "✅ Marked as done.",
        "snoozed_ok": "⏰ Snoozed until *{when}*.",
        "err_stt": "😕 I couldn't understand the audio. Try again or send text.",
        "err_llm": "😕 I'm having trouble right now. Please try again in a moment.",
        "err_generic": "😕 Something went wrong. Please try again.",
        "expired": "This reminder is no longer available.",
    },
    "ru": {
        "btn_webapp": "📅 Мои напоминания",
        "btn_save": "✅ Сохранить",
        "btn_edit": "✏️ Изменить",
        "btn_cancel": "❌ Отмена",
        "btn_done": "✅ Готово",
        "btn_snooze": "⏰ Отложить на час",
        "start_greeting": (
            "👋 Привет, {name}!\n\n"
            "Я бот-напоминалка. Просто пришли голосовое или текст — скажи, *о чём* "
            "напомнить и *когда*. Например:\n"
            "• «напомни завтра в 6 вечера купить молоко»\n"
            "• «позвонить маме через 2 часа»\n\n"
            "Понимаю много языков и отвечаю на твоём."
        ),
        "start_tz_hint": (
            "🌍 Твой часовой пояс — *{tz}*. Если он неверный, задай его командой "
            "/timezone, чтобы напоминания приходили вовремя."
        ),
        "help": (
            "🤖 *Как мной пользоваться*\n\n"
            "Пришли голосовое или текст с напоминанием — что и когда.\n\n"
            "*Команды*\n"
            "/list — ближайшие напоминания\n"
            "/timezone — установить часовой пояс\n"
            "/help — эта справка\n\n"
            "Открой 📅 *Мои напоминания* для календаря."
        ),
        "list_empty": "Ближайших напоминаний нет. 🎉",
        "list_header": "🗓 *Твои ближайшие напоминания:*",
        "list_item": "• *{title}* — {when}",
        "recognized": "🎙 Распознал: _{text}_",
        "confirm": "📝 Напомнить: *{title}*\n🕒 Когда: *{when}*",
        "saved_ok": "✅ Сохранил! Напомню *{when}*.",
        "cancelled": "❌ Отменено.",
        "edit_prompt": "✏️ Хорошо, пришли напоминание заново (что и когда).",
        "needs_time": "🤔 Не понял время. {message}",
        "needs_time_generic": (
            "🤔 Когда напомнить? Например: «завтра в 18:00» или «через 2 часа»."
        ),
        "tz_current": "🌍 Твой часовой пояс: *{tz}*.",
        "tz_usage": (
            "Пришли часовой пояс в формате IANA, например "
            "`/timezone Europe/Moscow` или `/timezone Europe/Berlin`."
        ),
        "tz_set_ok": "✅ Часовой пояс установлен: *{tz}*.",
        "tz_invalid": "⚠️ Неизвестный пояс. Используй IANA-имя, напр. `Europe/Berlin`.",
        "reminder_fire": "🔔 *Напоминание:* {title}",
        "done_ok": "✅ Отметил выполненным.",
        "snoozed_ok": "⏰ Отложил до *{when}*.",
        "err_stt": "😕 Не разобрал аудио. Попробуй ещё раз или пришли текстом.",
        "err_llm": "😕 Сейчас не получается. Попробуй через минуту.",
        "err_generic": "😕 Что-то пошло не так. Попробуй ещё раз.",
        "expired": "Это напоминание больше недоступно.",
    },
    "de": {
        "btn_webapp": "📅 Meine Erinnerungen",
        "btn_save": "✅ Speichern",
        "btn_edit": "✏️ Ändern",
        "btn_cancel": "❌ Abbrechen",
        "btn_done": "✅ Erledigt",
        "btn_snooze": "⏰ 1 Std. später",
        "start_greeting": (
            "👋 Hallo, {name}!\n\n"
            "Ich bin dein Erinnerungs-Bot. Schick mir einfach eine Sprach- oder "
            "Textnachricht — sag mir *woran* und *wann* ich dich erinnern soll. "
            "Zum Beispiel:\n"
            "• „erinnere mich morgen um 18 Uhr, Milch zu kaufen“\n"
            "• „Mama in 2 Stunden anrufen“\n\n"
            "Ich verstehe viele Sprachen und antworte in deiner."
        ),
        "start_tz_hint": (
            "🌍 Deine Zeitzone ist *{tz}*. Falls das falsch ist, setze sie mit "
            "/timezone, damit Erinnerungen pünktlich kommen."
        ),
        "help": (
            "🤖 *So funktioniert's*\n\n"
            "Schick eine Sprach- oder Textnachricht — was und wann.\n\n"
            "*Befehle*\n"
            "/list — kommende Erinnerungen\n"
            "/timezone — Zeitzone setzen\n"
            "/help — diese Hilfe\n\n"
            "Öffne 📅 *Meine Erinnerungen* für den Kalender."
        ),
        "list_empty": "Keine kommenden Erinnerungen. 🎉",
        "list_header": "🗓 *Deine kommenden Erinnerungen:*",
        "list_item": "• *{title}* — {when}",
        "recognized": "🎙 Verstanden: _{text}_",
        "confirm": "📝 Erinnern an: *{title}*\n🕒 Wann: *{when}*",
        "saved_ok": "✅ Gespeichert! Ich erinnere dich am *{when}*.",
        "cancelled": "❌ Abgebrochen.",
        "edit_prompt": "✏️ Okay, schick die Erinnerung erneut (was und wann).",
        "needs_time": "🤔 Ich habe die Zeit nicht verstanden. {message}",
        "needs_time_generic": (
            "🤔 Wann soll ich dich erinnern? Z. B. „morgen um 18 Uhr“ oder "
            "„in 2 Stunden“."
        ),
        "tz_current": "🌍 Deine Zeitzone: *{tz}*.",
        "tz_usage": (
            "Schick deine Zeitzone als IANA-Name, z. B. `/timezone Europe/Berlin`."
        ),
        "tz_set_ok": "✅ Zeitzone gesetzt: *{tz}*.",
        "tz_invalid": "⚠️ Unbekannte Zeitzone. Nutze IANA wie `Europe/Berlin`.",
        "reminder_fire": "🔔 *Erinnerung:* {title}",
        "done_ok": "✅ Als erledigt markiert.",
        "snoozed_ok": "⏰ Verschoben bis *{when}*.",
        "err_stt": "😕 Audio nicht verstanden. Versuch es erneut oder als Text.",
        "err_llm": "😕 Gerade gibt's ein Problem. Bitte gleich noch mal.",
        "err_generic": "😕 Etwas ist schiefgelaufen. Bitte erneut versuchen.",
        "expired": "Diese Erinnerung ist nicht mehr verfügbar.",
    },
    "uk": {
        "btn_webapp": "📅 Мої нагадування",
        "btn_save": "✅ Зберегти",
        "btn_edit": "✏️ Змінити",
        "btn_cancel": "❌ Скасувати",
        "btn_done": "✅ Готово",
        "btn_snooze": "⏰ Відкласти на годину",
        "start_greeting": (
            "👋 Привіт, {name}!\n\n"
            "Я бот-нагадувач. Просто надішли голосове або текст — скажи, *про що* "
            "нагадати й *коли*. Наприклад:\n"
            "• «нагадай завтра о 18:00 купити молоко»\n"
            "• «зателефонувати мамі за 2 години»\n\n"
            "Розумію багато мов і відповідаю твоєю."
        ),
        "start_tz_hint": (
            "🌍 Твій часовий пояс — *{tz}*. Якщо він неправильний, задай його "
            "командою /timezone, щоб нагадування приходили вчасно."
        ),
        "help": (
            "🤖 *Як мною користуватися*\n\n"
            "Надішли голосове або текст із нагадуванням — що і коли.\n\n"
            "*Команди*\n"
            "/list — найближчі нагадування\n"
            "/timezone — встановити часовий пояс\n"
            "/help — ця довідка\n\n"
            "Відкрий 📅 *Мої нагадування* для календаря."
        ),
        "list_empty": "Найближчих нагадувань немає. 🎉",
        "list_header": "🗓 *Твої найближчі нагадування:*",
        "list_item": "• *{title}* — {when}",
        "recognized": "🎙 Розпізнав: _{text}_",
        "confirm": "📝 Нагадати: *{title}*\n🕒 Коли: *{when}*",
        "saved_ok": "✅ Зберіг! Нагадаю *{when}*.",
        "cancelled": "❌ Скасовано.",
        "edit_prompt": "✏️ Гаразд, надішли нагадування ще раз (що і коли).",
        "needs_time": "🤔 Не зрозумів час. {message}",
        "needs_time_generic": (
            "🤔 Коли нагадати? Наприклад: «завтра о 18:00» або «за 2 години»."
        ),
        "tz_current": "🌍 Твій часовий пояс: *{tz}*.",
        "tz_usage": (
            "Надішли часовий пояс у форматі IANA, напр. `/timezone Europe/Kyiv`."
        ),
        "tz_set_ok": "✅ Часовий пояс встановлено: *{tz}*.",
        "tz_invalid": "⚠️ Невідомий пояс. Використай IANA-ім'я, напр. `Europe/Kyiv`.",
        "reminder_fire": "🔔 *Нагадування:* {title}",
        "done_ok": "✅ Позначив виконаним.",
        "snoozed_ok": "⏰ Відклав до *{when}*.",
        "err_stt": "😕 Не розібрав аудіо. Спробуй ще раз або надішли текстом.",
        "err_llm": "😕 Зараз не виходить. Спробуй за хвилину.",
        "err_generic": "😕 Щось пішло не так. Спробуй ще раз.",
        "expired": "Це нагадування більше недоступне.",
    },
    "es": {
        "btn_webapp": "📅 Mis recordatorios",
        "btn_save": "✅ Guardar",
        "btn_edit": "✏️ Editar",
        "btn_cancel": "❌ Cancelar",
        "btn_done": "✅ Hecho",
        "btn_snooze": "⏰ Posponer 1h",
        "start_greeting": (
            "👋 ¡Hola, {name}!\n\n"
            "Soy tu bot de recordatorios. Envíame un mensaje de voz o texto — dime "
            "*qué* recordarte y *cuándo*. Por ejemplo:\n"
            "• «recuérdame mañana a las 6 de la tarde comprar leche»\n"
            "• «llamar a mamá en 2 horas»\n\n"
            "Entiendo muchos idiomas y respondo en el tuyo."
        ),
        "start_tz_hint": (
            "🌍 Tu zona horaria es *{tz}*. Si no es correcta, configúrala con "
            "/timezone para que los recordatorios lleguen a tiempo."
        ),
        "help": (
            "🤖 *Cómo usarme*\n\n"
            "Envía un mensaje de voz o texto con el recordatorio — qué y cuándo.\n\n"
            "*Comandos*\n"
            "/list — próximos recordatorios\n"
            "/timezone — configurar zona horaria\n"
            "/help — esta ayuda\n\n"
            "Abre 📅 *Mis recordatorios* para ver el calendario."
        ),
        "list_empty": "No tienes recordatorios próximos. 🎉",
        "list_header": "🗓 *Tus próximos recordatorios:*",
        "list_item": "• *{title}* — {when}",
        "recognized": "🎙 Escuché: _{text}_",
        "confirm": "📝 Recordarte: *{title}*\n🕒 Cuándo: *{when}*",
        "saved_ok": "✅ ¡Guardado! Te recordaré el *{when}*.",
        "cancelled": "❌ Cancelado.",
        "edit_prompt": "✏️ Vale, envía el recordatorio de nuevo (qué y cuándo).",
        "needs_time": "🤔 No entendí la hora. {message}",
        "needs_time_generic": (
            "🤔 ¿Cuándo te recuerdo? Prueba «mañana a las 18:00» o «en 2 horas»."
        ),
        "tz_current": "🌍 Tu zona horaria: *{tz}*.",
        "tz_usage": (
            "Envía tu zona horaria como nombre IANA, p. ej. "
            "`/timezone Europe/Madrid`."
        ),
        "tz_set_ok": "✅ Zona horaria configurada: *{tz}*.",
        "tz_invalid": "⚠️ Zona desconocida. Usa un nombre IANA como `Europe/Madrid`.",
        "reminder_fire": "🔔 *Recordatorio:* {title}",
        "done_ok": "✅ Marcado como hecho.",
        "snoozed_ok": "⏰ Pospuesto hasta *{when}*.",
        "err_stt": "😕 No entendí el audio. Inténtalo de nuevo o envía texto.",
        "err_llm": "😕 Tengo problemas ahora mismo. Inténtalo en un momento.",
        "err_generic": "😕 Algo salió mal. Inténtalo de nuevo.",
        "expired": "Este recordatorio ya no está disponible.",
    },
}
