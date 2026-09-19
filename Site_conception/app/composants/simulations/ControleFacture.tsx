"use client";

import { useMemo, useState } from "react";

/**
 * Simulation : le moteur de conformité contrôle une facture.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * CE QU'ELLE MONTRE, ET CE QU'ELLE NE MONTRE PAS
 *
 * Elle montre **la forme** de ce que le moteur produit : des constats gradués, chacun
 * portant une conséquence fiscale chiffrée et le fondement qui le justifie. C'est la
 * notion la plus mal comprise du projet, parce qu'on attend d'un contrôle qu'il
 * réponde « conforme » ou « non conforme », et qu'il répond tout autre chose.
 *
 * ⚠️ **Elle ne contient pas le moteur.** Les règles écrites ici sont une transcription
 * lisible de quelques règles réelles, avec des valeurs d'illustration. Le vrai moteur
 * évalue des expressions décrites en données, et lit ses seuils dans un référentiel
 * daté. Une simulation qui embarquerait une copie des règles finirait par en donner
 * une version périmée : c'est exactement le défaut que le projet combat.
 *
 * ⚠️ **Les valeurs affichées ne sont pas opposables**, et le pied du cadre le dit.
 * ─────────────────────────────────────────────────────────────────────────────
 */

type Gravite = "BLOQUANT" | "MAJEUR" | "AVERTISSEMENT" | "INFORMATION";

type Constat = {
  code: string;
  gravite: Gravite;
  message: string;
  consequence?: string;
  fondement: string;
};

type Facture = {
  montantTtc: number;
  tauxTva: number;
  modeReglement: "VIREMENT" | "ESPECES" | "MOBILE";
  niuFournisseur: boolean;
  mentionTva: boolean;
  dateEmission: string;
  joursDeRetard: number;
};

const SEUIL_ESPECES = 100_000;

function franc(montant: number): string {
  return `${Math.round(montant).toLocaleString("fr-FR")} FCFA`;
}

/** Les règles, transcrites. Chacune rend un constat, ou rien. */
function controler(facture: Facture): Constat[] {
  const constats: Constat[] = [];
  const base = facture.montantTtc / (1 + facture.tauxTva / 100);
  const tva = facture.montantTtc - base;

  if (!facture.niuFournisseur) {
    constats.push({
      code: "FAC-ACH-007",
      gravite: "MAJEUR",
      message:
        "Le numéro d'identifiant unique du fournisseur est absent. La charge n'est pas déductible, et la TVA correspondante non plus.",
      consequence: `TVA non déductible : ${franc(tva)}`,
      fondement: "Obligation de mention de l'identifiant du fournisseur sur la facture",
    });
  }

  if (facture.modeReglement === "ESPECES" && facture.montantTtc >= SEUIL_ESPECES) {
    constats.push({
      code: "FAC-ACH-012",
      gravite: "BLOQUANT",
      message: `Règlement en espèces d'un montant au moins égal à ${franc(
        SEUIL_ESPECES,
      )}. La déduction de la TVA est écartée pour la totalité de la facture.`,
      consequence: `TVA non déductible : ${franc(tva)}`,
      fondement: "Seuil de règlement en espèces excluant la déduction de la TVA",
    });
  }

  if (!facture.mentionTva && facture.tauxTva > 0) {
    constats.push({
      code: "FAC-ACH-003",
      gravite: "MAJEUR",
      message:
        "La facture ne porte pas la mention distincte de la taxe. Sans elle, la taxe ne peut pas être récupérée.",
      consequence: `TVA non déductible : ${franc(tva)}`,
      fondement: "Mentions obligatoires d'une facture ouvrant droit à déduction",
    });
  }

  if (facture.joursDeRetard > 90) {
    constats.push({
      code: "FAC-ACH-021",
      gravite: "AVERTISSEMENT",
      message: `Pièce reçue ${facture.joursDeRetard} jours après son émission. Au-delà du délai de rattachement, la déduction se perd même si la facture est régulière.`,
      fondement: "Délai de rattachement d'une charge à son exercice",
    });
  } else if (facture.joursDeRetard > 30) {
    constats.push({
      code: "FAC-ACH-020",
      gravite: "INFORMATION",
      message: `Pièce reçue ${facture.joursDeRetard} jours après son émission. Le contrôle reste possible, la régularisation auprès du fournisseur devient plus difficile.`,
      fondement: "Bonne pratique de collecte du cabinet",
    });
  }

  if (facture.modeReglement === "MOBILE" && facture.montantTtc >= SEUIL_ESPECES) {
    constats.push({
      code: "FAC-ACH-014",
      gravite: "INFORMATION",
      message:
        "Règlement par transfert d'argent mobile. La preuve de règlement doit être jointe : le relevé du compte marchand, et non la capture de l'écran du téléphone.",
      fondement: "Pièce justificative du règlement",
    });
  }

  return constats;
}

const ORDRE: Gravite[] = ["BLOQUANT", "MAJEUR", "AVERTISSEMENT", "INFORMATION"];

