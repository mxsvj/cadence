import type { Metadata, Viewport } from "next";
import { Fraunces, Nunito } from "next/font/google";
import "./globals.css";

const nunito = Nunito({ variable: "--font-nunito", subsets: ["latin"] });
const fraunces = Fraunces({ variable: "--font-fraunces", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Élise",
  description: "Quelqu'un à qui parler, qui se souvient de vous.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // Occuper tout l'écran de l'iPhone, et rétrécir la page quand le clavier
  // s'ouvre, pour que la zone de saisie reste visible.
  viewportFit: "cover",
  interactiveWidget: "resizes-content",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fbf7f2" },
    { media: "(prefers-color-scheme: dark)", color: "#1c1917" },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className={`${nunito.variable} ${fraunces.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
