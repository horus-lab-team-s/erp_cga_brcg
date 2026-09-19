"use client";

import { useCallback, useEffect, useState } from "react";

/**
 * Simulation : le journal chaîné, et ce qui se passe quand on modifie une ligne.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ LES EMPREINTES SONT DE VRAIES EMPREINTES
 *
 * Elles sont calculées par le navigateur avec SHA-256, la même fonction que le
 * serveur. Un simulacre, par exemple une somme de caractères, aurait montré le
 * mécanisme et enseigné une fausse idée : que l'empreinte est un résumé approximatif
 * qu'on pourrait reproduire à la main.
 *
 * ⚠️ `crypto.subtle` n'existe que dans un contexte sûr, c'est-à-dire en HTTPS ou sur
 * la machine locale. Ailleurs, la simulation le dit au lieu de tomber en panne.
 * ─────────────────────────────────────────────────────────────────────────────
 */

type Entree = {
  rang: number;
  acteur: string;
  action: string;
  objet: string;
  precedente: string;
  empreinte: string;
};

const GENESE = "0".repeat(64);

const DEPART = [
  { acteur: "l.fotso", action: "piece.deposee", objet: "F-2026-0412" },
  { acteur: "l.fotso", action: "ecriture.saisie", objet: "ACH-2026-0188" },
  { acteur: "a.bouba", action: "ecriture.validee", objet: "ACH-2026-0188" },
  { acteur: "a.bouba", action: "mois.transmis", objet: "2026-04" },
];

async function empreindre(texte: string): Promise<string> {
  const octets = new TextEncoder().encode(texte);
  const brut = await crypto.subtle.digest("SHA-256", octets);
  return [...new Uint8Array(brut)].map((o) => o.toString(16).padStart(2, "0")).join("");
}

function corps(e: Omit<Entree, "empreinte">): string {
  // Le vrai corps canonique porte davantage de champs, et il est sérialisé avec des clés
  // triées : deux machines doivent produire exactement la même chaîne, sinon la
  // vérification échouerait ailleurs que là où elle a été écrite.
  return JSON.stringify({
    rang: e.rang,
    acteur: e.acteur,
    action: e.action,
    objet: e.objet,
    precedente: e.precedente,
  });
}

