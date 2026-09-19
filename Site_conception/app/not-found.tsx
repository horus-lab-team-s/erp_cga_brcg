import type { Metadata } from "next";

import { Entete, Pied } from "@/app/composants/Coquille";
import { Carte } from "@/app/composants/Bouts";
import site from "@/donnees/site.json";

export const metadata: Metadata = { title: "Page introuvable" };

/**
 * Une adresse inconnue.
 *
 * ⚠️ Elle propose les quatre portes du site plutôt qu'un seul lien de retour : un
 * lecteur qui arrive ici vient souvent d'un lien ancien, et lui rendre la navigation
 * complète coûte trois lignes.
 */
export default function Introuvable() {
  return (
    <>
      <Entete courant="" />
      <main className="page page--etroite">
        <section className="bandeau">
          <p className="bandeau__oeil">Adresse inconnue</p>
          <h1>Cette page n&apos;existe pas</h1>
          <p className="bandeau__chapo">
            Elle a peut-être changé d&apos;adresse, ou le lien qui vous a mené ici est ancien.
            Voici tout ce que porte ce site.
          </p>
        </section>
        <section className="bloc">
          <div className="grille">
            {site.navigation.map((entree) => (
              <Carte key={entree.href} titre={entree.libelle} href={entree.href}>
                <p>{entree.resume}</p>
              </Carte>
            ))}
          </div>
        </section>
      </main>
      <Pied />
    </>
  );
}
