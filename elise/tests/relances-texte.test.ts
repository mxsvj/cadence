// Ce que l'IA reçoit pour prendre des nouvelles, et ce qu'on garde de sa
// réponse.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { absence, cleanRelance, relanceTask } from "../lib/relances";

describe("prendre des nouvelles : la consigne", () => {
  it("dit depuis combien de temps la personne n'est pas venue", () => {
    assert.equal(absence(20), "un jour");
    assert.equal(absence(50), "2 jours");
    assert.match(relanceTask(75), /n'est pas venue depuis 3 jours/);
  });

  it("interdit reproches, attachement, vente et histoires inventées", () => {
    const task = relanceTask(48);
    assert.match(task, /Aucun reproche, aucune culpabilité, aucune insistance/);
    assert.match(task, /tu m'as manqué/);
    assert.match(task, /Rien qui crée de l'attachement ou de la dépendance/);
    assert.match(task, /Aucune vente, aucun contenu, aucune offre, aucune balise/);
    assert.match(task, /sa vie en dehors d'ici compte plus que cette conversation/);
    assert.match(task, /n'invente pas d'événement de ta vie/);
  });
});

describe("prendre des nouvelles : la réponse", () => {
  it("retire toute balise d'offre et la mise en forme", () => {
    assert.equal(cleanRelance("Coucou ! **Comment** s'est passée ta randonnée ?\n[[PROPOSER prix=9]]"), "Coucou ! Comment s'est passée ta randonnée ?");
  });

  it("n'enregistre rien si la réponse est vide", () => {
    assert.equal(cleanRelance("  [[PROPOSER]] "), null);
  });
});

describe("après une prise de nouvelles, la conversation d'abord", async () => {
  const { mayPropose, NO_SALE_AFTER_RELANCE } = await import("../lib/sales");
  const settings = { sales_min_messages: 0, sales_gap_messages: 0 };
  const base = { next: { trigger_mode: "ia" as const }, pending: false, userMessages: 20, sinceLastOffer: Infinity, withinCap: true };

  it("aucune offre avant que la personne ait écrit quelques messages", () => {
    assert.equal(NO_SALE_AFTER_RELANCE, 3);
    assert.equal(mayPropose({ ...base, sinceRelance: 1 }, settings), false);
    assert.equal(mayPropose({ ...base, sinceRelance: 2 }, settings), false);
    assert.equal(mayPropose({ ...base, sinceRelance: 3 }, settings), true);
  });

  it("sans prise de nouvelles, les garde-fous habituels seulement", () => {
    assert.equal(mayPropose({ ...base, sinceRelance: null }, settings), true);
    assert.equal(mayPropose({ ...base, sinceRelance: null, pending: true }, settings), false);
    assert.equal(mayPropose({ ...base, sinceRelance: null, next: { trigger_mode: "equipe" } }, settings), false);
    assert.equal(mayPropose({ ...base, sinceRelance: null, withinCap: false }, settings), false);
  });
});
