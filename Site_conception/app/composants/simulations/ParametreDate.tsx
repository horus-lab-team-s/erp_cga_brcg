"use client";

import { useMemo, useState } from "react";

/**
 * Simulation : un paramètre légal résolu à une date.
 *
 * ⚠️ Elle sert à faire comprendre pourquoi il n'existe **aucune** façon de lire « la
 * valeur courante ». Tant qu'on ne l'a pas vu, cette interdiction passe pour une
 * rigueur gratuite ; une fois qu'on a contrôlé deux fois la même facture à deux dates
 * différentes et obtenu deux résultats, elle devient évidente.
 */

type Version = {
  valeur: number;
  du: string;
  au: string | null;
  statut: "VALIDE" | "A_VALIDER";
  fondement: string;
};

const VERSIONS: Version[] = [
  {
    valeur: 50_000,
    du: "2019-01-01",
    au: "2023-12-31",
    statut: "VALIDE",
    fondement: "Loi de finances 2019, valeur d'illustration",
  },
  {
    valeur: 100_000,
    du: "2024-01-01",
    au: "2025-12-31",
    statut: "VALIDE",
    fondement: "Loi de finances 2024, valeur d'illustration",
  },
  {
    valeur: 500_000,
    du: "2026-01-01",
    au: null,
    statut: "A_VALIDER",
    fondement: "Non confirmée sur le texte : attend le contreseing du fiscaliste",
  },
];

function resoudre(date: string): Version | null {
  return (
    VERSIONS.find((v) => date >= v.du && (v.au === null || date <= v.au)) ?? null
  );
}

export function ParametreDate() {
  const [date, setDate] = useState("2024-06-15");
  const [montant, setMontant] = useState(120_000);
  const version = useMemo(() => resoudre(date), [date]);

  const atteint = version !== null && montant >= version.valeur;

  return (
    <div className="simu">
      <div className="simu__tete">
        <span className="simu__marque">Simulation</span>
        <span className="simu__titre">Résoudre un paramètre à une date</span>
        <span className="simu__aide">
          Le même paramètre, le même montant, deux dates : deux réponses. C&apos;est la raison
          pour laquelle « la valeur courante » n&apos;existe pas dans ce système.
        </span>
      </div>

      <div className="simu__corps simu__corps--deux">
        <div>
          <div className="champ">
            <label htmlFor="simu-date">Date de la pièce contrôlée</label>
            <input
              id="simu-date"
              type="date"
              value={date}
              min="2019-01-01"
              max="2027-12-31"
              onChange={(e) => setDate(e.target.value)}
            />
            <span className="champ__aide">
              Pas la date du jour : la date de la <b>pièce</b>. Une facture de 2024 se contrôle
              avec les règles de 2024, même relue en 2027.
            </span>
          </div>
          <div className="champ">
            <label htmlFor="simu-montant2">Montant réglé en espèces</label>
            <input
              id="simu-montant2"
              type="number"
              step={10000}
              min={0}
              value={montant}
              onChange={(e) => setMontant(Number(e.target.value) || 0)}
            />
          </div>
          <div className="champ">
            <label>Dates d&apos;essai</label>
            <div className="interrupteurs">
              {["2022-03-10", "2024-06-15", "2026-02-20"].map((essai) => (
                <button
                  key={essai}
                  type="button"
                  className="interrupteur"
                  aria-pressed={date === essai}
                  onClick={() => setDate(essai)}
                >
                  {essai}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          {version === null ? (
            <div className="verdict verdict--rouge">
              <span className="verdict__pastille" aria-hidden="true" />
              <span className="verdict__texte">
                <b>Aucune version applicable</b>
                Le paramètre ne couvre pas cette date. Le service lève plutôt que de rendre une
                valeur : un contrôle silencieusement faux vaut moins qu&apos;un contrôle qui
                s&apos;arrête.
              </span>
            </div>
          ) : (
            <>
              <div className={`verdict verdict--${atteint ? "rouge" : "vert"}`}>
                <span className="verdict__pastille" aria-hidden="true" />
                <span className="verdict__texte">
                  <b>
                    Seuil applicable : {version.valeur.toLocaleString("fr-FR")} FCFA
                  </b>
                  {atteint
                    ? "Le montant atteint le seuil : la déduction de la taxe est écartée."
                    : "Le montant reste sous le seuil : la déduction est possible."}
                </span>
              </div>
              <div className="constat constat--INFORMATION">
                <div className="constat__tete">
                  <span className="constat__code">SEUIL_ESPECES_DEDUCTIBILITE_TVA</span>
                  <span className="constat__gravite">{version.statut}</span>
                </div>
                <div className="constat__message">
                  Version applicable du {version.du} {version.au ? `au ${version.au}` : "à aujourd'hui"}.
                </div>
                <div className="constat__fondement">Fondement : {version.fondement}</div>
              </div>
              {version.statut === "A_VALIDER" ? (
                <p style={{ fontSize: 13.5, color: "var(--ambre)", marginTop: 10 }}>
                  Cette version n&apos;a pas été confirmée sur le texte. Le chiffre produit
                  illustre le mécanisme, il n&apos;engage personne tant qu&apos;un fiscaliste
                  nommé ne l&apos;a pas contresignée.
                </p>
              ) : null}
            </>
          )}
        </div>
      </div>

      <div className="simu__pied">
        <b>Ce qu&apos;il faut retenir.</b> Le paramètre porte ses versions, chacune avec sa
        période, son fondement et son statut. Le code demande <b>toujours</b> une date, et le
        service refuse de répondre s&apos;il n&apos;a rien pour elle. Une valeur déclarée exacte
        porte en plus le nom de qui l&apos;a validée et la date de validation : sans ces deux
        champs, le modèle la refuse à l&apos;écriture.
      </div>
    </div>
  );
}
