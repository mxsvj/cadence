// Essai du « cerveau » d'Élise, sans base de données ni site :
//   npm run essai:llm
// Lit les clés dans .env.local, envoie la persona et un début de conversation
// fictive au modèle choisi par LLM_PROVIDER, et affiche la réponse.

import { loadEnvConfig } from "@next/env";

loadEnvConfig(process.cwd());

async function main() {
  const { generate } = await import("../lib/llm");
  const { getPersona, getFirstMessage } = await import("../lib/persona");

  const first = getFirstMessage();
  const userMessage =
    process.argv.slice(2).join(" ") ||
    "Bonsoir. Moi c'est Karim, tu peux me tutoyer. Première semaine sans les enfants depuis la séparation, l'appart est bien silencieux.";

  console.log(`Fournisseur : ${process.env.LLM_PROVIDER ?? "gemini"}\n`);
  console.log(`Élise (premier message) :\n${first}\n`);
  console.log(`Utilisateur :\n${userMessage}\n`);

  const start = Date.now();
  const reply = await generate({
    system: getPersona(),
    messages: [
      { role: "assistant", content: first },
      { role: "user", content: userMessage },
    ],
    maxTokens: 400,
  });
  console.log(`Élise (${((Date.now() - start) / 1000).toFixed(1)} s) :\n${reply}`);
}

main().catch((err) => {
  console.error(`\nÉchec : ${err instanceof Error ? err.message : err}`);
  process.exit(1);
});
