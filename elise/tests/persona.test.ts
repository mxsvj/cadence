import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { parseEuros, parseProposal } from "../lib/offers";
import { sanitizePersona } from "../lib/persona-profile";
import { readFileSync } from "node:fs";
import { chatSystemPrompt, genderRule, negotiationSection, personSection, personaSection, saidItsAnAi, salesSection, type SalePrompt } from "../lib/prompts";

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

  it("parle d'elle au féminin (une créatrice sans genre réglé aussi), d'un homme au masculin", () => {
    for (const genre of ["Femme", undefined, " femme "]) {
      const rule = genderRule(genre, 24);
      assert.match(rule, /Ton personnage est une femme, et ça doit s'entendre dans chaque message/);
      assert.match(rule, /Tu parles de toi au féminin, sans exception \(« contente de te lire », « fatiguée ce soir… »/);
      assert.match(rule, /jamais plus d'un par message/);
      assert.match(rule, /comme une femme de 24 ans qui écrit à quelqu'un qu'elle apprécie : chaleureuse et expressive/);
      assert.match(rule, /pas de « Re ! », « La forme \? »/);
      assert.match(rule, /Féminine ne veut pas dire séductrice : ni drague, ni sous-entendu/);
    }
    assert.match(genderRule("Femme"), /comme une femme de ton âge/);
    assert.match(genderRule("Homme"), /Tu parles de toi au masculin/);
    assert.match(genderRule("Non binaire"), /tournures qui ne marquent pas le genre/);
    assert.match(genderRule("Femme trans"), /une femme/);
    assert.match(genderRule("Autre"), /Le genre de ton personnage : Autre/);
    assert.match(personaSection(persona, {}), /comme une femme de 29 ans/);
    assert.match(personaSection({}, {}), /Tu parles de toi au féminin/);
  });

  it("les règles de base : une vraie messagerie, pas un assistant, et les limites intactes", () => {
    const base = readFileSync(new URL("../elise-persona.md", import.meta.url), "utf8");
    assert.match(base, /pas comme un assistant/);
    assert.match(base, /jamais deux\s+questions dans le même/);
    assert.match(base, /Tu ne caches jamais que tu es une IA/);
    assert.match(base, /jamais de contenu ni\s+de sous-entendu sexuel/);
    assert.match(base, /Tu ne proposes jamais de rencontre/);
    assert.match(base, /le 3114/);
    assert.doesNotMatch(base, /Tu reformules avec tes mots/);
    assert.match(base, /tu n'imites jamais un style sec ou abrupt/);
    // Écouter avec les réflexes d'une psy, sans jamais se dire psychologue.
    assert.match(base, /## Écouter quand la personne se confie/);
    assert.match(base, /Tu n'es pas psychologue et tu ne le prétends jamais/);
    assert.match(base, /pas de diagnostic, pas de traitement/);
    assert.match(base, /en parler à un professionnel/);
    // Faire vivre la conversation, sans jamais retenir la personne qui s'en va.
    assert.match(base, /Tu ne fermes jamais la conversation\s+toi-même/);
    assert.match(base, /tu la laisses partir chaleureusement, sans la\s+retenir ni la culpabiliser/);
    // Le style messagerie : ultra-court, pas de chatbot, un emoji au plus, et les numéros d'aide passent avant la longueur.
    assert.match(base, /Tu n'es pas une assistante virtuelle : tu n'es pas là pour rendre\s+service, tu es là pour partager un moment de vie/);
    assert.match(base, /une ou deux phrases,\s+jamais plus/);
    assert.match(base, /tu entres directement dans le vif du\s+sujet/);
    assert.match(base, /pas une question à la fin de chaque\s+message par réflexe/);
    assert.match(base, /« jsais pas »/);
    // Les abréviations des textos, sans rien d'affectueux.
    for (const abbr of ["« cc » (coucou)", "« mdr »", "« tkt »", "« jsp »", "« chui »", "« vrmt »"]) assert.ok(base.includes(abbr), abbr);
    assert.match(base, /Mets-en\s+dans presque chaque message, deux ou trois/);
    // S'adapter à son style, jamais pour le faire courir après elle ; recadrer une demande intime.
    assert.match(base, /Tu t'adaptes à son style/);
    assert.match(base, /pas de\s+chaud-froid, pas de manque entretenu, pas de jalousie/);
    assert.match(base, /Tu n'inventes pas de scène intime/);
    assert.match(base, /ahah non, ça c'est pas le genre de photos que j'envoie/);
    assert.match(base, /Jamais d'abréviation\s+affectueuse ou amoureuse \(« jtm »,\s+« bsx »/);
    assert.match(base, /Tu tutoies, comme sur WhatsApp/);
    assert.match(base, /Le classique\.\.\. Courage/);
    assert.match(base, /si elle est en\s+danger, tu\s+donnes toujours les numéros d'aide/);
    for (const banned of [/« Je\s+comprends… »/, /« En tant que… »/, /« Comment puis-je t'aider \? »/, /« N'hésite pas à partager… »/]) {
      assert.match(base, banned);
    }
    assert.match(base, /au plus un par message, et pas à chaque message/);
    assert.match(base, /Je viens de me\s+poser dans mon canapé avec un thé/);
  });

  it("par défaut, le personnage s'appelle Élise", () => {
    assert.match(personaSection({}, {}), /Nom : Élise/);
  });

  it("ses emojis préférés : des emojis seulement, sans ceux qui sont refusés", () => {
    assert.equal(sanitizePersona({ emojis: "🍵 du thé ✨ 🍑" }).persona.emojis, "🍵 ✨");
    assert.equal(sanitizePersona({ emojis: "rien" }).persona.emojis, undefined);
    const prompt = chatSystemPrompt({ base: "Règles.", persona: { nom: "Kath", emojis: "🍵 ✨" }, person: {}, facts: [], summary: null, now });
    assert.match(prompt, /de préférence les tiens \(🍵 ✨\)/);
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

describe("pas de message d'accueil : elle dit qu'elle est une IA en passant", () => {
  const base = { base: "Règles.", facts: [], summary: null, now };

  it("tant qu'elle ne l'a pas dit, la consigne le lui demande dans cette réponse", () => {
    const prompt = chatSystemPrompt({ ...base, introduce: true });
    assert.match(prompt, /## Dire que tu es une IA/);
    assert.match(prompt, /glisse-le dans cette réponse, naturellement et en passant/);
    assert.doesNotMatch(chatSystemPrompt(base), /## Dire que tu es une IA/);
  });

  it("repère qu'elle l'a déjà dit (et pas quand c'est la personne qui en parle)", () => {
    assert.equal(saidItsAnAi([{ role: "assistant", content: "au fait, je suis une IA, mais une IA bavarde" }]), true);
    assert.equal(saidItsAnAi([{ role: "assistant", content: "Je suis une intelligence artificielle 😄" }]), true);
    assert.equal(saidItsAnAi([{ role: "user", content: "t'es une IA ?" }, { role: "assistant", content: "coucou !" }]), false);
    assert.equal(saidItsAnAi([{ role: "assistant", content: "j'adore la Sicilia" }]), false);
  });
});

describe("sa réaction à une contre-offre", () => {
  const bid = { description: "Un carnet (2 photos)", basePriceCents: 800, minCents: 500, bidCents: 600, finalPriceCents: 600, triesLeft: null };

  it("acceptée : avec enthousiasme, sans jamais dire le minimum à la personne", () => {
    const text = negotiationSection({ ...bid, accepted: true });
    assert.match(text, /^## Sa contre-offre/);
    assert.match(text, /te proposer 6,00 € pour ton contenu \(Un carnet \(2 photos\)\), affiché à 8,00 €/);
    assert.match(text, /Le minimum que l'équipe accepte est 5,00 € : c'est un repère pour toi, ne le dis jamais/);
    assert.match(text, /C'est accepté : le contenu est à elle pour 6,00 €/);
    assert.match(text, /allez, ça marche pour cette fois/);
  });

  it("refusée : de façon joueuse, jamais sous le minimum, sans pousser", () => {
    const text = negotiationSection({ ...bid, bidCents: 300, accepted: false, finalPriceCents: 800, triesLeft: 2 });
    assert.match(text, /refuse gentiment, de façon joueuse/);
    assert.match(text, /ahah bien tenté/);
    assert.match(text, /Ne descends jamais sous le minimum et ne le dis pas/);
    assert.match(text, /sans insister ni la pousser/);
    assert.match(negotiationSection({ ...bid, bidCents: 300, accepted: false, finalPriceCents: 800, triesLeft: 0 }), /Elle ne peut plus faire de proposition/);
  });

  it("en créatrice, sans vocabulaire de commerçant ni jeu sur l'attachement", () => {
    const text = negotiationSection({ ...bid, accepted: true });
    assert.match(text, /jamais de vocabulaire de commerçant ou de système de paiement/);
    assert.match(text, /pas de « juste parce que c'est toi »/);
    const prompt = chatSystemPrompt({ base: "R", facts: [], summary: null, now, sale: null, bid: { ...bid, accepted: true } });
    assert.match(prompt, /## Sa contre-offre/);
    assert.match(prompt, /Ne propose aucun contenu et n'écris aucune balise/);
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
    assert.match(text, /uniquement ceux-là, selon la discussion \(au plus un par message, et pas à chaque message\) : 😊 🌿/);
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
    const order = ["## Maintenant", "RÈGLES", "## Ton personnage", "## La personne", "## Ce que tu sais", "## Résumé", "## Vente", "## Consignes de l'équipe", "## Repères"];
    const positions = order.map((h) => system.indexOf(h));
    assert.ok(positions.every((p) => p >= 0), JSON.stringify(positions));
    assert.deepEqual([...positions].sort((a, b) => a - b), positions);
  });
});
