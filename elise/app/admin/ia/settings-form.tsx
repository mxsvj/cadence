"use client";

import { useState } from "react";
import {
  GENRES,
  MAX_TEXT,
  MIN_PERSONA_AGE,
  SILHOUETTES,
  type CustomGroup,
  type InterestCategory,
  type PersonaProfile,
} from "@/lib/persona-profile";
import type { AiMode, AiSettings } from "@/lib/settings";
import { EmojiPicker } from "../emoji-picker";
import { saveEmojis, saveSettings, setAiEnabled } from "./actions";

export type PersonRow = { user_id: string; name: string; ai_enabled: boolean; emojis: string };

const MODES: { value: AiMode; title: string; text: string }[] = [
  { value: "auto", title: "Automatique", text: "L'IA répond à tout le monde, tout de suite." },
  { value: "hybride", title: "Hybride", text: "L'IA ne répond qu'aux personnes cochées ; l'équipe répond aux autres." },
  { value: "manuel", title: "Manuel", text: "L'IA est coupée : l'équipe répond à tout, depuis l'onglet Messages." },
];

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

export function AiSettingsForm({
  initial,
  people: initialPeople,
  languages,
}: {
  initial: AiSettings;
  people: PersonRow[];
  languages: { code: string; nom: string }[];
}) {
  const [mode, setMode] = useState<AiMode>(initial.mode);
  const [persona, setPersona] = useState<PersonaProfile>(initial.persona ?? {});
  const [people, setPeople] = useState(initialPeople);
  const [search, setSearch] = useState("");
  const [emojiFor, setEmojiFor] = useState(initialPeople[0]?.user_id ?? "");
  const [notice, setNotice] = useState<string | null>(null);
  const [peopleNotice, setPeopleNotice] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const set = <K extends keyof PersonaProfile>(key: K, value: PersonaProfile[K]) =>
    setPersona((p) => ({ ...p, [key]: value }));
  const text = (key: keyof PersonaProfile) => (persona[key] as string | undefined) ?? "";

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    const result = await saveSettings({ mode, persona });
    setSaving(false);
    setNotice(result.ok ? "Réglages enregistrés. Ils valent dès le prochain message." : result.error);
  }

  async function toggle(person: PersonRow) {
    const enabled = !person.ai_enabled;
    setPeople((list) => list.map((p) => (p.user_id === person.user_id ? { ...p, ai_enabled: enabled } : p)));
    const result = await setAiEnabled(person.user_id, enabled);
    if (!result.ok) {
      setPeople((list) => list.map((p) => (p.user_id === person.user_id ? { ...p, ai_enabled: !enabled } : p)));
      setPeopleNotice(result.error);
    } else setPeopleNotice(null);
  }

  async function storeEmojis() {
    const person = people.find((p) => p.user_id === emojiFor);
    if (!person) return;
    const result = await saveEmojis(person.user_id, person.emojis);
    setPeopleNotice(result.ok ? `Emojis enregistrés pour ${person.name}.` : result.error);
  }

  const groups = persona.groupes ?? [];
  const interests = persona.interets ?? [];
  const setGroups = (g: CustomGroup[]) => set("groupes", g);
  const setInterests = (i: InterestCategory[]) => set("interets", i);
  const visible = people.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()));
  const emojiPerson = people.find((p) => p.user_id === emojiFor);

  return (
    <form onSubmit={submit} className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 pb-28 sm:px-6">
      <header>
        <h1 className="font-serif text-3xl">IA</h1>
        <p className="text-sm text-muted">
          Qui répond, et qui est le personnage. Les réglages fins et les garde-fous de la vente sont dans
          Paramètres.
        </p>
      </header>

      {/* Le mode */}
      <section className={card} aria-labelledby="titre-mode">
        <h2 id="titre-mode" className="font-bold">
          Qui répond
        </h2>
        <div className="grid gap-3 sm:grid-cols-3" role="radiogroup" aria-labelledby="titre-mode">
          {MODES.map((m) => (
            <label
              key={m.value}
              className={`flex cursor-pointer flex-col gap-1 rounded-2xl border p-4 ${
                mode === m.value ? "border-accent bg-accent-soft" : "border-line"
              }`}
            >
              <span className="flex items-center gap-2 font-semibold">
                <input
                  type="radio"
                  name="mode"
                  value={m.value}
                  checked={mode === m.value}
                  onChange={() => setMode(m.value)}
                  className="accent-[var(--accent)]"
                />
                {m.title}
              </span>
              <span className="text-sm text-muted">{m.text}</span>
            </label>
          ))}
        </div>
        <p className="text-xs text-muted">
          Dans tous les cas, chaque réponse est marquée pour la personne : « IA » ou « Équipe ».
        </p>
      </section>

      {/* Les personnes (mode hybride) et leurs emojis */}
      <section className={card} aria-labelledby="titre-personnes">
        <h2 id="titre-personnes" className="font-bold">
          Personnes
        </h2>
        <p className="text-sm text-muted">
          En mode hybride, l&apos;IA ne parle qu&apos;aux personnes cochées. Enregistré à chaque clic.
        </p>
        {people.length === 0 ? (
          <p className="text-sm text-muted">Personne ne s&apos;est encore inscrit.</p>
        ) : (
          <>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Chercher une personne"
              aria-label="Chercher une personne"
              className={input}
            />
            <ul className="grid max-h-64 gap-1 overflow-y-auto sm:grid-cols-2">
              {visible.map((p) => (
                <li key={p.user_id}>
                  <label className="flex items-center gap-2 rounded-xl px-2 py-1.5 hover:bg-accent-soft">
                    <input
                      type="checkbox"
                      checked={p.ai_enabled}
                      onChange={() => toggle(p)}
                      className="size-4 accent-[var(--accent)]"
                      aria-label={`L'IA peut parler à ${p.name}`}
                    />
                    <span className="truncate">{p.name}</span>
                    {p.emojis && <span className="ml-auto shrink-0">{p.emojis}</span>}
                  </label>
                </li>
              ))}
            </ul>
            <div className="flex flex-col gap-2 border-t border-line pt-4">
              <h3 className="font-semibold">Emojis par personne</h3>
              <p className="text-sm text-muted">L&apos;IA n&apos;utilisera que ceux-là avec la personne choisie.</p>
              <select value={emojiFor} onChange={(e) => setEmojiFor(e.target.value)} aria-label="Personne" className={input}>
                {people.map((p) => (
                  <option key={p.user_id} value={p.user_id}>
                    {p.name}
                  </option>
                ))}
              </select>
              {emojiPerson && (
                <>
                  <EmojiPicker
                    value={emojiPerson.emojis}
                    onChange={(emojis) =>
                      setPeople((list) => list.map((p) => (p.user_id === emojiPerson.user_id ? { ...p, emojis } : p)))
                    }
                  />
                  <button type="button" onClick={storeEmojis} className="self-start rounded-full border border-line px-4 py-2 text-sm font-semibold">
                    Enregistrer les emojis
                  </button>
                </>
              )}
            </div>
          </>
        )}
        {peopleNotice && (
          <p role="status" className="text-sm text-muted">
            {peopleNotice}
          </p>
        )}
      </section>

      {/* Le personnage */}
      <section className={card} aria-labelledby="titre-personnage">
        <div>
          <h2 id="titre-personnage" className="font-bold">
            Profil du personnage
          </h2>
          <p className="text-sm text-muted">
            L&apos;IA incarne ce personnage et s&apos;appuie sur tout ce qui est rempli. Elle reste une IA et le dit
            toujours si on le lui demande.
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Nom">
            <input value={text("nom")} onChange={(e) => set("nom", e.target.value)} placeholder="Élise" className={input} />
          </Field>
          <Field label="Pseudo">
            <input value={text("pseudo")} onChange={(e) => set("pseudo", e.target.value)} className={input} />
          </Field>
          <Field label="Genre">
            <input list="genres" value={text("genre")} onChange={(e) => set("genre", e.target.value)} className={input} />
          </Field>
          <Field label="Âge" hint={`${MIN_PERSONA_AGE} ans minimum.`}>
            <input
              type="number"
              min={MIN_PERSONA_AGE}
              max={99}
              value={persona.age ?? ""}
              onChange={(e) => set("age", e.target.value ? Number(e.target.value) : undefined)}
              className={input}
            />
          </Field>
          <Field label="Anniversaire">
            <input type="date" value={text("anniversaire")} onChange={(e) => set("anniversaire", e.target.value)} className={input} />
          </Field>
          <Field label="Profession">
            <input value={text("profession")} onChange={(e) => set("profession", e.target.value)} className={input} />
          </Field>
          <Field label="Ville">
            <input value={text("ville")} onChange={(e) => set("ville", e.target.value)} className={input} />
          </Field>
          <Field label="Langue maternelle">
            <select value={text("langue_maternelle")} onChange={(e) => set("langue_maternelle", e.target.value)} className={input}>
              <option value="">—</option>
              {languages.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.nom}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            checked={persona.pres_de_la_personne ?? false}
            onChange={(e) => set("pres_de_la_personne", e.target.checked)}
            className="mt-1 size-4 accent-[var(--accent)]"
          />
          <span>
            <span className="font-semibold">Se dire dans la même région que la personne</span>
            <span className="block text-xs text-muted">
              D&apos;après la ville de sa fiche. C&apos;est une simple information : l&apos;IA ne propose jamais de
              rencontre et refuse toujours d&apos;en organiser une.
            </span>
          </span>
        </label>

        <h3 className="font-semibold">Apparence</h3>
        <div className="grid gap-3 sm:grid-cols-4">
          <Field label="Taille">
            <input value={text("taille")} onChange={(e) => set("taille", e.target.value)} placeholder="1,68 m" className={input} />
          </Field>
          <Field label="Poids">
            <input value={text("poids")} onChange={(e) => set("poids", e.target.value)} placeholder="55 kg" className={input} />
          </Field>
          <Field label="Pointure">
            <input value={text("pointure")} onChange={(e) => set("pointure", e.target.value)} placeholder="38" className={input} />
          </Field>
          <Field label="Taille de bonnet">
            <input value={text("bonnet")} onChange={(e) => set("bonnet", e.target.value)} placeholder="B" className={input} />
          </Field>
          <Field label="Cheveux">
            <input value={text("cheveux")} onChange={(e) => set("cheveux", e.target.value)} placeholder="châtains" className={input} />
          </Field>
          <Field label="Yeux">
            <input value={text("yeux")} onChange={(e) => set("yeux", e.target.value)} placeholder="verts" className={input} />
          </Field>
          <Field label="Origine">
            <input value={text("ethnicite")} onChange={(e) => set("ethnicite", e.target.value)} className={input} />
          </Field>
          <Field label="Silhouette">
            <input list="silhouettes" value={text("corps")} onChange={(e) => set("corps", e.target.value)} className={input} />
          </Field>
        </div>

        <h3 className="font-semibold">Groupes personnalisés</h3>
        <p className="-mt-3 text-sm text-muted">Tatouages, piercings, style, animaux… tout ce que l&apos;IA doit prendre en compte.</p>
        {groups.map((g, i) => (
          <div key={i} className="flex flex-wrap gap-2">
            <input
              value={g.titre}
              onChange={(e) => setGroups(groups.map((x, j) => (j === i ? { ...x, titre: e.target.value } : x)))}
              placeholder="Tatouages"
              aria-label="Nom du groupe"
              className={`${input} w-40`}
            />
            <input
              value={g.valeur}
              onChange={(e) => setGroups(groups.map((x, j) => (j === i ? { ...x, valeur: e.target.value } : x)))}
              placeholder="Une hirondelle sur le poignet"
              aria-label="Détail"
              className={`${input} min-w-0 flex-1`}
            />
            <button type="button" onClick={() => setGroups(groups.filter((_, j) => j !== i))} className="px-2 text-sm text-muted underline">
              Retirer
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setGroups([...groups, { titre: "", valeur: "" }])}
          className="self-start rounded-full border border-line px-4 py-1.5 text-sm font-semibold"
        >
          Ajouter un groupe
        </button>

        <h3 className="font-semibold">Centres d&apos;intérêt et préférences</h3>
        <p className="-mt-3 text-sm text-muted">Vos propres catégories : musique, cuisine, voyages…</p>
        {interests.map((c, i) => (
          <div key={i} className="flex flex-wrap gap-2">
            <input
              value={c.categorie}
              onChange={(e) => setInterests(interests.map((x, j) => (j === i ? { ...x, categorie: e.target.value } : x)))}
              placeholder="Musique"
              aria-label="Catégorie"
              className={`${input} w-40`}
            />
            <input
              value={c.elements}
              onChange={(e) => setInterests(interests.map((x, j) => (j === i ? { ...x, elements: e.target.value } : x)))}
              placeholder="jazz, bossa nova, concerts en plein air"
              aria-label="Préférences"
              className={`${input} min-w-0 flex-1`}
            />
            <button type="button" onClick={() => setInterests(interests.filter((_, j) => j !== i))} className="px-2 text-sm text-muted underline">
              Retirer
            </button>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setInterests([...interests, { categorie: "", elements: "" }])}
          className="self-start rounded-full border border-line px-4 py-1.5 text-sm font-semibold"
        >
          Ajouter une catégorie
        </button>

        <Field label={`À propos du personnage (${text("a_propos").length} / ${MAX_TEXT})`}>
          <textarea
            value={text("a_propos")}
            maxLength={MAX_TEXT}
            rows={6}
            onChange={(e) => set("a_propos", e.target.value)}
            placeholder="Son histoire, son caractère, ses habitudes…"
            className={input}
          />
        </Field>
        <datalist id="genres">
          {GENRES.map((g) => (
            <option key={g} value={g} />
          ))}
        </datalist>
        <datalist id="silhouettes">
          {SILHOUETTES.map((s) => (
            <option key={s} value={s} />
          ))}
        </datalist>
      </section>

      {/* Juste au-dessus de la barre d'onglets. */}
      <div className="fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-10 border-t border-line bg-background/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center gap-3">
          <button type="submit" disabled={saving} className="rounded-full bg-accent px-5 py-2.5 font-bold text-white disabled:opacity-60">
            {saving ? "Enregistrement…" : "Enregistrer les réglages"}
          </button>
          {notice && (
            <p role="status" className="text-sm text-muted">
              {notice}
            </p>
          )}
        </div>
      </div>
    </form>
  );
}
