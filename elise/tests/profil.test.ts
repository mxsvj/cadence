// Plusieurs messages d'affilée et le profil de discussion (humeur, style,
// sujet) noté tous les 5 messages par un petit modèle.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import type { SupabaseClient } from "@supabase/supabase-js";
import { afterEach, before, describe, it } from "node:test";
import { crossed, memoryDue } from "../lib/memory";
import { PROFILE_EVERY, parseProfile, profileDue, profileSystemPrompt, updateDiscussionProfile } from "../lib/profiling";
import { chatSystemPrompt, personSection } from "../lib/prompts";
import { freshDatabase } from "./db";

const now = new Date("2026-09-28T19:14:00Z");

describe("plusieurs messages d'affilée", () => {
  it("la mémoire se met à jour quand un lot franchit un multiple de 3", () => {
    assert.equal(memoryDue(3, 3), true); // 1, 2, 3 d'un coup
    assert.equal(memoryDue(4, 2), true); // 3 et 4
    assert.equal(memoryDue(5, 2), false); // 4 et 5
    assert.equal(memoryDue(7, 4), true); // 4 à 7 : passe par 6
    assert.equal(memoryDue(0, 0), false);
    assert.equal(crossed(10, 10, 5), true);
    assert.equal(crossed(9, 3, 5), false); // 7, 8, 9
  });

  it("la persona répond à l'ensemble, en un seul message", () => {
    const persona = readFileSync(path.join(import.meta.dirname, "..", "elise-persona.md"), "utf8");
    assert.match(persona.replace(/\s+/g, " "), /plusieurs messages d'affilée, tu les lis tous et tu réponds à l'ensemble, en un seul message/);
  });
});

describe("le profil de discussion", () => {
  it("se met à jour tous les 5 messages de la personne, lots compris", () => {
    assert.equal(PROFILE_EVERY, 5);
    assert.deepEqual([1, 2, 3, 4, 5, 6, 9, 10].map((n) => profileDue(n)), [false, false, false, false, true, false, false, true]);
    assert.equal(profileDue(6, 2), true); // 5 et 6
    assert.equal(profileDue(0), false);
  });

  it("la consigne du petit modèle : listes fermées, rien de sensible", () => {
    const text = profileSystemPrompt();
    assert.match(text, /joyeux, en forme, neutre, fatigué, stressé/);
    assert.match(text, /timide, joueur, direct/);
    assert.match(text, /JAMAIS rien sur la santé .* la religion, l'orientation sexuelle .* l'argent/);
  });

  it("ne garde que des valeurs de la liste et un sujet court, jamais sensible", () => {
    assert.deepEqual(parseProfile('{"humeur": "Fatigué", "style": "timide", "centre_interet": "la randonnée"}'), {
      humeur: "fatigué",
      style: "timide",
      interet: "la randonnée",
    });
    assert.deepEqual(parseProfile('voilà : {"humeur": "déprimé", "style": "séducteur", "centre_interet": "son traitement contre la dépression"}'), {
      humeur: "",
      style: "",
      interet: "",
    });
    assert.equal(parseProfile(`{"centre_interet": "${"a".repeat(81)}"}`).interet, "");
    assert.equal(parseProfile('{"centre_interet": "son salaire"}').interet, "");
    assert.deepEqual(parseProfile("pas de JSON"), { humeur: "", style: "", interet: "" });
    assert.deepEqual(parseProfile("{cassé"), { humeur: "", style: "", interet: "" });
  });

  it("revient dans la consigne du message suivant, seulement pour le ton", () => {
    const text = personSection({ name: "Karim", mood: "fatigué", style: "timide", interest: "la randonnée" }, now);
    assert.match(text, /Ce que tu as remarqué ces derniers messages \(indicatif, ne le dis jamais\) : humeur du moment : fatigué ; style : timide ; sujet qui lui plaît : la randonnée\./);
    assert.match(text, /jamais pour vendre/);
    assert.doesNotMatch(personSection({ name: "Karim" }, now), /Ce que tu as remarqué/);
    const prompt = chatSystemPrompt({ base: "R", facts: [], summary: null, now, sale: null, person: { name: "Karim", style: "joueur" } });
    assert.match(prompt, /style : joueur\./);
  });
});

