import type { Metadata } from "next";

import { Note } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";
import { Onglets } from "@/app/composants/Onglets";

export const metadata: Metadata = {
  title: "Prérequis",
  description:
    "Quatre cours : les concepts, les langages, les outils et le poste de travail, avec des simulations interactives.",
};

/**
 * Le sommaire des cours.
 *
 * ⚠️ **Les onglets présentent, les pages enseignent.** Mettre les quatre cours entiers
 * dans quatre onglets d'une seule page ferait une page de plusieurs centaines de
 * kilo-octets dont le lecteur ne verrait jamais les trois quarts, et dont le plan
 * latéral, qui suit la lecture, n'aurait plus de sens. Chaque cours a donc sa page,
 * avec son propre plan et sa propre barre de progression.
 */

type Cours = {
  cle: string;
  libelle: string;
  href: string;
  titre: string;
  duree: string;
  chapitres: number;
  simulations: number;
  resume: string;
  pour: string;
  plan: string[];
  acquis: string[];
};

const COURS: Cours[] = [
  {
    cle: "concepts",
    libelle: "Les concepts",
    href: "/prerequis/concepts",
    titre: "Les concepts qui tiennent ce projet",
    duree: "environ 50 minutes",
    chapitres: 9,
    simulations: 4,
    resume:
      "Le métier d'abord, parce qu'il commande tout le reste : un centre agréé répond de ses chiffres, et le droit fiscal change chaque année. Ensuite le découpage du code, le moteur et sa configuration, le cloisonnement des clients, le journal qu'on ne peut pas réécrire, et ce qu'une transaction ne couvre pas.",
    pour: "Commencez par celui-ci, même si vous êtes pressé. Le reste ne se comprend pas sans lui.",
    plan: [
      "Le métier commande tout",
      "Le contexte borné",
      "Ports et adaptateurs",
      "Le moteur et sa configuration",
      "Plusieurs clients, une seule base",
      "Le journal chaîné",
      "Ce qu'une transaction ne couvre pas",
      "Ce que le code refuse",
      "Comment le projet avance",
    ],
    acquis: [
      "Dire où va un nouveau bout de code, et pourquoi il ne va pas ailleurs",
      "Lire un rapport de conformité et comprendre pourquoi il ne répond pas par oui ou par non",
      "Expliquer pourquoi la plateforme répond « introuvable » à un client suspendu",
    ],
  },
  {
    cle: "langages",
    libelle: "Les langages",
    href: "/prerequis/langages",
    titre: "Les langages, tels qu'ils sont employés ici",
    duree: "environ 40 minutes",
    chapitres: 8,
    simulations: 1,
    resume:
      "Python, TypeScript, SQL, YAML et HTML. Pas un cours de langage : la part de chacun qui sert réellement ici, les conventions du projet, et les pièges qui ont déjà coûté quelque chose.",
    pour: "À lire après les concepts, avant d'ouvrir un fichier.",
    plan: [
      "Pourquoi ces langages",
      "Python : des modèles qui refusent",
      "Python : le style du projet",
      "YAML : le référentiel",
      "SQL : deux ceintures",
      "TypeScript et React",
      "HTML et CSS",
      "Les pièges par langage",
    ],
    acquis: [
      "Écrire un modèle qui refuse d'exister dans un état impossible",
      "Lire un fichier du référentiel et dire ce que le code en fera",
      "Choisir entre un composant rendu sur le serveur et un composant interactif",
    ],
  },
  {
    cle: "outils",
    libelle: "Les outils",
    href: "/prerequis/outils",
    titre: "Les outils, et ce qu'ils évitent d'écrire",
    duree: "environ 30 minutes",
    chapitres: 7,
    simulations: 0,
    resume:
      "FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, pytest, Ruff, Next.js. Chaque dépendance est justifiée par ce qu'il aurait fallu écrire sans elle, et les absences par ce qui les ferait entrer.",
    pour: "Utile avant la première revue de code, indispensable avant la première livraison.",
    plan: [
      "Choisir une dépendance",
      "FastAPI et Pydantic",
      "SQLAlchemy, Alembic, PostgreSQL",
      "pytest, et la mutation",
      "Next.js et React",
      "Docker, orchestrateur, ordonnanceur",
      "Ce qui est absent, et pourquoi",
    ],
    acquis: [
      "Savoir où une requête entre, où elle est validée, où elle est journalisée",
      "Interpréter un compte de tests ignorés",
      "Écrire une batterie de mutation autour de votre propre code",
    ],
  },
  {
    cle: "poste",
    libelle: "Le poste de travail",
    href: "/prerequis/poste",
    titre: "Séance pratique : votre poste, en une heure",
    duree: "environ 60 minutes",
    chapitres: 9,
    simulations: 0,
    resume:
      "À faire, pas à lire. La base, la pile de démonstration, la suite de tests, l'introspection de la plateforme, la lecture du code dans le bon ordre, et la façon de livrer une modification prouvée.",
    pour: "En dernier, quand vous savez ce que vous allez faire tourner.",
    plan: [
      "Ce qu'il faut avoir",
      "La base de données",
      "La pile de démonstration",
      "La suite de tests",
      "Ce que la plateforme dit d'elle-même",
      "Lire le code dans le bon ordre",
      "Faire une modification, et la prouver",
      "Quand ça ne marche pas",
      "Ce site, en local",
    ],
    acquis: [
      "Faire tourner la plateforme complète sur votre machine",
      "Reconnaître une suite de tests qui ment",
      "Remonter d'un comportement observé jusqu'à la règle qui le produit",
    ],
  },
];

