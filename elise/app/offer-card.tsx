"use client";

import { useEffect, useState } from "react";
import { formatEuros } from "@/lib/dashboard";
import { MAX_REFUSED_BIDS, contentLabel, type Offer } from "@/lib/offers";

type Unlocked = { type: Offer["content_type"]; texte: string; items: { kind: "image" | "video"; url: string }[] };

/** « 3 photos et 1 vidéo à débloquer », « Texte à débloquer ». */
function lockedLabel(offer: Offer): string {
  const photos = offer.photo_count ?? 0;
  const videos = offer.video_count ?? 0;
  if (!photos && !videos) return "Texte à débloquer";
  const text = contentLabel(photos, videos);
  return `${text.charAt(0).toUpperCase()}${text.slice(1)} à débloquer`;
}

// Une offre dans la conversation. Tant qu'elle n'est pas achetée, rien du
// contenu n'est chargé : ni aperçu, ni flou, seulement ce qu'elle contient
// (« 3 photos ») et le prix.
export function OfferCard({ offer, onChange }: { offer: Offer; onChange: (offer: Offer) => void }) {
  const [step, setStep] = useState<"idle" | "confirm" | "bid">("idle");
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [content, setContent] = useState<Unlocked | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const unlocked = offer.status === "achetee" || offer.status === "offerte";

  useEffect(() => {
    if (!unlocked || content) return;
    let cancelled = false;
    fetch(`/api/offres/${offer.id}/contenu`, { cache: "no-store" })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (cancelled) return;
        if (!res.ok) setLoadError(data.error ?? "Le contenu n'a pas pu être chargé.");
        else setContent(data as Unlocked);
      })
      .catch(() => !cancelled && setLoadError("Le contenu n'a pas pu être chargé."));
    return () => {
      cancelled = true;
    };
  }, [unlocked, content, offer.id]);

  async function call(path: string, body?: unknown) {
    setBusy(true);
    setNotice(null);
    try {
      const res = await fetch(`/api/offres/${offer.id}/${path}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setNotice(data.error ?? "L'opération n'a pas abouti.");
        return null;
      }
      if (data.offer) onChange(data.offer as Offer);
      return data;
    } catch {
      setNotice("La connexion a été perdue. Réessayez.");
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function buy() {
    if (await call("acheter")) setStep("idle");
  }

  async function bid(e: React.FormEvent) {
    e.preventDefault();
    const data = await call("proposition", { montant: amount });
    if (!data) return;
    const r = data.result as { statut: string; prix_cents: number; essais_restants?: number };
    if (r.statut === "acceptee") {
      setNotice(`Offre acceptée : le contenu est à vous pour ${formatEuros(r.prix_cents)}.`);
      setStep("confirm");
    } else {
      const left = r.essais_restants ?? 0;
      setNotice(
        left > 0
          ? `Offre refusée : c'est en dessous du prix accepté. Il vous reste ${left} essai${left > 1 ? "s" : ""}.`
          : "Offre refusée. Vous ne pouvez plus faire d'offre sur ce contenu.",
      );
      setStep("idle");
    }
    setAmount("");
  }

  if (offer.status === "retiree") {
    return <p className="mt-2 rounded-2xl bg-background px-3 py-2 text-sm text-muted">Cette offre n&apos;est plus disponible.</p>;
  }

  if (unlocked) {
    return (
      <div className="mt-2 flex flex-col gap-2">
        <p className="text-xs font-semibold text-muted">
          {offer.status === "offerte" ? "Offert" : `Débloqué · ${formatEuros(offer.price_cents)}`}
        </p>
        {loadError && <p className="text-sm text-muted">{loadError}</p>}
        {!content && !loadError && <p className="text-sm text-muted">Chargement…</p>}
        {content && content.items.length > 0 && (
          <div className={`grid gap-2 ${content.items.length > 1 ? "grid-cols-2" : ""}`}>
            {content.items.map((item, i) =>
              item.kind === "video" ? (
                <video key={item.url} src={item.url} controls playsInline className="max-h-96 w-full rounded-2xl bg-background" />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element -- lien signé temporaire, hors de l'optimiseur d'images
                <img
                  key={item.url}
                  src={item.url}
                  alt={content.items.length > 1 ? `Contenu débloqué, ${i + 1} sur ${content.items.length}` : "Contenu débloqué"}
                  className="max-h-96 w-full rounded-2xl object-contain"
                />
              ),
            )}
          </div>
        )}
        {content?.texte && (
          <p className={`whitespace-pre-wrap ${content.items.length ? "text-sm" : "rounded-2xl bg-background px-3 py-2"}`}>
            {content.texte}
          </p>
        )}
      </div>
    );
  }

  const canBid = offer.bids_refused < MAX_REFUSED_BIDS;
  return (
    <div className="mt-2 flex flex-col gap-2 rounded-2xl border border-line bg-background p-3">
      <div className="flex items-center gap-3">
        <span aria-hidden className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-accent-soft text-accent">
          <svg viewBox="0 0 24 24" className="size-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="4" y="11" width="16" height="10" rx="2" />
            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
          </svg>
        </span>
        <div className="min-w-0">
          <p className="font-semibold">{lockedLabel(offer)}</p>
          <p className="text-sm">
            <span className="font-bold">{formatEuros(offer.price_cents)}</span>
            {offer.personalized && <span className="text-muted"> · prix personnalisé pour vous</span>}
          </p>
        </div>
      </div>

      {step === "confirm" ? (
        <div className="flex flex-col gap-2">
          <p className="text-sm">
            Confirmer l&apos;achat pour <strong>{formatEuros(offer.price_cents)}</strong> ?
            <span className="block text-xs text-muted">Paiement de démonstration : aucun débit n&apos;est effectué.</span>
          </p>
          <div className="flex gap-2">
            <button type="button" disabled={busy} onClick={buy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60">
              Confirmer
            </button>
            <button type="button" disabled={busy} onClick={() => setStep("idle")} className="rounded-full px-4 py-2 text-sm text-muted">
              Annuler
            </button>
          </div>
        </div>
      ) : step === "bid" ? (
        <form onSubmit={bid} className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <span>Votre offre</span>
            <input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              inputMode="decimal"
              placeholder="0,00"
              aria-label="Montant de votre offre en euros"
              className="w-24 rounded-full border border-line bg-surface px-3 py-1.5 outline-none focus:border-accent"
            />
            <span>€</span>
          </label>
          <button type="submit" disabled={busy || !amount.trim()} className="rounded-full bg-accent px-4 py-1.5 text-sm font-bold text-white disabled:opacity-60">
            Proposer
          </button>
          <button type="button" onClick={() => setStep("idle")} className="px-2 text-sm text-muted">
            Annuler
          </button>
        </form>
      ) : (
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => setStep("confirm")} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white">
            Débloquer pour {formatEuros(offer.price_cents)}
          </button>
          {canBid && (
            <button type="button" onClick={() => setStep("bid")} className="rounded-full border border-line px-4 py-2 text-sm font-semibold">
              Faire une offre
            </button>
          )}
        </div>
      )}
      {notice && (
        <p role="status" className="text-sm text-muted">
          {notice}
        </p>
      )}
    </div>
  );
}
