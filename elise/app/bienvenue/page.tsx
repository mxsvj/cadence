import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { connection } from "next/server";
import { SetupNotice, missingSettings } from "@/app/notice";
import { loadProfile } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";
import { ProfileForm } from "./form";

export const metadata: Metadata = { title: "Bienvenue · Élise" };

// Avant la première conversation : prénom et âge (18 ans minimum).
export default async function WelcomePage() {
  await connection();
  if (missingSettings().length) return <SetupNotice />;
  const supabase = await createClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/connexion");
  if (await loadProfile(supabase, data.user.id).catch(() => null)) redirect("/");

  const meta = data.user.user_metadata as { display_name?: string; birthdate?: string };
  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center gap-8 px-6 py-12">
      <header className="text-center">
        <h1 className="font-serif text-4xl text-accent">Bienvenue</h1>
        <p className="mt-3 text-muted">Avant de commencer, deux informations. Élise est réservée aux personnes majeures.</p>
      </header>
      <ProfileForm name={meta.display_name} birthdate={meta.birthdate} />
    </main>
  );
}
