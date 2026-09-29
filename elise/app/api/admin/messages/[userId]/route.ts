import { NextResponse } from "next/server";
import { requireAdmin } from "@/lib/admin";
import { loadThread } from "@/lib/team";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Une conversation (une personne, la créatrice `c`), avec la fiche de la
// personne et ses offres.
export async function GET(request: Request, ctx: RouteContext<"/api/admin/messages/[userId]">) {
  const { userId } = await ctx.params;
  const creatorId = Number(new URL(request.url).searchParams.get("c"));
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });
  try {
    await requireAdmin(supabase);
  } catch {
    return NextResponse.json({ error: "Introuvable." }, { status: 404 });
  }
  if (!/^[0-9a-f-]{36}$/i.test(userId) || !Number.isSafeInteger(creatorId) || creatorId <= 0) {
    return NextResponse.json({ error: "Introuvable." }, { status: 404 });
  }
  try {
    const thread = await loadThread(supabase, userId, creatorId);
    if (!thread) return NextResponse.json({ error: "Introuvable." }, { status: 404 });
    return NextResponse.json(thread, { headers: { "cache-control": "no-store" } });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "La conversation n'a pas pu être chargée." }, { status: 500 });
  }
}
