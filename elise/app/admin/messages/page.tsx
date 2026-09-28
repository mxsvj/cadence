import type { Metadata } from "next";
import { Notice } from "@/app/notice";
import { loadInbox } from "@/lib/team";
import { adminGate } from "../gate";
import { Inbox } from "./inbox";

export const metadata: Metadata = { title: "Messages · Élise" };

// La messagerie de l'équipe : toutes les conversations, comme dans une
// application de messagerie, et la fiche de chaque personne.
export default async function MessagesPage({ searchParams }: PageProps<"/admin/messages">) {
  const gate = await adminGate();
  if ("node" in gate) return gate.node;
  const { u } = await searchParams;

  let inbox: Awaited<ReturnType<typeof loadInbox>> | null = null;
  try {
    inbox = await loadInbox(gate.supabase);
  } catch (err) {
    console.error(err);
  }
  if (!inbox) {
    return (
      <Notice title="Les conversations n'ont pas pu être chargées">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
      </Notice>
    );
  }
  return <Inbox initial={inbox} initialUser={typeof u === "string" && /^[0-9a-f-]{36}$/i.test(u) ? u : null} />;
}
