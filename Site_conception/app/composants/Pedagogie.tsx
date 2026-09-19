/**
 * Les blocs propres à un cours : objectifs, exercice, réponse à dévoiler.
 *
 * ⚠️ **Une réponse se dévoile, elle ne s'affiche pas.** Un exercice dont la solution
 * est visible à côté de l'énoncé n'est pas un exercice, c'est un exemple : le lecteur
 * lit la réponse avant d'avoir cherché, et croit avoir compris. `details` fait cela
 * sans une ligne de JavaScript, et fonctionne même si le script ne se charge pas.
 */

export function Objectifs({ titre = "À la fin de ce cours, vous saurez", points }: { titre?: string; points: string[] }) {
  return (
    <div className="objectifs">
      <h2>{titre}</h2>
      <ul>
        {points.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ul>
    </div>
  );
}

export function Exercice({
  enonce,
  children,
  reponse,
}: {
  enonce: string;
  children?: React.ReactNode;
  reponse: React.ReactNode;
}) {
  return (
    <div className="exercice">
      <p className="exercice__marque">À vous</p>
      <p style={{ margin: 0, fontWeight: 600 }}>{enonce}</p>
      {children}
      <details>
        <summary>Voir la réponse</summary>
        {reponse}
      </details>
    </div>
  );
}

export function Faits({ faits }: { faits: { mot: string; valeur: string }[] }) {
  return (
    <div className="cours-tete__faits">
      {faits.map((fait) => (
        <span className="etiquette" key={fait.mot}>
          {fait.mot} · {fait.valeur}
        </span>
      ))}
    </div>
  );
}

export function FilDAriane({ pieces }: { pieces: { libelle: string; href?: string }[] }) {
  return (
    <p className="cours-tete__fil">
      {pieces.map((piece, rang) => (
        <span key={piece.libelle}>
          {rang > 0 ? <span aria-hidden="true"> › </span> : null}
          {piece.href ? <a href={piece.href}>{piece.libelle}</a> : <span>{piece.libelle}</span>}
        </span>
      ))}
    </p>
  );
}
