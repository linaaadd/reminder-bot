import { useEffect, useState } from "react";
import type { Strings } from "../i18n";
import type { Reminder } from "../types";
import { CheckIcon, CloseIcon, TrashIcon } from "./icons";

/** Format a Date as the value expected by <input type="datetime-local">. */
function toLocalInput(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}`
  );
}

export function ReminderModal({
  reminder,
  initialDate,
  t,
  onSave,
  onDelete,
  onMarkDone,
  onClose,
}: {
  reminder: Reminder | null; // null = create mode
  initialDate: Date;
  t: Strings;
  onSave: (title: string, when: Date) => void;
  onDelete: (id: number) => void;
  onMarkDone: (id: number) => void;
  onClose: () => void;
}) {
  const [title, setTitle] = useState("");
  const [when, setWhen] = useState(toLocalInput(initialDate));

  useEffect(() => {
    if (reminder) {
      setTitle(reminder.title);
      setWhen(toLocalInput(new Date(reminder.remind_at)));
    } else {
      setTitle("");
      setWhen(toLocalInput(initialDate));
    }
  }, [reminder, initialDate]);

  const isEdit = reminder !== null;

  const submit = () => {
    const trimmed = title.trim();
    if (!trimmed || !when) return;
    onSave(trimmed, new Date(when));
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-grabber" />

        <header className="modal-head">
          <h2>{isEdit ? t.editReminder : t.newReminder}</h2>
          <button
            className="icon-btn"
            onClick={onClose}
            aria-label={t.cancel}
          >
            <CloseIcon />
          </button>
        </header>

        <label className="field">
          <span>{t.titleLabel}</span>
          <input
            type="text"
            value={title}
            placeholder={t.titlePlaceholder}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </label>

        <label className="field">
          <span>{t.whenLabel}</span>
          <input
            type="datetime-local"
            value={when}
            onChange={(e) => setWhen(e.target.value)}
          />
        </label>

        <div className="modal-actions">
          <button className="btn primary" onClick={submit}>
            <CheckIcon size={18} />
            {t.save}
          </button>
          {isEdit && reminder.status === "pending" && (
            <button className="btn" onClick={() => onMarkDone(reminder.id)}>
              {t.markDone}
            </button>
          )}
          {isEdit && (
            <button
              className="btn danger"
              onClick={() => onDelete(reminder.id)}
              aria-label={t.delete}
            >
              <TrashIcon size={18} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