export function JournalChaine() {
  const [entrees, setEntrees] = useState<Entree[]>([]);
  const [altere, setAltere] = useState<number | null>(null);
  const [possible, setPossible] = useState(true);

  const construire = useCallback(async (modifiee: number | null) => {
    const resultat: Entree[] = [];
    let precedente = GENESE;
    for (let i = 0; i < DEPART.length; i += 1) {
      const source = DEPART[i];
      const acteur = modifiee === i + 1 ? "quelqu-un-dautre" : source.acteur;
      const sans = { rang: i + 1, acteur, action: source.action, objet: source.objet, precedente };
      const empreinte = await empreindre(corps(sans));
      resultat.push({ ...sans, empreinte });
      // ⚠️ Le chaînage reprend l'empreinte **d'origine** pour les entrées suivantes :
      // c'est ce qui se passe réellement quand quelqu'un modifie une ligne en base,
      // puisqu'il ne recalcule pas toute la suite. C'est cela que la vérification voit.
      precedente =
        modifiee !== null && i + 1 === modifiee ? resultat[i].empreinte : empreinte;
    }
    return resultat;
  }, []);

  useEffect(() => {
    if (typeof crypto === "undefined" || !crypto.subtle) {
      setPossible(false);
      return;
    }
    let vivant = true;
    construire(null).then((liste) => {
      if (vivant) setEntrees(liste);
    });
    return () => {
      vivant = false;
    };
  }, [construire]);

  async function alterer(rang: number | null) {
    setAltere(rang);
    if (rang === null) {
      setEntrees(await construire(null));
      return;
    }
    // On recalcule l'entrée modifiée, et **seulement elle** : c'est ce qu'un
    // administrateur pressé ferait, et c'est ce qui casse la chaîne.
    const base = await construire(null);
    const source = DEPART[rang - 1];
    const sans = {
      rang,
      acteur: "quelqu-un-dautre",
      action: source.action,
      objet: source.objet,
      precedente: base[rang - 1].precedente,
    };
    const nouvelle = await empreindre(corps(sans));
    const liste = base.map((e) =>
      e.rang === rang ? { ...sans, empreinte: nouvelle } : e,
    );
    setEntrees(liste);
  }

  if (!possible) {
    return (
      <div className="simu">
        <div className="simu__tete">
          <span className="simu__marque">Simulation</span>
          <span className="simu__titre">Le journal chaîné</span>
        </div>
        <div className="simu__corps">
          <p className="vide">
            Cette simulation calcule de vraies empreintes SHA-256, ce que le navigateur ne
            permet que sur une adresse sécurisée. Ouvrez cette page en HTTPS ou sur la
            machine locale.
          </p>
        </div>
      </div>
    );
  }

  const rupture =
    altere === null
      ? -1
      : entrees.findIndex(
          (e, i) => i > 0 && e.precedente !== entrees[i - 1].empreinte,
        );

  return (
    <div className="simu">
      <div className="simu__tete">
        <span className="simu__marque">Simulation</span>
        <span className="simu__titre">Modifier une ligne du journal</span>
        <span className="simu__aide">
          Chaque entrée porte l&apos;empreinte de la précédente. Changez l&apos;auteur
          d&apos;une entrée ancienne et regardez où la chaîne se rompt.
        </span>
      </div>

      <div className="simu__corps">
        <div className="interrupteurs" style={{ marginBottom: 16 }}>
          <button
            type="button"
            className="interrupteur"
            aria-pressed={altere === null}
            onClick={() => alterer(null)}
          >
            Journal intact
          </button>
          {[1, 2, 3].map((rang) => (
            <button
              key={rang}
              type="button"
              className="interrupteur"
              aria-pressed={altere === rang}
              onClick={() => alterer(rang)}
            >
              Réécrire l&apos;auteur de l&apos;entrée {rang}
            </button>
          ))}
        </div>

        {entrees.map((entree, i) => {
          const rompu = i > 0 && entree.precedente !== entrees[i - 1].empreinte;
          const apres = rupture !== -1 && i > rupture;
          return (
            <div
              key={entree.rang}
              className={`chainon${rompu ? " chainon--rompu" : apres ? " chainon--apres-rupture" : ""}`}
            >
              <span className="chainon__rang">{String(entree.rang).padStart(2, "0")}</span>
              <span>
                <span className="chainon__action">{entree.action}</span>{" "}
                <span style={{ color: "var(--encre-tres-doux)" }}>
                  {entree.objet} · par {entree.acteur}
                </span>
                <span className="chainon__empreinte">
                  précédente {entree.precedente.slice(0, 16)}…
                </span>
                <span className="chainon__empreinte">
                  empreinte&nbsp;&nbsp;{entree.empreinte.slice(0, 16)}…
                </span>
                {rompu ? (
                  <span
                    style={{
                      display: "block",
                      marginTop: 6,
                      fontWeight: 600,
                      color: "var(--rouge)",
                      fontSize: 13,
                    }}
                  >
                    Rupture : cette entrée annonce une empreinte précédente qui ne correspond
                    plus à celle de l&apos;entrée {entree.rang - 1}.
                  </span>
                ) : null}
              </span>
            </div>
          );
        })}

        <div className={`verdict verdict--${altere === null ? "vert" : "rouge"}`} style={{ marginTop: 14 }}>
          <span className="verdict__pastille" aria-hidden="true" />
          <span className="verdict__texte">
            <b>{altere === null ? "Chaîne vérifiée" : "Chaîne rompue"}</b>
            {altere === null
              ? "Chaque entrée annonce l'empreinte de la précédente, et l'annonce est exacte de bout en bout."
              : `L'entrée ${altere} a été réécrite. Son empreinte a changé, mais l'entrée suivante annonce toujours l'ancienne : la vérification s'arrête là et nomme le rang.`}
          </span>
        </div>
      </div>

      <div className="simu__pied">
        <b>Ce qu&apos;il faut retenir.</b> Pour effacer une trace sans être vu, il ne suffit
        pas de modifier une ligne : il faudrait recalculer toutes celles qui suivent, et le
        faire au même instant, sans qu&apos;aucune copie ni sauvegarde ne conserve la
        version d&apos;avant. C&apos;est ce qui distingue un historique d&apos;un journal
        d&apos;audit, et c&apos;est pourquoi il n&apos;existe dans le produit ni mise à jour
        ni suppression sur ce journal, pas même pour un administrateur.
      </div>
    </div>
  );
}
