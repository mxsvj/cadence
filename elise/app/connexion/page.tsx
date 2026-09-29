import { connection } from "next/server";
import { SetupNotice } from "@/app/notice";
import { supabaseEnv } from "@/lib/supabase/env";
import { AuthForm } from "./form";

// Les messages des liens qui ramènent ici (?erreur=…).
const ERRORS: Record<string, string> = {
  lien: "Ce lien n'est plus valable. Connectez-vous, ou recommencez l'inscription.",
  acces: "Ce lien d'accès n'est pas valable.",
  equipe:
    "Le lien de l'équipe est prêt, mais aucun compte administrateur n'existe encore : inscrivez-vous, puis exécutez supabase/admin.sql dans Supabase.",
  "acces-panne": "Le lien de l'équipe n'a pas pu ouvrir la session. Réessayez dans un instant.",
};

export default async function ConnexionPage({ searchParams }: PageProps<"/connexion">) {
  await connection();
  if (!supabaseEnv()) return <SetupNotice />;
  const { erreur } = await searchParams;
  const message = typeof erreur === "string" && Object.hasOwn(ERRORS, erreur) ? ERRORS[erreur] : null;

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center gap-8 px-6 py-12">
      <header className="text-center">
        <h1 className="font-serif text-5xl text-accent">Élise</h1>
        <p className="mt-3 text-muted">Quelqu&apos;un à qui parler, qui se souvient de vous.</p>
      </header>

      {message && (
        <p role="alert" className="rounded-2xl bg-accent-soft px-4 py-3 text-sm">
          {message}
        </p>
      )}

      <AuthForm />

      <p className="text-center text-xs leading-relaxed text-muted">
        Élise est une intelligence artificielle.
        <br />
        Prototype de test : n&apos;y écrivez que des conversations fictives.
      </p>
    </main>
  );
}
