"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, useTransition } from "react";
import { MAX_MESSAGE_LENGTH } from "@/lib/limits";
import { eraseMyData, signOut } from "./actions";

type Message = { id: number; role: "user" | "assistant"; content: string; created_at: string };

const dayFormat = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  weekday: "long",
  day: "numeric",
  month: "long",
});
const dayKey = new Intl.DateTimeFormat("fr-CA", { timeZone: "Europe/Paris" }); // AAAA-MM-JJ

function dayLabel(iso: string): string {
  const key = dayKey.format(new Date(iso));
  const today = new Date();
  if (key === dayKey.format(today)) return "Aujourd'hui";
  if (key === dayKey.format(new Date(today.getTime() - 86_400_000))) return "Hier";
  return dayFormat.format(new Date(iso));
}

export function Chat({ initialMessages, isAdmin = false }: { initialMessages: Message[]; isAdmin?: boolean }) {
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [erasing, startErasing] = useTransition();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const firstScroll = useRef(true);
  const router = useRouter();

  // Toujours voir le dernier message, et l'indicateur « Élise écrit ».
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end", behavior: firstScroll.current ? "instant" : "smooth" });
    firstScroll.current = false;
  }, [messages.length, waiting]);

  // La zone de saisie grandit avec le texte, jusqu'à une limite.
  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [draft]);

  async function send() {
    const content = draft.trim();
    if (!content || waiting) return;
    setError(null);
    const pending: Message = { id: -Date.now(), role: "user", content, created_at: new Date().toISOString() };
    setMessages((m) => [...m, pending]);
    setDraft("");
    setWaiting(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ content }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.status === 401) {
        router.replace("/connexion");
        return;
      }
      if (!res.ok) throw new Error(data.error ?? "Élise n'a pas pu répondre. Réessayez dans un instant.");
      setMessages((m) => [...m.filter((x) => x.id !== pending.id), ...(data.messages as Message[])]);
    } catch (err) {
      // Rien n'a été enregistré : le message revient dans la zone de saisie.
      setMessages((m) => m.filter((x) => x.id !== pending.id));
      setDraft((current) => current || content);
      setError(
        err instanceof TypeError
          ? "La connexion a été perdue. Vérifiez votre réseau et réessayez."
          : (err as Error).message,
      );
    } finally {
      setWaiting(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Sur ordinateur, Entrée envoie et Maj+Entrée va à la ligne. Sur
    // téléphone, Entrée va à la ligne : on envoie avec le bouton.
    const touch = window.matchMedia("(pointer: coarse)").matches;
    if (e.key === "Enter" && !e.shiftKey && !touch && !e.nativeEvent.isComposing) {
      e.preventDefault();
      void send();
    }
  }

  function erase() {
    startErasing(async () => {
      const result = await eraseMyData();
      if (result?.error) setError(result.error);
      setConfirming(false);
    });
  }

  // Un intitulé de jour (« Aujourd'hui », « Hier »…) au premier message de chaque journée.
  const rows = messages.map((m, i) => {
    const day = dayLabel(m.created_at);
    return { m, day: i === 0 || day !== dayLabel(messages[i - 1].created_at) ? day : null };
  });

  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col">
      <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-line bg-background/90 px-4 py-3 backdrop-blur pt-[max(0.75rem,env(safe-area-inset-top))]">
        <div
          aria-hidden
          className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent-soft font-serif text-xl text-accent"
        >
          É
        </div>
        <div className="flex-1 leading-tight">
          <h1 className="font-serif text-xl">Élise</h1>
          <p className="text-xs text-muted">Intelligence artificielle · prototype</p>
        </div>
        <div className="relative">
          <button
            type="button"
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Menu"
            aria-expanded={menuOpen}
            className="flex size-10 items-center justify-center rounded-full text-muted hover:bg-accent-soft"
          >
            <svg viewBox="0 0 24 24" className="size-6" fill="currentColor" aria-hidden>
              <circle cx="5" cy="12" r="2" />
              <circle cx="12" cy="12" r="2" />
              <circle cx="19" cy="12" r="2" />
            </svg>
          </button>
          {menuOpen && (
            <>
              <div className="fixed inset-0" onClick={() => setMenuOpen(false)} aria-hidden />
              <div className="absolute right-0 top-12 z-20 w-64 overflow-hidden rounded-2xl border border-line bg-surface shadow-lg">
                {isAdmin && (
                  <Link href="/admin" className="block border-b border-line px-4 py-3 hover:bg-accent-soft">
                    Tableau de bord
                  </Link>
                )}
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false);
                    setConfirming(true);
                  }}
                  className="block w-full px-4 py-3 text-left hover:bg-accent-soft"
                >
                  Effacer toutes mes données
                </button>
                <form action={signOut} className="border-t border-line">
                  <button type="submit" className="block w-full px-4 py-3 text-left hover:bg-accent-soft">
                    Se déconnecter
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      </header>

      <main aria-live="polite" className="flex flex-1 flex-col gap-2 px-4 py-4">
        {rows.map(({ m, day }) => {
          const mine = m.role === "user";
          return (
            <div key={m.id} className="flex flex-col">
              {day && (
                <p suppressHydrationWarning className="my-3 text-center text-xs font-semibold text-muted first-letter:uppercase">
                  {day}
                </p>
              )}
              <p
                className={`max-w-[85%] whitespace-pre-wrap break-words rounded-3xl px-4 py-2.5 leading-normal ${
                  mine
                    ? "self-end rounded-br-md bg-accent-soft"
                    : "self-start rounded-bl-md border border-line bg-surface"
                } ${m.id < 0 ? "opacity-70" : ""}`}
              >
                {m.content}
              </p>
            </div>
          );
        })}

        {waiting && (
          <div
            role="status"
            aria-label="Élise écrit"
            className="flex gap-1.5 self-start rounded-3xl rounded-bl-md border border-line bg-surface px-4 py-4"
          >
            {[0, 150, 300].map((delay) => (
              <span
                key={delay}
                className="size-2 animate-bounce rounded-full bg-muted"
                style={{ animationDelay: `${delay}ms` }}
              />
            ))}
          </div>
        )}
        <div ref={endRef} />
      </main>

      <footer className="sticky bottom-0 border-t border-line bg-background px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
        {error && (
          <p role="alert" className="mb-2 rounded-2xl bg-accent-soft px-4 py-2 text-sm">
            {error}
          </p>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void send();
          }}
          className="flex items-end gap-2"
        >
          <textarea
            ref={inputRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            maxLength={MAX_MESSAGE_LENGTH}
            placeholder="Écrire à Élise…"
            aria-label="Votre message"
            className="max-h-40 flex-1 resize-none rounded-3xl border border-line bg-surface px-4 py-2.5 leading-normal outline-none focus:border-accent"
          />
          <button
            type="submit"
            disabled={!draft.trim() || waiting}
            aria-label="Envoyer"
            className="flex size-11 shrink-0 items-center justify-center rounded-full bg-accent text-white transition-opacity disabled:opacity-40"
          >
            <svg viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M12 19V5M5 12l7-7 7 7" />
            </svg>
          </button>
        </form>
        <p className="mt-2 text-center text-[11px] text-muted">Prototype de test : conversations fictives uniquement.</p>
      </footer>

      {confirming && (
        <div className="fixed inset-0 z-30 flex items-end justify-center bg-black/40 p-4 sm:items-center">
          <div role="dialog" aria-modal="true" aria-labelledby="effacer-titre" className="w-full max-w-sm rounded-3xl bg-surface p-6 shadow-xl">
            <h2 id="effacer-titre" className="font-serif text-2xl">
              Tout effacer ?
            </h2>
            <p className="mt-3 leading-relaxed text-muted">
              Vos messages, ce qu&apos;Élise sait de vous et le résumé de vos conversations seront supprimés
              définitivement. Votre compte, lui, reste ouvert.
            </p>
            <div className="mt-6 flex flex-col gap-2">
              <button
                type="button"
                onClick={erase}
                disabled={erasing}
                className="rounded-2xl bg-accent px-4 py-3 font-bold text-white disabled:opacity-60"
              >
                {erasing ? "Effacement…" : "Oui, tout effacer"}
              </button>
              <button
                type="button"
                onClick={() => setConfirming(false)}
                disabled={erasing}
                className="rounded-2xl px-4 py-3 font-semibold text-muted"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
