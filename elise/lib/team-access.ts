import "server-only";
import { createHash, timingSafeEqual } from "node:crypto";

// Le lien secret de l'équipe : https://…/acces?cle=<ADMIN_ACCESS_KEY>. Il ouvre
// la session du compte administrateur sans e-mail ni mot de passe. Ce lien
// vaut un mot de passe : quiconque l'a entre dans l'espace de l'équipe.

/** Une clé plus courte serait devinable : le lien reste alors désactivé. */
export const MIN_ACCESS_KEY = 24;

/** La clé du lien, ou null si elle manque ou est trop courte. */
export function accessKey(): string | null {
  const key = process.env.ADMIN_ACCESS_KEY?.trim();
  return key && key.length >= MIN_ACCESS_KEY ? key : null;
}

/** Compare sans laisser deviner la clé au temps de réponse. */
export function sameKey(given: string, expected: string): boolean {
  const a = createHash("sha256").update(given).digest();
  const b = createHash("sha256").update(expected).digest();
  return timingSafeEqual(a, b);
}
