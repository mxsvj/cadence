// Les fautes de frappe « écrit trop vite » : rares, lisibles, jamais dans un
// nom, un chiffre ou les mots qui disent qu'elle est une IA.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TYPO_RATE, addTypo, typoIn } from "../lib/typos";

/** Un hasard rejoué : les valeurs données, puis 0. */
const seq = (...values: number[]) => () => values.shift() ?? 0;

describe("les fautes de frappe", () => {
  it("environ une réponse sur cinq, et coupées par HUMAN_TYPOS=off", () => {
    assert.equal(TYPO_RATE, 0.2);
    const text = "chui trop crevée ce soir, journée interminable";
    assert.equal(addTypo(text, { random: seq(0.5), setting: "" }), text); // pas cette fois
    assert.notEqual(addTypo(text, { random: seq(0.1), setting: "" }), text);
    assert.equal(addTypo(text, { random: seq(0.1), setting: "off" }), text);
    let changed = 0;
    for (let i = 0; i < 2000; i++) if (addTypo(text, { setting: "" }) !== text) changed++;
    assert.ok(changed > 300 && changed < 500, `${changed} sur 2000`);
  });

  it("une seule faute, dans un seul mot, le reste intact", () => {
    for (let i = 0; i < 300; i++) {
      const text = "Karim, tu as vraiment raison pour demain soir 😊";
      const out = addTypo(text, { rate: 1, setting: "" });
      const before = text.split(" ");
      const after = out.split(" ");
      assert.equal(after.length, before.length, out);
      const diff = before.filter((w, j) => w !== after[j]);
      assert.equal(diff.length, 1, out);
      assert.ok(["vraiment", "raison", "demain"].includes(diff[0]), out); // jamais « Karim », « tu », « as », « soir », l'emoji
    }
  });

  it("jamais dans un prénom, un chiffre, un lien ou les mots qui disent qu'elle est une IA", () => {
    const text = "Je suis une intelligence artificielle, Katherine, 3114 ou https://exemple.fr";
    for (let i = 0; i < 200; i++) assert.equal(addTypo(text, { rate: 1, setting: "" }), text);
    assert.equal(addTypo("ok mdr tkt", { rate: 1, setting: "" }), "ok mdr tkt"); // rien d'assez long
  });

  it("des fautes de téléphone : lettres inversées, oubliée, doublée, accent qui saute", () => {
    assert.equal(typoIn("vraiment", seq(0, 0.1)), "variment"); // inversées
    assert.equal(typoIn("vraiment", seq(0.4, 0)), "vaiment"); // oubliée
    assert.equal(typoIn("vraiment", seq(0.7, 0)), "vrraiment"); // doublée
    assert.equal(typoIn("journée", seq(0.9)), "journee"); // accent
  });
});
