"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { EmojiPicker } from "../emoji-picker";
import { saveCreator } from "./actions";

export type PersonRow = { user_id: string; name: string; ai_enabled: boolean; emojis: string };


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

/** Une créatrice telle qu'on la modifie : son profil et son premier message. */
export type CreatorDraft = { id: number | null; persona: PersonaProfile; first_message: string };

// La page d'une créatrice : les personnes (ce qu'elle fait avec chacune),
// son profil, son premier message, puis « Valider ». Quand l'IA est active,
// c'est cette créatrice qu'elle incarne, avec tout ce qui est rempli ici.
export function CreatorForm({
  creator,
  people: initialPeople,
  languages,
}: {
  creator: CreatorDraft;
  people: PersonRow[];
  languages: { code: string; nom: string }[];
}) {
  const router = useRouter();
  const [persona, setPersona] = useState<PersonaProfile>(creator.persona ?? {});
  const [firstMessage, setFirstMessage] = useState(creator.first_message);
  const [people, setPeople] = useState(initialPeople);
  const [search, setSearch] = useState("");
  const [emojiFor, setEmojiFor] = useState(initialPeople[0]?.user_id ?? "");
  const [notice, setNotice] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const set = <K extends keyof PersonaProfile>(key: K, value: PersonaProfile[K]) =>
    setPersona((p) => ({ ...p, [key]: value }));
  const text = (key: keyof PersonaProfile) => (persona[key] as string | undefined) ?? "";

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    const result = await saveCreator({
      id: creator.id,
      persona,
      first_message: firstMessage,
      people: people.map(({ user_id, ai_enabled, emojis }) => ({ user_id, ai_enabled, emojis })),
    });
    setSaving(false);
    if (!result.ok) return setNotice(result.error);
    router.push("/admin/creatrices");
    router.refresh();
  }

  function toggle(person: PersonRow) {
    setPeople((list) => list.map((p) => (p.user_id === person.user_id ? { ...p, ai_enabled: !p.ai_enabled } : p)));
  }

  const groups = persona.groupes ?? [];
  const interests = persona.interets ?? [];
  const setGroups = (g: CustomGroup[]) => set("groupes", g);
  const setInterests = (i: InterestCategory[]) => set("interets", i);
  const visible = people.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()));
  const emojiPerson = people.find((p) => p.user_id === emojiFor);
  const name = text("nom").trim();

  return (
    <form onSubmit={submit} className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 pb-28 sm:px-6">
      <header>
        <Link href="/admin/creatrices" className="text-sm text-muted underline underline-offset-4">
          ← Créatrices
        </Link>
        <h1 className="mt-2 font-serif text-3xl">{creator.id ? name || "Créatrice" : "Nouvelle créatrice"}</h1>
        <p className="text-sm text-muted">
          Tout ce qui est rempli ici appartient à cette créatrice : quand l&apos;IA l&apos;incarne, elle agit selon ce
          profil. Elle reste une IA et le dit toujours si on le lui demande.
        </p>
      </header>

      {/* Les personnes (mode hybride) et leurs emojis */}
      <section className={card} aria-labelledby="titre-personnes">
        <h2 id="titre-personnes" className="font-bold">
          Personnes
        </h2>
        <p className="text-sm text-muted">
          Ce que cette créatrice fait avec chaque personne. En mode hybride, l&apos;IA ne parle qu&apos;aux personnes
          cochées. Tout est enregistré avec « Valider », en bas de la page.
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
                <EmojiPicker
                    value={emojiPerson.emojis}
                    onChange={(emojis) =>
                      setPeople((list) => list.map((p) => (p.user_id === emojiPerson.user_id ? { ...p, emojis } : p)))
                    }
                  />
              )}
            </div>
          </>
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
              className={`${input} w-28 shrink-0 sm:w-40`}
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
              className={`${input} w-28 shrink-0 sm:w-40`}
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

      {/* Le premier message */}
      <section className={card} aria-labelledby="titre-premier-message">
        <h2 id="titre-premier-message" className="font-bold">
          Premier message
        </h2>
        <Field label="Le message d'accueil" hint="Envoyé à chaque nouvelle personne. Vide : le message d'accueil par défaut. {nom} devient le nom de la créatrice.">
          <textarea
            value={firstMessage}
            rows={5}
            maxLength={2000}
            onChange={(e) => setFirstMessage(e.target.value)}
            placeholder="Bonjour, je suis {nom}…"
            className={input}
          />
        </Field>
      </section>

      {/* Juste au-dessus de la barre d'onglets. */}
      <div className="fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-10 border-t border-line bg-background/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center gap-3">
          <button type="submit" disabled={saving} className="rounded-full bg-accent px-6 py-2.5 font-bold text-white disabled:opacity-60">
            {saving ? "Enregistrement…" : "Valider"}
          </button>
          <Link href="/admin/creatrices" className="px-2 text-sm text-muted">
            Annuler
          </Link>
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
