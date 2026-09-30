// Un garde-fou contre les rafales de messages (un script, un bouton
// maintenu) : au plus N messages par personne sur une fenêtre glissante.
// Il protège le quota du modèle et la base. Compté en mémoire, par
// instance du serveur : c'est un frein, pas une comptabilité exacte.

export class RateLimiter {
  private hits = new Map<string, number[]>();

  constructor(
    readonly max: number,
    readonly windowMs: number,
  ) {}

  /** Enregistre une tentative ; false si la limite est dépassée. */
  allow(key: string, now: number = Date.now()): boolean {
    const since = now - this.windowMs;
    const recent = (this.hits.get(key) ?? []).filter((t) => t > since);
    if (recent.length >= this.max) {
      this.hits.set(key, recent);
      return false;
    }
    recent.push(now);
    this.hits.set(key, recent);
    // De temps en temps, on oublie les personnes silencieuses.
    if (this.hits.size > 5000) {
      for (const [k, times] of this.hits) if (!times.some((t) => t > since)) this.hits.delete(k);
    }
    return true;
  }
}

/** Messages par minute et par personne : bien au-delà de ce qu'on tape à la main. */
export const CHAT_MESSAGES_PER_MINUTE = 12;

/** La limite, réglable par la variable CHAT_RATE_LIMIT (facultative). */
export function chatMessagesPerMinute(): number {
  const value = Number(process.env.CHAT_RATE_LIMIT);
  return Number.isInteger(value) && value >= 1 ? value : CHAT_MESSAGES_PER_MINUTE;
}
