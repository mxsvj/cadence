// Les emojis d'une créatrice avec une personne : ce qui est gardé, ce que
// l'IA reçoit selon le réglage choisi.
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EMOJI_GROUPS, cleanEmojis, emojiInstruction, emojiSummary, splitEmojis } from "../lib/emojis";

describe("la liste d'emojis", () => {
  it("ne garde que les emojis, une seule fois chacun", () => {
    assert.equal(cleanEmojis("😊 bonjour 🌸🌸 ☕ ❤️ ❤️"), "😊 🌸 ☕ ❤️");
    assert.equal(cleanEmojis(42), "");
  });

  it("garde les emojis composés entiers", () => {
    assert.deepEqual(splitEmojis("❤️‍🔥🧘‍♀️🇫🇷"), ["❤️‍🔥", "🧘‍♀️", "🇫🇷"]);
  });

  it("refuse les sous-entendus sexuels, même collés à la main", () => {
    assert.equal(cleanEmojis("🍑 😊 🍆 💦 👅 🔞"), "😊");
  });

  it("le catalogue ne propose que des emojis acceptés", () => {
    for (const group of EMOJI_GROUPS) {
      for (const emoji of group.emojis.split(" ")) assert.equal(cleanEmojis(emoji), emoji, `${group.label} : ${emoji}`);
    }
  });
});

describe("ce que l'IA reçoit", () => {
  it("au choix de l'IA : selon la discussion, un au plus par message", () => {
    assert.match(emojiInstruction("libre", "😊"), /à toi de choisir ceux qui vont avec la discussion/);
    assert.match(emojiInstruction(undefined, ""), /à toi de choisir/);
    assert.match(emojiInstruction("libre", ""), /au plus un par message, et pas à chaque message/);
    assert.equal(emojiSummary("libre", "😊"), "au choix de l'IA");
  });

  it("au choix de l'IA : de préférence les emojis préférés de la créatrice (sans ceux qui sont refusés)", () => {
    assert.match(emojiInstruction("libre", "", "🍵 ✨ 🍑"), /de préférence les tiens \(🍵 ✨\), ou d'autres qui vont avec la discussion ; au plus un par message/);
    // La liste choisie pour la personne l'emporte toujours.
    assert.doesNotMatch(emojiInstruction("choisis", "😊", "🍵"), /🍵/);
    assert.equal(emojiInstruction("aucun", "", "🍵"), "- N'utilise aucun emoji avec elle.");
  });

  it("seulement ceux-là", () => {
    assert.match(emojiInstruction("choisis", "😊 🌸"), /uniquement ceux-là, selon la discussion \(au plus un par message, et pas à chaque message\) : 😊 🌸/);
    assert.equal(emojiSummary("choisis", "😊 🌸"), "😊 🌸");
  });

  it("aucun, ou une liste vide", () => {
    assert.equal(emojiInstruction("aucun", "😊"), "- N'utilise aucun emoji avec elle.");
    assert.equal(emojiInstruction("choisis", " "), "- N'utilise aucun emoji avec elle.");
    assert.equal(emojiSummary("choisis", ""), "aucun");
  });
});
