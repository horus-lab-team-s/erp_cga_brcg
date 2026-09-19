import type { Metadata, Viewport } from "next";

import "./globals.css";

import document from "@/contenu/document.json";
import site from "@/donnees/site.json";

/**
 * La page HTML qui accueille le site.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * CE QU'ELLE SERT, ET CE QU'ELLE NE SERT PAS
 *
 * ⚠️ **Elle ne sert pas le document.** L'adresse `/document` est réécrite vers
 * `public/document.html`, engendré à la construction : voir `next.config.ts`, qui dit
 * ce que le rendu React coûtait en double. Cette mise en page habille les pages du
 * site, et garde les métadonnées à un seul endroit.
 *
 * ⚠️ **Le thème est posé avant le premier rendu.** Posé après, la page s'afficherait
 * claire une fraction de seconde avant de virer au sombre, ce qui est exactement ce
 * qu'un lecteur en mode sombre déteste. Le script est minuscule et bloquant, et c'est
 * le seul endroit du site où cela se justifie.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export const metadata: Metadata = {
  title: {
    default: `${site.nom} · conception`,
    template: `%s · ${site.nom}`,
  },
  description: site.accroche,
  authors: [{ name: site.concepteur.nom }],
  openGraph: {
    title: `${site.nom} · conception`,
    description: site.accroche,
    type: "article",
    locale: "fr_FR",
  },
  // Le dossier décrit l'organisation interne d'un cabinet : il se partage par son
  // adresse, il ne se cherche pas sur un moteur.
  robots: { index: false, follow: false },
  other: { "document-version": String(document.version) },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f7f8fa" },
    { media: "(prefers-color-scheme: dark)", color: "#0b1117" },
  ],
};

export default function Racine({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap"
        />
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var t=localStorage.getItem('cga-theme');if(t){document.documentElement.dataset.theme=t;}}catch(e){}",
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
