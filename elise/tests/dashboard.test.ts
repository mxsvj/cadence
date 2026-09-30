import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  addMonths,
  bucketLabel,
  change,
  comparisonLabel,
  describePurchase,
  filtersFromParams,
  filtersToParams,
  formatEuros,
  formatEurosRound,
  parisToday,
  periodLabel,
  periodRange,
  timeAgo,
} from "../lib/dashboard";

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
    assert.equal(change(100, null), null);
  });
});

describe("tableau de bord : les périodes", () => {
  const today = "2026-09-30";

  it("aujourd'hui, hier, les derniers jours, mois et année, depuis le début", () => {
    assert.deepEqual(periodRange({ period: "aujourdhui" }, today), { debut: today, fin: today });
    assert.deepEqual(periodRange({ period: "hier" }, today), { debut: "2026-09-29", fin: "2026-09-29" });
    assert.deepEqual(periodRange({ period: "7j" }, today), { debut: "2026-09-24", fin: today });
    assert.deepEqual(periodRange({ period: "30j" }, today), { debut: "2026-09-01", fin: today });
    assert.deepEqual(periodRange({ period: "90j" }, today), { debut: "2026-07-03", fin: today });
    assert.deepEqual(periodRange({ period: "6m" }, today), { debut: "2026-03-31", fin: today });
    assert.deepEqual(periodRange({ period: "1a" }, today), { debut: "2025-10-01", fin: today });
    assert.deepEqual(periodRange({ period: "tout" }, today), { debut: null, fin: today });
  });

  it("des dates précises, seulement si elles sont complètes et dans l'ordre", () => {
    assert.deepEqual(periodRange({ period: "dates", from: "2026-09-03", to: "2026-09-12" }, today), {
      debut: "2026-09-03",
      fin: "2026-09-12",
    });
    assert.equal(periodRange({ period: "dates", from: "2026-09-12", to: "2026-09-03" }, today), null);
    assert.equal(periodRange({ period: "dates", from: "2026-02-30", to: "2026-03-03" }, today), null);
    assert.equal(periodRange({ period: "dates" }, today), null);
    assert.equal(plain(periodLabel({ period: "dates", from: "2026-09-03", to: "2026-09-12" })), "du 3 sept. 2026 au 12 sept. 2026");
    assert.equal(periodLabel({ period: "6m" }), "6 derniers mois");
  });

  it("un mois plus court garde un jour qui existe", () => {
    assert.equal(addMonths("2026-03-31", -1), "2026-02-28");
    assert.equal(addMonths("2026-08-31", -6), "2026-02-28");
  });

  it("aujourd'hui, c'est à l'heure de Paris", () => {
    assert.equal(parisToday(new Date("2026-09-29T22:30:00Z")), "2026-09-30");
    assert.equal(parisToday(new Date("2026-09-29T21:30:00Z")), "2026-09-29");
  });

  it("à quoi on compare", () => {
    assert.equal(comparisonLabel("aujourdhui", 1), "par rapport à hier");
    assert.equal(comparisonLabel("hier", 1), "par rapport à avant-hier");
    assert.equal(comparisonLabel("30j", 30), "par rapport aux 30 jours d'avant");
  });

  it("les filtres passent par l'adresse, et une valeur inconnue retombe sur 30 jours", () => {
    const f = { period: "dates" as const, from: "2026-09-03", to: "2026-09-12", creator: 2, net: true };
    assert.equal(filtersToParams(f).toString(), "periode=dates&du=2026-09-03&au=2026-09-12&createur=2&net=1");
    assert.deepEqual(filtersFromParams(filtersToParams(f)), f);
    assert.deepEqual(filtersFromParams(new URLSearchParams("periode=12ans&createur=abc")), {
      period: "30j",
      from: undefined,
      to: undefined,
      creator: null,
      net: false,
    });
  });

  it("les tranches de LTV", () => {
    assert.equal(bucketLabel(0, 1000), "Moins de 10 €");
    assert.equal(bucketLabel(1000, 2500), "10 à 25 €");
    assert.equal(bucketLabel(10000, null), "100 € et plus");
  });
});
