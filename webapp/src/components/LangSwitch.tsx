import { SUPPORTED_LANGS, type Lang } from "../i18n";

const LABELS: Record<Lang, string> = {
  en: "EN",
  ru: "RU",
  de: "DE",
  uk: "UK",
  es: "ES",
};

export function LangSwitch({
  lang,
  onChange,
}: {
  lang: Lang;
  onChange: (lang: Lang) => void;
}) {
  return (
    <select
      className="lang-switch"
      value={lang}
      onChange={(e) => onChange(e.target.value as Lang)}
      aria-label="Language"
    >
      {SUPPORTED_LANGS.map((l) => (
        <option key={l} value={l}>
          {LABELS[l]}
        </option>
      ))}
    </select>
  );
}
