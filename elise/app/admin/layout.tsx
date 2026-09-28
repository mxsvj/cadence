import { adminGate } from "./gate";
import { AdminNav } from "./nav";

// L'espace de l'équipe : une barre d'onglets au-dessus de chaque page.
export default async function AdminLayout({ children }: LayoutProps<"/admin">) {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  return (
    <div className="flex min-h-dvh flex-col">
      <AdminNav />
      {children}
    </div>
  );
}
