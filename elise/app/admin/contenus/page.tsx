import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import type { Script, Step } from "@/lib/offers";
import type { PersonaProfile } from "@/lib/persona-profile";
import { adminGate } from "../gate";
import { ContentEditor } from "./editor";

export const metadata: Metadata = { title: "Contenus · Élise" };

// L'onglet Contenus : les scripts de vente, étape par étape, dans l'ordre.
export default async function ContentsPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const [scripts, steps, creators] = await Promise.all([
    // « * » : creator_id n'existe qu'une fois schema.sql relancé.
    gate.supabase.from("scripts").select("*").order("position").order("id"),
    gate.supabase.from("script_steps").select("*").order("position").order("id"),
    gate.supabase.from("creators").select("id, persona").order("id"),
  ]);
  if (scripts.error || steps.error) {
    return (
      <Notice title="Les contenus n'ont pas pu être chargés">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const creatorList = (creators.data ?? []).map((c) => {
    const p = (c.persona ?? {}) as PersonaProfile;
    return { id: Number(c.id), name: p.nom?.trim() || p.pseudo?.trim() || "Sans prénom" };
  });
  return (
    <ContentEditor
      scripts={(scripts.data as Script[]).map((s) => ({ ...s, creator_id: s.creator_id == null ? null : Number(s.creator_id) }))}
      steps={steps.data as Step[]}
      creators={creatorList}
    />
  );
}
