import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { connection } from "next/server";
import { Notice, SetupNotice } from "@/app/notice";
import { adminStatus, loadDashboard } from "@/lib/admin";
import type { DashboardData } from "@/lib/dashboard";
import { supabaseEnv } from "@/lib/supabase/env";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { Dashboard } from "./dashboard";

export const metadata: Metadata = { title: "Tableau de bord · Élise" };

// Le tableau de bord des gains, réservé aux administrateurs : pour les
// autres, la page n'existe pas.
export default async function AdminPage() {
  await connection();
  if (!supabaseEnv()) return <SetupNotice />;
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) redirect("/connexion");

  const status = await adminStatus(supabase);
  if (status === "schema_outdated") {
    return (
      <Notice title="Le tableau de bord n'est pas prêt">
        <p>
          La base de données ne connaît pas encore le tableau de bord : relancez le script supabase/schema.sql dans
          Supabase (SQL Editor), puis rechargez cette page.
        </p>
      </Notice>
    );
  }
  if (status !== "admin") notFound();

  let data: DashboardData | null = null;
  try {
    data = await loadDashboard(supabase, null, 30);
  } catch (err) {
    console.error(err);
  }
  if (!data) {
    return (
      <Notice title="Les chiffres n'ont pas pu être chargés">
        <p>La base de données ne répond pas. Rechargez la page dans un instant.</p>
      </Notice>
    );
  }
  return <Dashboard initial={data} />;
}
