// Les codes d'accès des clients (comme une carte de médiathèque) : leur forme,
// leur empreinte, et qui peut les lire dans la base.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { CODE_ALPHABET, formatCode, newCode, normalizeCode } from "../lib/access-code";
import { codeEmail, codeHash } from "../lib/code-login";
import { freshDatabase } from "./db";

describe("la forme d'un code", () => {
  it("8 caractères sans ceux qu'on confond, affichés ABCD-EFGH", () => {
    const seen = new Set<string>();
    for (let i = 0; i < 500; i++) {
      const code = newCode();
      assert.match(code, /^[A-Z2-9]{4}-[A-Z2-9]{4}$/);
      assert.ok([...code.replace("-", "")].every((c) => CODE_ALPHABET.includes(c)), code);
      seen.add(code);
    }
    assert.equal(seen.size, 500); // 31^8 possibilités : pas de doublon
    for (const c of "01ILO") assert.ok(!CODE_ALPHABET.includes(c), c);
  });

  it("ce que la personne tape : minuscules, espaces et tirets acceptés", () => {
    assert.equal(normalizeCode("abcd-efgh"), "ABCDEFGH");
    assert.equal(normalizeCode(" AB CD EF GH "), "ABCDEFGH");
    assert.equal(normalizeCode("abcd—efgh"), "ABCDEFGH");
    assert.equal(formatCode("abcdefgh"), "ABCD-EFGH");
  });

  it("refuse ce qui ne peut pas être un code", () => {
    for (const bad of ["", "ABC", "ABCD-EFGH-J", "ABCD-EFG0", "ABCD-EFGI", "ÀBCD-EFGH", null, 12345678]) {
      assert.equal(normalizeCode(bad), null, String(bad));
    }
  });
});

describe("l'empreinte d'un code", () => {
  it("dépend du code et de la clé secrète, sans jamais contenir le code", () => {
    const h = codeHash("ABCDEFGH", "cle-1");
    assert.match(h, /^[0-9a-f]{64}$/);
    assert.equal(codeHash("ABCDEFGH", "cle-1"), h);
    assert.notEqual(codeHash("ABCDEFGJ", "cle-1"), h);
    assert.notEqual(codeHash("ABCDEFGH", "cle-2"), h); // changer la clé secrète invalide les codes
    assert.ok(!h.includes("ABCDEFGH"));
  });

  it("sans clé secrète, rien n'est vérifié", () => {
    assert.throws(() => codeHash("ABCDEFGH", ""), /SUPABASE_SECRET_KEY/);
  });

  it("un compte de client n'a pas d'adresse e-mail réelle", () => {
    const a = codeEmail();
    assert.match(a, /^client-[0-9a-f-]{36}@code\.elise\.invalid$/);
    assert.notEqual(codeEmail(), a);
  });
});

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const NADIA = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const HASH = "a".repeat(64);

describe("les codes dans la base", () => {
  let base: Awaited<ReturnType<typeof freshDatabase>>;
  before(async () => {
    base = await freshDatabase([
      { id: ADMIN, email: "admin@example.com" },
      { id: NADIA, email: "client-1@code.elise.invalid" },
    ]);
    await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
    await base.as("service", "insert into public.access_codes (user_id, code_hash, hint, label, created_by) values ($1, $2, 'EFGH', 'Nadia', $3)", [
      NADIA,
      HASH,
      ADMIN,
    ]);
  });

  it("un client ne lit ni n'écrit aucun code, pas même le sien", async () => {
    await assert.rejects(base.as(NADIA, "select * from public.access_codes"), /permission denied/);
    await assert.rejects(base.as(null, "select 1 from public.access_codes"), /permission denied/);
    await assert.rejects(base.as(NADIA, "update public.access_codes set code_hash = $1", ["b".repeat(64)]), /permission denied/);
    await assert.rejects(
      base.as(NADIA, "insert into public.access_codes (user_id, code_hash) values ($1, $2)", [NADIA, "c".repeat(64)]),
      /permission denied/,
    );
    await assert.rejects(base.as(NADIA, "select public.admin_codes()"), /Réservé/);
  });

  it("l'équipe voit à qui est chaque code, jamais l'empreinte", async () => {
    await assert.rejects(base.as(ADMIN, "select code_hash from public.access_codes"), /permission denied/);
    const [{ r }] = await base.as<{ r: Record<string, unknown>[] }>(ADMIN, "select public.admin_codes() as r");
    assert.equal(r.length, 1);
    assert.deepEqual(Object.keys(r[0]).sort(), ["cree_le", "hint", "label", "nom", "user_id", "utilise_le"]);
    assert.equal(r[0].nom, "Nadia");
    assert.equal(r[0].hint, "EFGH");
    // Le prénom choisi à la première entrée l'emporte sur l'étiquette de l'équipe.
    await base.db.query("insert into public.profiles (user_id, display_name, birthdate) values ($1, 'Nad', '1979-06-02')", [NADIA]);
    const [{ r: again }] = await base.as<{ r: { nom: string }[] }>(ADMIN, "select public.admin_codes() as r");
    assert.equal(again[0].nom, "Nad");
  });

  it("une seule empreinte par code, un seul code par client", async () => {
    await assert.rejects(
      base.as("service", "insert into public.access_codes (user_id, code_hash) values ($1, $2)", [ADMIN, HASH]),
      /duplicate key/,
    );
    await assert.rejects(
      base.as("service", "insert into public.access_codes (user_id, code_hash) values ($1, $2)", [NADIA, "d".repeat(64)]),
      /duplicate key/,
    );
    await assert.rejects(base.as("service", "insert into public.access_codes (user_id, code_hash) values ($1, 'court')", [ADMIN]), /check constraint/);
  });

  it("supprimer le compte supprime son code", async () => {
    await base.db.query("delete from auth.users where id = $1", [NADIA]);
    const rows = await base.as("service", "select * from public.access_codes");
    assert.deepEqual(rows, []);
  });
});
