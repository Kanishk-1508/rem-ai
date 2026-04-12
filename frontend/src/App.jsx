import { useEffect, useMemo, useState } from "react";
import FileUpload from "./FileUpload";
import Chat from "./Chat";
import "./App.css";

const THEME_KEY = "remai_theme";

const THEMES = [
  { id: "aqua-orange", label: "Aqua Orange" },
  { id: "forest-cream", label: "Forest Cream" },
  { id: "midnight-copper", label: "Midnight Copper" },
];

function App() {
  const [theme, setTheme] = useState(() => {
    const cachedTheme = localStorage.getItem(THEME_KEY);
    return cachedTheme || "aqua-orange";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const activeThemeLabel = useMemo(() => {
    const current = THEMES.find((item) => item.id === theme);
    return current ? current.label : "Aqua Orange";
  }, [theme]);

  return (
    <div className="app">
      <header className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">Document intelligence</p>
          <h1 className="title">rem.ai</h1>
          <p className="subtitle">
            Upload PDFs or text files, then ask questions grounded in your own documents.
          </p>

          <div className="theme-switcher" role="group" aria-label="Theme selector">
            <span className="theme-label">Theme: {activeThemeLabel}</span>
            <div className="theme-options">
              {THEMES.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`theme-pill ${theme === item.id ? "active" : ""}`}
                  onClick={() => setTheme(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="hero-metrics">
          <div className="metric-card coral">
            <span className="metric-value">PDF</span>
            <span className="metric-label">and TXT support</span>
          </div>
          <div className="metric-card blue">
            <span className="metric-value">FAISS</span>
            <span className="metric-label">fast document search</span>
          </div>
          <div className="metric-card gold">
            <span className="metric-value">LLM</span>
            <span className="metric-label">context-aware answers</span>
          </div>
        </div>
      </header>

      <main className="content-grid">
        <section className="panel panel-upload">
          <FileUpload />
        </section>

        <section className="panel panel-chat">
          <Chat />
        </section>
      </main>
    </div>
  );
}

export default App;
