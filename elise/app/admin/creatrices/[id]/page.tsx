import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Notice } from "@/app/notice";
import { languageOptions, type PersonaProfile } from "@/lib/persona-profile";
import { adminGate } from "../../gate";
import { CreatorForm, type CreatorDraft, type PersonRow } from "../creator-form";
import { loadPeople } from "../load";

export const metadata: Metadata = { title: "Créatrice · Élise" };

// Modifier une créatrice : la même page que pour la créer, déjà remplie.
export default async function CreatorPage({ params }: PageProps<"/admin/creatrices/[id]">) {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const id = Number((await params).id);
  if (!Number.isSafeInteger(id) || id <= 0) notFound();

  const { data, error } = await gate.supabase.from("creators").select("id, persona, first_message").eq("id", id).maybeSingle();
  if (!error && !data) notFound();
  let people: PersonRow[] | null = null;
  if (!error) {
    try {
      people = await loadPeople(gate.supabase, id);
    } catch (err) {
      console.error(err);
    }
  }
  if (error || !data || !people) {
    return (
      <Notice title="La créatrice n'a pas pu être chargée">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const creator: CreatorDraft = {
    id,
    persona: (data.persona ?? {}) as PersonaProfile,
    first_message: (data.first_message as string) ?? "",
  };
  return <CreatorForm creator={creator} people={people} languages={languageOptions()} />;
}
