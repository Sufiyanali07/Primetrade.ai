import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  email: string | null;
  role: string | null;
  setAuth: (token: string, email?: string, role?: string) => void;
  logout: () => void;
  isAdmin: () => boolean;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      email: null,
      role: null,
      setAuth: (token, email, role) => {
        if (token) localStorage.setItem("token", token);
        set({ token, email: email ?? null, role: role ?? null });
      },
      logout: () => {
        localStorage.removeItem("token");
        set({ token: null, email: null, role: null });
      },
      isAdmin: () => get().role === "admin",
      isAuthenticated: () => !!get().token,
    }),
    { name: "auth-storage" }
  )
);
