// Le profil de Katherine (supabase/katherine.sql) : il se charge après
// schema.sql, se relance sans doublon, et passe tel quel dans l'onglet
// Créatrices (rien n'est tronqué à l'enregistrement).
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { before, describe, it } from "node:test";
import { firstMessageFor } from "../lib/conversation";
import { sanitizePersona, type PersonaProfile } from "../lib/persona-profile";
import { personaSection } from "../lib/prompts";
import { freshDatabase } from "./db";

const sql = readFileSync(path.join(import.meta.dirname, "..", "supabase", "katherine.sql"), "utf8");
let rows: { id: number; persona: PersonaProfile; first_message: string; active: boolean }[];

before(async () => {
  const base = await freshDatabase([]);
  await base.db.exec(sql);
  await base.db.exec(sql); // relançable
  rows = (await base.db.query<(typeof rows)[number]>("select id, persona, first_message, active from public.creators where persona ->> 'nom' = 'Katherine'")).rows;
});

describe("Katherine", () => {
  it("existe une seule fois, en ligne, 24 ans", () => {
    assert.equal(rows.length, 1);
    assert.equal(rows[0].active, true);
    assert.equal(rows[0].persona.age, 24);
  });

  it("son profil passe tel quel dans l'onglet Créatrices", () => {
    const { persona, error } = sanitizePersona(rows[0].persona);
    assert.equal(error, undefined);
    assert.deepEqual(persona, rows[0].persona);
  });

  it("son premier message dit tout de suite qu'elle est une IA, et engage la conversation", () => {
    const text = firstMessageFor(rows[0]);
    assert.match(text, /^Coucou ! Moi c'est Katherine/);
    assert.match(text, /je suis une intelligence artificielle/);
    assert.match(text, /\?$/);
  });

  it("sa personnalité arrive dans la consigne, sous les règles de base", () => {
    const section = personaSection(rows[0].persona, {});
    assert.match(section, /## Ta personnalité et ta façon d'écrire/);
    assert.match(section, /sans jamais enfreindre les règles de base/);
    assert.match(section, /Tu es solaire/);
    assert.match(section, /Complice, jamais séductrice/);
    assert.match(section, /tu réponds franchement que tu es une IA/);
  });
});
