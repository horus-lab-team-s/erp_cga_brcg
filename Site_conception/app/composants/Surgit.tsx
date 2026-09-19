"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Fait apparaître son contenu quand il entre dans l'écran.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ IL NE CACHE RIEN TANT QUE LE SCRIPT N'A PAS PRIS LA MAIN
 *
 * Le contenu est rendu **visible par défaut**, et la classe qui l'efface n'est posée
 * qu'une fois le composant monté dans le navigateur. Si le script ne se charge pas,
 * si l'utilisateur le refuse, ou si le rendu est celui du serveur, la page reste
 * entièrement lisible.
 *
 * L'ordre inverse est le piège classique : cacher en CSS et révéler en JavaScript
 * donne une page blanche à quiconque n'exécute pas le script, et une documentation
 * invisible est pire qu'une documentation sans animation.
 *
 * ⚠️ La préférence système « animations réduites » est respectée par la feuille de
 * style, qui neutralise alors la transition sans que ce composant ait à la connaître.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export function Surgit({
  children,
  delai = 0,
}: {
  children: React.ReactNode;
  delai?: number;
}) {
  const cible = useRef<HTMLDivElement>(null);
  const [arme, setArme] = useState(false);
  const [vu, setVu] = useState(false);

  useEffect(() => {
    setArme(true);
    const element = cible.current;
    if (!element) return;
    const observateur = new IntersectionObserver(
      (entrees) => {
        if (entrees.some((e) => e.isIntersecting)) {
          setVu(true);
          observateur.disconnect();
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 },
    );
    observateur.observe(element);
    return () => observateur.disconnect();
  }, []);

  return (
    <div
      ref={cible}
      className={arme ? `surgit${vu ? " est-visible" : ""}` : undefined}
      style={arme && !vu ? { transitionDelay: `${delai}ms` } : undefined}
    >
      {children}
    </div>
  );
}
