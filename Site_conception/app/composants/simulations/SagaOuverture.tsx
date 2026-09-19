"use client";

import { useState } from "react";

/**
 * Simulation : la saga d'ouverture d'un espace client, et ses compensations.
 *
 * ⚠️ Elle rend visible la propriété qu'une transaction de base de données ne peut pas
 * offrir ici : **les sept étapes touchent des systèmes différents**, dont aucun ne
 * participe à la transaction des autres. Quand la cinquième échoue, les quatre
 * premières ont déjà eu lieu, et il faut les défaire dans l'ordre inverse.
 */

const ETAPES = [
  { cle: "slug", titre: "Réserver le sous-domaine", compense: "Libérer la réservation" },
  { cle: "ligne", titre: "Créer la ligne du client", compense: "Marquer la ligne abandonnée" },
  { cle: "schema", titre: "Créer l'espace de données", compense: "Détruire l'espace de données" },
  { cle: "stockage", titre: "Ouvrir le stockage des pièces", compense: "Fermer le stockage" },
  { cle: "compte", titre: "Créer le compte administrateur", compense: "Désactiver le compte" },
  { cle: "metier", titre: "Amorcer les données métier", compense: "Vider les données amorcées" },
  { cle: "actif", titre: "Basculer en actif", compense: "Revenir en ouverture" },
];

type Etat = "attente" | "faite" | "echouee" | "compensee";

export function SagaOuverture() {
  const [echecA, setEchecA] = useState<number | null>(null);
  const [avancement, setAvancement] = useState(0);
  const [compense, setCompense] = useState(false);

  function jouer() {
    setCompense(false);
    const limite = echecA === null ? ETAPES.length : echecA;
    setAvancement(limite + (echecA === null ? 0 : 1));
    if (echecA !== null) {
      // La compensation se déroule après un temps visible : c'est la seule animation de
      // cette simulation, et elle sert à montrer que les étapes se défont dans l'ordre
      // inverse, ce qu'une bascule instantanée ne montrerait pas.
      setTimeout(() => setCompense(true), 700);
    }
  }

  function etatDe(rang: number): Etat {
    if (echecA !== null && rang === echecA) return avancement > rang ? "echouee" : "attente";
    if (rang < avancement) {
      if (compense && echecA !== null && rang < echecA) return "compensee";
      return "faite";
    }
    return "attente";
  }

  const fini = avancement > 0;
  const reussi = fini && echecA === null;

  return (
    <div className="simu">
      <div className="simu__tete">
        <span className="simu__marque">Simulation</span>
        <span className="simu__titre">Ouvrir un espace client, et le défaire</span>
        <span className="simu__aide">
          Choisissez l&apos;étape qui échoue, puis lancez l&apos;ouverture. Les étapes déjà
          faites se défont dans l&apos;ordre inverse.
        </span>
      </div>

      <div className="simu__corps">
        <div className="champ">
          <label>Quelle étape échoue</label>
          <div className="interrupteurs">
            <button
              type="button"
              className="interrupteur"
              aria-pressed={echecA === null}
              onClick={() => {
                setEchecA(null);
                setAvancement(0);
                setCompense(false);
              }}
            >
              Aucune
            </button>
            {ETAPES.map((etape, rang) => (
              <button
                key={etape.cle}
                type="button"
                className="interrupteur"
                aria-pressed={echecA === rang}
                onClick={() => {
                  setEchecA(rang);
                  setAvancement(0);
                  setCompense(false);
                }}
              >
                {rang + 1}
              </button>
            ))}
          </div>
          <span className="champ__aide">
            {echecA === null
              ? "Le cas nominal : les sept étapes passent."
              : `Étape ${echecA + 1} : ${ETAPES[echecA].titre.toLowerCase()}.`}
          </span>
        </div>

        <button type="button" className="site-bouton site-bouton--plein" onClick={jouer}>
          Lancer l&apos;ouverture
        </button>

        <div className="frise" role="list" aria-label="Étapes de l'ouverture">
          {ETAPES.map((etape, rang) => {
            const etat = etatDe(rang);
            return (
              <div
                key={etape.cle}
                role="listitem"
                className={`frise__etape${
                  etat === "faite"
                    ? " est-faite"
                    : etat === "echouee"
                      ? " est-echouee"
                      : etat === "compensee"
                        ? " est-compensee"
                        : ""
                }`}
              >
                <b>Étape {rang + 1}</b>
                {etat === "compensee" ? etape.compense : etape.titre}
              </div>
            );
          })}
        </div>

        {fini ? (
          <div className={`verdict verdict--${reussi ? "vert" : compense ? "ambre" : "rouge"}`}>
            <span className="verdict__pastille" aria-hidden="true" />
            <span className="verdict__texte">
              <b>
                {reussi
                  ? "Espace ouvert"
                  : compense
                    ? "Ouverture défaite proprement"
                    : `Échec à l'étape ${(echecA ?? 0) + 1}`}
              </b>
              {reussi
                ? "Les sept étapes ont abouti. Le client reçoit son lien d'activation, et son sous-domaine répond."
                : compense
                  ? "Les étapes déjà faites ont été défaites dans l'ordre inverse. Le sous-domaine reste réservé et n'est jamais réattribué : le rendre enverrait les anciens liens chez quelqu'un d'autre."
                  : "Les étapes précédentes ont déjà eu lieu. Elles vont être défaites."}
            </span>
          </div>
        ) : null}
      </div>

      <div className="simu__pied">
        <b>Ce qu&apos;il faut retenir.</b> Trois de ces étapes demandent une infrastructure
        qui n&apos;existe pas encore en développement. Elles ne lèvent pas pour autant :
        elles sont <b>substituées</b>, et elles le disent. Une saga qui échouerait à la
        troisième étape sur toutes les machines de développement n&apos;apprendrait rien à
        personne ; une étape qui réussirait en silence sans rien faire produirait un client
        marqué actif dont l&apos;espace n&apos;existe pas, et c&apos;est la première requête
        qui le découvrirait.
      </div>
    </div>
  );
}
