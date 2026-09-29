import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";
import { MIN_ACCESS_KEY, accessKey, sameKey } from "../lib/team-access";

describe("le lien secret de l'équipe", () => {
  const saved = process.env.ADMIN_ACCESS_KEY;
  afterEach(() => {
    if (saved === undefined) delete process.env.ADMIN_ACCESS_KEY;
    else process.env.ADMIN_ACCESS_KEY = saved;
  });

  it("reste désactivé sans clé, ou avec une clé trop courte", () => {
    delete process.env.ADMIN_ACCESS_KEY;
    assert.equal(accessKey(), null);
    process.env.ADMIN_ACCESS_KEY = "   ";
    assert.equal(accessKey(), null);
    process.env.ADMIN_ACCESS_KEY = "a".repeat(MIN_ACCESS_KEY - 1);
    assert.equal(accessKey(), null);
  });

  it("accepte une clé assez longue, sans les espaces autour", () => {
    const key = "Zq7vR2mK9xLp4TsW8nYb3cHf6Jd1";
    process.env.ADMIN_ACCESS_KEY = `  ${key}\n`;
    assert.equal(accessKey(), key);
  });

  it("ne reconnaît que la clé exacte", () => {
    const key = "Zq7vR2mK9xLp4TsW8nYb3cHf6Jd1";
    assert.equal(sameKey(key, key), true);
    assert.equal(sameKey("", key), false);
    assert.equal(sameKey(key.slice(0, -1), key), false);
    assert.equal(sameKey(`${key}x`, key), false);
    assert.equal(sameKey(key.toLowerCase(), key), false);
  });
});
