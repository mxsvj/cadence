import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import { languageOptions } from "@/lib/persona-profile";
import { adminGate } from "../../gate";
import { CreatorForm, type PersonRow } from "../creator-form";
import { loadPeople } from "../load";

export const metadata: Metadata = { title: "Nouvelle créatrice · Élise" };

// « Créer une créatrice » : la page complète s'ouvre tout de suite (le nom se
// remplit dans le profil), puis « Valider ».
export default async function NewCreatorPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  let people: PersonRow[] | null = null;
  try {
    people = await loadPeople(gate.supabase, null);
  } catch (err) {
    console.error(err);
  }
  if (!people) {
    return (
      <Notice title="La page n'a pas pu être chargée">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  return <CreatorForm creator={{ id: null, persona: {}, first_message: "" }} people={people} languages={languageOptions()} />;
}
