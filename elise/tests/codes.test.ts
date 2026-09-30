// Le code d'entrée unique : sa forme, sa comparaison, et qui peut le lire ou
// le changer dans la base.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { CODE_ALPHABET, formatCode, newCode, normalizeCode } from "../lib/access-code";
import { codeEmail, sameCode } from "../lib/code-login";
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

describe("vérifier le code", () => {
  it("le même code passe, tout autre est refusé", () => {
    assert.equal(sameCode("ABCDEFGH", normalizeCode("abcd-efgh")), true);
    assert.equal(sameCode("ABCDEFGH", "ABCDEFGJ"), false);
    assert.equal(sameCode("ABCDEFGH", "ABCD"), false);
    assert.equal(sameCode(null, "ABCDEFGH"), false); // pas encore de code : personne n'entre
    assert.equal(sameCode(null, null), false);
  });

  it("un compte de test n'a pas d'adresse e-mail réelle", () => {
    const a = codeEmail();
    assert.match(a, /^client-[0-9a-f-]{36}@code\.elise\.invalid$/);
    assert.notEqual(codeEmail(), a);
  });
});

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const NADIA = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";

describe("le code dans la base", () => {
  let base: Awaited<ReturnType<typeof freshDatabase>>;
  const one = async <T>(user: string | null, sql: string, params: unknown[] = []) =>
    (await base.as<{ r: T }>(user, sql, params))[0].r;
  before(async () => {
    base = await freshDatabase([
      { id: ADMIN, email: "admin@example.com" },
      { id: NADIA, email: "client-1@code.elise.invalid" },
    ]);
    await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
  });

  it("à la première visite de l'équipe, le code proposé devient le code, puis ne bouge plus", async () => {
    const first = await one<{ code: string }>(ADMIN, "select public.admin_code_entree('ABCD-EFGH') as r");
    assert.equal(first.code, "ABCD-EFGH");
    const again = await one<{ code: string }>(ADMIN, "select public.admin_code_entree('WXYZ-2345') as r");
    assert.equal(again.code, "ABCD-EFGH");
  });

  it("l'équipe change le code ; un code mal formé est refusé", async () => {
    const changed = await one<{ code: string }>(ADMIN, "select public.admin_changer_code_entree('WXYZ-2345') as r");
    assert.equal(changed.code, "WXYZ-2345");
    assert.equal((await one<{ code: string }>(ADMIN, "select public.admin_code_entree('ABCD-EFGH') as r")).code, "WXYZ-2345");
    for (const bad of ["1234", "abcd-efgh", "ABCD-EFG0", "ABCDEFGH"]) {
      await assert.rejects(base.as(ADMIN, "select public.admin_changer_code_entree($1)", [bad]), /check constraint/, bad);
    }
    const [{ n }] = await base.as<{ n: number }>("service", "select count(*)::integer as n from public.entry_code");
    assert.equal(n, 1); // un seul code à la fois
  });

  it("personne d'autre ne lit ni ne change le code, seul le serveur le vérifie", async () => {
    for (const user of [NADIA, null]) {
      await assert.rejects(base.as(user, "select code from public.entry_code"), /permission denied/);
    }
    await assert.rejects(base.as(ADMIN, "select code from public.entry_code"), /permission denied/);
    await assert.rejects(base.as(NADIA, "select public.admin_code_entree('ABCD-EFGH')"), /Réservé/);
    await assert.rejects(base.as(NADIA, "select public.admin_changer_code_entree('ABCD-EFGH')"), /Réservé/);
    await assert.rejects(base.as(null, "select public.admin_changer_code_entree('ABCD-EFGH')"), /permission denied/);
    const [{ code }] = await base.as<{ code: string }>("service", "select code from public.entry_code where id = 1");
    assert.equal(code, "WXYZ-2345");
  });
});
