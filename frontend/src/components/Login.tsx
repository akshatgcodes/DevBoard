import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api";

type Props = { error: string | null; onLoggedIn: () => void };

export default function Login({ error, onLoggedIn }: Props) {
  const [config, setConfig] = useState<{ github: boolean; dev_login: boolean } | null>(null);
  const [username, setUsername] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    api.authConfig().then(setConfig).catch(() => setConfig(null));
  }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.devLogin(username.trim());
      onLoggedIn();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <main className="login">
      <div className="login-card">
        <h1 className="logo">
          <span className="logo-mark" aria-hidden /> DevBoard
        </h1>
        <p className="muted">
          Your commits, LeetCode solves and daily goals in one place, plus a warning before a
          streak breaks.
        </p>

        {error && <p className="error">{error}</p>}

        {config?.github && (
          <a className="btn btn-primary btn-block" href={api.githubLoginUrl}>
            Continue with GitHub
          </a>
        )}

        {config?.dev_login && (
          <form onSubmit={submit} className="dev-login">
            <label htmlFor="gh-user" className="label">
              Dev login: any public GitHub username
            </label>
            <div className="row">
              <input
                id="gh-user"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="octocat"
                required
              />
              <button className="btn" type="submit">
                Open
              </button>
            </div>
            {formError && <p className="error">{formError}</p>}
          </form>
        )}

        {config && !config.github && !config.dev_login && (
          <p className="error">
            No login method configured. Set GITHUB_CLIENT_ID or DEV_LOGIN=true in backend/.env.
          </p>
        )}
      </div>
    </main>
  );
}
