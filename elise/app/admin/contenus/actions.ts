"use server";

import { randomUUID } from "node:crypto";
import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
import { MAX_MEDIA, mainType, parseEuros, type MediaItem, type Step } from "@/lib/offers";
import { CONTENT_BUCKET, createAdminClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";

// L'onglet Contenus : les scripts de vente et leurs étapes, dans l'ordre.
// Chaque action vérifie qu'on est administrateur ; la base le revérifie.

type Result<T = object> = ({ ok: true } & T) | { ok: false; error: string };

async function adminClient() {
  const supabase = await createClient();
  await requireAdmin(supabase);
  return supabase;
}

function failure(err: unknown, fallback: string): { ok: false; error: string } {
  console.error(fallback, err);
  if (schemaOutdated(err)) return { ok: false, error: `${fallback.replace(/\.$/, "")} : ${SCHEMA_HINT}` };
  return { ok: false, error: fallback };
}

/** Une créatrice (son numéro) ou null : le script sert alors à toutes. */
const creatorOrNull = (value: unknown): number | null | undefined =>
  value === null ? null : Number.isSafeInteger(value) && (value as number) > 0 ? (value as number) : undefined;

export async function createScript(name: string, creatorId: number | null = null): Promise<Result<{ id: number }>> {
  try {
    const supabase = await adminClient();
    const clean = name.trim().slice(0, 120);
    if (!clean) return { ok: false, error: "Donnez un nom au script." };
    const creator = creatorOrNull(creatorId);
    if (creator === undefined) return { ok: false, error: "Créatrice inconnue. Rechargez la page." };
    const { data: last } = await supabase.from("scripts").select("position").order("position", { ascending: false }).limit(1);
    const position = ((last?.[0]?.position as number | undefined) ?? 0) + 1;
    // Sans créatrice, on n'écrit pas la colonne : la création marche même avant de relancer schema.sql.
    const row: { name: string; position: number; creator_id?: number } = { name: clean, position };
    if (creator !== null) row.creator_id = creator;
    const { data, error } = await supabase.from("scripts").insert(row).select("id").single();
    if (error) throw error;
    return { ok: true, id: data.id as number };
  } catch (err) {
    return failure(err, "Le script n'a pas été créé.");
  }
}

export async function renameScript(id: number, name: string): Promise<Result> {
  try {
    const supabase = await adminClient();
    const clean = name.trim().slice(0, 120);
    if (!clean) return { ok: false, error: "Donnez un nom au script." };
    const { error } = await supabase.from("scripts").update({ name: clean }).eq("id", id);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "Le script n'a pas été renommé.");
  }
}

/** Rattacher un script à une créatrice, ou le rendre à toutes (null). */
export async function setScriptCreator(id: number, creatorId: number | null): Promise<Result> {
  try {
    const supabase = await adminClient();
    const creator = creatorOrNull(creatorId);
    if (creator === undefined) return { ok: false, error: "Créatrice inconnue. Rechargez la page." };
    const { error } = await supabase.from("scripts").update({ creator_id: creator }).eq("id", id);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "Le script n'a pas été associé.");
  }
}

export async function deleteScript(id: number): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { data: steps } = await supabase.from("script_steps").select("media, media_path").eq("script_id", id);
    const { error } = await supabase.from("scripts").delete().eq("id", id);
    if (error) throw error;
    await removeMedia((steps ?? []).flatMap(stepFiles));
    return { ok: true };
  } catch (err) {
    return failure(err, "Le script n'a pas été supprimé.");
  }
}

/** Monter ou descendre un script ; le premier est celui de tout le monde par défaut. */
export async function moveScript(id: number, direction: -1 | 1): Promise<Result> {
  return swap("scripts", id, direction, null);
}

export async function moveStep(id: number, direction: -1 | 1): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { data } = await supabase.from("script_steps").select("script_id").eq("id", id).single();
    return swap("script_steps", id, direction, data?.script_id as number);
  } catch (err) {
    return failure(err, "L'ordre n'a pas changé.");
  }
}

