import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // La persona est lue sur le disque au moment de répondre : on s'assure
  // qu'elle part bien avec le code sur le serveur.
  outputFileTracingIncludes: {
    "/**": ["./elise-persona.md"],
  },
};

export default nextConfig;
