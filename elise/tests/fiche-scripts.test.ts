// La fiche d'une personne ne propose que les scripts utilisables avec la
// créatrice active.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { usableScripts } from "../lib/team";

const scripts = [
  { id: 1, name: "Pour toutes", position: 1, creator_id: null },
  { id: 2, name: "Chloé", position: 2, creator_id: 7 },
  { id: 3, name: "Inès", position: 3, creator_id: 8 },
];

describe("les scripts de la fiche", () => {
  it("ceux de la créatrice active et ceux qui servent à toutes", () => {
    assert.deepEqual(usableScripts(scripts, 7, null).map((s) => s.name), ["Pour toutes", "Chloé"]);
    assert.deepEqual(usableScripts(scripts, null, null).map((s) => s.name), ["Pour toutes"]);
  });

  it("celui déjà choisi pour une autre créatrice reste visible, signalé", () => {
    assert.deepEqual(usableScripts(scripts, 7, 3).map((s) => s.name), ["Pour toutes", "Chloé", "Inès (autre créatrice : pas utilisé)"]);
  });

  it("avant la mise à jour de la base (pas de colonne) : tous servent à toutes", () => {
    const old = [{ id: 1, name: "Ancien", position: 1 }];
    assert.deepEqual(usableScripts(old, 7, null), [{ id: 1, name: "Ancien", position: 1, creator_id: null }]);
  });
});
