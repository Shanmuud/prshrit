"use client";

// Demo only: flips the `dark` class so both themes can be checked.
export function ThemeToggle() {
  return (
    <button
      type="button"
      onClick={() => document.documentElement.classList.toggle("dark")}
      className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground hover:bg-muted"
    >
      Theme
    </button>
  );
}
