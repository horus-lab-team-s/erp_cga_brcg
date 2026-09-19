"use client";

import { useMemo, useState } from "react";

/**
 * Simulation : du nom d'hôte au locataire, ou au refus.
 *
 * ⚠️ Elle existe pour rendre visible la règle la moins intuitive du projet : **hors
 * périmètre, on répond que la ressource n'existe pas, jamais qu'elle est interdite**.
 * Dite en une phrase, elle paraît excessive. Essayée sur un sous-domaine suspendu,
 * elle devient évidente : tout autre code de réponse apprendrait au visiteur que ce
 * client existe, et la liste des clients du cabinet se découvrirait au hasard.
 */

type Statut = "ACTIF" | "SUSPENDU" | "RESILIE" | "EN_OUVERTURE";

const REPERTOIRE: { slug: string; statut: Statut; nom: string }[] = [
  { slug: "brcg", statut: "ACTIF", nom: "Le cabinet lui-même" },
  { slug: "station-bonaberi", statut: "ACTIF", nom: "Station-service, tenant entreprise" },
  { slug: "boulangerie", statut: "SUSPENDU", nom: "Honoraires échus depuis deux mois" },
  { slug: "ancien-client", statut: "RESILIE", nom: "Parti en juin" },
  { slug: "futur", statut: "EN_OUVERTURE", nom: "Payé, espace en cours d'ouverture" },
];

const RESERVES = ["api", "www", "admin", "app", "blog", "cdn", "demo"];

type Verdict = {
  code: number;
  ton: "vert" | "ambre" | "rouge";
  titre: string;
  explication: string;
  locataire: string | null;
};

function resoudre(hote: string): Verdict {
  const propre = hote.trim().toLowerCase();
  const racine = ".cga.cm";

  if (propre === "" || propre === "cga.cm" || propre === "localhost") {
    return {
      code: 200,
      ton: "ambre",
      titre: "Aucun locataire désigné",
      explication:
        "Le nom d'hôte ne porte pas de sous-domaine. En développement, la requête retombe sur le locataire configuré ; en production, ce chemin disparaîtra le jour où la vitrine aura son propre service.",
      locataire: "le locataire par défaut",
    };
  }

  if (!propre.endsWith(racine)) {
    return {
      code: 404,
      ton: "rouge",
      titre: "Domaine inconnu",
      explication:
        "Le nom d'hôte ne dépend pas du domaine de la plateforme. Rien à résoudre, et rien à dire de plus.",
      locataire: null,
    };
  }

  const slug = propre.slice(0, -racine.length);

  if (RESERVES.includes(slug)) {
    return {
      code: 404,
      ton: "rouge",
      titre: "Nom réservé à la plateforme",
      explication:
        "Ce sous-domaine appartient à la plateforme et ne peut être attribué à personne. La liste vit au référentiel, et elle grandit sans livraison.",
      locataire: null,
    };
  }

  const tenant = REPERTOIRE.find((t) => t.slug === slug);

  if (!tenant) {
    return {
      code: 404,
      ton: "rouge",
      titre: "Aucun locataire à ce nom",
      explication:
        "Le répertoire ne connaît pas ce sous-domaine. La réponse est la même que pour un client suspendu ou résilié, et c'est voulu : elle n'apprend rien.",
      locataire: null,
    };
  }

  if (tenant.statut === "ACTIF") {
    return {
      code: 200,
      ton: "vert",
      titre: "Locataire établi",
      explication:
        "Le locataire est posé au bord de la requête, une seule fois. Toutes les lectures de données qui suivront seront filtrées sur lui, sans qu'aucune requête n'ait à le demander.",
      locataire: tenant.slug,
    };
  }

  if (tenant.statut === "SUSPENDU") {
    return {
      code: 402,
      ton: "ambre",
      titre: "Locataire suspendu",
      explication:
        "C'est la seule exception à la règle du 404, et elle est assumée : un client suspendu pour impayé doit comprendre pourquoi son espace ne répond plus, sinon il appelle le cabinet qui perd une heure à expliquer ce qu'un code aurait dit.",
      locataire: null,
    };
  }

  return {
    code: 404,
    ton: "rouge",
    titre: tenant.statut === "RESILIE" ? "Locataire résilié" : "Ouverture en cours",
    explication:
      tenant.statut === "RESILIE"
        ? "Un espace résilié répond comme un espace inexistant. Le slug, lui, n'est jamais réattribué : le rendre enverrait les anciens liens chez quelqu'un d'autre."
        : "L'espace est payé mais pas encore complet. Le servir à moitié donnerait une première impression que rien ne rattrape.",
    locataire: null,
  };
}

export function ResolutionTenant() {
  const [hote, setHote] = useState("station-bonaberi.cga.cm");
  const verdict = useMemo(() => resoudre(hote), [hote]);

  return (
    <div className="simu">
      <div className="simu__tete">
        <span className="simu__marque">Simulation</span>
        <span className="simu__titre">Résoudre un sous-domaine</span>
        <span className="simu__aide">
          Tapez une adresse, ou choisissez un exemple. Observez surtout ce que les réponses
          ont en commun.
        </span>
      </div>

      <div className="simu__corps simu__corps--deux">
        <div>
          <div className="champ">
            <label htmlFor="simu-hote">Nom d&apos;hôte demandé</label>
            <input
              id="simu-hote"
              type="text"
              value={hote}
              spellCheck={false}
              onChange={(e) => setHote(e.target.value)}
            />
          </div>
          <div className="champ">
            <label>Exemples</label>
            <div className="interrupteurs">
              {[
                "station-bonaberi.cga.cm",
                "boulangerie.cga.cm",
                "ancien-client.cga.cm",
                "futur.cga.cm",
                "api.cga.cm",
                "jamais-vu.cga.cm",
              ].map((exemple) => (
                <button
                  key={exemple}
                  type="button"
                  className="interrupteur"
                  aria-pressed={hote === exemple}
                  onClick={() => setHote(exemple)}
                >
                  {exemple.replace(".cga.cm", "")}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className={`verdict verdict--${verdict.ton}`}>
            <span className="verdict__pastille" aria-hidden="true" />
            <span className="verdict__texte">
              <b>
                {verdict.code} · {verdict.titre}
              </b>
              {verdict.explication}
            </span>
          </div>
          {verdict.locataire ? (
            <p style={{ fontSize: 14, color: "var(--encre-doux)" }}>
              Locataire établi pour cette requête : <code>{verdict.locataire}</code>. Toutes
              les lectures qui suivent sont filtrées sur lui, par la couche de persistance
              <b> et</b> par une règle écrite dans la base.
            </p>
          ) : null}
        </div>
      </div>

      <div className="simu__pied">
        <b>Ce qu&apos;il faut retenir.</b> Quatre situations très différentes rendent la même
        réponse : inconnu, réservé, résilié, en cours d&apos;ouverture. C&apos;est
        délibéré. Distinguer « ce client n&apos;existe pas » de « ce client existe mais vous
        n&apos;y avez pas accès » permettrait à n&apos;importe qui de découvrir le
        portefeuille du cabinet en essayant des noms. La seule exception, le client suspendu,
        est un choix commercial assumé et documenté.
      </div>
    </div>
  );
}