export default function Prerequis() {
  return (
    <>
      <Entete courant="/prerequis" />
      <main className="page page--etroite">
        <section className="bandeau">
          <p className="bandeau__oeil">Quatre cours</p>
          <h1>Ce qu&apos;il faut savoir avant de lire le code</h1>
          <p className="bandeau__chapo">
            Trois heures de lecture au total, dans l&apos;ordre. Les notions d&apos;abord, parce
            que le découpage du code ne se devine pas ; les langages et les outils ensuite ; le
            poste de travail à la fin, quand vous savez ce que vous allez y faire tourner.
          </p>
          <div className="bandeau__gestes">
            <a className="site-bouton site-bouton--plein" href="/prerequis/concepts">
              Commencer par les concepts
            </a>
            <a className="site-bouton" href="/prerequis/poste">
              Aller droit à la pratique
            </a>
          </div>
        </section>

        <section className="bloc" style={{ paddingTop: "40px" }}>
          <h2 className="bloc__titre">Le parcours</h2>
          <p className="bloc__intro">
            Chaque onglet présente un cours : sa durée, son plan, et ce que vous saurez faire à
            la fin. Cinq simulations sont réparties dans les deux premiers : elles rendent
            tangibles les notions qui se comprennent mal en paragraphes.
          </p>

          <Onglets
            etiquette="Les quatre cours"
            onglets={COURS.map((cours) => ({
              cle: cours.cle,
              libelle: cours.libelle,
              contenu: <FicheDeCours cours={cours} />,
            }))}
          />
        </section>

        <section className="bloc">
          <h2 className="bloc__titre">Les simulations</h2>
          <p className="bloc__intro">
            Elles ne demandent aucune installation : tout se passe dans votre navigateur. Chacune
            se termine par ce qu&apos;il faut en retenir, et dit franchement ce qu&apos;elle ne
            montre pas.
          </p>
          <div className="grille">
            {[
              {
                titre: "Contrôler une facture",
                ou: "/prerequis/concepts#moteur",
                quoi: "Changez une mention, un mode de règlement, un délai, et regardez le rapport se refaire. Le moteur ne répond jamais par oui ou par non.",
              },
              {
                titre: "Résoudre un sous-domaine",
                ou: "/prerequis/concepts#cloisonnement",
                quoi: "Quatre situations très différentes rendent la même réponse. C'est délibéré, et cette simulation explique pourquoi.",
              },
              {
                titre: "Modifier le journal",
                ou: "/prerequis/concepts#journal",
                quoi: "De vraies empreintes, calculées par votre navigateur. Réécrivez une entrée ancienne et voyez la chaîne se rompre.",
              },
              {
                titre: "Ouvrir un espace client",
                ou: "/prerequis/concepts#saga",
                quoi: "Choisissez l'étape qui échoue et regardez les précédentes se défaire dans l'ordre inverse.",
              },
              {
                titre: "Résoudre un paramètre à une date",
                ou: "/prerequis/langages#yaml",
                quoi: "Le même montant, deux dates, deux réponses. La raison pour laquelle « la valeur courante » n'existe pas ici.",
              },
            ].map((simu, rang) => (
              <a
                className="carte"
                href={simu.ou}
                key={simu.titre}
                data-teinte={(["accent", "azur", "rouge", "ambre", "accent"] as const)[rang]}
              >
                <span className="carte__oeil">Simulation</span>
                <h3 className="carte__titre">{simu.titre}</h3>
                <p>{simu.quoi}</p>
              </a>
            ))}
          </div>
        </section>

        <section className="bloc">
          <Note titre="Ce que ces cours ne remplacent pas" ton="attention">
            <p>
              Ils expliquent <b>ce projet</b>. Ils ne remplacent ni un cours de Python, ni un
              cours de comptabilité. Un développeur qui découvre Python fera bien de
              l&apos;apprendre ailleurs ; ce qu&apos;il ne trouvera nulle part ailleurs, c&apos;est
              pourquoi les noms sont en français ici, pourquoi un modèle refuse une clé inconnue,
              et pourquoi aucune valeur légale n&apos;est écrite dans le code.
            </p>
          </Note>
        </section>
      </main>
      <Pied />
    </>
  );
}

