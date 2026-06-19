/**
 * Thin wrapper around the Telegram WebApp SDK.
 *
 * Exposes initData (for backend auth), the user's language_code, and applies
 * Telegram's theme (light/dark via themeParams) to CSS variables.
 */

interface TelegramThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
}

interface TelegramWebApp {
  initData: string;
  initDataUnsafe: { user?: { language_code?: string } };
  colorScheme: "light" | "dark";
  themeParams: TelegramThemeParams;
  ready: () => void;
  expand: () => void;
}

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}

export const tg = window.Telegram?.WebApp;

/**
 * Raw initData string sent to the backend in the X-Telegram-Init-Data header.
 *
 * Read LAZILY (not as a module-load constant): the Telegram SDK may not have
 * populated initData at the moment this module is first imported, which would
 * cache an empty string and cause every API call to 401. Reading it per request
 * guarantees we get the real value once the WebApp is initialized.
 */
export function getInitData(): string {
  return window.Telegram?.WebApp?.initData ?? "";
}

/** Telegram-reported UI language (e.g. "de", "ru"); undefined outside Telegram. */
export const tgLanguage = tg?.initDataUnsafe?.user?.language_code;

/** Map Telegram themeParams onto CSS variables and call ready()/expand(). */
export function applyTelegramTheme(): void {
  if (!tg) return;
  tg.ready();
  tg.expand();

  const p = tg.themeParams;
  const root = document.documentElement.style;
  const set = (name: string, value?: string) => value && root.setProperty(name, value);

  set("--tg-bg", p.bg_color);
  set("--tg-text", p.text_color);
  set("--tg-hint", p.hint_color);
  set("--tg-link", p.link_color);
  set("--tg-button", p.button_color);
  set("--tg-button-text", p.button_text_color);
  set("--tg-secondary-bg", p.secondary_bg_color);

  document.documentElement.dataset.theme = tg.colorScheme;
}
