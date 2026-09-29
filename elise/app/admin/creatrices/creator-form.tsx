"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useEffectEvent, useRef, useState } from "react";
import { emojiSummary, type EmojiMode } from "@/lib/emojis";
import {
  GENRES,
  MAX_TEXT,
  MIN_PERSONA_AGE,
  SILHOUETTES,
  type CustomGroup,
  type InterestCategory,
  type PersonaProfile,
} from "@/lib/persona-profile";
import { EmojiChoice } from "../emoji-picker";
import { saveCreator, type PersonSetting } from "./actions";

export type PersonRow = PersonSetting & { name: string };

const input = "rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent";
const card = "flex flex-col gap-4 rounded-3xl border border-line bg-surface p-5";
/** Après la dernière frappe, le temps d'attendre avant d'enregistrer. */
const AUTOSAVE_MS = 700;
/** Personnes affichées d'un coup ; « Afficher plus » pour la suite. */
const PAGE = 20;

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

type Values = { persona: PersonaProfile; firstMessage: string; people: PersonRow[] };
type Status = { state: "idle" | "saving" | "saved" } | { state: "error"; message: string };

const sameSetting = (a: PersonSetting, b: PersonSetting) =>
  a.ai_enabled === b.ai_enabled && a.emoji_mode === b.emoji_mode && a.emojis === b.emojis;

