import { Entete, Pied } from "@/app/composants/Coquille";
import { Carte, Note } from "@/app/composants/Bouts";
import { Surgit } from "@/app/composants/Surgit";
import document from "@/contenu/document.json";
import site from "@/donnees/site.json";

/**
 * L'accueil : ce que fait la plateforme, et comment lire ce site.
 *
 * ⚠️ Volontairement court. Une page d'accueil qui explique tout est une page que
 * personne ne finit : elle dit de quoi il s'agit, elle donne les quatre portes, et
 * elle laisse le reste aux pages qui ont la place de le faire.
 */
export default function Accueil() {
  return (
    <>
      <Entete courant="/" />
      <main className="page">
        <section className="bandeau">
          <p className="bandeau__oeil">Dossier de conception</p>
          <h1>Une plateforme pour un centre de gestion agréé</h1>
          <p className="bandeau__chapo">{site.accroche}</p>
          <div className="bandeau__gestes">
            <a className="site-bouton site-bouton--plein" href="/document">
              Lire le document de conception
            </a>
            <a className="site-bouton" href="/prerequis">
              Commencer par les prérequis
            </a>
          </div>
          <p className="signature">
            <span>
              Conception et réalisation <b>{site.concepteur.nom}</b>, {site.concepteur.titre}
            </span>
          </p>
        </section>

        <section className="bloc" id="le-produit">
          <h2 className="bloc__titre">Ce que fait la plateforme</h2>
          <p className="bloc__intro">
            Un centre de gestion agréé tient la comptabilité, la fiscalité et la paie
            d&apos;entreprises qui lui confient leurs pièces. Il engage son agrément sur ce
            qu&apos;il produit. La plateforme déplace le contrôle fiscal <b>en amont</b> : une
            facture non conforme repérée à sa réception se régularise auprès du fournisseur ;
            découverte trois mois plus tard, elle ne laisse qu&apos;une perte sèche pour
            l&apos;adhérent.
          </p>

          <div className="grille">
            <Surgit>
            <Carte oeil="Le cœur" titre="Un moteur de règles, et de la configuration" teinte="accent">
              <p>
                Les taux, les seuils et les délais ne sont pas écrits dans le code : ils vivent
                dans des fichiers datés que le cabinet modifie. Une loi de finances se traduit
                par une valeur changée, pas par une livraison.
              </p>
            </Carte>
            </Surgit>
            <Surgit delai={80}>
            <Carte oeil="La conséquence" titre="Un chiffre, pas un avertissement" teinte="ambre">
              <p>
                Chaque anomalie produit une conséquence fiscale chiffrée, par exemple une TVA
                non déductible, qui se propage jusqu&apos;à la déclaration du mois puis à la
                liasse de l&apos;année.
              </p>
            </Carte>
            </Surgit>
            <Surgit delai={160}>
            <Carte oeil="La preuve" titre="Tout se justifie, trois ans plus tard" teinte="azur">
              <p>
                Quelle règle, quelle version, quel fondement légal, quelle date, et qui a
                décidé. Le journal est chaîné : une ligne modifiée après coup se voit.
              </p>
            </Carte>
            </Surgit>
            <Surgit delai={240}>
            <Carte oeil="Les clients" titre="Chacun chez soi" teinte="rouge">
              <p>
                Chaque cabinet et chaque entreprise dispose de son sous-domaine et de ses
                données cloisonnées. Hors de son périmètre, la plateforme répond que la
                ressource n&apos;existe pas, jamais qu&apos;elle est interdite.
              </p>
            </Carte>
            </Surgit>
          </div>

          <div className="chiffres">
            {site.chiffres.map((chiffre) => (
              <div className="chiffre" key={chiffre.libelle}>
                <div className="chiffre__valeur">{chiffre.valeur}</div>
                <div className="chiffre__libelle">{chiffre.libelle}</div>
                <div className="chiffre__precision">{chiffre.precision}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="bloc" id="comment-lire">
          <h2 className="bloc__titre">Comment lire ce site</h2>
          <p className="bloc__intro">
            Il est écrit pour être lu par quelqu&apos;un qui découvre le projet, dans
            l&apos;ordre, et il se lit comme une séance de travail plutôt que comme une
            brochure. Chaque notion est expliquée avant d&apos;être employée, et chacune
            renvoie à l&apos;endroit du code où elle vit.
          </p>
          <div className="grille">
            {site.navigation
              .filter((entree) => entree.href !== "/")
              .map((entree, rang) => (
                <Surgit key={entree.href} delai={rang * 80}>
                  <Carte titre={entree.libelle} href={entree.href}>
                    <p>{entree.resume}</p>
                  </Carte>
                </Surgit>
              ))}
          </div>

          <Note titre="Par où commencer, selon qui vous êtes">
            <p>
              <b>Vous rejoignez le développement</b> : les prérequis, puis le document dans
              l&apos;ordre. Comptez une demi-journée pour la première lecture.
            </p>
            <p>
              <b>Vous décidez</b> : l&apos;accueil, puis la mise en œuvre, qui dit ce qui reste
              à faire et ce qui bloque.
            </p>
            <p>
              <b>Vous cherchez un point précis</b> : le sommaire du document, qui donne accès
              à ses {document.sections} sections.
            </p>
          </Note>
        </section>

        <section className="bloc" id="cours">
          <h2 className="bloc__titre">Quatre cours, et cinq simulations</h2>
          <p className="bloc__intro">
            La documentation ne se contente pas de décrire le système : elle l&apos;enseigne.
            Chaque notion part d&apos;un problème concret du métier, et cinq simulations
            permettent d&apos;essayer les mécanismes qui se comprennent mal en paragraphes,
            sans rien installer.
          </p>
          <div className="grille">
            {[
              {
                oeil: "50 minutes · 4 simulations",
                titre: "Les concepts",
                href: "/prerequis/concepts",
                quoi: "Le métier, le découpage du code, le moteur et sa configuration, le cloisonnement, le journal chaîné, les sagas.",
                teinte: "accent" as const,
              },
              {
                oeil: "40 minutes · 1 simulation",
                titre: "Les langages",
                href: "/prerequis/langages",
                quoi: "Python, TypeScript, SQL, YAML, HTML, tels qu'ils servent ici, avec les pièges qui ont déjà coûté quelque chose.",
                teinte: "azur" as const,
              },
              {
                oeil: "30 minutes",
                titre: "Les outils",
                href: "/prerequis/outils",
                quoi: "Chaque dépendance justifiée par ce qu'elle évite d'écrire, et chaque absence par ce qui la ferait entrer.",
                teinte: "ambre" as const,
              },
              {
                oeil: "60 minutes · à faire",
                titre: "Le poste de travail",
                href: "/prerequis/poste",
                quoi: "La séance pratique : la base, la pile de démonstration, la suite de tests, et livrer une modification prouvée.",
                teinte: "rouge" as const,
              },
            ].map((cours, rang) => (
              <Surgit key={cours.href} delai={rang * 70}>
                <Carte oeil={cours.oeil} titre={cours.titre} href={cours.href} teinte={cours.teinte}>
                  <p>{cours.quoi}</p>
                </Carte>
              </Surgit>
            ))}
          </div>
        </section>

        <section className="bloc" id="honnetete">
          <h2 className="bloc__titre">Ce que ce dossier ne promet pas</h2>
          <p className="bloc__intro">
            Le produit est construit et éprouvé. Il n&apos;est pas, en revanche, prêt à servir
            un adhérent réel demain matin, et le dire est plus utile que de laisser le
            découvrir.
          </p>
          <Note titre="À lire avant toute mise en service" ton="attention">
            <p>
              Aucune valeur légale de ce système, taux, seuil, délai ou pénalité, n&apos;a été
              validée sur le Code Général des Impôts par un fiscaliste nommé. Toutes portent
              leur statut dans le référentiel, et quarante d&apos;entre elles attendent encore
              ce contreseing. Aucun chiffre produit n&apos;est opposable tant qu&apos;il
              manque.
            </p>
            <p>
              La page <a href="/mise-en-oeuvre">Mise en œuvre</a> dresse la liste complète de
              ce qui reste, en séparant ce qui bloque de ce qui attend.
            </p>
          </Note>
        </section>
      </main>
      <Pied />
    </>
  );
}
