import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { fetchMockDashboard } from "./mock-adapter";
import { fetchDashboardFromApi } from "./rest-adapter";
import type { DashboardState } from "./dashboard-types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const POLL_INTERVAL_MS = 2500;

type AdapterMode = "mock" | "api";

type DashboardContextValue = {
  state: DashboardState | null;
  error: string | null;
  mode: AdapterMode;
  lastUpdated: string | null;
  refresh: () => void;
};

const DashboardContext = createContext<DashboardContextValue | null>(null);

/**
 * Provider that owns the dashboard state and the polling loop.
 *
 * - If VITE_API_BASE_URL is set, the REST adapter is used.
 * - Otherwise, the mock adapter keeps the UI working offline.
 * - Polls every ~2.5 seconds and keeps the last valid state
 *   if a poll fails.
 */
export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DashboardState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const loadState = useCallback(async () => {
    try {
      const nextState = API_BASE_URL
        ? await fetchDashboardFromApi(API_BASE_URL)
        : await fetchMockDashboard();

      setState(nextState);
      setError(null);
      setLastUpdated(nextState.updatedAt);
    } catch (err) {
      // Keep the last valid state. Only surface the failure.
      setError(err instanceof Error ? err.message : "Failed to load dashboard state");
    }
  }, []);

  useEffect(() => {
    void loadState();
    const intervalId = window.setInterval(loadState, POLL_INTERVAL_MS);
    return () => window.clearInterval(intervalId);
  }, [loadState]);

  return (
    <DashboardContext.Provider
      value={{ state, error, mode: API_BASE_URL ? "api" : "mock", lastUpdated, refresh: loadState }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboardState() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardState must be used within DashboardProvider");
  }
  return context;
}