async function swap(table: "scripts" | "script_steps", id: number, direction: -1 | 1, scriptId: number | null): Promise<Result> {
  try {
    const supabase = await adminClient();
    let query = supabase.from(table).select("id, position").order("position").order("id");
    if (scriptId !== null) query = query.eq("script_id", scriptId);
    const { data, error } = await query;
    if (error) throw error;
    const rows = data as { id: number; position: number }[];
    const i = rows.findIndex((r) => r.id === id);
    const j = i + direction;
    if (i < 0 || j < 0 || j >= rows.length) return { ok: true };
    [rows[i], rows[j]] = [rows[j], rows[i]];
    // Renumérote tout proprement : 1, 2, 3…
    for (const [index, row] of rows.entries()) {
      const { error: updateError } = await supabase.from(table).update({ position: index + 1 }).eq("id", row.id);
      if (updateError) throw updateError;
    }
    return { ok: true };
  } catch (err) {
    return failure(err, "L'ordre n'a pas changé.");
  }
}

export type StepForm = {
  id: number | null;
  script_id: number;
  title: string;
  content_text: string;
  media: MediaItem[];
  ai_description: string;
  message_mode: "ia" | "fixe";
  message_text: string;
  trigger_mode: "ia" | "equipe";
  is_paid: boolean;
  price: string;
  min_price: string;
  max_price: string;
};

export async function saveStep(form: StepForm): Promise<Result<{ step: Step }>> {
  try {
    const supabase = await adminClient();
    const title = form.title.trim();
    if (!title || title.length > 120) return { ok: false, error: "Donnez un titre au message (120 caractères au plus)." };
    const media = Array.isArray(form.media) ? form.media : [];
    if (media.length > MAX_MEDIA) return { ok: false, error: `${MAX_MEDIA} photos ou vidéos au plus par message.` };
    // Seulement des fichiers envoyés par uploadLink, dans le dossier privé.
    if (!media.every((m) => MEDIA_PATH.test(m.path) && (m.kind === "image" || m.kind === "video"))) {
      return { ok: false, error: "Un fichier n'est pas reconnu : renvoyez-le." };
    }
    if (!media.length && !form.content_text.trim()) {
      return { ok: false, error: "Ajoutez des photos ou des vidéos, ou écrivez un texte." };
    }
    if (form.message_mode === "fixe" && !form.message_text.trim()) {
      return { ok: false, error: "Écrivez le texte que l'IA doit envoyer mot pour mot, ou laissez-la l'écrire." };
    }
    let price = 0;
    let min = 0;
    let max = 0;
    if (form.is_paid) {
      const p = parseEuros(form.price);
      const lo = parseEuros(form.min_price || form.price);
      const hi = parseEuros(form.max_price || form.price);
      if (p === null || lo === null || hi === null) return { ok: false, error: "Prix illisibles : indiquez des montants en euros." };
      if (lo <= 0 || !(lo <= p && p <= hi)) {
        return { ok: false, error: "Il faut : 0 < minimum ≤ prix ≤ maximum." };
      }
      [price, min, max] = [p, lo, hi];
    }
    const row = {
      script_id: form.script_id,
      title,
      content_type: mainType(media),
      content_text: form.content_text.trim().slice(0, 10000),
      media: media.map((m) => ({ path: m.path, kind: m.kind })),
      media_path: null,
      ai_description: form.ai_description.trim().slice(0, 3000),
      message_mode: form.message_mode,
      message_text: form.message_text.trim().slice(0, 2000),
      trigger_mode: form.trigger_mode,
      is_paid: form.is_paid,
      price_cents: price,
      min_price_cents: min,
      max_price_cents: max,
    };
    if (form.id === null) {
      const { data: last } = await supabase
        .from("script_steps")
        .select("position")
        .eq("script_id", form.script_id)
        .order("position", { ascending: false })
        .limit(1);
      const position = ((last?.[0]?.position as number | undefined) ?? 0) + 1;
      const { data, error } = await supabase.from("script_steps").insert({ ...row, position }).select("*").single();
      if (error) throw error;
      return { ok: true, step: data as Step };
    }
    const { data: previous } = await supabase.from("script_steps").select("media, media_path").eq("id", form.id).single();
    const { data, error } = await supabase.from("script_steps").update(row).eq("id", form.id).select("*").single();
    if (error) throw error;
    // Les fichiers retirés du message quittent aussi le dossier privé.
    const kept = new Set(row.media.map((m) => m.path));
    await removeMedia(previous ? stepFiles(previous).filter((path) => !kept.has(path)) : []);
    return { ok: true, step: data as Step };
  } catch (err) {
    return failure(err, "Le message n'a pas été enregistré.");
  }
}

