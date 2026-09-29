import type { SupabaseClient } from "@supabase/supabase-js";
import { notFound, redirect } from "next/navigation";
import { connection } from "next/server";
import { cache, type ReactNode } from "react";
import { Notice, SetupNotice, missingSettings } from "@/app/notice";
import { adminStatus } from "@/lib/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// La porte de l'espace de l'équipe : pour qui n'est pas administrateur, les
// pages n'existent pas. Chaque page la passe, en plus de la mise en page ;
// cache() fait qu'elle ne vérifie qu'une fois par requête.
export const adminGate = cache(async function adminGate(): Promise<
  { supabase: SupabaseClient; userId: string } | { node: ReactNode }
> {
  await connection();
  if (missingSettings().length) return { node: <SetupNotice /> };
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) redirect("/connexion");

  const status = await adminStatus(supabase);
  if (status === "schema_outdated") {
    return {
      node: (
        <Notice title="L'espace de l'équipe n'est pas prêt">
          <p>
            La base de données n&apos;est pas à jour : relancez le script supabase/schema.sql dans Supabase (SQL
            Editor), puis rechargez cette page.
          </p>
        </Notice>
      ),
    };
  }
  if (status !== "admin") notFound();
  return { supabase, userId };
});
