"use server";

import { randomUUID } from "node:crypto";
import { requireAdmin } from "@/lib/admin";
import { parseEuros, type ContentType, type Step } from "@/lib/offers";
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
  return { ok: false, error: fallback };
}

export async function createScript(name: string): Promise<Result<{ id: number }>> {
  try {
    const supabase = await adminClient();
    const clean = name.trim().slice(0, 120);
    if (!clean) return { ok: false, error: "Donnez un nom au script." };
    const { data: last } = await supabase.from("scripts").select("position").order("position", { ascending: false }).limit(1);
    const position = ((last?.[0]?.position as number | undefined) ?? 0) + 1;
    const { data, error } = await supabase.from("scripts").insert({ name: clean, position }).select("id").single();
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

export async function deleteScript(id: number): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { data: steps } = await supabase.from("script_steps").select("media_path").eq("script_id", id);
    const { error } = await supabase.from("scripts").delete().eq("id", id);
    if (error) throw error;
    await removeMedia((steps ?? []).map((s) => s.media_path as string | null));
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
  content_type: ContentType;
  content_text: string;
  media_path: string | null;
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
    if (!title || title.length > 120) return { ok: false, error: "Donnez un titre à l'étape (120 caractères au plus)." };
    if (!["image", "video", "texte"].includes(form.content_type)) return { ok: false, error: "Type de contenu inconnu." };
    if (form.content_type === "texte" && !form.content_text.trim()) return { ok: false, error: "Écrivez le texte à vendre." };
    if (form.content_type !== "texte" && !form.media_path) return { ok: false, error: "Ajoutez le fichier à vendre." };
    if (form.message_mode === "fixe" && !form.message_text.trim()) {
      return { ok: false, error: "Écrivez le message qui accompagne l'offre, ou laissez l'IA l'écrire." };
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
      content_type: form.content_type,
      content_text: form.content_type === "texte" ? form.content_text : form.content_text.slice(0, 10000),
      media_path: form.content_type === "texte" ? null : form.media_path,
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
    const { data: previous } = await supabase.from("script_steps").select("media_path").eq("id", form.id).single();
    const { data, error } = await supabase.from("script_steps").update(row).eq("id", form.id).select("*").single();
    if (error) throw error;
    if (previous?.media_path && previous.media_path !== row.media_path) await removeMedia([previous.media_path as string]);
    return { ok: true, step: data as Step };
  } catch (err) {
    return failure(err, "L'étape n'a pas été enregistrée.");
  }
}

export async function deleteStep(id: number): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { data } = await supabase.from("script_steps").select("media_path").eq("id", id).single();
    const { error } = await supabase.from("script_steps").delete().eq("id", id);
    if (error) throw error;
    await removeMedia([data?.media_path as string | null]);
    return { ok: true };
  } catch (err) {
    return failure(err, "L'étape n'a pas été supprimée.");
  }
}

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
