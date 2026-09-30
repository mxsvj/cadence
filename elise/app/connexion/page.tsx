import { connection } from "next/server";
import { SetupNotice } from "@/app/notice";
import { supabaseEnv } from "@/lib/supabase/env";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { CodeForm } from "./code-form";
import { AuthForm } from "./form";

// Les messages des liens qui ramènent ici (?erreur=…).
const ERRORS: Record<string, string> = {
  lien: "Ce lien n'est plus valable. Connectez-vous, ou recommencez l'inscription.",
};

export default async function ConnexionPage({ searchParams }: PageProps<"/connexion">) {
  await connection();
  if (!supabaseEnv()) return <SetupNotice />;
  const { erreur, code } = await searchParams;
  const message = typeof erreur === "string" && Object.hasOwn(ERRORS, erreur) ? ERRORS[erreur] : null;
  // Déjà connecté (seulement possible avec un lien ?code=…) : le code ouvre un autre compte.
  const signedIn = typeof code === "string" && (await currentUserId(await createClient())) !== null;

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

      {signedIn && (
        <p role="status" className="rounded-2xl border border-line px-4 py-3 text-sm">
          Vous êtes déjà connecté. Entrer avec ce code vous fait changer de compte : vous serez déconnecté du vôtre.
        </p>
      )}

      {/* Les clients entrent avec leur code ; l'équipe, avec son e-mail. */}
      <CodeForm initialCode={typeof code === "string" ? code.slice(0, 20) : undefined} />

      <details className="group rounded-2xl border border-line px-4 py-3">
        <summary className="cursor-pointer text-sm text-muted">Accès de l&apos;équipe (e-mail et mot de passe)</summary>
        <div className="mt-4">
          <AuthForm />
        </div>
      </details>

      <p className="text-center text-xs leading-relaxed text-muted">
        Élise est une intelligence artificielle.
        <br />
        Prototype de test : n&apos;y écrivez que des conversations fictives.
      </p>
    </main>
  );
}