describe("le petit modèle relit la conversation", () => {
  const realFetch = globalThis.fetch;
  const savedEnv = { ...process.env };
  afterEach(() => {
    globalThis.fetch = realFetch;
    process.env = { ...savedEnv };
  });

  const recent = Array.from({ length: 14 }, (_, i) => ({
    role: i % 2 ? ("assistant" as const) : ("user" as const),
    content: `message ${i + 1}`,
  }));

  function fakeAdmin(saved: Record<string, unknown>[], error: { message: string } | null = null) {
    return {
      from: (table: string) => ({
        upsert: async (row: Record<string, unknown>, options: { onConflict: string }) => {
          assert.equal(table, "contacts");
          assert.equal(options.onConflict, "user_id");
          saved.push(row);
          return { error };
        },
      }),
    } as unknown as SupabaseClient;
  }

  function gemini(text: string, urls: string[], bodies: Record<string, unknown>[]) {
    globalThis.fetch = (async (url: string, init: RequestInit) => {
      urls.push(String(url));
      bodies.push(JSON.parse(String(init.body)));
      return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text }] } }] }), { status: 200 });
    }) as typeof fetch;
  }

  it("avec le petit modèle, sur les 10 derniers messages, et enregistre ce qui est sûr", async () => {
    process.env.GEMINI_API_KEY = "cle";
    delete process.env.LLM_PROVIDER;
    delete process.env.GEMINI_LIGHT_MODEL;
    const urls: string[] = [];
    const bodies: Record<string, unknown>[] = [];
    gemini('{"humeur": "joyeux", "style": "inconnu", "centre_interet": "son chien"}', urls, bodies);
    const saved: Record<string, unknown>[] = [];
    const profile = await updateDiscussionProfile(fakeAdmin(saved), "u1", recent, now);

    assert.deepEqual(profile, { humeur: "joyeux", style: "", interet: "son chien" });
    assert.match(urls[0], /models\/gemini-flash-lite-latest:generateContent$/);
    assert.equal(urls.length, 1);
    const sent = (bodies[0].contents as { parts: { text: string }[] }[])[0].parts[0].text;
    assert.match(sent, /message 5\b/);
    assert.doesNotMatch(sent, /message 4\b/);
    assert.match(sent, /message 14/);
    // Le style incertain ne remplace pas celui déjà noté.
    assert.deepEqual(saved, [{ user_id: "u1", profil_maj_le: now.toISOString(), humeur: "joyeux", centre_interet: "son chien" }]);
  });

  it("GEMINI_LIGHT_MODEL choisit un autre petit modèle ; une erreur d'enregistrement remonte", async () => {
    process.env.GEMINI_API_KEY = "cle";
    process.env.GEMINI_LIGHT_MODEL = "gemini-2.5-flash-lite";
    delete process.env.LLM_PROVIDER;
    const urls: string[] = [];
    gemini('{"humeur": "neutre"}', urls, []);
    await assert.rejects(updateDiscussionProfile(fakeAdmin([], { message: "colonne absente" }), "u1", recent, now), /colonne absente/);
    assert.match(urls[0], /models\/gemini-2\.5-flash-lite:generateContent$/);
  });
});

describe("le profil dans la base", () => {
  const KARIM = "cccccccc-cccc-cccc-cccc-cccccccccccc";
  let base: Awaited<ReturnType<typeof freshDatabase>>;
  before(async () => {
    base = await freshDatabase([{ id: KARIM, email: "karim@example.com" }]);
  });

  it("n'accepte que les mots de la liste, et s'efface avec ses données", async () => {
    await base.as(
      "service",
      `insert into public.contacts (user_id, humeur, style_discussion, centre_interet, profil_maj_le)
       values ($1, 'fatigué', 'timide', 'la randonnée', now())
       on conflict (user_id) do update set humeur = excluded.humeur, style_discussion = excluded.style_discussion,
         centre_interet = excluded.centre_interet, profil_maj_le = excluded.profil_maj_le`,
      [KARIM],
    );
    await assert.rejects(base.as("service", "update public.contacts set humeur = 'déprimé' where user_id = $1", [KARIM]), /check constraint/);
    await assert.rejects(base.as("service", "update public.contacts set style_discussion = 'séducteur' where user_id = $1", [KARIM]), /check constraint/);
    await assert.rejects(base.as("service", `update public.contacts set centre_interet = '${"a".repeat(81)}' where user_id = $1`, [KARIM]), /check constraint/);
    // La personne elle-même ne lit pas sa fiche.
    assert.deepEqual(await base.as(KARIM, "select humeur from public.contacts"), []);

    await base.as(KARIM, "select public.effacer_mes_donnees()");
    const [row] = await base.as<{ humeur: string; style_discussion: string; centre_interet: string; profil_maj_le: string | null }>(
      "service",
      "select humeur, style_discussion, centre_interet, profil_maj_le from public.contacts where user_id = $1",
      [KARIM],
    );
    assert.deepEqual(row, { humeur: "", style_discussion: "", centre_interet: "", profil_maj_le: null });
  });
});
