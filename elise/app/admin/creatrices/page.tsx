import type { Metadata } from "next";
import Link from "next/link";
import { Notice } from "@/app/notice";
import type { PersonaProfile } from "@/lib/persona-profile";
import { adminGate } from "../gate";
import { CreatorList, type CreatorCard } from "./creator-list";

export const metadata: Metadata = { title: "Créatrices · Élise" };

// L'onglet Créatrices : les personnages que l'IA peut incarner. On en crée
// une, on remplit sa page, on valide ; l'onglet IA choisit laquelle est active.
export default async function CreatorsPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const [creators, settings, scripts] = await Promise.all([
    gate.supabase.from("creators").select("id, persona").order("id"),
    gate.supabase.from("ai_settings").select("creator_id").eq("id", 1).maybeSingle(),
    // « * » : creator_id n'existe qu'une fois schema.sql relancé.
    gate.supabase.from("scripts").select("*").order("position").order("id"),
  ]);
  if (creators.error || settings.error) {
    return (
      <Notice title="Les créatrices n'ont pas pu être chargées">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const active = settings.data?.creator_id === null || settings.data?.creator_id === undefined ? null : Number(settings.data.creator_id);
  const scriptRows = (scripts.data ?? []) as { name: string; creator_id?: number | null }[];
  const cards: CreatorCard[] = (creators.data ?? []).map((c) => {
    const p = (c.persona ?? {}) as PersonaProfile;
    return {
      id: Number(c.id),
      name: p.nom?.trim() || p.pseudo?.trim() || null,
      details: [p.age ? `${p.age} ans` : "", p.ville ?? "", p.profession ?? ""].filter(Boolean).join(" · "),
      active: Number(c.id) === active,
      scripts: scriptRows.filter((s) => s.creator_id != null && Number(s.creator_id) === Number(c.id)).map((s) => s.name),
    };
  });

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-serif text-3xl">Créatrices</h1>
          <p className="text-sm text-muted">
            Les personnages que l&apos;IA peut incarner. Touchez une créatrice pour reprendre sa page là où vous
            l&apos;avez laissée. Celle que l&apos;IA incarne se choisit dans l&apos;onglet IA.
          </p>
        </div>
        <Link href="/admin/creatrices/nouvelle" className="rounded-full bg-accent px-5 py-2.5 font-bold text-white">
          Créer une créatrice
        </Link>
      </header>
      <CreatorList creators={cards} />
    </div>
  );
}
