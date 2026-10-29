import { useEffect, useState } from "react";
import { api, ApiError } from "./api";
import type { Me } from "./types";
import Login from "./components/Login";
import DashboardPage from "./components/DashboardPage";

export default function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMe = async () => {
    try {
      setMe(await api.me());
      setError(null);
    } catch (e) {
      setMe(null);
      // 401 just means "show the login screen"; anything else is a real problem
      if (!(e instanceof ApiError && e.status === 401)) {
        setError("Can't reach the DevBoard API. Is the backend running on :8000?");
      }
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    loadMe();
  }, []);

  if (checking) return <div className="center muted">Loading…</div>;
  if (!me) return <Login error={error} onLoggedIn={loadMe} />;
  return (
    <DashboardPage
      me={me}
      onMeChange={setMe}
      onLogout={async () => {
        await api.logout();
        setMe(null);
      }}
    />
  );
}
