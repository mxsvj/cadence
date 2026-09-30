// Les garde-fous de la vente, réunis : quand l'IA peut proposer le contenu
// suivant du script, et sinon pourquoi (ce que l'équipe lit dans la fiche).
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { NO_SALE_AFTER_RELANCE, describeBlock, mayPropose, saleBlock, type SaleInput } from "../lib/sales";

const rules = { sales_min_messages: 10, sales_gap_messages: 12 };
const paid = { trigger_mode: "ia" as const, is_paid: true, min_price_cents: 500 };
const free = { ...paid, is_paid: false, min_price_cents: 0 };
const ok: SaleInput = {
  next: paid,
  pending: false,
  userMessages: 20,
  sinceLastOffer: Infinity,
  sinceRelance: null,
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

describe("le rythme des offres", () => {
  it("ni pause après un achat, ni nombre maximum par jour : seulement l'espacement réglé par l'équipe", () => {
    assert.equal(reason({}), null);
    assert.equal(reason({ next: free, sinceLastOffer: 1 }), "espacement");
    assert.equal(saleBlock({ ...ok, sinceLastOffer: 0 }, { ...rules, sales_gap_messages: 0 }), null);
  });
});
