import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { change, describePurchase, formatEuros, formatEurosRound, timeAgo } from "../lib/dashboard";

// Intl sépare les milliers et l'euro par des espaces insécables : on les
// remplace par des espaces ordinaires pour comparer.
const plain = (s: string) => s.replace(/[  ]/g, " ");

describe("tableau de bord : affichage", () => {
  it("formate les montants en euros, à la française", () => {
    assert.equal(plain(formatEuros(123456)), "1 234,56 €");
    assert.equal(plain(formatEuros(0)), "0,00 €");
    assert.equal(plain(formatEurosRound(2000)), "20 €");
  });

  it("décrit chaque sorte d'achat", () => {
    assert.equal(plain(describePurchase({ type: "tip", quantite: 1, cents: 500 })), "Pourboire de 5,00 €");
    assert.equal(plain(describePurchase({ type: "message", quantite: 10, cents: 349 })), "10 messages achetés · 3,49 €");
    assert.equal(plain(describePurchase({ type: "abonnement", quantite: 1, cents: 999 })), "Abonnement mensuel · 9,99 €");
  });

  it("dit depuis combien de temps", () => {
    const now = Date.parse("2026-09-28T12:00:00Z");
    assert.equal(timeAgo("2026-09-28T11:59:55Z", now), "à l'instant");
    assert.equal(timeAgo("2026-09-28T11:59:15Z", now), "il y a 45 s");
    assert.equal(timeAgo("2026-09-28T11:57:00Z", now), "il y a 3 min");
    assert.equal(timeAgo("2026-09-28T09:00:00Z", now), "il y a 3 h");
    assert.equal(plain(timeAgo("2026-09-26T08:30:00Z", now)), "26 sept., 10:30");
  });

  it("calcule l'évolution, sauf s'il n'y a rien à comparer", () => {
    assert.equal(change(150, 100), 50);
    assert.equal(change(50, 100), -50);
    assert.equal(change(100, 0), null);
  });
});
