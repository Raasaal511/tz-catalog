"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void;
        expand: () => void;
        themeParams?: Record<string, string>;
        colorScheme?: "light" | "dark";
      };
    };
  }
}

/**
 * Initializes Telegram Mini App SDK when opened inside Telegram.
 * Safe no-op in a regular browser.
 */
export function TelegramProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const scriptId = "telegram-web-app-script";
    if (document.getElementById(scriptId)) {
      window.Telegram?.WebApp?.ready();
      window.Telegram?.WebApp?.expand();
      return;
    }

    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://telegram.org/js/telegram-web-app.js";
    script.async = true;
    script.onload = () => {
      window.Telegram?.WebApp?.ready();
      window.Telegram?.WebApp?.expand();
    };
    document.head.appendChild(script);
  }, []);

  return <>{children}</>;
}
