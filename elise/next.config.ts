import type { NextConfig } from "next";

// En-têtes de sécurité envoyés avec chaque page : le site ne peut pas être
// affiché dans le cadre d'un autre site (hameçonnage par superposition), le
// navigateur ne devine pas le type des fichiers, l'adresse complète d'une
// page (et le lien secret de l'équipe) n'est jamais transmise à un autre
// site, et ni caméra, ni micro, ni position ne sont demandés.
const SECURITY_HEADERS = [
  { key: "Content-Security-Policy", value: "frame-ancestors 'none'; base-uri 'self'; object-src 'none'" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), browsing-topics=()" },
  { key: "Strict-Transport-Security", value: "max-age=63072000" },
];

const nextConfig: NextConfig = {
  // Ne pas annoncer « Next.js » à qui cherche une faille connue.
  poweredByHeader: false,
  // La persona est lue sur le disque au moment de répondre : on s'assure
  // qu'elle part bien avec le code sur le serveur.
  outputFileTracingIncludes: {
    "/**": ["./elise-persona.md"],
  },
  async headers() {
    return [{ source: "/(.*)", headers: SECURITY_HEADERS }];
  },
};

export default nextConfig;
