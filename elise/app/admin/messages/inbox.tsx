"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { formatEuros, timeAgo } from "@/lib/dashboard";
import type { Message } from "@/lib/memory";
import { contentLabel, mediaCounts, type Step } from "@/lib/offers";
import type { AiMode } from "@/lib/settings";
import type { InboxItem, TeamOffer, Thread } from "@/lib/team";
import { EmojiChoice } from "../emoji-picker";
import {
  draftOfferMessage,
  markRead,
  proposeNext,
  saveContact,
  sendTeamMessage,
  withdrawOffer,
  type ContactForm,
} from "./actions";

const REFRESH_MS = 4000;

const MODE_LABEL: Record<AiMode, string> = { auto: "Automatique", hybride: "Hybride", manuel: "Manuel" };
const STATUS_LABEL: Record<TeamOffer["status"], string> = {
  proposee: "En attente",
  achetee: "Acheté",
  offerte: "Offert",
  retiree: "Retirée",
};
/** « 3 photos et 1 vidéo », avec une majuscule. */
const label = (photos: number, videos: number) => {
  const text = contentLabel(photos, videos);
  return text.charAt(0).toUpperCase() + text.slice(1);
};

function zones(): string[] {
  try {
    return Intl.supportedValuesOf("timeZone");
  } catch {
    return ["Europe/Paris"];
  }
}

const euros = (cents: number) => (cents / 100).toFixed(2).replace(".", ",");

function contactForm(t: Thread): ContactForm {
  return {
    ai_enabled: t.contact.ai_enabled,
    city: t.contact.city,
    timezone: t.contact.timezone,
    emoji_mode: t.contact.emoji_mode,
    emojis: t.contact.emojis,
    notes: t.contact.notes,
    script_id: t.contact.script_id,
    spending_cap: t.contact.spending_cap_cents === null ? "" : euros(t.contact.spending_cap_cents),
  };
}

