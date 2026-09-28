// L'âge minimum : Élise est réservée aux personnes majeures. La base de
// données le vérifie aussi (fonction enregistrer_profil).

export const MIN_AGE = 18;

/** L'âge en années révolues, d'après une date AAAA-MM-JJ. */
export function ageFrom(birthdate: string, now = new Date()): number {
  const [y, m, d] = birthdate.slice(0, 10).split("-").map(Number);
  let age = now.getFullYear() - y;
  if (now.getMonth() + 1 < m || (now.getMonth() + 1 === m && now.getDate() < d)) age -= 1;
  return age;
}

/** Une date de naissance plausible (après 1900, pas dans le futur) ? */
export function validBirthdate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T12:00:00Z`);
  return !Number.isNaN(date.getTime()) && value >= "1900-01-01" && date.getTime() <= Date.now();
}

/** La date la plus récente permise dans le champ « date de naissance ». */
export function latestBirthdate(now = new Date()): string {
  const d = new Date(now);
  d.setFullYear(d.getFullYear() - MIN_AGE);
  return d.toISOString().slice(0, 10);
}

/** Vérifie prénom et date de naissance ; renvoie l'erreur à afficher, ou null. */
export function checkProfile(name: string, birthdate: string): string | null {
  if (!name.trim() || name.trim().length > 60) return "Indiquez un prénom ou un pseudo (60 caractères au plus).";
  if (!validBirthdate(birthdate)) return "Indiquez votre date de naissance.";
  if (ageFrom(birthdate) < MIN_AGE) return "Élise est réservée aux personnes majeures (18 ans et plus).";
  return null;
}