export async function deleteStep(id: number): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { data } = await supabase.from("script_steps").select("media, media_path").eq("id", id).single();
    const { error } = await supabase.from("script_steps").delete().eq("id", id);
    if (error) throw error;
    await removeMedia(data ? stepFiles(data) : []);
    return { ok: true };
  } catch (err) {
    return failure(err, "Le message n'a pas été supprimé.");
  }
}

/** Les fichiers d'un message du script (et celui de l'ancien format, s'il reste). */
function stepFiles(row: { media?: unknown; media_path?: unknown }): string[] {
  const media = Array.isArray(row.media) ? (row.media as MediaItem[]) : [];
  const paths = media.map((m) => m.path);
  if (typeof row.media_path === "string" && row.media_path) paths.push(row.media_path);
  return paths;
}

/** Les noms donnés par uploadLink : un identifiant au hasard et l'extension. */
const MEDIA_PATH = /^[0-9a-f-]{36}\.(jpg|png|webp|gif|heic|mp4|mov|webm)$/;

const EXTENSIONS: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
  "image/gif": "gif",
  "image/heic": "heic",
  "video/mp4": "mp4",
  "video/quicktime": "mov",
  "video/webm": "webm",
};

/** Un lien pour envoyer un fichier directement dans le dossier privé (50 Mo au plus). */
export async function uploadLink(contentType: string, size: number): Promise<Result<{ path: string; url: string }>> {
  try {
    await adminClient();
    const ext = EXTENSIONS[contentType];
    if (!ext) return { ok: false, error: "Format non pris en charge : photo (JPG, PNG, WebP, GIF, HEIC) ou vidéo (MP4, MOV, WebM)." };
    if (size > 50 * 1024 * 1024) return { ok: false, error: "Fichier trop lourd : 50 Mo au plus." };
    const path = `${randomUUID()}.${ext}`;
    const { data, error } = await createAdminClient().storage.from(CONTENT_BUCKET).createSignedUploadUrl(path);
    if (error) throw error;
    return { ok: true, path, url: data.signedUrl };
  } catch (err) {
    return failure(err, "L'envoi du fichier n'a pas pu commencer.");
  }
}

/** Un lien de lecture de quelques minutes, pour que l'équipe voie le fichier. */
export async function previewLink(path: string): Promise<Result<{ url: string }>> {
  try {
    await adminClient();
    const { data, error } = await createAdminClient().storage.from(CONTENT_BUCKET).createSignedUrl(path, 300);
    if (error) throw error;
    return { ok: true, url: data.signedUrl };
  } catch (err) {
    return failure(err, "Le fichier n'a pas pu être affiché.");
  }
}

async function removeMedia(paths: (string | null | undefined)[]) {
  const list = paths.filter((p): p is string => Boolean(p));
  if (!list.length) return;
  const { error } = await createAdminClient().storage.from(CONTENT_BUCKET).remove(list);
  if (error) console.error("Fichiers non supprimés :", error);
}
