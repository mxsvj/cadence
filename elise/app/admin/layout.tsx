import { adminGate } from "./gate";
import { AdminNav } from "./nav";

// L'espace de l'équipe : les onglets en bas de l'écran, comme dans une appli.
// Le bas de chaque page laisse la place à la barre (4 rem + marge de l'iPhone).
export default async function AdminLayout({ children }: LayoutProps<"/admin">) {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  return (
    <div className="flex min-h-dvh flex-col pt-[env(safe-area-inset-top)] pb-[calc(4rem+env(safe-area-inset-bottom))]">
      {children}
      <AdminNav />
    </div>
  );
}
