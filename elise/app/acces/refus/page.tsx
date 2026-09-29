import Link from "next/link";
import { Notice } from "@/app/notice";
import { MIN_ACCESS_KEY } from "@/lib/team-access";

// Pourquoi le lien de l'équipe n'a pas ouvert le tableau de bord. Une page à
// part : elle s'affiche même à qui est déjà connecté (la page de connexion,
// elle, renverrait vers la conversation et le message se perdrait).
const REASONS: Record<string, string> = {
  cle: "Ce lien d'accès n'est pas valable. Vérifiez qu'il a été copié en entier.",
  absente: `Le lien de l'équipe n'est pas encore activé sur ce site : la variable ADMIN_ACCESS_KEY (au moins ${MIN_ACCESS_KEY} caractères) manque dans Vercel, ou le site n'a pas été redéployé depuis qu'elle a été ajoutée.`,
  equipe:
    "Aucun compte administrateur n'existe encore. Inscrivez-vous sur le site, puis exécutez supabase/admin.sql dans Supabase (SQL Editor) avec l'adresse de ce compte, et rouvrez ce lien.",
  panne: "La session n'a pas pu s'ouvrir. Réessayez dans un instant.",
};

export default async function AccessRefused({ searchParams }: PageProps<"/acces/refus">) {
  const { raison } = await searchParams;
  const message = typeof raison === "string" && Object.hasOwn(REASONS, raison) ? REASONS[raison] : REASONS.cle;
  return (
    <Notice title="Le lien de l'équipe n'a pas marché">
      <p>{message}</p>
      <p>
        <Link href="/" className="text-accent underline underline-offset-4">
          Aller sur le site
        </Link>
      </p>
    </Notice>
  );
}
