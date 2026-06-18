import React from "react";
import ReactDOM from "react-dom/client";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "./styles.css";
import App from "./App";
import { applyTelegramTheme } from "./telegram";

// Apply Telegram light/dark theme before first paint.
applyTelegramTheme();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
