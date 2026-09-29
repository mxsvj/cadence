import type { Metadata } from "next";
import Link from "next/link";
import { signOut } from "@/app/actions";
import { Notice } from "@/app/notice";
import { currentModel } from "@/lib/llm";
import { cronSecret } from "@/lib/relances";
import { DEFAULT_SETTINGS, type AiSettings } from "@/lib/settings";
import { accessKey } from "@/lib/team-access";
import { adminGate } from "../gate";
import { ParametersForm } from "./parameters-form";

export const metadata: Metadata = { title: "Paramètres · Élise" };

const card = "flex flex-col gap-3 rounded-3xl border border-line bg-surface p-5";

// L'onglet Paramètres : les réglages fins de l'IA, les garde-fous de la vente,
// l'état du site et le compte de l'équipe.
export default async function ParametersPage() {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const { supabase } = gate;

  const [settings, claims] = await Promise.all([
    supabase.from("ai_settings").select("*").eq("id", 1).maybeSingle(),
    supabase.auth.getClaims(),
  ]);
  if (settings.error) {
    return (
      <Notice title="Les paramètres n'ont pas pu être chargés">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  const current: AiSettings = { ...DEFAULT_SETTINGS, ...(settings.data ?? {}) };
  const model = currentModel();
  const email = claims.data?.claims?.email as string | undefined;
  const linkReady = accessKey() !== null;
  const cronReady = cronSecret() !== null;

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6">
      <header>
        <h1 className="font-serif text-3xl">Paramètres</h1>
        <p className="text-sm text-muted">Les réglages fins de l&apos;IA, les garde-fous de la vente, et le compte de l&apos;équipe.</p>
      </header>

      <ParametersForm initial={current} />

      <section className={card} aria-labelledby="titre-site">
        <h2 id="titre-site" className="font-bold">
          Le site
        </h2>
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <dt className="text-muted">Modèle d&apos;IA</dt>
          <dd className="min-w-0 break-words">
            {model.provider === "claude" ? "Claude" : "Gemini"} · {model.model}
            {model.provider !== "claude" && (
              <span className="block text-xs text-muted">
                Offre gratuite : Google peut réutiliser les messages, conversations fictives uniquement.
              </span>
            )}
          </dd>
          <dt className="text-muted">Lien de l&apos;équipe</dt>
          <dd className="min-w-0">
            {linkReady ? (
              "Activé"
            ) : (
              <>
                Désactivé
                <span className="block text-xs text-muted">ADMIN_ACCESS_KEY manque dans Vercel (au moins 24 caractères).</span>
              </>
            )}
          </dd>
          <dt className="text-muted">Prendre des nouvelles</dt>
          <dd className="min-w-0">
            {!cronReady ? (
              <>
                Bloqué
                <span className="block text-xs text-muted">CRON_SECRET manque dans Vercel (au moins 16 caractères).</span>
              </>
            ) : current.relance_active ? (
              "Activé · chaque jour en fin d'après-midi"
            ) : (
              "Désactivé (réglage ci-dessus)"
            )}
          </dd>
        </dl>
      </section>

      <section className={card} aria-labelledby="titre-compte">
        <h2 id="titre-compte" className="font-bold">
          Compte
        </h2>
        {email && (
          <p className="text-sm">
            Connecté en tant que <strong className="break-all">{email}</strong>
          </p>
        )}
        <div className="flex flex-wrap gap-3">
          {/* Ce que voit une personne qui parle à l'IA, pour tester. */}
          <Link href="/?vue=conversation" className="rounded-full border border-line px-4 py-2 text-sm font-semibold">
            Tester la conversation
          </Link>
          <form action={signOut}>
            <button type="submit" className="rounded-full px-4 py-2 text-sm text-muted underline underline-offset-4">
              Se déconnecter
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
