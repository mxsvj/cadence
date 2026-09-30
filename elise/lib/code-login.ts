import "server-only";
import { createHmac, randomUUID } from "node:crypto";
import { RateLimiter } from "./rate-limit";

// L'empreinte d'un code d'accès, calculée avec une clé secrète du serveur (la
// clé secrète Supabase) : même avec une copie de la base, on ne retrouve pas
// les codes. Si cette clé change un jour, les codes existants ne marchent
// plus : l'équipe en crée de nouveaux (« Nouveau code »).

export function codeHash(normalizedCode: string, secret = process.env.SUPABASE_SECRET_KEY?.trim()): string {
  if (!secret) throw new Error("SUPABASE_SECRET_KEY manquante : impossible de vérifier un code.");
  return createHmac("sha256", secret).update(`code-elise:${normalizedCode}`).digest("hex");
}

/**
 * Le compte d'un client entré par code n'a pas d'adresse e-mail réelle :
 * Supabase en demande une, on en invente une qui ne peut recevoir aucun
 * message (domaine réservé « .invalid »).
 */
export function codeEmail(): string {
  return `client-${randomUUID()}@code.elise.invalid`;
}

/** Des essais de code au hasard sont freinés : au plus 10 par adresse IP toutes les 10 minutes. */
export const codeAttempts = new RateLimiter(10, 10 * 60_000);
