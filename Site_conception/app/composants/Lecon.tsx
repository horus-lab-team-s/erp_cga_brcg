"use client";

import { useEffect, useRef, useState } from "react";

/**
 * La charpente d'un cours : sommaire qui suit la lecture, et barre de progression.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ POURQUOI UN OBSERVATEUR PLUTÔT QU'UN CALCUL AU DÉFILEMENT
 *
 * Suivre la lecture en écoutant chaque événement de défilement oblige à mesurer la
 * position de tous les chapitres à chaque pixel parcouru. Sur un cours de trente
 * sections, cela fait trente mesures par image, et chaque mesure force le navigateur
 * à recalculer la mise en page : le défilement devient saccadé sur un téléphone
 * d'entrée de gamme, c'est-à-dire exactement sur les appareils du public visé.
 *
 * `IntersectionObserver` fait le même travail dans le navigateur, sans réveiller le
 * code à chaque pixel. Il ne signale que les entrées et les sorties.
 *
 * ⚠️ **La barre de progression, elle, écoute le défilement**, parce qu'elle a
 * réellement besoin d'une valeur continue. Elle ne lit que deux nombres déjà connus
 * du navigateur, et l'écoute est déclarée passive pour ne pas retenir le défilement.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export type Chapitre = { id: string; titre: string };

export function Lecon({
  chapitres,
  children,
}: {
  chapitres: Chapitre[];
  children: React.ReactNode;
}) {
  const [courant, setCourant] = useState(chapitres[0]?.id ?? "");
  const [avance, setAvance] = useState(0);
  const corps = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const cibles = chapitres
      .map((c) => document.getElementById(c.id))
      .filter((e): e is HTMLElement => e !== null);

    const observateur = new IntersectionObserver(
      (entrees) => {
        // Le chapitre courant est le plus haut de ceux qui sont visibles. Prendre le
        // premier signalé donnerait un sommaire qui saute en arrière quand deux
        // chapitres entrent dans la fenêtre en même temps.
        const visibles = entrees
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visibles.length > 0) setCourant(visibles[0].target.id);
      },
      // La zone active commence sous l'en-tête collant et s'arrête au milieu de
      // l'écran : un chapitre n'est « courant » que lorsqu'on le lit vraiment.
      { rootMargin: "-96px 0px -55% 0px", threshold: 0 },
    );

    cibles.forEach((cible) => observateur.observe(cible));
    return () => observateur.disconnect();
  }, [chapitres]);

  useEffect(() => {
    function mesurer() {
      const zone = corps.current;
      if (!zone) return;
      const haut = zone.offsetTop;
      const hauteur = zone.offsetHeight - window.innerHeight;
      const fait = hauteur > 0 ? (window.scrollY - haut) / hauteur : 1;
      setAvance(Math.max(0, Math.min(1, fait)));
    }
    mesurer();
    window.addEventListener("scroll", mesurer, { passive: true });
    window.addEventListener("resize", mesurer);
    return () => {
      window.removeEventListener("scroll", mesurer);
      window.removeEventListener("resize", mesurer);
    };
  }, []);

  return (
    <>
      <div
        className="progression"
        style={{ width: `${(avance * 100).toFixed(1)}%` }}
        role="progressbar"
        aria-label="Progression dans le cours"
        aria-valuenow={Math.round(avance * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
      />
      <div className="lecon">
        <nav className="lecon__sommaire" aria-label="Chapitres du cours">
          <p>Le plan</p>
          <ol>
            {chapitres.map((chapitre) => (
              <li key={chapitre.id}>
                <a
                  href={`#${chapitre.id}`}
                  aria-current={chapitre.id === courant ? "true" : undefined}
                >
                  {chapitre.titre}
                </a>
              </li>
            ))}
          </ol>
        </nav>
        <div ref={corps}>{children}</div>
      </div>
    </>
  );
}

/** Un chapitre, avec son rang et son ancre. Le rang aide à se repérer dans un long cours. */
export function Chapitre({
  id,
  rang,
  titre,
  children,
}: {
  id: string;
  rang: string;
  titre: string;
  children: React.ReactNode;
}) {
  return (
    <section className="chapitre" id={id}>
      <p className="chapitre__rang">{rang}</p>
      <h2>{titre}</h2>
      {children}
    </section>
  );
}
