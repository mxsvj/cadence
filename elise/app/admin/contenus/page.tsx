import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import type { Script, Step } from "@/lib/offers";
import { adminGate } from "../gate";
import { ContentEditor } from "./editor";

export const metadata: Metadata = { title: "Contenus · Élise" };

// L'onglet Contenus : les scripts de vente, étape par étape, dans l'ordre.
export default async function ContentsPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const [scripts, steps] = await Promise.all([
    gate.supabase.from("scripts").select("id, name, position").order("position").order("id"),
    gate.supabase.from("script_steps").select("*").order("position").order("id"),
  ]);
  if (scripts.error || steps.error) {
    return (
      <Notice title="Les contenus n'ont pas pu être chargés">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  return <ContentEditor scripts={scripts.data as Script[]} steps={steps.data as Step[]} />;
}
