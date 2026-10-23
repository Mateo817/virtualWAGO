import { useEffect, useState } from "react";
type Theme = "light" | "dark" | "system";
const storageKey = "virtualwago.theme";
function preference(): Theme {
  try {
    const value = localStorage.getItem(storageKey);
    if (value === "light" || value === "dark") return value;
  } catch {
    /* Storage may be disabled. */
  }
  return "system";
}
function resolve(theme: Theme) {
  return theme === "system"
    ? matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light"
    : theme;
}
document.documentElement.dataset.theme = resolve(preference());
export function ThemeControl() {
  const [theme, setTheme] = useState<Theme>(preference);
  useEffect(() => {
    const media = matchMedia("(prefers-color-scheme: dark)");
    const update = () => {
      document.documentElement.dataset.theme = resolve(theme);
    };
    update();
    media.addEventListener("change", update);
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      /* Keep session preference. */
    }
    return () => media.removeEventListener("change", update);
  }, [theme]);
  return (
    <label className="theme-control">
      <span>Farbschema</span>
      <select
        aria-label="Farbschema"
        value={theme}
        onChange={(e) => setTheme(e.target.value as Theme)}
      >
        <option value="system">System</option>
        <option value="light">Hell</option>
        <option value="dark">Dunkel</option>
      </select>
    </label>
  );
}
