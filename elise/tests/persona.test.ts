import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { parseEuros, parseProposal } from "../lib/offers";
import { sanitizePersona } from "../lib/persona-profile";
import { chatSystemPrompt, personSection, personaSection, salesSection, type SalePrompt } from "../lib/prompts";

const now = new Date("2026-09-28T19:14:00Z");

describe("le personnage", () => {
  const persona = {
    nom: "Chloé",
    pseudo: "chlo",
    genre: "Femme",
    age: 29,
    anniversaire: "1997-05-12",
    profession: "Illustratrice",
    ville: "Annecy",
    langue_maternelle: "it",
    taille: "1,68 m",
    cheveux: "châtains",
    corps: "Athlétique",
    groupes: [{ titre: "Tatouages", valeur: "une hirondelle sur le poignet" }],
    interets: [{ categorie: "Musique", elements: "jazz, bossa nova" }],
    a_propos: "Adore les marchés du dimanche.",
  };

  it("décrit le personnage et rappelle qu'il s'agit d'une IA", () => {
    const text = personaSection(persona, {});
    assert.match(text, /Nom : Chloé \(pseudo : chlo\)/);
    assert.match(text, /Âge : 29 ans, anniversaire le 12 mai/);
    assert.match(text, /Lieu de vie : Annecy/);
    assert.match(text, /Langue maternelle : italien/);
    assert.match(text, /Apparence : taille 1,68 m ; cheveux châtains ; silhouette Athlétique/);
    assert.match(text, /Tatouages : une hirondelle sur le poignet/);
    assert.match(text, /Musique : jazz, bossa nova/);
    assert.match(text, /réponds toujours franchement que tu es une IA/);
    assert.match(text, /jamais dans un registre sexuel/);
  });

  it("« près de la personne » : sa ville, et jamais de rencontre", () => {
    const text = personaSection({ ...persona, pres_de_la_personne: true }, { city: "Lyon" });
    assert.match(text, /Lieu de vie : dans la même région que la personne, près de Lyon/);
    assert.match(text, /Tu ne proposes jamais de la rencontrer/);
    // Sans ville connue pour la personne, on garde la ville du personnage.
    assert.match(personaSection({ ...persona, pres_de_la_personne: true }, {}), /Lieu de vie : Annecy/);
  });

  it("par défaut, le personnage s'appelle Élise", () => {
    assert.match(personaSection({}, {}), /Nom : Élise/);
  });

  it("refuse un personnage de moins de 18 ans, et nettoie le reste", () => {
    assert.match(sanitizePersona({ age: 17 }).error ?? "", /au moins 18 ans/);
    const { persona: clean, error } = sanitizePersona({
      nom: "  Chloé ",
      age: "29",
      inconnu: "x",
      groupes: [{ titre: "Piercing", valeur: "oreille" }, { titre: "", valeur: "vide" }],
      pres_de_la_personne: true,
    });
    assert.equal(error, undefined);
    assert.deepEqual(clean, {
      nom: "Chloé",
      age: 29,
      pres_de_la_personne: true,
      groupes: [{ titre: "Piercing", valeur: "oreille" }],
    });
  });
});

describe("la personne", () => {
  it("donne l'heure chez elle, ses emojis et les notes de l'équipe", () => {
    const text = personSection(
      { name: "Karim", age: 44, city: "Montréal", timezone: "America/Toronto", emojiMode: "choisis", emojis: "😊 🌿", notes: "Préfère les messages courts." },
      now,
    );
    assert.match(text, /Prénom ou pseudo : Karim/);
    assert.match(text, /Âge : 44 ans/);
    assert.match(text, /lundi 28 septembre à 15:14 \(America\/Toronto\)/);
    assert.match(text, /uniquement ceux-là, selon la discussion : 😊 🌿/);
    assert.match(text, /Préfère les messages courts\./);
  });
});

describe("la vente", () => {
  const next: SalePrompt["next"] = {
    description: "un carnet de voyage illustré",
    isPaid: true,
    priceCents: 800,
    minCents: 500,
    maxCents: 1200,
    messageMode: "ia",
  };

  it("n'autorise une offre que si le serveur l'a permis, avec la fourchette de prix", () => {
    const allowed = salesSection({ owned: [], pending: null, next, canPropose: true });
    assert.match(allowed, /Le prochain contenu, dans l'ordre prévu : un carnet de voyage illustré/);
    assert.match(allowed, /entre 5,00 € et 12,00 €/);
    assert.match(allowed, /\[\[PROPOSER prix=NN\]\]/);
    const refused = salesSection({ owned: [], pending: null, next, canPropose: false });
    assert.match(refused, /Ne propose aucun contenu dans cette réponse/);
    assert.ok(!refused.includes("5,00 €"));
  });

  it("ne propose un contenu que s'il illustre le sujet en cours", () => {
    const free = salesSection({ owned: [], pending: null, next, canPropose: true });
    assert.match(free, /seulement s'il enrichit naturellement ce dont vous parlez en ce moment/);
    assert.match(free, /Dans le doute, ne le propose pas/);
    assert.match(free, /jamais pour relancer la conversation, combler un silence ou changer de sujet/);
    const themed = salesSection({ owned: [], pending: null, next: { ...next, moment: "quand il parle de voyages" }, canPropose: true });
    assert.match(themed, /Il illustre ce sujet : quand il parle de voyages\. Propose-le seulement si la conversation en cours porte vraiment là-dessus/);
  });

  it("rappelle toujours les garde-fous", () => {
    const text = salesSection({ owned: ["un poème"], pending: { description: "une photo", priceCents: 700 }, next: null, canPropose: false });
    assert.match(text, /la solitude, l'attachement, la culpabilité ou l'urgence/);
    assert.match(text, /difficultés d'argent/);
    assert.match(text, /Aucun contenu ni sous-entendu sexuel/);
    assert.match(text, /Une offre attend sa réponse \(une photo, 7,00 €\)/);
    assert.match(text, /- un poème/);
  });

  it("lit la balise de l'IA et la retire du texte", () => {
    assert.deepEqual(parseProposal("Je t'ai préparé quelque chose.\n[[PROPOSER prix=9,50]]"), {
      text: "Je t'ai préparé quelque chose.",
      proposal: { priceCents: 950 },
    });
    assert.deepEqual(parseProposal("Un cadeau ! [[PROPOSER]]"), { text: "Un cadeau !", proposal: { priceCents: null } });
    assert.deepEqual(parseProposal("Rien à vendre."), { text: "Rien à vendre.", proposal: null });
  });

  it("lit un montant en euros", () => {
    assert.equal(parseEuros("7,50"), 750);
    assert.equal(parseEuros("12 €"), 1200);
    assert.equal(parseEuros("12.5"), 1250);
    assert.equal(parseEuros("douze"), null);
  });

  it("la consigne complète assemble tout, dans l'ordre", () => {
    const system = chatSystemPrompt({
      base: "RÈGLES",
      persona: { nom: "Chloé" },
      person: { name: "Karim" },
      facts: [],
      summary: null,
      sale: { owned: [], pending: null, next, canPropose: true },
      extra: "Parle un peu de cuisine.",
      now,
    });
    const order = ["RÈGLES", "## Ton personnage", "## La personne", "## Ce que tu sais", "## Résumé", "## Vente", "## Consignes de l'équipe", "## Repères"];
    const positions = order.map((h) => system.indexOf(h));
    assert.ok(positions.every((p) => p >= 0), JSON.stringify(positions));
    assert.deepEqual([...positions].sort((a, b) => a - b), positions);
  });
});
