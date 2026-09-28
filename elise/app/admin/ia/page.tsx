import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import { languageOptions } from "@/lib/persona-profile";
import { DEFAULT_SETTINGS, type AiSettings } from "@/lib/settings";
import { adminGate } from "../gate";
import { AiSettingsForm, type PersonRow } from "./settings-form";

export const metadata: Metadata = { title: "IA · Élise" };

// L'onglet IA : le mode, le personnage, les paramètres, et les réglages par personne.
export default async function AiPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const { supabase } = gate;

  const [settings, profiles, contacts] = await Promise.all([
    supabase.from("ai_settings").select("*").eq("id", 1).maybeSingle(),
    supabase.from("profiles").select("user_id, display_name").order("display_name"),
    supabase.from("contacts").select("user_id, ai_enabled, emojis"),
  ]);
  if (settings.error || profiles.error || contacts.error) {
    return (
      <Notice title="Les réglages n'ont pas pu être chargés">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const byUser = new Map((contacts.data ?? []).map((c) => [c.user_id as string, c]));
  const people: PersonRow[] = (profiles.data ?? []).map((p) => ({
    user_id: p.user_id as string,
    name: p.display_name as string,
    ai_enabled: (byUser.get(p.user_id)?.ai_enabled as boolean | undefined) ?? true,
    emojis: (byUser.get(p.user_id)?.emojis as string | undefined) ?? "",
  }));
  const current: AiSettings = { ...DEFAULT_SETTINGS, ...(settings.data ?? {}) };
  current.temperature = Number(current.temperature);

  return <AiSettingsForm initial={current} people={people} languages={languageOptions()} />;
}
