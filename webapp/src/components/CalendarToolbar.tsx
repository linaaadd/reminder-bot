import type { ToolbarProps, View } from "react-big-calendar";
import type { Strings } from "../i18n";
import { ChevronLeft, ChevronRight } from "./icons";

/** Custom react-big-calendar toolbar: nav arrows + label + segmented views. */
export function CalendarToolbar({
  label,
  onNavigate,
  onView,
  view,
  views,
  t,
}: ToolbarProps<any, object> & { t: Strings }) {
  const viewList = (Array.isArray(views) ? views : ["month"]) as View[];
  const viewLabel: Record<string, string> = {
    month: t.month,
    week: t.week,
    day: t.day,
    agenda: t.agenda,
  };

  return (
    <div className="cal-toolbar">
      <div className="cal-nav">
        <button
          className="icon-btn"
          onClick={() => onNavigate("PREV")}
          aria-label={t.previous}
        >
          <ChevronLeft />
        </button>
        <button className="today-btn" onClick={() => onNavigate("TODAY")}>
          {t.today}
        </button>
        <button
          className="icon-btn"
          onClick={() => onNavigate("NEXT")}
          aria-label={t.next}
        >
          <ChevronRight />
        </button>
        <span className="cal-label">{label}</span>
      </div>

      <div className="seg" role="tablist" aria-label="View">
        {viewList.map((v) => (
          <button
            key={v}
            role="tab"
            aria-selected={view === v}
            className={`seg-item${view === v ? " active" : ""}`}
            onClick={() => onView(v)}
          >
            {viewLabel[v] ?? v}
          </button>
        ))}
      </div>
    </div>
  );
}
