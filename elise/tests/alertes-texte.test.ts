// Les alertes de l'équipe, côté serveur : repérer une urgence, retirer la
// balise [[EQUIPE]], les phrases des alertes, l'envoi sur Discord ou
// Telegram, les garde-fous de vente qui s'y rattachent, la prise de main.
import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import type { SupabaseClient } from "@supabase/supabase-js";
import { alertMessage, alertSummary } from "../lib/alerts";
import { memoryDue } from "../lib/memory";
import { alertChannels, channelStatus, flushAlerts } from "../lib/notify";
import { chatSystemPrompt } from "../lib/prompts";
import { RateLimiter } from "../lib/rate-limit";
import { describeBlock, saleBlock, type SaleInput } from "../lib/sales";
import { aiMayReply, DEFAULT_SETTINGS, defaultContact } from "../lib/settings";
import { detectUrgency, parseTeamFlag } from "../lib/urgency";

describe("repérer une urgence dans le message d'une personne", () => {
  it("une demande explicite d'humain", () => {
    for (const text of [
      "Je veux parler à un humain",
      "est-ce que je peux parler avec une vraie personne ?",
      "Passez-moi un conseiller svp",
      "j'aimerais discuter avec quelqu'un de réel",
      "Comment contacter l'équipe ?",
      "je voudrais un humain",
    ]) {
      assert.equal(detectUrgency(text), "humain", text);
    }
  });

  it("pas une simple question sur l'IA, ni une phrase ordinaire", () => {
    for (const text of [
      "T'es une vraie personne ?",
      "Tu es humaine ou pas ?",
      "J'ai passé une journée horrible au travail",
      "ce film m'a tué de rire",
      "je vais me tuer de rire avec toi",
      "J'ai hâte d'en finir avec ce dossier",
      "j'ai 12 ans d'ancienneté dans ma boîte",
      "Ma fille a 15 ans",
      "Je veux parler à Katherine",
    ]) {
      assert.equal(detectUrgency(text), null, text);
    }
  });

  it("un message qui demande de l'attention, sans dire lequel", () => {
    for (const text of ["Je n'ai plus envie de vivre", "je pense au suicide", "J'ai envie d'en finir", "il me frappe quand il boit"]) {
      assert.equal(detectUrgency(text), "attention", text);
    }
  });

  it("une personne qui dit avoir moins de 18 ans", () => {
    assert.equal(detectUrgency("j'ai 16 ans au fait"), "age");
    assert.equal(detectUrgency("Je suis mineure"), "age");
  });

  it("un problème de paiement", () => {
    for (const text of ["Je veux être remboursé", "c'est une arnaque", "J'ai payé mais j'ai rien reçu", "j'ai été débité deux fois"]) {
      assert.equal(detectUrgency(text), "reclamation", text);
    }
  });

  it("la raison la plus grave l'emporte", () => {
    assert.equal(detectUrgency("je veux parler à un humain, je n'ai plus envie de vivre"), "attention");
  });
});

