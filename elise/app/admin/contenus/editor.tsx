"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { formatEuros } from "@/lib/dashboard";
import type { ContentType, Script, Step } from "@/lib/offers";
import {
  createScript,
  deleteScript,
  deleteStep,
  moveScript,
  moveStep,
  previewLink,
  renameScript,
  saveStep,
  uploadLink,
  type StepForm,
} from "./actions";

const input = "rounded-xl border border-line bg-surface px-3 py-2 outline-none focus:border-accent";
const TYPE_LABEL: Record<ContentType, string> = { image: "Photo", video: "Vidéo", texte: "Texte" };
const euros = (cents: number) => (cents ? (cents / 100).toFixed(2).replace(".", ",") : "");

export function ContentEditor({ scripts, steps }: { scripts: Script[]; steps: Step[] }) {
  const router = useRouter();
  const [selected, setSelected] = useState<number | null>(scripts[0]?.id ?? null);
  const [newName, setNewName] = useState("");
  const [editing, setEditing] = useState<number | "new" | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const script = scripts.find((s) => s.id === selected) ?? scripts[0] ?? null;
  const scriptSteps = steps.filter((s) => s.script_id === script?.id);

  async function run(action: Promise<{ ok: boolean; error?: string }>, done?: string) {
    const result = await action;
    setNotice(result.ok ? (done ?? null) : (result.error ?? "L'opération n'a pas abouti."));
    router.refresh();
    return result.ok;
  }

  async function addScript(e: React.FormEvent) {
    e.preventDefault();
    const result = await createScript(newName);
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
          Des scripts de vente, étape par étape. L&apos;IA ne propose jamais que l&apos;étape suivante, dans cet ordre,
          jamais sous le prix minimum. Les titres ne sont visibles que de l&apos;équipe.
        </p>
      </header>

      {/* Les scripts */}
      <section className="flex flex-col gap-3 rounded-3xl border border-line bg-surface p-5">
        <h2 className="font-bold">Scripts</h2>
        {scripts.length > 0 && (
          <div className="flex flex-wrap gap-2" role="tablist" aria-label="Scripts">
            {scripts.map((s, i) => (
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
                {i === 0 && <span className="ml-1 font-normal opacity-80">· par défaut</span>}
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
            className={`${input} min-w-0 flex-1`}
          />
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
        <p className="text-xs text-muted">
          Chaque personne suit le script choisi dans sa fiche (onglet Messages), sinon le premier de la liste.
        </p>
      </section>

      {/* Les étapes du script */}
      {script && (
        <section className="flex flex-col gap-3">
          <h2 className="font-bold">Étapes de « {script.name} »</h2>
          {scriptSteps.length === 0 && editing !== "new" && (
            <p className="text-sm text-muted">Aucune étape : ajoutez le premier contenu à proposer.</p>
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
                <li key={step.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-line bg-surface p-4">
                  <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-accent-soft font-bold text-accent">
                    {i + 1}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block font-semibold">{step.title}</span>
                    <span className="block text-sm text-muted">
                      {TYPE_LABEL[step.content_type]} ·{" "}
                      {step.is_paid
                        ? `${formatEuros(step.price_cents)} (de ${formatEuros(step.min_price_cents)} à ${formatEuros(step.max_price_cents)})`
                        : "Gratuit"}{" "}
                      · proposé par {step.trigger_mode === "ia" ? "l'IA" : "l'équipe"} · message{" "}
                      {step.message_mode === "ia" ? "écrit par l'IA" : "fixe"}
                    </span>
                  </span>
                  <span className="flex shrink-0 gap-1">
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
                    <button type="button" onClick={() => run(deleteStep(step.id), "Étape supprimée.")} className="rounded-lg px-2 py-1 text-sm text-bad underline">
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
              Ajouter une étape
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
    content_type: step?.content_type ?? "image",
    content_text: step?.content_text ?? "",
    media_path: step?.media_path ?? null,
    ai_description: step?.ai_description ?? "",
    message_mode: step?.message_mode ?? "ia",
    message_text: step?.message_text ?? "",
    trigger_mode: step?.trigger_mode ?? "ia",
    is_paid: step?.is_paid ?? true,
    price: euros(step?.price_cents ?? 0),
    min_price: euros(step?.min_price_cents ?? 0),
    max_price: euros(step?.max_price_cents ?? 0),
  });
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const set = <K extends keyof StepForm>(key: K, value: StepForm[K]) => setForm((f) => ({ ...f, [key]: value }));

  async function upload(file: File) {
    setBusy(true);
    setStatus("Envoi du fichier…");
    const link = await uploadLink(file.type, file.size);
    if (!link.ok) {
      setBusy(false);
      return setStatus(link.error);
    }
    const res = await fetch(link.url, {
      method: "PUT",
      headers: { "content-type": file.type, "x-upsert": "true" },
      body: file,
    }).catch(() => null);
    setBusy(false);
    if (!res?.ok) return setStatus("Le fichier n'a pas pu être envoyé. Réessayez.");
    set("media_path", link.path);
    set("content_type", file.type.startsWith("video/") ? "video" : "image");
    setPreview(URL.createObjectURL(file));
    setStatus("Fichier envoyé. Pensez à enregistrer l'étape.");
  }

  async function showExisting() {
    if (!form.media_path) return;
    const link = await previewLink(form.media_path);
    if (link.ok) setPreview(link.url);
    else setStatus(link.error);
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const result = await saveStep(form);
    setBusy(false);
    if (result.ok) onDone(step ? "Étape enregistrée." : "Étape ajoutée.");
    else setStatus(result.error);
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4 rounded-2xl border-2 border-accent bg-surface p-4">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-semibold">Titre (visible uniquement par l&apos;équipe)</span>
        <input value={form.title} maxLength={120} onChange={(e) => set("title", e.target.value)} className={input} required />
      </label>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-1 font-semibold">Ce qui est vendu</legend>
        <div className="flex gap-2">
          {(["image", "video", "texte"] as ContentType[]).map((t) => (
            <label key={t} className={`rounded-full border px-3 py-1.5 ${form.content_type === t ? "border-accent bg-accent-soft" : "border-line"}`}>
              <input type="radio" name="type" className="sr-only" checked={form.content_type === t} onChange={() => set("content_type", t)} />
              {TYPE_LABEL[t]}
            </label>
          ))}
        </div>
        {form.content_type === "texte" ? (
          <textarea
            value={form.content_text}
            onChange={(e) => set("content_text", e.target.value)}
            rows={5}
            maxLength={10000}
            placeholder="Le texte que la personne découvrira après l'achat"
            aria-label="Texte à vendre"
            className={input}
          />
        ) : (
          <div className="flex flex-col gap-2">
            <input
              type="file"
              accept={form.content_type === "video" ? "video/mp4,video/quicktime,video/webm" : "image/jpeg,image/png,image/webp,image/gif,image/heic"}
              onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
              aria-label="Fichier à vendre"
              className="text-sm"
            />
            {form.media_path && !preview && (
              <button type="button" onClick={showExisting} className="self-start text-sm underline">
                Voir le fichier actuel
              </button>
            )}
            {preview &&
              (form.content_type === "video" ? (
                <video src={preview} controls className="max-h-60 rounded-xl" />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element -- aperçu local ou lien signé temporaire
                <img src={preview} alt="Aperçu du contenu" className="max-h-60 self-start rounded-xl" />
              ))}
          </div>
        )}
      </fieldset>

      <label className="flex flex-col gap-1 text-sm">
        <span className="font-semibold">À quoi ça ressemble (pour l&apos;IA)</span>
        <textarea
          value={form.ai_description}
          onChange={(e) => set("ai_description", e.target.value)}
          rows={3}
          maxLength={3000}
          placeholder="Ce que l'IA peut en dire, sans le montrer : « une photo du lac au coucher du soleil, prise depuis la terrasse »"
          className={input}
        />
      </label>

      <fieldset className="flex flex-col gap-2 text-sm">
        <legend className="mb-1 font-semibold">Le message qui accompagne l&apos;offre</legend>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.message_mode === "ia"} onChange={() => set("message_mode", "ia")} className="accent-[var(--accent)]" />
          Écrit par l&apos;IA, dans le fil de la conversation
        </label>
        <label className="flex items-center gap-2">
          <input type="radio" checked={form.message_mode === "fixe"} onChange={() => set("message_mode", "fixe")} className="accent-[var(--accent)]" />
          Un texte fixe, écrit par l&apos;équipe
        </label>
        {form.message_mode === "fixe" && (
          <textarea value={form.message_text} onChange={(e) => set("message_text", e.target.value)} rows={3} maxLength={2000} aria-label="Message fixe" className={input} />
        )}
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
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.is_paid} onChange={(e) => set("is_paid", e.target.checked)} className="size-4 accent-[var(--accent)]" />
          Payant (sinon, offert)
        </label>
        {form.is_paid && (
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
        )}
        <p className="text-xs text-muted">
          L&apos;IA ou l&apos;équipe peuvent choisir un prix entre le minimum et le maximum ; il est alors affiché comme
          personnalisé. Une contre-offre sous le minimum est toujours refusée.
        </p>
      </fieldset>

      <div className="flex flex-wrap items-center gap-2">
        <button type="submit" disabled={busy} className="rounded-full bg-accent px-4 py-2 text-sm font-bold text-white disabled:opacity-60">
          Enregistrer l&apos;étape
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