function FicheDeCours({ cours }: { cours: Cours }) {
  return (
    <div>
      <h3 style={{ fontFamily: "var(--serif)", fontSize: 24, margin: "0 0 10px", fontWeight: 600 }}>
        {cours.titre}
      </h3>
      <div className="cours-tete__faits" style={{ marginBottom: 18 }}>
        <span className="etiquette">durée · {cours.duree}</span>
        <span className="etiquette">{cours.chapitres} chapitres</span>
        {cours.simulations > 0 ? (
          <span className="etiquette etiquette--fait">
            {cours.simulations} simulation{cours.simulations > 1 ? "s" : ""}
          </span>
        ) : null}
      </div>
      <p>{cours.resume}</p>
      <p style={{ color: "var(--encre-tres-doux)", fontSize: 14 }}>{cours.pour}</p>

      <div className="grille" style={{ marginTop: 22 }}>
        <div className="carte">
          <span className="carte__oeil">Le plan</span>
          <ol style={{ margin: 0, paddingLeft: 20, fontSize: 14, color: "var(--encre-doux)" }}>
            {cours.plan.map((chapitre) => (
              <li key={chapitre} style={{ marginBottom: 4 }}>
                {chapitre}
              </li>
            ))}
          </ol>
        </div>
        <div className="carte">
          <span className="carte__oeil">À la fin, vous saurez</span>
          <ul style={{ margin: 0, paddingLeft: 20, fontSize: 14, color: "var(--encre-doux)" }}>
            {cours.acquis.map((acquis) => (
              <li key={acquis} style={{ marginBottom: 6 }}>
                {acquis}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p style={{ marginTop: 24 }}>
        <a className="site-bouton site-bouton--plein" href={cours.href}>
          Ouvrir le cours
        </a>
      </p>
    </div>
  );
}
