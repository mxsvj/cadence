// Les messages du script : ce qu'ils contiennent, comment on l'annonce sans
// rien montrer, et ce que l'IA doit dire en les proposant.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { contentLabel, describeStep, mainType, mediaCounts, type MediaItem, type Step } from "../lib/offers";
import { salesSection } from "../lib/prompts";

const pack: MediaItem[] = [
  { path: "a.jpg", kind: "image" },
  { path: "b.jpg", kind: "image" },
  { path: "c.mp4", kind: "video" },
];

const step = (over: Partial<Step>): Step => ({
  id: 1,
  script_id: 1,
  position: 1,
  title: "Titre interne",
  content_type: "image",
  content_text: "",
  media: [],
  ai_description: "",
  message_mode: "ia",
  message_text: "",
  trigger_mode: "ia",
  is_paid: true,
  price_cents: 900,
  min_price_cents: 600,
  max_price_cents: 1200,
  ...over,
});

describe("ce que contient un message du script", () => {
  it("se compte et s'annonce sans rien montrer", () => {
    assert.deepEqual(mediaCounts(pack), { photos: 2, videos: 1 });
    assert.equal(contentLabel(2, 1), "2 photos et 1 vidéo");
    assert.equal(contentLabel(1, 0), "1 photo");
    assert.equal(contentLabel(0, 3), "3 vidéos");
    assert.equal(contentLabel(0, 0), "un texte");
  });

  it("a pour type principal la vidéo s'il y en a une, sinon la photo, sinon le texte", () => {
    assert.equal(mainType(pack), "video");
    assert.equal(mainType(pack.slice(0, 2)), "image");
    assert.equal(mainType([]), "texte");
  });

  it("se décrit à l'IA avec sa description et son contenu, jamais son titre interne", () => {
    const d = describeStep(step({ media: pack, ai_description: "des photos du lac" }));
    assert.equal(d, "des photos du lac (2 photos et 1 vidéo)");
    assert.ok(!d.includes("Titre interne"));
    assert.equal(describeStep(step({ media: [] })), "un texte");
  });
});

describe("ce que l'IA dit avec", () => {
  const base = {
    owned: [],
    pending: null,
    canPropose: true,
    next: { description: "des photos du lac (2 photos)", isPaid: true, priceCents: 900, minCents: 600, maxCents: 1200, messageMode: "ia" as const },
  };

  it("suit la consigne de l'équipe, reformulée", () => {
    const text = salesSection({ ...base, next: { ...base.next, instruction: "dis que tu les as prises pour lui" } });
    assert.match(text, /Ce que l'équipe veut que tu dises en le proposant, à reformuler avec tes mots, sans rien y ajouter : « dis que tu les as prises pour lui »/);
    assert.match(text, /jamais/); // les garde-fous restent
  });

  it("sans consigne, présente le contenu librement", () => {
    assert.match(salesSection(base), /présente le contenu en une ou deux phrases/);
  });

  it("en mot pour mot, n'annonce pas le prix elle-même", () => {
    assert.match(salesSection({ ...base, next: { ...base.next, messageMode: "fixe" } }), /message écrit par l'équipe/);
  });
});
