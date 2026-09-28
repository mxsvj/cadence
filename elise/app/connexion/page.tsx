import { connection } from "next/server";
import { SetupNotice } from "@/app/notice";
import { supabaseEnv } from "@/lib/supabase/env";
import { AuthForm } from "./form";

export default async function ConnexionPage({ searchParams }: PageProps<"/connexion">) {
  await connection();
  if (!supabaseEnv()) return <SetupNotice />;
  const { erreur } = await searchParams;

  return (
    <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center gap-8 px-6 py-12">
      <header className="text-center">
        <h1 className="font-serif text-5xl text-accent">Élise</h1>
        <p className="mt-3 text-muted">Quelqu&apos;un à qui parler, qui se souvient de vous.</p>
      </header>

      {erreur === "lien" && (
        <p role="alert" className="rounded-2xl bg-accent-soft px-4 py-3 text-sm">
          Ce lien n&apos;est plus valable. Connectez-vous, ou recommencez l&apos;inscription.
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