// La page d'une créatrice : les personnes (ce qu'elle fait avec chacune),
// son profil, son premier message. Tout s'enregistre tout seul à chaque
// changement : on peut partir et revenir. « Valider » quand elle est prête ;
// quand l'IA l'incarne, elle agit selon tout ce qui est rempli ici.
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
  const [limit, setLimit] = useState(PAGE);
  const [emojiFor, setEmojiFor] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>({ state: creator.id ? "saved" : "idle" });
  const [validating, setValidating] = useState(false);
  const [version, setVersion] = useState(0);
  const firstNameRef = useRef<HTMLInputElement>(null);

  // L'enregistrement automatique : une seule sauvegarde à la fois, dans
  // l'ordre (la première crée la créatrice, les suivantes la modifient).
  const idRef = useRef(creator.id);
  const savedPeople = useRef(new Map(initialPeople.map((p) => [p.user_id, p as PersonSetting])));
  const chain = useRef<Promise<unknown>>(Promise.resolve());
  const pending = useRef<(() => Promise<unknown>) | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const touch = () => setVersion((v) => v + 1);
  const set = <K extends keyof PersonaProfile>(key: K, value: PersonaProfile[K]) => {
    setPersona((p) => ({ ...p, [key]: value }));
    touch();
  };
  const text = (key: keyof PersonaProfile) => (persona[key] as string | undefined) ?? "";

  async function persist(values: Values, validate: boolean) {
    setStatus({ state: "saving" });
    const changed = values.people.filter((p) => {
      const saved = savedPeople.current.get(p.user_id);
      return !saved || !sameSetting(saved, p);
    });
    let result: Awaited<ReturnType<typeof saveCreator>>;
    try {
      result = await saveCreator({
        id: idRef.current,
        persona: values.persona,
        first_message: values.firstMessage,
        people: changed.map(({ user_id, ai_enabled, emoji_mode, emojis }) => ({ user_id, ai_enabled, emoji_mode, emojis })),
        validate,
      });
    } catch {
      result = { ok: false, error: "Pas de connexion : les derniers changements ne sont pas enregistrés. Réessayez." };
    }
    if (!result.ok) {
      setStatus({ state: "error", message: result.error });
      return result;
    }
    idRef.current = result.id;
    for (const p of changed) savedPeople.current.set(p.user_id, p);
    setStatus({ state: "saved" });
    return result;
  }

  /** Enregistre tout de suite ce qui attend encore. */
  const flush = useCallback(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    const job = pending.current;
    pending.current = null;
    if (job) chain.current = chain.current.then(job);
    return chain.current;
  }, []);

  const schedule = useEffectEvent(() => {
    const values = { persona, firstMessage, people };
    pending.current = () => persist(values, false);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(flush, AUTOSAVE_MS);
  });
  useEffect(() => {
    if (version > 0) schedule();
  }, [version]);
  // En quittant la page (onglet, retour) : rien de ce qui a été tapé ne se perd.
  useEffect(() => () => void flush(), [flush]);

  async function leave(e: React.MouseEvent) {
    e.preventDefault();
    await flush();
    router.push("/admin/creatrices");
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setValidating(true);
    await flush();
    const values = { persona, firstMessage, people };
    const result = (await (chain.current = chain.current.then(() => persist(values, true)))) as Awaited<
      ReturnType<typeof persist>
    >;
    setValidating(false);
    if (!result.ok) {
      if (!persona.nom?.trim()) {
        firstNameRef.current?.focus();
        firstNameRef.current?.scrollIntoView({ block: "center" });
      }
      return;
    }
    router.push("/admin/creatrices");
  }

  function updatePerson(userId: string, change: Partial<PersonSetting>) {
    setPeople((list) => list.map((p) => (p.user_id === userId ? { ...p, ...change } : p)));
    touch();
  }

  function sameForEveryone(from: PersonRow) {
    setPeople((list) => list.map((p) => ({ ...p, emoji_mode: from.emoji_mode, emojis: from.emojis })));
    touch();
  }

  const groups = persona.groupes ?? [];
  const interests = persona.interets ?? [];
  const setGroups = (g: CustomGroup[]) => set("groupes", g);
  const setInterests = (i: InterestCategory[]) => set("interets", i);
  const visible = people.filter((p) => p.name.toLowerCase().includes(search.trim().toLowerCase()));
  const name = text("nom").trim();

  return (
    <form onSubmit={submit} className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 pb-32 sm:px-6">
      <header>
        <Link href="/admin/creatrices" onClick={leave} className="text-sm text-muted underline underline-offset-4">
          ← Créatrices
        </Link>
        <h1 className="mt-2 font-serif text-3xl">{name || (creator.id ? "Créatrice sans prénom" : "Nouvelle créatrice")}</h1>
        <p className="text-sm text-muted">
          Tout s&apos;enregistre tout seul, à chaque changement : vous pouvez partir et revenir quand vous voulez.
          Quand l&apos;IA incarne cette créatrice, elle agit selon tout ce qui est rempli ici, et reste une IA qui
          le dit toujours si on le lui demande.
        </p>
      </header>

      {/* Les personnes : l'IA leur répond-elle (mode hybride), et avec quels emojis */}
      <section className={card} aria-labelledby="titre-personnes">
        <div>
          <h2 id="titre-personnes" className="font-bold">
            Personnes
          </h2>
          <p className="text-sm text-muted">
            Les personnes inscrites qui parlent à {name || "cette créatrice"}. Pour chacune : l&apos;IA peut-elle lui
            répondre (en mode hybride), et avec quels emojis.
          </p>
        </div>
        {people.length === 0 ? (
          <p className="text-sm text-muted">
            Personne ne s&apos;est encore inscrit : les réglages de chaque personne apparaîtront ici.
          </p>
        ) : (
          <>
            {people.length > 6 && (
              <input
                type="search"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setLimit(PAGE);
                }}
                placeholder="Chercher une personne inscrite"
                aria-label="Chercher une personne inscrite"
                className={input}
              />
            )}
            <ul className="flex flex-col gap-2">
              {visible.slice(0, limit).map((p) => {
                const open = emojiFor === p.user_id;
                const summary = emojiSummary(p.emoji_mode, p.emojis);
                return (
                  <li key={p.user_id} className="flex flex-col gap-2 rounded-2xl border border-line p-3">
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                      <span className="min-w-0 flex-1 truncate font-semibold">{p.name}</span>
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={p.ai_enabled}
                          onChange={() => updatePerson(p.user_id, { ai_enabled: !p.ai_enabled })}
                          className="size-4 accent-[var(--accent)]"
                          aria-label={`L'IA peut parler à ${p.name}`}
                        />
                        L&apos;IA lui répond
                      </label>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEmojiFor(open ? null : p.user_id)}
                      aria-expanded={open}
                      aria-label={`Emojis avec ${p.name} : ${summary}`}
                      className="flex items-center justify-between gap-2 rounded-xl bg-background px-3 py-2 text-left text-sm"
                    >
                      <span className="min-w-0">
                        Emojis :{" "}
                        <span className={p.emoji_mode === "choisis" && p.emojis ? "text-lg" : "text-muted"}>{summary}</span>
                      </span>
                      <span className="shrink-0 font-semibold text-accent">{open ? "Fermer" : "Choisir"}</span>
                    </button>
                    {open && (
                      <div className="flex flex-col gap-2">
                        <EmojiChoice
                          who={p.name}
                          mode={p.emoji_mode}
                          emojis={p.emojis}
                          onChange={(emoji_mode: EmojiMode, emojis: string) => updatePerson(p.user_id, { emoji_mode, emojis })}
                        />
                        {people.length > 1 && (
                          <button type="button" onClick={() => sameForEveryone(p)} className="self-start text-sm text-accent underline">
                            Mettre les mêmes emojis pour tout le monde
                          </button>
                        )}
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
            {visible.length > limit && (
              <button
                type="button"
                onClick={() => setLimit((l) => l + PAGE)}
                className="self-start rounded-full border border-line px-4 py-1.5 text-sm font-semibold"
              >
                Afficher plus ({visible.length - limit})
              </button>
            )}
            {search && visible.length === 0 && <p className="text-sm text-muted">Personne à ce nom.</p>}
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
          <Field label="Prénom">
            <input
              ref={firstNameRef}
              value={text("nom")}
              onChange={(e) => set("nom", e.target.value)}
              placeholder="Katherine"
              className={input}
            />
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
        <Field label="Le message d'accueil" hint="Envoyé à chaque nouvelle personne. Vide : le message d'accueil par défaut. {nom} devient son prénom.">
          <textarea
            value={firstMessage}
            rows={5}
            maxLength={2000}
            onChange={(e) => {
              setFirstMessage(e.target.value);
              touch();
            }}
            placeholder="Bonjour, je suis {nom}…"
            className={input}
          />
        </Field>
      </section>

      {/* Juste au-dessus de la barre d'onglets. */}
      <div className="fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-10 border-t border-line bg-background/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-4xl flex-col gap-2">
          {status.state === "error" && (
            <p role="alert" className="rounded-xl border border-bad px-3 py-2 text-sm font-semibold text-bad">
              {status.message}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={validating}
              className="rounded-full bg-accent px-6 py-2.5 font-bold text-white disabled:opacity-60"
            >
              {validating ? "Validation…" : "Valider"}
            </button>
            <p role="status" className="text-sm text-muted">
              {status.state === "saving"
                ? "Enregistrement…"
                : status.state === "saved"
                  ? "✓ Enregistré"
                  : status.state === "error"
                    ? ""
                    : "S'enregistre tout seul dès que vous écrivez."}
            </p>
            {status.state === "error" && (
              <button type="button" onClick={touch} className="text-sm font-semibold text-accent underline">
                Réessayer
              </button>
            )}
          </div>
        </div>
      </div>
    </form>
  );
}
