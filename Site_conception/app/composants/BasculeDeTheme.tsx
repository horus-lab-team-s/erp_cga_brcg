"use client";

import { useEffect, useState } from "react";

/**
 * Le bouton clair / sombre, et la mémoire du choix.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ IL NE SAIT RIEN AVANT LE PREMIER RENDU, ET C'EST VOULU
 *
 * Le thème est posé sur `<html>` par un script du `layout`, avant la peinture. Ce
 * composant, lui, est rendu une première fois sur le serveur, où `localStorage`
 * n'existe pas. S'il annonçait un état dès ce rendu, React trouverait deux textes
 * différents entre le serveur et le navigateur, et se plaindrait d'une divergence.
 *
 * Il s'affiche donc sans libellé jusqu'à ce que le navigateur l'ait lu, puis se nomme.
 * La largeur est réservée d'avance pour que la barre ne saute pas.
 *
 * ⚠️ **`localStorage` peut lever** (navigation privée, données de site bloquées). Le
 * thème vaut alors pour la page, et rien ne casse : une préférence d'affichage n'est
 * pas une donnée dont la perte mérite une erreur.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export function BasculeDeTheme() {
  const [sombre, setSombre] = useState<boolean | null>(null);

  useEffect(() => {
    const choisi = lire();
    setSombre(
      choisi === null
        ? window.matchMedia("(prefers-color-scheme: dark)").matches
        : choisi === "dark",
    );
  }, []);

  function basculer() {
    const prochain = sombre ? "light" : "dark";
    document.documentElement.dataset.theme = prochain;
    ecrire(prochain);
    setSombre(prochain === "dark");
  }

  return (
    <button
      type="button"
      className="site-bouton"
      onClick={basculer}
      aria-pressed={sombre ?? false}
      style={{ minWidth: "5.4rem", justifyContent: "center" }}
    >
      {sombre === null ? " " : sombre ? "Clair" : "Sombre"}
    </button>
  );
}

function lire(): string | null {
  try {
    return localStorage.getItem("cga-theme");
  } catch {
    return null;
  }
}

function ecrire(valeur: string): void {
  try {
    localStorage.setItem("cga-theme", valeur);
  } catch {
    /* navigation privée : le thème vaut pour cette page, et c'est assez. */
  }
}
