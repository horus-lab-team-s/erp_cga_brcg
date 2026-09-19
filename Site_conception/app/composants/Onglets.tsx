"use client";

import { useId, useState } from "react";

/**
 * Des onglets, au clavier comme à la souris.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * POURQUOI DES ONGLETS PLUTÔT QUE QUATRE PAGES
 *
 * Les prérequis se lisent en comparant : on hésite entre deux notions, on revient
 * sur la précédente, on vérifie dans quel langage elle est écrite. Quatre pages
 * imposeraient un aller-retour réseau à chaque hésitation, et feraient perdre la
 * position de lecture à chaque retour.
 *
 * ⚠️ **LES PANNEAUX CACHÉS SONT RENDUS, PAS ABSENTS**, et il faut être exact sur ce
 * que cela apporte. Une première rédaction de ce commentaire affirmait que la
 * recherche du navigateur les trouverait : **c'est faux**, `hidden` vaut
 * `display: none`, et Ctrl+F ne descend pas dedans. Vérifié plutôt que supposé.
 *
 * Ce que cela apporte réellement : le changement d'onglet est instantané et ne
 * reconstruit rien, la position de lecture de chaque panneau est conservée, et le
 * texte complet part dans la page servie, donc **l'impression le rend en entier**
 * grâce à la règle d'impression de `globals.css`.
 *
 * ⚠️ **Les flèches déplacent la sélection.** C'est la convention des onglets : un
 * lecteur au clavier qui doit tabuler quatre fois pour changer d'onglet abandonne.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export type Onglet = {
  cle: string;
  libelle: string;
  contenu: React.ReactNode;
};

export function Onglets({ onglets, etiquette }: { onglets: Onglet[]; etiquette: string }) {
  const [actif, setActif] = useState(0);
  const identifiant = useId();

  function auClavier(evenement: React.KeyboardEvent<HTMLDivElement>) {
    const pas =
      evenement.key === "ArrowRight" ? 1 : evenement.key === "ArrowLeft" ? -1 : 0;
    if (pas === 0) {
      if (evenement.key === "Home") setActif(0);
      else if (evenement.key === "End") setActif(onglets.length - 1);
      else return;
    } else {
      // Le tour est circulaire : arrivé au dernier, la flèche droite revient au premier.
      setActif((courant) => (courant + pas + onglets.length) % onglets.length);
    }
    evenement.preventDefault();
  }

  return (
    <div>
      <div
        className="onglets__barre"
        role="tablist"
        aria-label={etiquette}
        onKeyDown={auClavier}
      >
        {onglets.map((onglet, rang) => (
          <button
            key={onglet.cle}
            type="button"
            role="tab"
            id={`${identifiant}-onglet-${onglet.cle}`}
            aria-controls={`${identifiant}-panneau-${onglet.cle}`}
            aria-selected={rang === actif}
            // ⚠️ Un seul onglet est atteignable par la tabulation : le sélectionné. Les
            // autres se rejoignent aux flèches. C'est ce que fait un vrai jeu d'onglets,
            // et ce qui évite d'avoir à tabuler à travers toute la barre pour atteindre
            // le contenu.
            tabIndex={rang === actif ? 0 : -1}
            className="onglet"
            onClick={() => setActif(rang)}
          >
            {onglet.libelle}
          </button>
        ))}
      </div>
      {onglets.map((onglet, rang) => (
        <div
          key={onglet.cle}
          role="tabpanel"
          id={`${identifiant}-panneau-${onglet.cle}`}
          aria-labelledby={`${identifiant}-onglet-${onglet.cle}`}
          className="onglets__panneau"
          hidden={rang !== actif}
          tabIndex={0}
        >
          {onglet.contenu}
        </div>
      ))}
    </div>
  );
}