export function Inbox({
  initial,
  initialUser,
}: {
  initial: { mode: AiMode; conversations: InboxItem[] };
  initialUser: string | null;
}) {
  const [list, setList] = useState(initial.conversations);
  const [mode, setMode] = useState(initial.mode);
  const [selected, setSelected] = useState<string | null>(initialUser);
  const [thread, setThread] = useState<Thread | null>(null);
  const [showPanel, setShowPanel] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const [reply, setReply] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<ContactForm | null>(null);
  const [formNotice, setFormNotice] = useState<string | null>(null);
  const [offerPrice, setOfferPrice] = useState("");
  const [offerMessage, setOfferMessage] = useState("");
  const [offerNotice, setOfferNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const selectedRef = useRef(selected);
  const formFor = useRef<string | null>(null);
  const reloadForm = useRef(false);
  const endRef = useRef<HTMLDivElement>(null);
  const lastSeen = useRef(0);

  const loadList = useCallback(async () => {
    const res = await fetch("/api/admin/messages", { cache: "no-store" }).catch(() => null);
    if (!res?.ok) return;
    const data = (await res.json()) as { mode: AiMode; conversations: InboxItem[] };
    setList(data.conversations);
    setMode(data.mode);
  }, []);

  const loadThread = useCallback(async (userId: string) => {
    const res = await fetch(`/api/admin/messages/${userId}`, { cache: "no-store" }).catch(() => null);
    if (!res?.ok || selectedRef.current !== userId) return;
    const data = (await res.json()) as Thread;
    setThread(data);
    // La fiche n'est remplie qu'à l'ouverture (ou après un enregistrement) :
    // on n'écrase pas une saisie en cours.
    const switched = formFor.current !== userId;
    if (switched || reloadForm.current) {
      formFor.current = userId;
      reloadForm.current = false;
      setForm(contactForm(data));
      const next = data.person.prochaine_etape;
      setOfferPrice(next?.is_paid ? euros(next.price_cents) : "");
      setOfferMessage(next?.message_mode === "fixe" ? next.message_text : "");
      if (switched) {
        setOfferNotice(null);
        setFormNotice(null);
      }
    }
    const lastUserMessage = Math.max(0, ...data.messages.filter((m) => m.role === "user").map((m) => m.id));
    if (lastUserMessage > lastSeen.current) {
      lastSeen.current = lastUserMessage;
      void markRead(userId).then(loadList);
    }
  }, [loadList]);

  function open(userId: string) {
    selectedRef.current = userId;
    lastSeen.current = 0;
    setSelected(userId);
    setThread(null);
    setShowPanel(false);
    setError(null);
    window.history.replaceState(null, "", `/admin/messages?u=${userId}`);
    void loadThread(userId);
  }

  // Au premier affichage, et ensuite toutes les quelques secondes.
  useEffect(() => {
    if (initialUser) void loadThread(initialUser);
  }, [initialUser, loadThread]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      void loadList();
      if (selectedRef.current) void loadThread(selectedRef.current);
    }, REFRESH_MS);
    const tick = window.setInterval(() => setNow(Date.now()), 15_000);
    return () => {
      window.clearInterval(timer);
      window.clearInterval(tick);
    };
  }, [loadList, loadThread]);

  const messageCount = thread?.messages.length ?? 0;
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messageCount, selected]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!selected || !reply.trim()) return;
    setSending(true);
    setError(null);
    const result = await sendTeamMessage(selected, reply);
    setSending(false);
    if (!result.ok) return setError(result.error);
    setReply("");
    setThread((t) => (t ? { ...t, messages: [...t.messages, result.message] } : t));
    void loadList();
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!selected || !form) return;
    setBusy(true);
    const result = await saveContact(selected, form);
    setBusy(false);
    setFormNotice(result.ok ? "Fiche enregistrée." : result.error);
    if (result.ok) {
      reloadForm.current = true; // relire la fiche telle qu'enregistrée
      void loadThread(selected);
      void loadList();
    }
  }

  async function propose(step: Step) {
    if (!selected) return;
    setBusy(true);
    const result = await proposeNext(selected, step.id, offerPrice, offerMessage);
    setBusy(false);
    setOfferNotice(result.ok ? "Offre envoyée." : result.error);
    if (result.ok) {
      reloadForm.current = true;
      void loadThread(selected);
    }
  }

  async function draft(step: Step) {
    if (!selected) return;
    setBusy(true);
    setOfferNotice("L'IA écrit…");
    const result = await draftOfferMessage(selected, step.id, offerPrice);
    setBusy(false);
    if (result.ok) {
      setOfferMessage(result.text);
      setOfferNotice("Relisez le message avant de l'envoyer.");
    } else setOfferNotice(result.error);
  }

  async function withdraw(offer: TeamOffer) {
    if (!selected) return;
    setBusy(true);
    const result = await withdrawOffer(offer.id);
    setBusy(false);
    setOfferNotice(result.ok ? "Offre retirée : l'étape pourra être proposée à nouveau." : result.error);
    if (result.ok) {
      reloadForm.current = true;
      void loadThread(selected);
    }
  }

  const person = thread?.person;
  const next = person?.prochaine_etape ?? null;
  const pending = thread?.offers.find((o) => o.status === "proposee") ?? null;
  const offersById = Object.fromEntries((thread?.offers ?? []).map((o) => [o.id, o]));
  const aiLine =
    mode === "manuel"
      ? "Mode manuel : l'IA ne répond à personne, l'équipe répond à tout."
      : mode === "auto"
        ? "Mode automatique : l'IA répond à tout le monde. Cette case ne compte qu'en mode hybride."
        : "Mode hybride : l'IA ne répond qu'aux personnes cochées.";

  return (
    <div
      className="mx-auto grid w-full max-w-6xl grid-cols-1 lg:grid-cols-[20rem_1fr]"
      style={{ height: "calc(100dvh - 4rem - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px))" }}
    >
      {/* La liste des conversations */}
      <aside className={`min-h-0 flex-col border-r border-line ${selected ? "hidden lg:flex" : "flex"}`}>
        <div className="flex items-center justify-between gap-2 border-b border-line px-4 py-3">
          <h1 className="font-serif text-2xl">Messages</h1>
          <Link href="/admin/ia" className="rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold">
            Mode {MODE_LABEL[mode]}
          </Link>
        </div>
        <ul className="min-h-0 flex-1 overflow-y-auto">
          {list.length === 0 && <li className="p-4 text-sm text-muted">Personne n&apos;a encore écrit.</li>}
          {list.map((c) => {
            const aiOff = mode === "manuel" || (mode === "hybride" && !c.ia_autorisee);
            const prefix = c.dernier.auteur === "ai" ? "IA : " : c.dernier.auteur === "team" ? "Équipe : " : "";
            return (
              <li key={c.user_id}>
                <button
                  type="button"
                  onClick={() => open(c.user_id)}
                  className={`flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-accent-soft ${
                    selected === c.user_id ? "bg-accent-soft" : ""
                  }`}
                >
                  <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-accent font-serif text-lg text-white">
                    {c.nom.charAt(0).toUpperCase()}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-baseline justify-between gap-2">
                      <span className={`truncate ${c.non_lus ? "font-bold" : "font-semibold"}`}>{c.nom}</span>
                      <span className="shrink-0 text-xs text-muted" suppressHydrationWarning>
                        {timeAgo(c.dernier.date, now)}
                      </span>
                    </span>
                    <span className="flex items-center justify-between gap-2">
                      <span className={`truncate text-sm ${c.non_lus ? "text-foreground" : "text-muted"}`}>
                        {prefix}
                        {c.dernier.type === "offer" ? "📎 " : ""}
                        {c.dernier.texte}
                      </span>
                      {c.non_lus > 0 && (
                        <span className="flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-accent px-1.5 text-xs font-bold text-white">
                          {c.non_lus}
                        </span>
                      )}
                    </span>
                    <span className="mt-0.5 flex gap-2 text-xs text-muted">
                      {aiOff && <span className="rounded bg-background px-1.5">IA coupée</span>}
                      {c.depense_cents > 0 && <span>LTV {formatEuros(c.depense_cents)}</span>}
                    </span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </aside>

      {/* Le fil de la conversation, et la fiche de la personne */}
      <section className={`min-h-0 flex-col ${selected ? "flex" : "hidden lg:flex"}`}>
        {!selected ? (
          <p className="m-auto p-6 text-muted">Choisissez une conversation.</p>
        ) : !thread || !person ? (
          <p className="m-auto p-6 text-muted">Chargement…</p>
        ) : (
          <div className="grid min-h-0 flex-1 grid-cols-1 xl:grid-cols-[1fr_22rem]">
            <div className={`min-h-0 flex-col ${showPanel ? "hidden xl:flex" : "flex"}`}>
              <header className="flex items-center gap-3 border-b border-line px-4 py-3">
                <button
                  type="button"
                  onClick={() => {
                    selectedRef.current = null;
                    setSelected(null);
                    window.history.replaceState(null, "", "/admin/messages");
                  }}
                  className="text-sm text-muted lg:hidden"
                  aria-label="Retour à la liste"
                >
                  ←
                </button>
                <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent font-serif text-white">
                  {person.nom.charAt(0).toUpperCase()}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate font-bold">{person.nom}</span>
                  <span className="block truncate text-xs text-muted">
                    {person.age ? `${person.age} ans · ` : ""}LTV {formatEuros(person.depense_cents)}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => setShowPanel(true)}
                  className="rounded-full border border-line px-3 py-1 text-sm font-semibold xl:hidden"
                >
                  Fiche
                </button>
              </header>

              <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
                <ol className="flex flex-col gap-2">
                  {thread.messages.map((m: Message) => {
                    const theirs = m.role === "user";
                    const offer = m.offer_id !== null ? offersById[m.offer_id] : undefined;
                    return (
                      <li key={m.id} className={`flex max-w-[85%] flex-col ${theirs ? "self-start" : "self-end items-end"}`}>
                        <div
                          className={`whitespace-pre-wrap break-words rounded-3xl px-4 py-2.5 ${
                            theirs
                              ? "rounded-bl-md border border-line bg-surface"
                              : m.author === "team"
                                ? "rounded-br-md bg-accent text-white"
                                : "rounded-br-md bg-accent-soft"
                          }`}
                        >
                          {m.content}
                          {m.kind === "offer" && offer && (
                            <span className="mt-2 block rounded-xl bg-background/80 px-3 py-2 text-sm text-foreground">
                              <span className="block font-semibold">
                                {offer.step_id !== null && thread.steps[offer.step_id]
                                  ? thread.steps[offer.step_id].title
                                  : "Étape supprimée"}
                              </span>
                              {label(offer.photo_count, offer.video_count)} · {formatEuros(offer.price_cents)}
                              {offer.personalized ? " (personnalisé)" : ""} · {STATUS_LABEL[offer.status]}
                              {offer.last_bid_cents !== null && (
                                <span className="block text-xs text-muted">
                                  Dernière offre : {formatEuros(offer.last_bid_cents)} (
                                  {offer.last_bid_status === "acceptee" ? "acceptée" : "refusée"})
                                </span>
                              )}
                            </span>
                          )}
                        </div>
                        <span className="mt-1 px-2 text-[11px] font-semibold text-muted" suppressHydrationWarning>
                          {theirs ? person.nom : m.author === "team" ? "Équipe" : "IA"} · {timeAgo(m.created_at, now)}
                        </span>
                      </li>
                    );
                  })}
                </ol>
                <div ref={endRef} />
              </div>

              <form onSubmit={send} className="flex items-end gap-2 border-t border-line p-3">
                <textarea
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  rows={2}
                  placeholder="Répondre au nom de l'équipe…"
                  aria-label="Réponse de l'équipe"
                  className="min-h-11 flex-1 resize-none rounded-2xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
                />
                <button
                  type="submit"
                  disabled={sending || !reply.trim()}
                  className="rounded-full bg-accent px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50"
                >
                  Envoyer
                </button>
              </form>
              <p className="px-3 pb-2 text-xs text-muted">
                {error ?? "La personne verra ce message signé « Équipe »."}
              </p>
            </div>

            {/* La fiche */}
            <aside className={`min-h-0 overflow-y-auto border-l border-line p-4 ${showPanel ? "block" : "hidden xl:block"}`}>
              <div className="mb-4 flex items-center justify-between xl:hidden">
                <h2 className="font-bold">Fiche de {person.nom}</h2>
                <button type="button" onClick={() => setShowPanel(false)} className="text-sm text-muted underline">
                  Retour au fil
                </button>
              </div>

              <dl className="mb-5 grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
                <dt className="text-muted">E-mail</dt>
                <dd className="truncate">{person.email}</dd>
                <dt className="text-muted">Âge</dt>
                <dd>{person.age ? `${person.age} ans` : "—"}</dd>
                <dt className="text-muted">LTV</dt>
                <dd className="font-bold">{formatEuros(person.depense_cents)}</dd>
                <dt className="text-muted">Ce mois-ci</dt>
                <dd>
                  {formatEuros(person.depense_mois_cents)}
                  {person.plafond_cents !== null ? ` / ${formatEuros(person.plafond_cents)}` : ""}
                </dd>
              </dl>

              {form && (
                <form onSubmit={save} className="mb-6 flex flex-col gap-3">
                  <label className="flex items-start gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={form.ai_enabled}
                      disabled={!thread?.creatorName}
                      onChange={(e) => setForm({ ...form, ai_enabled: e.target.checked })}
                      className="mt-1 size-4 accent-[var(--accent)] disabled:opacity-50"
                    />
                    <span>
                      <span className="font-semibold">L&apos;IA peut répondre à cette personne</span>
                      <span className="block text-xs text-muted">{aiLine}</span>
                      <span className="block text-xs text-muted">
                        {thread?.creatorName
                          ? `Réglage de ${thread.creatorName}, la créatrice active (comme les emojis).`
                          : "Choisissez d'abord une créatrice dans l'onglet IA."}
                      </span>
                    </span>
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold">Ville</span>
                    <input
                      value={form.city}
                      onChange={(e) => setForm({ ...form, city: e.target.value })}
                      className="rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
                    />
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold">Fuseau horaire</span>
                    <select
                      value={form.timezone}
                      onChange={(e) => setForm({ ...form, timezone: e.target.value })}
                      className="rounded-xl border border-line bg-surface px-3 py-2"
                    >
                      {zones().map((z) => (
                        <option key={z} value={z}>
                          {z}
                        </option>
                      ))}
                    </select>
                  </label>
                  {thread?.creatorName && (
                    <div className="flex flex-col gap-1 text-sm">
                      <span className="font-semibold">Emojis de {thread.creatorName} avec cette personne</span>
                      <EmojiChoice
                        who={thread.person.nom}
                        mode={form.emoji_mode}
                        emojis={form.emojis}
                        onChange={(emoji_mode, emojis) => setForm({ ...form, emoji_mode, emojis })}
                      />
                    </div>
                  )}
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="flex justify-between font-semibold">
                      Comment se comporter avec elle
                      <span className="font-normal text-muted">{form.notes.length} / 5000</span>
                    </span>
                    <textarea
                      value={form.notes}
                      maxLength={5000}
                      rows={6}
                      onChange={(e) => setForm({ ...form, notes: e.target.value })}
                      placeholder="Ce qui aide l'IA : ce qu'elle aime, ce qu'il vaut mieux éviter, le ton à prendre…"
                      className="rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
                    />
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold">Script de vente</span>
                    <select
                      value={form.script_id ?? ""}
                      onChange={(e) => setForm({ ...form, script_id: e.target.value ? Number(e.target.value) : null })}
                      className="rounded-xl border border-line bg-surface px-3 py-2"
                    >
                      <option value="">Script par défaut{thread.creatorName ? ` de ${thread.creatorName}` : ""}</option>
                      {thread.scripts.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold">Plafond de dépenses par mois (€)</span>
                    <input
                      value={form.spending_cap}
                      onChange={(e) => setForm({ ...form, spending_cap: e.target.value })}
                      inputMode="decimal"
                      placeholder="Vide : celui des réglages de l'IA"
                      className="rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
                    />
                  </label>
                  <button type="submit" disabled={busy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60">
                    Enregistrer la fiche
                  </button>
                  {formNotice && (
                    <p role="status" className="text-sm text-muted">
                      {formNotice}
                    </p>
                  )}
                </form>
              )}

              <section className="mb-6">
                <h3 className="mb-2 font-bold">Ce que l&apos;IA sait</h3>
                {thread.facts.length === 0 ? (
                  <p className="text-sm text-muted">Rien pour l&apos;instant.</p>
                ) : (
                  <ul className="list-disc pl-5 text-sm">
                    {thread.facts.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                )}
              </section>

              <section className="flex flex-col gap-3">
                <h3 className="font-bold">Vente</h3>
                {pending && (
                  <div className="rounded-xl border border-line p-3 text-sm">
                    <p>
                      <span className="font-semibold">En attente :</span>{" "}
                      {pending.step_id !== null && thread.steps[pending.step_id]?.title} ·{" "}
                      {formatEuros(pending.price_cents)}
                      {pending.personalized ? " (personnalisé)" : ""}
                    </p>
                    <button type="button" disabled={busy} onClick={() => withdraw(pending)} className="mt-2 text-sm text-bad underline">
                      Retirer l&apos;offre
                    </button>
                  </div>
                )}
                {!next ? (
                  <p className="text-sm text-muted">Plus rien à proposer : le script est terminé (ou vide).</p>
                ) : (
                  <div className="flex flex-col gap-2 rounded-xl border border-line p-3 text-sm">
                    <p>
                      <span className="font-semibold">Étape suivante :</span> {next.title} ({contentLabel(mediaCounts(next.media ?? []).photos, mediaCounts(next.media ?? []).videos)})
                    </p>
                    <p className="text-muted">
                      {next.is_paid
                        ? `Prix ${formatEuros(next.price_cents)}, entre ${formatEuros(next.min_price_cents)} et ${formatEuros(next.max_price_cents)}`
                        : "Gratuite (cadeau)"}{" "}
                      · proposée par {next.trigger_mode === "ia" ? "l'IA" : "l'équipe"}
                    </p>
                    {!pending && (
                      <>
                        {next.is_paid && (
                          <label className="flex items-center gap-2">
                            <span>Prix</span>
                            <input
                              value={offerPrice}
                              onChange={(e) => setOfferPrice(e.target.value)}
                              inputMode="decimal"
                              aria-label="Prix de l'offre en euros"
                              className="w-24 rounded-xl border border-line bg-surface px-2 py-1"
                            />
                            <span>€</span>
                          </label>
                        )}
                        <textarea
                          value={offerMessage}
                          onChange={(e) => setOfferMessage(e.target.value)}
                          rows={3}
                          placeholder="Le message qui accompagne l'offre"
                          aria-label="Message de l'offre"
                          className="rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent"
                        />
                        <div className="flex flex-wrap gap-2">
                          <button
                            type="button"
                            disabled={busy}
                            onClick={() => draft(next)}
                            className="rounded-full border border-line px-3 py-1.5 font-semibold disabled:opacity-60"
                          >
                            Faire écrire par l&apos;IA
                          </button>
                          <button
                            type="button"
                            disabled={busy}
                            onClick={() => propose(next)}
                            className="rounded-full bg-accent px-3 py-1.5 font-bold text-white disabled:opacity-60"
                          >
                            Envoyer l&apos;offre
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}
                {offerNotice && (
                  <p role="status" className="text-sm text-muted">
                    {offerNotice}
                  </p>
                )}
              </section>
            </aside>
          </div>
        )}
      </section>
    </div>
  );
}
