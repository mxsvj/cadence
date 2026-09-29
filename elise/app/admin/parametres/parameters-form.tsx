"use client";

import { useState } from "react";
import type { AiSettings } from "@/lib/settings";
import { saveParameters } from "./actions";

const input = "rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent";
const card = "flex flex-col gap-4 rounded-3xl border border-line bg-surface p-5";

function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-semibold">{label}</span>
      {children}
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </label>
  );
}

// Les réglages fins de l'IA et les garde-fous de la vente.
export function ParametersForm({ initial }: { initial: AiSettings }) {
  const [contextMessages, setContextMessages] = useState(initial.context_messages);
  const [extra, setExtra] = useState(initial.extra_instructions);
  const [cap, setCap] = useState((initial.spending_cap_cents / 100).toFixed(2).replace(".", ","));
  const [minMessages, setMinMessages] = useState(initial.sales_min_messages);
  const [gapMessages, setGapMessages] = useState(initial.sales_gap_messages);
  const [relanceActive, setRelanceActive] = useState(initial.relance_active);
  const [relanceHours, setRelanceHours] = useState(initial.relance_heures);
  const [notice, setNotice] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    const result = await saveParameters({
      context_messages: contextMessages,
      extra_instructions: extra,
      spending_cap: cap,
      sales_min_messages: minMessages,
      sales_gap_messages: gapMessages,
      // Seulement si ça a changé : le reste s'enregistre même avant la mise à jour de la base.
      relance:
        relanceActive !== initial.relance_active || relanceHours !== initial.relance_heures
          ? { active: relanceActive, hours: relanceHours }
          : undefined,
    });
    setSaving(false);
    setNotice(result.ok ? "Paramètres enregistrés. Ils valent dès le prochain message." : result.error);
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-6">
      <section className={card} aria-labelledby="titre-reglages">
        <h2 id="titre-reglages" className="font-bold">
          Réglages de l&apos;IA
        </h2>
        <p className="text-sm text-muted">
          La créativité est réglée au maximum fiable, et l&apos;IA choisit elle-même la longueur de chaque réponse. Le
          premier message se règle pour chaque créatrice, dans l&apos;onglet Créatrices.
        </p>
        <Field label="Messages relus à chaque réponse" hint="De 6 à 60. Au-delà du double, les plus anciens sont résumés.">
          <input type="number" min={6} max={60} value={contextMessages} onChange={(e) => setContextMessages(Number(e.target.value))} className={input} />
        </Field>
        <Field label={`Consignes supplémentaires (${extra.length} / 5000)`} hint="Ajoutées à la fin de la consigne de l'IA.">
          <textarea value={extra} rows={4} maxLength={5000} onChange={(e) => setExtra(e.target.value)} className={input} />
        </Field>
      </section>

      <section className={card} aria-labelledby="titre-garde-fous">
        <h2 id="titre-garde-fous" className="font-bold">
          Garde-fous de la vente
        </h2>
        <p className="text-sm text-muted">
          En plus des règles fixes : jamais de vente par la solitude, l&apos;attachement ou la pression, rien si la
          personne va mal, jamais sous le prix minimum.
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Plafond par personne et par mois (€)" hint="Réglable personne par personne dans sa fiche.">
            <input value={cap} inputMode="decimal" onChange={(e) => setCap(e.target.value)} className={input} />
          </Field>
          <Field label="Messages avant la première offre">
            <input type="number" min={0} value={minMessages} onChange={(e) => setMinMessages(Number(e.target.value))} className={input} />
          </Field>
          <Field label="Messages entre deux offres">
            <input type="number" min={0} value={gapMessages} onChange={(e) => setGapMessages(Number(e.target.value))} className={input} />
          </Field>
        </div>
      </section>

      <section className={card} aria-labelledby="titre-nouvelles">
        <h2 id="titre-nouvelles" className="font-bold">
          Prendre des nouvelles
        </h2>
        <p className="text-sm text-muted">
          Quand une personne ne vient plus, l&apos;IA lui écrit un court message amical pour prendre de ses nouvelles,
          une fois par jour en fin d&apos;après-midi. Un seul message par absence, jamais de vente dedans ni juste après, jamais de
          reproche, et chaque personne peut le refuser depuis son menu.
        </p>
        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            checked={relanceActive}
            onChange={(e) => setRelanceActive(e.target.checked)}
            className="mt-1 size-4 accent-[var(--accent)]"
          />
          <span className="font-semibold">Prendre des nouvelles des personnes absentes</span>
        </label>
        <Field label="Après une absence de" hint="Sans visite ni message. Le message part au passage quotidien suivant.">
          <select value={relanceHours} onChange={(e) => setRelanceHours(Number(e.target.value))} disabled={!relanceActive} className={input}>
            {[24, 48, 72, 96, 168, 336].map((h) => (
              <option key={h} value={h}>
                {h < 168 ? `${h} heures` : h === 168 ? "1 semaine" : "2 semaines"}
              </option>
            ))}
          </select>
        </Field>
      </section>

      <div className="flex flex-wrap items-center gap-3">
        <button type="submit" disabled={saving} className="rounded-full bg-accent px-5 py-2.5 font-bold text-white disabled:opacity-60">
          {saving ? "Enregistrement…" : "Enregistrer les paramètres"}
        </button>
        {notice && (
          <p role="status" className="text-sm text-muted">
            {notice}
          </p>
        )}
      </div>
    </form>
  );
}
