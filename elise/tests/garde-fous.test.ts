// Les garde-fous de la vente, réunis : quand l'IA peut proposer le contenu
// suivant du script, et sinon pourquoi (ce que l'équipe lit dans la fiche).
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { NO_SALE_AFTER_RELANCE, describeBlock, mayPropose, saleBlock, type SaleInput } from "../lib/sales";

const rules = { sales_min_messages: 10, sales_gap_messages: 12, sales_pause_hours: 24, sales_max_per_day: 1 };
const paid = { trigger_mode: "ia" as const, is_paid: true, min_price_cents: 500 };
const free = { ...paid, is_paid: false, min_price_cents: 0 };
const ok: SaleInput = {
  next: paid,
  pending: false,
  userMessages: 20,
  sinceLastOffer: Infinity,
  sinceRelance: null,
  remainingCents: null,
  hoursSincePurchase: null,
  paidOffersToday: 0,
};
const reason = (input: Partial<SaleInput>) => saleBlock({ ...ok, ...input }, rules)?.reason ?? null;

describe("l'avancement du script", () => {
  it("propose quand tout est réuni", () => {
    assert.equal(mayPropose(ok, rules), true);
    assert.match(describeBlock(null, { title: "Vlog du week-end" }), /L'IA peut proposer « Vlog du week-end »/);
  });

  it("jamais après la fin du script, ni un contenu que l'équipe propose elle-même", () => {
    assert.equal(reason({ next: null }), "fin");
    assert.equal(reason({ next: { ...paid, trigger_mode: "equipe" } }), "equipe");
  });

  it("une seule offre en attente à la fois, toutes créatrices confondues", () => {
    assert.equal(reason({ pending: true }), "attente");
  });

  it("d'abord la conversation : assez de messages avant la première offre, puis entre deux offres", () => {
    assert.deepEqual(saleBlock({ ...ok, userMessages: 7 }, rules), { reason: "premiers_messages", remaining: 3 });
    assert.deepEqual(saleBlock({ ...ok, sinceLastOffer: 10 }, rules), { reason: "espacement", remaining: 2 });
    assert.equal(describeBlock({ reason: "espacement", remaining: 2 }, null), "Prochaine offre dans 2 messages.");
  });

  it("après une prise de nouvelles, quelques messages de la personne avant toute offre", () => {
    assert.equal(NO_SALE_AFTER_RELANCE, 3);
    assert.equal(reason({ sinceRelance: 1 }), "nouvelles");
    assert.equal(reason({ sinceRelance: 3 }), null);
  });
});

describe("une dépense saine", () => {
  it("jamais au-delà du plafond du mois", () => {
    assert.equal(reason({ remainingCents: 400 }), "plafond");
    assert.equal(reason({ remainingCents: 500 }), null);
    assert.equal(describeBlock({ reason: "plafond" }, null), "Son plafond du mois ne permet pas ce contenu.");
  });

  it("une pause après chaque achat", () => {
    assert.deepEqual(saleBlock({ ...ok, hoursSincePurchase: 5.5 }, rules), { reason: "pause", hours: 19 });
    assert.equal(reason({ hoursSincePurchase: 30 }), null);
    assert.equal(saleBlock({ ...ok, hoursSincePurchase: 1 }, { ...rules, sales_pause_hours: 0 }), null);
    assert.equal(describeBlock({ reason: "pause", hours: 19 }, null), "Pause après son dernier achat : encore 19 heures.");
  });

  it("au plus N offres payantes proposées par l'IA sur 24 heures", () => {
    assert.equal(reason({ paidOffersToday: 1 }), "quota");
    assert.equal(saleBlock({ ...ok, paidOffersToday: 1 }, { ...rules, sales_max_per_day: 2 }), null);
  });

  it("un cadeau (gratuit) n'est freiné ni par le plafond, ni par la pause, ni par le nombre par jour", () => {
    assert.equal(reason({ next: free, remainingCents: 0, hoursSincePurchase: 1, paidOffersToday: 5 }), null);
    // Mais il attend quand même son tour dans la conversation.
    assert.equal(reason({ next: free, sinceLastOffer: 1 }), "espacement");
  });
});
