"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";
import { MAX_MESSAGE_LENGTH } from "@/lib/limits";
import type { Offer } from "@/lib/offers";
import { eraseMyData, setRelances, signOut } from "./actions";
import { OfferCard } from "./offer-card";

type Message = {
  id: number;
  role: "user" | "assistant";
  author: "user" | "ai" | "team";
  kind: "text" | "offer" | "relance";
  offer_id: number | null;
  content: string;
  created_at: string;
};

/** Les réponses de l'équipe arrivent toutes les quelques secondes. */
const POLL_MS = 5000;

const byId = (offers: Offer[]) => Object.fromEntries(offers.map((o) => [o.id, o])) as Record<number, Offer>;

/** Ajoute des messages sans doublon, dans l'ordre. */
function merge(current: Message[], incoming: Message[]): Message[] {
  const known = new Set(current.map((m) => m.id));
  const fresh = incoming.filter((m) => !known.has(m.id));
  return fresh.length ? [...current, ...fresh].sort((a, b) => (a.id < 0 ? 1 : b.id < 0 ? -1 : a.id - b.id)) : current;
}

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

export function Chat({
  creatorId,
  others = false,
  initialMessages,
  initialOffers,
  name,
  isAdmin = false,
  relances = null,
}: {
  /** La créatrice de cette conversation. */
  creatorId: number;
  /** D'autres créatrices sont en ligne : lien vers le choix. */
  others?: boolean;
  initialMessages: Message[];
  initialOffers: Offer[];
  name: string;
  isAdmin?: boolean;
  /** null : l'équipe n'a pas activé la prise de nouvelles. */
  relances?: { ok: boolean } | null;
}) {
  const [messages, setMessages] = useState(initialMessages);
  const [offers, setOffers] = useState(() => byId(initialOffers));
  const [notice, setNotice] = useState<string | null>(null);
  const sending = useRef(false);
  const [draft, setDraft] = useState("");
  const [waiting, setWaiting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const [confirming, setConfirming] = useState(false);
  const [relancesOk, setRelancesOk] = useState(relances?.ok ?? true);
  const [erasing, startErasing] = useTransition();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const firstScroll = useRef(true);
  const router = useRouter();

  // Le dernier message connu, lu par le rafraîchissement régulier.
  const messagesRef = useRef(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  // Une réponse qui arrive d'ailleurs (réaction à une contre-offre) : « … écrit »
  // le temps qu'il lui reste à taper, puis le message. La relecture régulière
  // attend, pour ne pas l'afficher avant.
  async function showTyped(incoming: Message[], typingMs: number) {
    sending.current = true;
    setWaiting(true);
    if (typingMs > 0) await new Promise((r) => setTimeout(r, typingMs));
    setMessages((m) => merge(m, incoming));
    setWaiting(false);
    sending.current = false;
  }

  // Les nouveaux messages (réponses de l'équipe, offres) et l'état des offres.
  const poll = useCallback(async () => {
    if (sending.current || document.visibilityState !== "visible") return;
    const lastId = Math.max(0, ...messagesRef.current.map((m) => m.id));
    try {
      const res = await fetch(`/api/chat?apres=${lastId}&c=${creatorId}`, { cache: "no-store" });
      if (!res.ok) return;
      const data = (await res.json()) as { messages: Message[]; offers: Offer[] };
      if (sending.current) return;
      setMessages((m) => merge(m, data.messages));
      setOffers(byId(data.offers));
      if (data.messages.some((m) => m.role === "assistant")) setNotice(null);
    } catch {
      // Réseau coupé : on réessaiera au prochain tour.
    }
  }, [creatorId]);

  useEffect(() => {
    const timer = window.setInterval(() => void poll(), POLL_MS);
    return () => window.clearInterval(timer);
  }, [poll]);

  // Le menu se referme dès qu'on touche ailleurs, ou avec Échap. (Un voile
  // en plein écran ne suffit pas : le flou de l'en-tête le confine à l'en-tête.)
  useEffect(() => {
    if (!menuOpen) return;
    const outside = (e: PointerEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) setMenuOpen(false);
    };
    const escape = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    document.addEventListener("pointerdown", outside);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("keydown", escape);
    };
  }, [menuOpen]);

  // Toujours voir le dernier message, et l'indicateur « … écrit ».
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
    setNotice(null);
    const pending: Message = {
      id: -Date.now(),
      role: "user",
      author: "user",
      kind: "text",
      offer_id: null,
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((m) => [...m, pending]);
    setDraft("");
    setWaiting(true);
    sending.current = true;
    const sentAt = Date.now();
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        // L'heure de son téléphone : l'IA vit au même rythme que la personne.
        body: JSON.stringify({ content, creator: creatorId, tz: Intl.DateTimeFormat().resolvedOptions().timeZone }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.status === 401) {
        router.replace("/connexion");
        return;
      }
      if (res.status === 403) {
        router.replace("/bienvenue");
        return;
      }
      if (res.status === 410) {
        // Plus en ligne : retour au choix des créatrices.
        router.replace("/");
        return;
      }
      // Sans message du serveur (coupé en route, délai dépassé) : au moins le code, pour savoir où chercher.
      if (!res.ok) throw new Error(data.error ?? `Pas de réponse cette fois-ci (erreur ${res.status}). Réessayez dans un instant.`);
      const incoming = data.messages as Message[];
      setMessages((m) => merge(m.filter((x) => x.id !== pending.id), incoming.filter((x) => x.role === "user")));
      // Comme une personne qui tape sa réponse : « … écrit » le temps qu'il faut, puis la réponse.
      const replies = incoming.filter((x) => x.role !== "user");
      const typing = Math.max(0, Number(data.typingMs ?? 0) - (Date.now() - sentAt));
      if (replies.length && typing > 0) await new Promise((r) => setTimeout(r, typing));
      setMessages((m) => merge(m, replies));
      if (data.offers?.length) setOffers((o) => ({ ...o, ...byId(data.offers as Offer[]) }));
      if (data.waiting) setNotice(data.notice ?? "Message envoyé. La réponse arrivera ici dès que possible.");
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
      sending.current = false;
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
        {others && (
          <Link
            href="/"
            aria-label="Toutes les créatrices"
            className="-ml-2 flex size-9 shrink-0 items-center justify-center rounded-full text-2xl text-muted hover:bg-accent-soft"
          >
            ‹
          </Link>
        )}
        <div
          aria-hidden
          className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent-soft font-serif text-xl text-accent"
        >
          {name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 leading-tight">
          <h1 className="font-serif text-xl">{name}</h1>
          <p className="text-xs text-muted">Intelligence artificielle · prototype</p>
        </div>
        <div ref={menuRef} className="relative">
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
              <div className="absolute right-0 top-12 z-20 w-64 overflow-hidden rounded-2xl border border-line bg-surface shadow-lg">
                {isAdmin && (
                  <Link href="/admin" className="block border-b border-line px-4 py-3 hover:bg-accent-soft">
                    Tableau de bord
                  </Link>
                )}
                {relances && (
                  <button
                    type="button"
                    role="switch"
                    aria-checked={relancesOk}
                    onClick={async () => {
                      const next = !relancesOk;
                      setRelancesOk(next);
                      const result = await setRelances(next);
                      if (result?.error) {
                        setRelancesOk(!next);
                        setNotice(result.error);
                      }
                    }}
                    className="flex w-full items-center justify-between gap-3 border-b border-line px-4 py-3 text-left hover:bg-accent-soft"
                  >
                    <span>
                      Recevoir des nouvelles de {name}
                      <span className="block text-xs text-muted">Un petit message si je ne viens pas pendant un moment</span>
                    </span>
                    <span
                      aria-hidden
                      className={`flex h-6 w-10 shrink-0 items-center rounded-full p-0.5 transition ${relancesOk ? "justify-end bg-accent" : "justify-start bg-line"}`}
                    >
                      <span className="size-5 rounded-full bg-white shadow" />
                    </span>
                  </button>
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
        {/* Pas de message d'accueil : c'est la personne qui commence. */}
        {rows.length === 0 && !waiting && (
          <p className="m-auto max-w-xs text-center text-muted">
            Dis bonjour à {name} 👋
            <span className="mt-1 block text-sm">C&apos;est toi qui commences.</span>
          </p>
        )}
        {rows.map(({ m, day }) => {
          const mine = m.role === "user";
          return (
            <div key={m.id} className="flex flex-col">
              {day && (
                <p suppressHydrationWarning className="my-3 text-center text-xs font-semibold text-muted first-letter:uppercase">
                  {day}
                </p>
              )}
              <div
                className={`max-w-[85%] break-words rounded-3xl px-4 py-2.5 leading-normal ${
                  mine
                    ? "self-end rounded-br-md bg-accent-soft"
                    : "self-start rounded-bl-md border border-line bg-surface"
                } ${m.id < 0 ? "opacity-70" : ""}`}
              >
                <p className="whitespace-pre-wrap">{m.content}</p>
                {m.kind === "offer" && m.offer_id !== null && offers[m.offer_id] && (
                  <OfferCard
                    offer={offers[m.offer_id]}
                    onChange={(o) => setOffers((current) => ({ ...current, [o.id]: o }))}
                    onReply={(incoming, typingMs) => void showTyped(incoming as Message[], typingMs)}
                  />
                )}
              </div>
              {/* Toujours dire qui répond : l'IA, ou quelqu'un de l'équipe. */}
              {!mine && (
                <p className="mt-1 ml-3 text-[11px] font-semibold text-muted">
                  {m.author === "team" ? "Équipe" : `${name} · IA`}
                </p>
              )}
            </div>
          );
        })}

        {waiting && (
          <div role="status" aria-label="Réponse en cours" className="flex flex-col items-start gap-1 self-start">
            <div className="flex gap-1.5 rounded-3xl rounded-bl-md border border-line bg-surface px-4 py-4">
              {[0, 150, 300].map((delay) => (
                <span
                  key={delay}
                  className="size-2 animate-bounce rounded-full bg-muted"
                  style={{ animationDelay: `${delay}ms` }}
                />
              ))}
            </div>
            <span className="px-4 text-xs text-muted">{name} écrit…</span>
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
        {notice && (
          <p role="status" className="mb-2 px-2 text-sm text-muted">
            {notice}
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
            placeholder={`Écrire à ${name}…`}
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
              Vos messages, ce que {name} sait de vous et le résumé de vos conversations seront supprimés
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
