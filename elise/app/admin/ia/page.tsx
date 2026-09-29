import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import type { PersonaProfile } from "@/lib/persona-profile";
import type { AiMode } from "@/lib/settings";
import { adminGate } from "../gate";
import { AiSettingsForm } from "./settings-form";

export const metadata: Metadata = { title: "IA · Élise" };

// L'onglet IA : qui répond, et quelle créatrice l'IA incarne.
export default async function AiPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const { supabase } = gate;

  const [settings, creators] = await Promise.all([
    supabase.from("ai_settings").select("mode, creator_id").eq("id", 1).maybeSingle(),
    supabase.from("creators").select("id, persona").order("id"),
  ]);
  if (settings.error || creators.error) {
    return (
      <Notice title="Les réglages n'ont pas pu être chargés">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const list = (creators.data ?? []).map((c) => {
    const p = (c.persona ?? {}) as PersonaProfile;
    return { id: Number(c.id), name: p.nom?.trim() || p.pseudo?.trim() || "Sans prénom", details: [p.age ? `${p.age} ans` : "", p.ville ?? ""].filter(Boolean).join(" · ") };
  });
  const creatorId = settings.data?.creator_id === null || settings.data?.creator_id === undefined ? null : Number(settings.data.creator_id);
  return (
    <AiSettingsForm
      mode={(settings.data?.mode ?? "auto") as AiMode}
      creatorId={creatorId}
      creators={list}
    />
  );
}
