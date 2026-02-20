import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "light" | "dark";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "light",
      setTheme: (theme) => {
        set({ theme });
        applyTheme(theme);
      },
      toggleTheme: () => {
        set((s) => {
          const next = s.theme === "dark" ? "light" : "dark";
          applyTheme(next);
          return { theme: next };
        });
      },
    }),
    { name: "theme-storage" }
  )
);

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
}

// Run once on load to sync class with stored theme (avoids flash)
if (typeof document !== "undefined") {
  const stored = localStorage.getItem("theme-storage");
  if (stored) {
    try {
      const { state } = JSON.parse(stored);
      if (state?.theme === "dark") document.documentElement.classList.add("dark");
      else document.documentElement.classList.remove("dark");
    } catch {
      // ignore
    }
  }
}
