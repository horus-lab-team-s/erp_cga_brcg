import Link from "next/link";

import { BasculeDeTheme } from "@/app/composants/BasculeDeTheme";

import document from "@/contenu/document.json";
import site from "@/donnees/site.json";

/**
 * L'en-tête et le pied, partagés par toutes les pages écrites en React.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ LA MÊME BARRE EXISTE EN HTML, DANS L'IMPORTATEUR
 *
 * La page du document est engendrée à la construction et servie comme fichier :
 * elle ne passe pas par React, et doit pourtant porter la même barre, sans quoi le
 * lecteur perdrait la navigation en ouvrant le document.
 *
 * Les deux la construisent donc depuis **`donnees/site.json`**. Une barre recopiée
 * dans deux langages diverge au premier onglet ajouté : l'un des deux l'oublie, et
 * la page devient introuvable autrement qu'en la devinant.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export function Entete({ courant }: { courant: string }) {
  return (
    <header className="site-entete">
      <div className="site-entete__barre">
        <span className="site-marque">
          <Link className="site-marque__nom" href="/">
            {site.nom}
          </Link>
          <span className="site-marque__detail">
            document version {document.version} · {document.sections} sections ·{" "}
            {document.figures} figures
          </span>
        </span>
        <nav className="site-nav" aria-label="Sections du site">
          {site.navigation.map((entree) =>
            entree.href === "/document" ? (
              // ⚠️ Une ancre ordinaire, et non `Link` : le document est un fichier servi
              // hors du routeur. Une navigation côté client vers lui chargerait la page
              // sans ses styles, puisque React ne les connaît pas.
              <a
                key={entree.href}
                className={lienActif(entree.href, courant)}
                href={entree.href}
                aria-current={entree.href === courant ? "page" : undefined}
              >
                {entree.libelle}
              </a>
            ) : (
              <Link
                key={entree.href}
                className={lienActif(entree.href, courant)}
                href={entree.href}
                aria-current={entree.href === courant ? "page" : undefined}
              >
                {entree.libelle}
              </Link>
            ),
          )}
        </nav>
        <span className="site-gestes">
          <BasculeDeTheme />
        </span>
      </div>
    </header>
  );
}

function lienActif(href: string, courant: string): string {
  return `site-nav__lien${href === courant ? " est-actif" : ""}`;
}

export function Pied() {
  return (
    <footer className="site-pied">
      <div className="site-pied__contenu">
        <div>
          <h2>Le site</h2>
          {site.navigation.map((entree) => (
            <a key={entree.href} href={entree.href}>
              {entree.libelle}
            </a>
          ))}
        </div>
        <div>
          <h2>Le document</h2>
          <p>
            {document.ligneDeVersion}. Il est la source de ce site : chaque construction le
            relit et engendre la page servie.
          </p>
        </div>
        <div>
          <h2>Conception et réalisation</h2>
          <p>
            <b style={{ color: "var(--encre)" }}>{site.concepteur.nom}</b>
            <br />
            {site.concepteur.titre}
            <br />
            {site.concepteur.role}
          </p>
        </div>
      </div>
    </footer>
  );
}
