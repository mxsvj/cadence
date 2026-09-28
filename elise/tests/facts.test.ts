import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { isSensitive, normalizeFact, parseFactsResponse, selectNewFacts } from "../lib/facts";

describe("isSensitive : jamais de santé, religion, orientation sexuelle ni argent", () => {
  const sensitive = [
    "Prend des antidépresseurs depuis la séparation.",
    "Suit une thérapie avec une psychologue.",
    "A été hospitalisé à l'hôpital Necker en mars.",
    "Souffre de migraines.",
    "Est diabétique.",
    "Va à la messe le dimanche.",
    "Est musulman pratiquant.",
    "Croit en Dieu.",
    "Est homosexuel.",
    "Est bisexuelle.",
    "Gagne 3 200 € par mois.",
    "A des dettes auprès de sa banque.",
    "Son loyer a augmenté.",
    "Touche le chômage depuis mai.",
    "Verse une pension alimentaire.",
  ];
  for (const fact of sensitive) {
    it(`écarte « ${fact} »`, () => assert.equal(isSensitive(fact), true));
  }

  const harmless = [
    "Se prénomme Karim.",
    "Préfère le tutoiement.",
    "A deux filles, Inès (12 ans) et Lou (9 ans), une semaine sur deux.",
    "Va à la piscine deux fois par semaine.",
    "Aime voyager en Europe, surtout en Italie.",
    "Est revenu de vacances en Bretagne.",
    "Travaille comme comptable dans une PME de Nantes.",
    "Dîne chez sa sœur le samedi 3 octobre 2026.",
    "Adore les films de Truffaut.",
    "Interprète des morceaux de jazz au piano.",
  ];
  for (const fact of harmless) {
    it(`garde « ${fact} »`, () => assert.equal(isSensitive(fact), false));
  }
});

describe("parseFactsResponse", () => {
  it("lit le format demandé", () => {
    assert.deepEqual(parseFactsResponse('{"faits": ["Se prénomme Karim."]}'), ["Se prénomme Karim."]);
  });
  it("lit une réponse entourée de ```json", () => {
    assert.deepEqual(parseFactsResponse('```json\n{"faits": ["A un chat."]}\n```'), ["A un chat."]);
  });
  it("accepte une simple liste", () => {
    assert.deepEqual(parseFactsResponse('["A un chat."]'), ["A un chat."]);
  });
  it("renvoie une liste vide sur une réponse illisible", () => {
    assert.deepEqual(parseFactsResponse("Rien de nouveau."), []);
    assert.deepEqual(parseFactsResponse("{faits: oups"), []);
  });
  it("ignore ce qui n'est pas du texte", () => {
    assert.deepEqual(parseFactsResponse('{"faits": ["A un chat.", 3, null]}'), ["A un chat."]);
  });
});

describe("selectNewFacts : sans doublon, sans donnée sensible", () => {
  it("écarte ce qui est déjà dans la fiche, même écrit autrement", () => {
    assert.deepEqual(
      selectNewFacts(["se prénomme  KARIM", "Aime le jazz."], ["Se prénomme Karim."]),
      ["Aime le jazz."],
    );
  });
  it("écarte les doublons à l'intérieur d'une même réponse", () => {
    assert.deepEqual(selectNewFacts(["Aime le jazz.", "aime le jazz"], []), ["Aime le jazz."]);
  });
  it("écarte les données sensibles, les vides et les trop longs", () => {
    assert.deepEqual(
      selectNewFacts(["Est catholique.", "  ", "x".repeat(300), "A un chien, Filou."], []),
      ["A un chien, Filou."],
    );
  });
  it("garde au plus cinq faits par tour", () => {
    const many = Array.from({ length: 8 }, (_, i) => `Fait numéro ${i}.`);
    assert.equal(selectNewFacts(many, []).length, 5);
  });
  it("normalise les accents et la ponctuation", () => {
    assert.equal(normalizeFact("  Élise, c'est ÇA ! "), "elise c est ca");
  });
});
