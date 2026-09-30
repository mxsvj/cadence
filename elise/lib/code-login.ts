import "server-only";
import { randomUUID, timingSafeEqual } from "node:crypto";
import { RateLimiter } from "./rate-limit";

// L'entrée par le code unique : chaque personne qui entre reçoit un compte de
// test à elle (sa propre conversation), sans e-mail ni mot de passe.

/** Deux codes déjà normalisés (8 caractères), comparés sans trahir par le temps de réponse. */
export function sameCode(a: string | null, b: string | null): boolean {
  if (!a || !b || a.length !== b.length) return false;
  return timingSafeEqual(Buffer.from(a), Buffer.from(b));
}

/**
 * Le compte d'une personne entrée par le code n'a pas d'adresse e-mail
 * réelle : Supabase en demande une, on en invente une qui ne peut recevoir
 * aucun message (domaine réservé « .invalid »).
 */
export function codeEmail(): string {
  return `client-${randomUUID()}@code.elise.invalid`;
}

/** Des essais au hasard sont freinés : au plus 10 entrées par adresse IP toutes les 10 minutes. */
export const codeAttempts = new RateLimiter(10, 10 * 60_000);
