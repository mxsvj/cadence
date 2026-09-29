"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { formatEuros } from "@/lib/dashboard";
import { MAX_MEDIA, contentLabel, mediaCounts, type MediaItem, type Script, type Step } from "@/lib/offers";
import {
  createScript,
  deleteScript,
  deleteStep,
  moveScript,
  moveStep,
  previewLink,
  renameScript,
  saveStep,
  setScriptCreator,
  uploadLink,
  type StepForm,
} from "./actions";

const input = "rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent";
/** « 3 photos et 1 vidéo · texte » : ce que contient un message du script. */
function summary(step: Step): string {
  const { photos, videos } = mediaCounts(step.media ?? []);
  const media = photos || videos ? contentLabel(photos, videos) : "";
  const text = step.content_text.trim() ? "texte" : "";
  const parts = [media, text].filter(Boolean).join(" · ");
  return parts.charAt(0).toUpperCase() + parts.slice(1);
}
const euros = (cents: number) => (cents ? (cents / 100).toFixed(2).replace(".", ",") : "");

type CreatorOption = { id: number; name: string };

/** « Pour » : à qui est le script. Vide : à toutes les créatrices. */
function CreatorSelect({
  creators,
  value,
  onChange,
  label,
  className = "",
}: {
  creators: CreatorOption[];
  value: number | null;
  onChange: (id: number | null) => void;
  label: string;
  className?: string;
}) {
  return (
    <select
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
      aria-label={label}
      className={`${input} min-w-0 ${className}`}
    >
      <option value="">Toutes les créatrices</option>
      {creators.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}
        </option>
      ))}
    </select>
  );
}

