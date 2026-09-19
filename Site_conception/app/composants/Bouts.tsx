/**
 * Les petits morceaux qui reviennent partout : une note, un tableau, une étape.
 *
 * Ils existent pour que le contenu des pages reste du **texte**, et non un empilement
 * de balises : une documentation qu'on n'ose plus modifier parce qu'elle est illisible
 * en source cesse d'être mise à jour, et une documentation périmée est pire qu'absente.
 */

export function Note({
  titre,
  ton = "normal",
  children,
}: {
  titre: string;
  ton?: "normal" | "attention" | "piege";
  children: React.ReactNode;
}) {
  const classes = {
    normal: "note",
    attention: "note note--attention",
    piege: "note note--piege",
  };
  return (
    <aside className={classes[ton]}>
      <p className="note__titre">{titre}</p>
      {children}
    </aside>
  );
}

export function Tableau({
  entetes,
  lignes,
}: {
  entetes: string[];
  lignes: React.ReactNode[][];
}) {
  return (
    // ⚠️ L'enveloppe défile, et le dit par ses ombres. Un tableau large au téléphone
    // coupe une colonne sans prévenir, et le lecteur croit la page fautive plutôt que
    // de la faire glisser.
    <div className="tableau">
      <table>
        <thead>
          <tr>
            {entetes.map((entete) => (
              <th key={entete}>{entete}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {lignes.map((ligne, rang) => (
            <tr key={rang}>
              {ligne.map((cellule, colonne) => (
                <td key={colonne}>{cellule}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Carte({
  oeil,
  titre,
  children,
  href,
  teinte,
}: {
  oeil?: string;
  titre: string;
  children: React.ReactNode;
  href?: string;
  /** Le filet de couleur en haut de la carte. Il distingue quatre familles d'un coup
   *  d'œil, ce qu'un titre seul ne fait pas dans une grille de huit cartes. */
  teinte?: "accent" | "azur" | "ambre" | "rouge";
}) {
  const dedans = (
    <>
      {oeil ? <span className="carte__oeil">{oeil}</span> : null}
      <h3 className="carte__titre">{titre}</h3>
      {children}
    </>
  );
  return href ? (
    <a className="carte" href={href} data-teinte={teinte}>
      {dedans}
    </a>
  ) : (
    <div className="carte" data-teinte={teinte}>
      {dedans}
    </div>
  );
}

export function Etiquette({
  ton = "neutre",
  children,
}: {
  ton?: "neutre" | "fait" | "bloquant" | "attente";
  children: React.ReactNode;
}) {
  const classes = {
    neutre: "etiquette",
    fait: "etiquette etiquette--fait",
    bloquant: "etiquette etiquette--bloquant",
    attente: "etiquette etiquette--attente",
  };
  return <span className={classes[ton]}>{children}</span>;
}
