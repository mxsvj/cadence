import type { MetadataRoute } from "next";

// Permet d'ajouter Élise à l'écran d'accueil du téléphone, comme une app.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Élise",
    short_name: "Élise",
    description: "Quelqu'un à qui parler, qui se souvient de vous.",
    lang: "fr",
    start_url: "/",
    display: "standalone",
    background_color: "#fbf7f2",
    theme_color: "#fbf7f2",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