export function ControleFacture() {
  const [facture, setFacture] = useState<Facture>({
    montantTtc: 1_970_650,
    tauxTva: 19.25,
    modeReglement: "VIREMENT",
    niuFournisseur: true,
    mentionTva: true,
    dateEmission: "2026-04-12",
    joursDeRetard: 12,
  });

  const constats = useMemo(() => controler(facture), [facture]);
  const trie = useMemo(
    () => [...constats].sort((a, b) => ORDRE.indexOf(a.gravite) - ORDRE.indexOf(b.gravite)),
    [constats],
  );

  const bloquant = constats.some((c) => c.gravite === "BLOQUANT");
  const majeur = constats.some((c) => c.gravite === "MAJEUR");
  const base = facture.montantTtc / (1 + facture.tauxTva / 100);
  const tva = facture.montantTtc - base;
  const perdue = constats.filter((c) => c.consequence).length > 0 ? tva : 0;

  return (
    <div className="simu">
      <div className="simu__tete">
        <span className="simu__marque">Simulation</span>
        <span className="simu__titre">Contrôler une facture d&apos;achat</span>
        <span className="simu__aide">
          Changez un élément de la facture et regardez le rapport se refaire. Le moteur ne
          répond jamais par oui ou par non : il rend des constats gradués, chacun chiffré.
        </span>
      </div>

      <div className="simu__corps simu__corps--deux">
        <div>
          <div className="champ">
            <label htmlFor="simu-montant">Montant toutes taxes comprises</label>
            <input
              id="simu-montant"
              type="number"
              min={0}
              step={1000}
              value={facture.montantTtc}
              onChange={(e) =>
                setFacture({ ...facture, montantTtc: Number(e.target.value) || 0 })
              }
            />
            <span className="champ__aide">
              Base {franc(base)} · taxe {franc(tva)}
            </span>
          </div>

          <div className="champ">
            <label htmlFor="simu-reglement">Mode de règlement</label>
            <select
              id="simu-reglement"
              value={facture.modeReglement}
              onChange={(e) =>
                setFacture({
                  ...facture,
                  modeReglement: e.target.value as Facture["modeReglement"],
                })
              }
            >
              <option value="VIREMENT">Virement bancaire</option>
              <option value="ESPECES">Espèces</option>
              <option value="MOBILE">Argent mobile</option>
            </select>
            <span className="champ__aide">
              Le seuil des espèces vaut {franc(SEUIL_ESPECES)} dans cette simulation.
            </span>
          </div>

          <div className="champ">
            <label htmlFor="simu-retard">Jours entre l&apos;émission et la réception</label>
            <input
              id="simu-retard"
              type="range"
              min={0}
              max={150}
              value={facture.joursDeRetard}
              onChange={(e) =>
                setFacture({ ...facture, joursDeRetard: Number(e.target.value) })
              }
            />
            <span className="champ__aide">{facture.joursDeRetard} jours</span>
          </div>

          <div className="champ">
            <label>Mentions portées par la facture</label>
            <div className="interrupteurs">
              <button
                type="button"
                className="interrupteur"
                aria-pressed={facture.niuFournisseur}
                onClick={() =>
                  setFacture({ ...facture, niuFournisseur: !facture.niuFournisseur })
                }
              >
                Identifiant du fournisseur
              </button>
              <button
                type="button"
                className="interrupteur"
                aria-pressed={facture.mentionTva}
                onClick={() => setFacture({ ...facture, mentionTva: !facture.mentionTva })}
              >
                Taxe mentionnée à part
              </button>
            </div>
          </div>
        </div>

        <div>
          <div
            className={
              bloquant
                ? "verdict verdict--rouge"
                : majeur
                  ? "verdict verdict--ambre"
                  : constats.length > 0
                    ? "verdict verdict--ambre"
                    : "verdict verdict--vert"
            }
          >
            <span className="verdict__pastille" aria-hidden="true" />
            <span className="verdict__texte">
              <b>
                {bloquant
                  ? "Comptabilisation interdite"
                  : constats.length === 0
                    ? "Aucun constat"
                    : `${constats.length} constat${constats.length > 1 ? "s" : ""} à traiter`}
              </b>
              {bloquant
                ? "Un constat bloquant empêche l'enregistrement tant qu'il n'est pas levé ou écarté avec un motif."
                : constats.length === 0
                  ? "La pièce est enregistrable en l'état."
                  : `Enjeu fiscal cumulé : ${franc(perdue)} de taxe qui ne serait pas récupérée.`}
            </span>
          </div>

          {trie.length === 0 ? (
            <p className="vide">
              Retirez une mention ou passez le règlement en espèces pour voir le moteur
              réagir.
            </p>
          ) : (
            trie.map((constat) => (
              <div className={`constat constat--${constat.gravite}`} key={constat.code}>
                <div className="constat__tete">
                  <span className="constat__code">{constat.code}</span>
                  <span className="constat__gravite">{constat.gravite}</span>
                </div>
                <div className="constat__message">{constat.message}</div>
                {constat.consequence ? (
                  <div className="constat__chiffre">{constat.consequence}</div>
                ) : null}
                <div className="constat__fondement">Fondement : {constat.fondement}</div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="simu__pied">
        <b>Ce qu&apos;il faut retenir.</b> La règle décrit, elle n&apos;agit pas. Aucun de
        ces constats ne bloque quoi que ce soit par lui-même : c&apos;est un service en aval
        qui décide, en lisant les gravités. C&apos;est ce qui permet au même moteur de servir
        le contrôle de facture, la tarification, l&apos;évaluation de charge et le contrôle
        interne. <b>Les valeurs employées ici illustrent le mécanisme et ne sont pas
        opposables</b> : dans le produit, elles viennent du référentiel daté et portent le nom
        du fiscaliste qui les a validées.
      </div>
    </div>
  );
}
