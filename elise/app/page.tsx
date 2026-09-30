import Link from "next/link";
import { redirect } from "next/navigation";
import { connection } from "next/server";
import { adminStatus } from "@/lib/admin";
import { loadProfile } from "@/lib/settings";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { signOut } from "./actions";
import { Notice, SetupNotice, missingSettings } from "./notice";

type Online = { id: number; nom: string; age: number | null; ville: string | null; profession: string | null };
type Last = { creator_id: number; role: "user" | "assistant"; content: string; created_at: string };

/** Messages relus pour montrer où en est chaque conversation. */
const RECENT = 300;

// L'accueil : choisir avec quelle créatrice parler. Chaque conversation est
// séparée des autres (messages, mémoire, contenus). Une seule créatrice en
// ligne : on va directement chez elle.
export default async function Home({ searchParams }: PageProps<"/">) {
  await connection(); // toujours calculée à la visite, jamais figée au déploiement
  if (missingSettings().length) return <SetupNotice />;
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) redirect("/connexion");

  // L'équipe arrive sur son tableau de bord, pas sur les conversations. Elle
  // peut tout de même les tester : /?vue=conversation.
  const isAdmin = (await adminStatus(supabase)) === "admin";
  const { vue } = await searchParams;
  if (isAdmin && vue !== "conversation") redirect("/admin");

  let online: Online[] = [];
  let recent: Last[] = [];
  let hasProfile = true;
  try {
    const [profile, list, messages] = await Promise.all([
      loadProfile(supabase, userId),
      supabase.rpc("creatrices_disponibles"),
      supabase
        .from("messages")
        .select("creator_id, role, content, created_at")
        .eq("user_id", userId)
        .order("id", { ascending: false })
        .limit(RECENT),
    ]);
    hasProfile = Boolean(profile);
    if (list.error) throw list.error;
    online = (list.data ?? []) as Online[];
    recent = (messages.data ?? []) as Last[];
  } catch (err) {
    console.error(err);
    return (
      <Notice title="Le site ne trouve pas ses souvenirs">
        <p>La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.</p>
        <p className="text-muted">Rechargez la page dans un instant.</p>
      </Notice>
    );
  }

  // Âge et prénom d'abord : le site est réservé aux personnes majeures.
  if (!hasProfile) redirect("/bienvenue");
  if (online.length === 1) redirect(`/c/${online[0].id}`);
  if (online.length === 0) {
    return (
      <Notice title="Personne n'est en ligne pour le moment">
        <p>Revenez un peu plus tard.</p>
      </Notice>
    );
  }

  // Les conversations déjà commencées d'abord, la plus récente en haut.
  const last = new Map<number, Last>();
  for (const m of recent) if (!last.has(Number(m.creator_id))) last.set(Number(m.creator_id), m);
  const sorted = [...online].sort((a, b) => {
    const la = last.get(a.id)?.created_at ?? "";
    const lb = last.get(b.id)?.created_at ?? "";
    return lb.localeCompare(la) || a.id - b.id;
  });

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-2xl flex-col gap-6 px-4 py-8">
      <header>
        <h1 className="font-serif text-3xl">Avec qui voulez-vous parler ?</h1>
        <p className="text-sm text-muted">
          Chacune est une intelligence artificielle. Chaque conversation est à part : ce que vous dites à l&apos;une,
          les autres ne le savent pas.
        </p>
      </header>
      <ul className="flex flex-col gap-3">
        {sorted.map((c) => {
          const m = last.get(c.id);
          const details = [c.age ? `${c.age} ans` : "", c.profession ?? "", c.ville ?? ""].filter(Boolean).join(" · ");
          return (
            <li key={c.id}>
              <Link
                href={`/c/${c.id}`}
                aria-label={`Parler avec ${c.nom}`}
                className="flex items-center gap-3 rounded-2xl border border-line bg-surface p-4 hover:bg-accent-soft"
              >
                <span aria-hidden className="flex size-12 shrink-0 items-center justify-center rounded-full bg-accent-soft font-serif text-xl text-accent">
                  {c.nom.charAt(0).toUpperCase()}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block font-semibold">
                    {c.nom} <span className="text-xs font-normal text-muted">· IA</span>
                  </span>
                  {details && <span className="block text-sm text-muted">{details}</span>}
                  <span className="block truncate text-sm text-muted">
                    {m ? `${m.role === "user" ? "Vous : " : ""}${m.content}` : "Nouvelle conversation"}
                  </span>
                </span>
                <span aria-hidden className="text-xl text-muted">
                  ›
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
      <form action={signOut} className="mt-auto text-center">
        <button type="submit" className="text-sm text-muted underline underline-offset-4">
          Se déconnecter
        </button>
      </form>
    </main>
  );
}