export function ContentEditor({
  scripts,
  steps,
  creators,
  activeCreator,
}: {
  scripts: Script[];
  steps: Step[];
  creators: CreatorOption[];
  activeCreator: number | null;
}) {
  const router = useRouter();
  const [selected, setSelected] = useState<number | null>(scripts[0]?.id ?? null);
  const [newName, setNewName] = useState("");
  const [newFor, setNewFor] = useState<number | null>(activeCreator);
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const script = scripts.find((s) => s.id === selected) ?? scripts[0] ?? null;
  const scriptSteps = steps.filter((s) => s.script_id === script?.id);
  const creatorName = (id: number | null | undefined) => creators.find((c) => c.id === id)?.name ?? null;
  // Le script suivi par défaut (sans script dans la fiche) : le premier de la
  // créatrice active, sinon le premier qui sert à toutes.
  const defaultScript =
    (activeCreator !== null && scripts.find((s) => s.creator_id === activeCreator)) || scripts.find((s) => s.creator_id == null) || null;

  async function run(action: Promise<{ ok: boolean; error?: string }>, done?: string) {
    const result = await action;
    setNotice(result.ok ? (done ?? null) : (result.error ?? "L'opération n'a pas abouti."));
    router.refresh();
    return result.ok;
  }

  async function addScript(e: React.FormEvent) {
    e.preventDefault();
    const result = await createScript(newName, newFor);
    if (result.ok) {
      setSelected(result.id);
      setNewName("");
      setNotice("Script créé.");
    } else setNotice(result.error);
    router.refresh();
  }

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6">
      <header>
        <h1 className="font-serif text-3xl">Contenus</h1>
        <p className="text-sm text-muted">
          Des scripts de vente, message par message : photos, vidéos ou texte, gratuits ou payants, avec ce que
          l&apos;IA dit en les proposant. L&apos;IA ne propose jamais que le message suivant, dans cet ordre, jamais
          sous le prix minimum. Les titres ne sont visibles que de l&apos;équipe.
        </p>
      </header>

      {/* Les scripts */}
      <section className="flex flex-col gap-3 rounded-3xl border border-line bg-surface p-5">
        <h2 className="font-bold">Scripts</h2>
        {scripts.length > 0 && (
          <div className="flex flex-wrap gap-2" role="tablist" aria-label="Scripts">
            {scripts.map((s) => (
              <button
                key={s.id}
                type="button"
                role="tab"
                aria-selected={s.id === script?.id}
                onClick={() => {
                  setSelected(s.id);
                  setEditing(null);
                  setConfirmDelete(false);
                }}
                className={`rounded-full px-4 py-1.5 text-sm font-semibold ${
                  s.id === script?.id ? "bg-accent text-white" : "border border-line"
                }`}
              >
                {s.name}
                {creators.length > 0 && (
                  <span className="ml-1 font-normal opacity-80">· {creatorName(s.creator_id) ?? "toutes"}</span>
                )}
                {s.id === defaultScript?.id && <span className="ml-1 font-normal opacity-80">· par défaut</span>}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={addScript} className="flex flex-wrap gap-2">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Nom d'un nouveau script"
            aria-label="Nom du nouveau script"
            className={`${input} min-w-0 ${creators.length > 0 ? "basis-full sm:basis-0" : ""} flex-1`}
          />
          {creators.length > 0 && (
            <CreatorSelect
              creators={creators}
              value={newFor}
              onChange={setNewFor}
              label="Créatrice du nouveau script"
              className="flex-1 sm:flex-none"
            />
          )}
          <button type="submit" disabled={!newName.trim()} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-50">
            Créer
          </button>
        </form>
        {script && (
          <ScriptHeader
            key={script.id}
            script={script}
            isFirst={script.id === scripts[0]?.id}
            isLast={script.id === scripts[scripts.length - 1]?.id}
            confirmDelete={confirmDelete}
            onConfirmDelete={setConfirmDelete}
            onRename={(name) => run(renameScript(script.id, name), "Script renommé.")}
            onMove={(d) => run(moveScript(script.id, d))}
            onDelete={async () => {
              if (await run(deleteScript(script.id), "Script supprimé.")) {
                setSelected(null);
                setConfirmDelete(false);
              }
            }}
          />
        )}
        {script && creators.length > 0 && (
          <label className="flex flex-wrap items-center gap-2 text-sm">
            <span className="font-semibold">Script de</span>
            <CreatorSelect
              creators={creators}
              value={script.creator_id ?? null}
              label="Créatrice du script"
              onChange={(id) =>
                run(
                  setScriptCreator(script.id, id),
                  id === null ? "Le script sert à toutes les créatrices." : `Script associé à ${creatorName(id)}.`,
                )
              }
            />
          </label>
        )}
        <p className="text-xs text-muted">
          L&apos;IA ne propose que les scripts de la créatrice qu&apos;elle incarne, ou ceux qui servent à toutes.
          Chaque personne suit le script choisi dans sa fiche (onglet Messages), sinon celui marqué « par défaut ».
        </p>
      </section>

      {/* Les étapes du script */}
      {script && (
        <section className="flex flex-col gap-3">
          <h2 className="font-bold">Messages de « {script.name} »</h2>
          {scriptSteps.length === 0 && editing !== "new" && (
            <p className="text-sm text-muted">Aucun message : ajoutez le premier contenu à proposer.</p>
          )}
          <ol className="flex flex-col gap-3">
            {scriptSteps.map((step, i) =>
              editing === step.id ? (
                <li key={step.id}>
                  <StepEditor
                    scriptId={script.id}
                    step={step}
                    onDone={(message) => {
                      setEditing(null);
                      setNotice(message);
                      router.refresh();
                    }}
                    onCancel={() => setEditing(null)}
                  />
                </li>
              ) : (
                <li key={step.id} className="flex flex-col gap-3 rounded-2xl border border-line bg-surface p-4 sm:flex-row sm:items-center">
                  <span className="min-w-0 flex-1">
                    <span className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-bold text-accent">Message {i + 1}</span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                          step.is_paid ? "bg-accent text-white" : "bg-accent-soft text-accent"
                        }`}
                      >
                        {step.is_paid ? `Payant · ${formatEuros(step.price_cents)}` : "Gratuit"}
                      </span>
                    </span>
                    <span className="block font-semibold">{step.title}</span>
                    <span className="block text-sm text-muted">
                      {summary(step)}
                      {step.is_paid && ` · de ${formatEuros(step.min_price_cents)} à ${formatEuros(step.max_price_cents)}`} ·
                      proposé par {step.trigger_mode === "ia" ? "l'IA" : "l'équipe"}
                    </span>
                    {step.message_text.trim() && (
                      <span className="mt-1 block text-sm">
                        <span className="text-muted">
                          {step.message_mode === "fixe" ? "L'IA envoie mot pour mot : " : "Consigne pour l'IA : "}
                        </span>
                        « {step.message_text.trim()} »
                      </span>
                    )}
                  </span>
                  <span className="flex shrink-0 flex-wrap gap-1">
                    <button type="button" aria-label="Monter" disabled={i === 0} onClick={() => run(moveStep(step.id, -1))} className="rounded-lg border border-line px-2 py-1 disabled:opacity-30">
                      ↑
                    </button>
                    <button
                      type="button"
                      aria-label="Descendre"
                      disabled={i === scriptSteps.length - 1}
                      onClick={() => run(moveStep(step.id, 1))}
                      className="rounded-lg border border-line px-2 py-1 disabled:opacity-30"
                    >
                      ↓
                    </button>
                    <button type="button" onClick={() => setEditing(step.id)} className="rounded-lg border border-line px-3 py-1 text-sm font-semibold">
                      Modifier
                    </button>
                    <button type="button" onClick={() => run(deleteStep(step.id), "Message supprimé.")} className="rounded-lg px-2 py-1 text-sm text-bad underline">
                      Supprimer
                    </button>
                  </span>
                </li>
              ),
            )}
          </ol>
          {editing === "new" ? (
            <StepEditor
              scriptId={script.id}
              step={null}
              onDone={(message) => {
                setEditing(null);
                setNotice(message);
                router.refresh();
              }}
              onCancel={() => setEditing(null)}
            />
          ) : (
            <button
              type="button"
              onClick={() => setEditing("new")}
              className="self-start rounded-full bg-accent px-4 py-2 text-sm font-bold text-white"
            >
              Ajouter un message au script
            </button>
          )}
        </section>
      )}

      {notice && (
        <p role="status" className="text-sm text-muted">
          {notice}
        </p>
      )}
    </div>
  );
}

function ScriptHeader({
  script,
  isFirst,
  isLast,
  confirmDelete,
  onConfirmDelete,
  onRename,
  onMove,
  onDelete,
}: {
  script: Script;
  isFirst: boolean;
  isLast: boolean;
  confirmDelete: boolean;
  onConfirmDelete: (v: boolean) => void;
  onRename: (name: string) => void;
  onMove: (d: -1 | 1) => void;
  onDelete: () => void;
}) {
  const [name, setName] = useState(script.name);
  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-line pt-3">
      <input value={name} onChange={(e) => setName(e.target.value)} aria-label="Nom du script" className={`${input} min-w-0 flex-1`} />
      <button type="button" disabled={name.trim() === script.name} onClick={() => onRename(name)} className="rounded-full border border-line px-3 py-1.5 text-sm font-semibold disabled:opacity-40">
        Renommer
      </button>
      <button type="button" aria-label="Monter le script" disabled={isFirst} onClick={() => onMove(-1)} className="rounded-lg border border-line px-2 py-1 disabled:opacity-30">
        ↑
      </button>
      <button type="button" aria-label="Descendre le script" disabled={isLast} onClick={() => onMove(1)} className="rounded-lg border border-line px-2 py-1 disabled:opacity-30">
        ↓
      </button>
      {confirmDelete ? (
        <button type="button" onClick={onDelete} className="rounded-full border border-bad px-3 py-1.5 text-sm font-bold text-bad">
          Confirmer la suppression
        </button>
      ) : (
        <button type="button" onClick={() => onConfirmDelete(true)} className="px-2 text-sm text-bad underline">
          Supprimer le script
        </button>
      )}
    </div>
  );
}

const ACCEPT = "image/jpeg,image/png,image/webp,image/gif,image/heic,video/mp4,video/quicktime,video/webm";

function StepEditor({
  scriptId,
  step,
  onDone,
  onCancel,
}: {
  scriptId: number;
  step: Step | null;
  onDone: (message: string) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<StepForm>({
    id: step?.id ?? null,
    script_id: scriptId,
    title: step?.title ?? "",
    content_text: step?.content_text ?? "",
    media: step?.media ?? [],
    ai_description: step?.ai_description ?? "",
    message_mode: step?.message_mode ?? "ia",
    message_text: step?.message_text ?? "",
    trigger_mode: step?.trigger_mode ?? "ia",
    is_paid: step?.is_paid ?? true,
    price: euros(step?.price_cents ?? 0),
    min_price: euros(step?.min_price_cents ?? 0),
    max_price: euros(step?.max_price_cents ?? 0),
  });
  // Aperçus : fichier local juste envoyé, ou lien signé de quelques minutes.
  const [previews, setPreviews] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const set = <K extends keyof StepForm>(key: K, value: StepForm[K]) => setForm((f) => ({ ...f, [key]: value }));
  const room = MAX_MEDIA - form.media.length;

  async function upload(files: File[]) {
    const list = files.slice(0, room);
    if (!list.length) return setStatus(`${MAX_MEDIA} photos ou vidéos au plus par message.`);
    setBusy(true);
    const added: MediaItem[] = [];
    let problem: string | null = null;
    for (const [i, file] of list.entries()) {
      setStatus(`Envoi ${i + 1} sur ${list.length}…`);
      const link = await uploadLink(file.type, file.size);
      if (!link.ok) {
        problem = `${file.name} : ${link.error}`;
        break;
      }
      const res = await fetch(link.url, {
        method: "PUT",
        headers: { "content-type": file.type, "x-upsert": "true" },
        body: file,
      }).catch(() => null);
      if (!res?.ok) {
        problem = `${file.name} n'a pas pu être envoyé. Réessayez.`;
        break;
      }
      const item: MediaItem = { path: link.path, kind: file.type.startsWith("video/") ? "video" : "image" };
      added.push(item);
      setPreviews((p) => ({ ...p, [item.path]: URL.createObjectURL(file) }));
    }
    setBusy(false);
    if (added.length) setForm((f) => ({ ...f, media: [...f.media, ...added] }));
    const skipped = files.length - list.length;
    setStatus(
      problem ??
        `${added.length} fichier${added.length > 1 ? "s" : ""} ajouté${added.length > 1 ? "s" : ""}.${
          skipped > 0 ? ` ${skipped} de trop (${MAX_MEDIA} au plus).` : ""
        } Pensez à enregistrer le message.`,
    );
  }

  async function showExisting() {
    for (const m of form.media) {
      if (previews[m.path]) continue;
      const link = await previewLink(m.path);
      if (link.ok) setPreviews((p) => ({ ...p, [m.path]: link.url }));
      else return setStatus(link.error);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const result = await saveStep(form);
    setBusy(false);
    if (result.ok) onDone(step ? "Message enregistré." : "Message ajouté au script.");
    else setStatus(result.error);
  }

  const hidden = form.media.some((m) => !previews[m.path]);
  return (
    <form onSubmit={submit} className="flex flex-col gap-4 rounded-2xl border-2 border-accent bg-surface p-4">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-semibold">Titre (visible uniquement par l&apos;équipe)</span>
        <input value={form.title} maxLength={120} onChange={(e) => set("title", e.target.value)} className={input} required />
      </label>

      <fieldset className="flex flex-col gap-3 text-sm">
        <legend className="mb-1 font-semibold">Ce que contient le message</legend>
        <div className="flex flex-col gap-2">
          <span>
            Photos et vidéos ({form.media.length} / {MAX_MEDIA})
          </span>
          {form.media.length > 0 && (
            <ul className="grid grid-cols-3 gap-2 sm:grid-cols-5">
              {form.media.map((m, i) => (
                <li key={m.path} className="relative aspect-square overflow-hidden rounded-xl border border-line bg-background">
                  {previews[m.path] ? (
                    m.kind === "video" ? (
                      <video src={previews[m.path]} muted playsInline className="size-full object-cover" />
                    ) : (
                      // eslint-disable-next-line @next/next/no-img-element -- aperçu local ou lien signé temporaire
                      <img src={previews[m.path]} alt={`Photo ${i + 1}`} className="size-full object-cover" />
                    )
                  ) : (
                    <span className="flex size-full items-center justify-center text-xs text-muted">
                      {m.kind === "video" ? "Vidéo" : "Photo"} {i + 1}
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => set("media", form.media.filter((x) => x.path !== m.path))}
                    aria-label={`Retirer ${m.kind === "video" ? "la vidéo" : "la photo"} ${i + 1}`}
                    className="absolute right-1 top-1 rounded-full bg-surface/90 px-2 text-sm font-bold"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
          {hidden && (
            <button type="button" onClick={showExisting} className="self-start text-sm underline">
              Voir les fichiers
            </button>
          )}
          {room > 0 && (
            <label
              className={`self-start rounded-full border border-line px-4 py-2 font-semibold focus-within:outline focus-within:outline-2 focus-within:outline-accent ${
                busy ? "opacity-60" : "cursor-pointer hover:border-accent"
              }`}
            >
              + Ajouter des photos ou des vidéos
              <input
                type="file"
                multiple
                accept={ACCEPT}
                disabled={busy}
                onChange={(e) => {
                  const files = Array.from(e.target.files ?? []);
                  e.target.value = "";
                  if (files.length) upload(files);
                }}
                className="sr-only"
              />
            </label>
          )}
        </div>
        <label className="flex flex-col gap-1">
          <span>Texte {form.media.length ? "(facultatif)" : ""}</span>
          <textarea
            value={form.content_text}
            onChange={(e) => set("content_text", e.target.value)}
            rows={4}
            maxLength={10000}
            placeholder="Le texte que la personne découvre avec le contenu : une lettre, une légende, un poème…"
            aria-label="Texte du message"
            className={input}
          />
        </label>
      </fieldset>

      <label className="flex flex-col gap-1 text-sm">
        <span className="font-semibold">À quoi ça ressemble (pour l&apos;IA)</span>
        <textarea
          value={form.ai_description}
          onChange={(e) => set("ai_description", e.target.value)}
          rows={3}
          maxLength={3000}
          placeholder="Ce que l'IA peut en dire, sans le montrer : « des photos du lac au coucher du soleil, prises depuis la terrasse »"
          className={input}
        />
      </label>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-1 font-semibold">Ce que l&apos;IA dit avec</legend>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.message_mode === "ia"} onChange={() => set("message_mode", "ia")} className="accent-[var(--accent)]" />
          L&apos;IA l&apos;écrit elle-même, en suivant votre consigne
        </label>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.message_mode === "fixe"} onChange={() => set("message_mode", "fixe")} className="accent-[var(--accent)]" />
          Mot pour mot : l&apos;IA envoie exactement ce texte
        </label>
        <textarea
          value={form.message_text}
          onChange={(e) => set("message_text", e.target.value)}
          rows={3}
          maxLength={2000}
          aria-label={form.message_mode === "fixe" ? "Texte envoyé mot pour mot" : "Consigne pour l'IA"}
          placeholder={
            form.message_mode === "fixe"
              ? "Le message exact qui accompagne l'offre"
              : "Facultatif. Ex. : dis que tu as pensé à lui en les prenant, et que c'est pour lui seul"
          }
          className={input}
        />
      </fieldset>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-1 font-semibold">Qui choisit le moment</legend>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.trigger_mode === "ia"} onChange={() => set("trigger_mode", "ia")} className="accent-[var(--accent)]" />
          L&apos;IA, quand la conversation s&apos;y prête (en mode automatique ou hybride)
        </label>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.trigger_mode === "equipe"} onChange={() => set("trigger_mode", "equipe")} className="accent-[var(--accent)]" />
          L&apos;équipe, depuis l&apos;onglet Messages
        </label>
      </fieldset>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-1 font-semibold">Prix</legend>
        <div className="flex gap-2">
          {(
            [
              [false, "Gratuit"],
              [true, "Payant"],
            ] as const
          ).map(([paid, label]) => (
            <label key={label} className={`rounded-full border px-4 py-1.5 ${form.is_paid === paid ? "border-accent bg-accent-soft" : "border-line"}`}>
              <input type="radio" name="prix" className="sr-only" checked={form.is_paid === paid} onChange={() => set("is_paid", paid)} />
              {label}
            </label>
          ))}
        </div>
        {form.is_paid ? (
          <>
            <div className="grid gap-2 sm:grid-cols-3">
              {(
                [
                  ["price", "Prix habituel (€)"],
                  ["min_price", "Minimum accepté (€)"],
                  ["max_price", "Maximum (€)"],
                ] as const
              ).map(([key, label]) => (
                <label key={key} className="flex flex-col gap-1">
                  <span>{label}</span>
                  <input value={form[key]} inputMode="decimal" onChange={(e) => set(key, e.target.value)} className={input} />
                </label>
              ))}
            </div>
            <p className="text-xs text-muted">
              L&apos;IA ou l&apos;équipe peuvent choisir un prix entre le minimum et le maximum ; il est alors affiché comme
              personnalisé. Une contre-offre sous le minimum est toujours refusée.
            </p>
          </>
        ) : (
          <p className="text-xs text-muted">Offert : la personne le reçoit directement, sans rien payer.</p>
        )}
      </fieldset>

      <div className="flex flex-wrap items-center gap-2">
        <button type="submit" disabled={busy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60">
          Enregistrer le message
        </button>
        <button type="button" onClick={onCancel} className="px-3 text-sm text-muted">
          Annuler
        </button>
        {status && (
          <p role="status" className="text-sm text-muted">
            {status}
          </p>
        )}
      </div>
    </form>
  );
}
