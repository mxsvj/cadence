import { NextResponse } from "next/server";
import { requireAdmin } from "@/lib/admin";
import { loadInbox } from "@/lib/team";
import { createClient, currentUserId } from "@/lib/supabase/server";

// La liste des conversations, redemandée régulièrement par l'onglet Messages.
export async function GET() {
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });
  try {
    await requireAdmin(supabase);
  } catch {
    return NextResponse.json({ error: "Introuvable." }, { status: 404 });
  }
  try {
    return NextResponse.json(await loadInbox(supabase), { headers: { "cache-control": "no-store" } });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Les conversations n'ont pas pu être chargées." }, { status: 500 });
  }
}
