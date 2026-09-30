import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import { loadDashboard } from "@/lib/admin";
import { filtersFromParams, type DashboardData } from "@/lib/dashboard";
import { Dashboard } from "./dashboard";
import { adminGate } from "./gate";

export const metadata: Metadata = { title: "Tableau de bord · Élise" };

// Le tableau de bord des gains, réservé aux administrateurs : pour les
// autres, la page n'existe pas.
export default async function AdminPage({ searchParams }: PageProps<"/admin">) {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  // Les filtres choisis restent dans l'adresse : recharger la page les garde.
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(await searchParams)) if (typeof value === "string") params.set(key, value);
  const filters = filtersFromParams(params);

  let data: DashboardData | null = null;
  try {
    data = await loadDashboard(gate.supabase, filters);
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
  return <Dashboard initial={data} initialFilters={filters} />;
}