describe("la balise [[EQUIPE]] de l'IA", () => {
  it("est retirée du message, et signalée", () => {
    assert.deepEqual(parseTeamFlag("Je préviens l'équipe, elle te répondra ici.\n[[EQUIPE]]"), {
      text: "Je préviens l'équipe, elle te répondra ici.",
      flagged: true,
    });
    assert.deepEqual(parseTeamFlag("[[ Équipe ]] Coucou"), { text: "Coucou", flagged: true });
    assert.deepEqual(parseTeamFlag("Rien à signaler"), { text: "Rien à signaler", flagged: false });
  });

  it("la consigne n'est donnée que dans la conversation, et dit quand l'équipe est déjà prévenue", () => {
    const base = { base: "Règles.", facts: [], summary: null, now: new Date("2026-09-30T10:00:00Z") };
    assert.doesNotMatch(chatSystemPrompt(base), /\[\[EQUIPE\]\]/);
    const prompt = chatSystemPrompt({ ...base, team: { alerted: false } });
    assert.match(prompt, /## Prévenir l'équipe/);
    assert.match(prompt, /demande à parler à un humain/);
    assert.doesNotMatch(prompt, /vient d'être prévenue/);
    assert.match(chatSystemPrompt({ ...base, team: { alerted: true } }), /L'équipe vient d'être prévenue pour ce message/);
  });
});

describe("le texte des alertes", () => {
  const alert = { user_id: "u-1", creator_id: 2, creatrice: "Katherine" };
  // Les montants s'écrivent avec des espaces insécables.
  const summary = (a: Parameters<typeof alertSummary>[0]) => alertSummary(a).replace(/[\u202f\u00a0]/g, " ");

  it("une phrase par type d'alerte", () => {
    assert.equal(alertSummary({ kind: "urgence", detail: { raison: "humain" } }), "Demande à parler à un humain");
    assert.equal(alertSummary({ kind: "urgence", detail: {} }), "Message à lire en priorité");
    assert.equal(
      summary({ kind: "contre_offre", detail: { montant_cents: 300, prix_cents: 800, statut: "refusee", essais_restants: 2 } }),
      "Propose 3,00 € pour un prix de 8,00 € (refusée, encore 2 essais)",
    );
    assert.equal(
      summary({ kind: "contre_offre", detail: { montant_cents: 600, prix_cents: 800, statut: "acceptee", essais_restants: null } }),
      "Propose 6,00 € pour un prix de 8,00 € (acceptée)",
    );
  });

  it("le message Discord/Telegram : ni prénom, ni texte de la conversation, un lien", () => {
    const text = alertMessage({ ...alert, kind: "urgence", detail: { raison: "humain" } }, "https://elise.example/");
    assert.equal(
      text,
      "🔴 Urgence · conversation avec Katherine\nDemande à parler à un humain\nOuvrir : https://elise.example/admin/messages?u=u-1&c=2",
    );
  });
});

describe("les garde-fous qui suivent les alertes", () => {
  const rules = { sales_min_messages: 10, sales_gap_messages: 12 };
  const paid = { trigger_mode: "ia" as const, is_paid: true, min_price_cents: 500 };
  const ok: SaleInput = {
    next: paid,
    pending: false,
    userMessages: 20,
    sinceLastOffer: Infinity,
    sinceRelance: null,
  };

  it("une urgence à traiter bloque toute offre, même un cadeau", () => {
    assert.equal(saleBlock({ ...ok, urgent: true }, rules)?.reason, "urgence");
    assert.equal(saleBlock({ ...ok, urgent: true, next: { ...paid, is_paid: false, min_price_cents: 0 } }, rules)?.reason, "urgence");
    assert.match(describeBlock({ reason: "urgence" }, null), /urgence est à traiter/);
  });

  it("« Prendre la main » fait taire l'IA dans tous les modes", () => {
    const contact = { ...defaultContact("u-1"), manual: true };
    for (const mode of ["auto", "hybride", "manuel"] as const) {
      assert.equal(aiMayReply({ ...DEFAULT_SETTINGS, mode }, contact), false, mode);
    }
    assert.equal(aiMayReply(DEFAULT_SETTINGS, defaultContact("u-1")), true);
  });
});

describe("envoyer les alertes sur Discord ou Telegram", () => {
  const env = { ...process.env };
  const realFetch = globalThis.fetch;
  afterEach(() => {
    process.env = { ...env };
    globalThis.fetch = realFetch;
  });

  const pending = [{ id: 1, kind: "contre_offre", user_id: "u-1", creator_id: 2, creatrice: "Katherine", detail: { montant_cents: 300 } }];
  const fakeAdmin = (calls: string[]) =>
    ({
      rpc: async (name: string) => {
        calls.push(name);
        return { data: pending, error: null };
      },
    }) as unknown as SupabaseClient;

  it("rien n'est lu ni envoyé tant qu'aucun canal n'est branché", async () => {
    delete process.env.DISCORD_WEBHOOK_URL;
    delete process.env.TELEGRAM_BOT_TOKEN;
    delete process.env.TELEGRAM_CHAT_ID;
    const calls: string[] = [];
    assert.equal(await flushAlerts(fakeAdmin(calls), "https://elise.example"), 0);
    assert.deepEqual(calls, []);
    assert.deepEqual(channelStatus(), { discord: "absent", telegram: "absent" });
  });

  it("une adresse mal copiée est ignorée, et signalée dans les Paramètres", () => {
    process.env.DISCORD_WEBHOOK_URL = "https://example.com/pas-discord";
    process.env.TELEGRAM_BOT_TOKEN = "abc";
    assert.equal(alertChannels().discord, null);
    assert.deepEqual(channelStatus(), { discord: "invalide", telegram: "invalide" });
  });

  it("envoie sur les deux canaux, sans aucune mention possible sur Discord", async () => {
    process.env.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/123456/abcDEF-ghi_jkl";
    process.env.TELEGRAM_BOT_TOKEN = "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi";
    process.env.TELEGRAM_CHAT_ID = "-100123";
    const sent: { url: string; body: Record<string, unknown> }[] = [];
    globalThis.fetch = (async (url: string, init: RequestInit) => {
      sent.push({ url, body: JSON.parse(init.body as string) });
      return new Response("{}", { status: 200 });
    }) as typeof fetch;
    const calls: string[] = [];
    assert.equal(await flushAlerts(fakeAdmin(calls), "https://elise.example"), 1);
    assert.deepEqual(calls, ["alertes_a_envoyer"]);
    assert.equal(sent.length, 2);
    assert.equal(sent[0].url, process.env.DISCORD_WEBHOOK_URL);
    assert.deepEqual(sent[0].body.allowed_mentions, { parse: [] });
    assert.match(String(sent[0].body.content), /^💬 Contre-offre · conversation avec Katherine/);
    assert.equal(sent[1].url, `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`);
    assert.equal(sent[1].body.chat_id, "-100123");
  });

  it("un canal en panne ne bloque rien", async () => {
    process.env.DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/123456/abcDEF-ghi_jkl";
    delete process.env.TELEGRAM_BOT_TOKEN;
    globalThis.fetch = (async () => new Response("", { status: 500 })) as typeof fetch;
    const errors = console.error;
    console.error = () => {};
    try {
      assert.equal(await flushAlerts(fakeAdmin([]), "https://elise.example"), 0);
    } finally {
      console.error = errors;
    }
  });
});

describe("ménager la base et le quota du modèle", () => {
  it("la fiche et le résumé se mettent à jour tous les 3 messages de la personne", () => {
    assert.deepEqual([1, 2, 3, 4, 5, 6, 7].map((n) => memoryDue(n)), [false, false, true, false, false, true, false]);
    assert.equal(memoryDue(0), false);
  });

  it("au plus 12 messages par minute et par personne", () => {
    const limiter = new RateLimiter(12, 60_000);
    const t0 = 1_000_000;
    for (let i = 0; i < 12; i++) assert.equal(limiter.allow("karim", t0 + i), true);
    assert.equal(limiter.allow("karim", t0 + 100), false);
    assert.equal(limiter.allow("lea", t0 + 100), true); // chacun son compte
    assert.equal(limiter.allow("karim", t0 + 60_001), true); // une minute plus tard
  });
});
