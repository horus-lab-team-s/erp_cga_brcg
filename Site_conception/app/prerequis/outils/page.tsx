import type { Metadata } from "next";

import { Note, Tableau } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";
import { Chapitre, Lecon } from "@/app/composants/Lecon";
import { Exercice, Faits, FilDAriane, Objectifs } from "@/app/composants/Pedagogie";

export const metadata: Metadata = {
  title: "Cours · Les outils",
  description:
    "FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, pytest, Ruff, Next.js : ce que chacun apporte, et ce qu'il évite d'écrire.",
};

const PLAN = [
  { id: "principe", titre: "1 · Choisir une dépendance" },
  { id: "fastapi", titre: "2 · FastAPI et Pydantic" },
  { id: "persistance", titre: "3 · SQLAlchemy, Alembic, PostgreSQL" },
  { id: "tests", titre: "4 · pytest, et la mutation" },
  { id: "front", titre: "5 · Next.js et React" },
  { id: "exploitation", titre: "6 · Docker, orchestrateur, ordonnanceur" },
  { id: "absents", titre: "7 · Ce qui est absent, et pourquoi" },
];

export default function CoursOutils() {
  return (
    <>
      <Entete courant="/prerequis" />
      <main className="page">
        <section className="cours-tete">
          <FilDAriane
            pieces={[{ libelle: "Prérequis", href: "/prerequis" }, { libelle: "Les outils" }]}
          />
          <h1>Les outils, et ce qu&apos;ils évitent d&apos;écrire</h1>
          <p className="cours-tete__chapo">
            Une liste de dépendances ne dit rien. Ce qui compte est ce qu&apos;il aurait fallu
            écrire à la main sans chacune, parce que c&apos;est exactement ce qu&apos;on
            récupère le jour où on envisage de la remplacer.
          </p>
          <Faits
            faits={[
              { mot: "durée", valeur: "environ 30 minutes" },
              { mot: "chapitres", valeur: "7" },
              { mot: "prérequis", valeur: "les concepts et les langages" },
            ]}
          />
          <Objectifs
            points={[
              "Justifier chaque dépendance du projet par ce qu'elle évite d'écrire.",
              "Savoir où une requête entre, où elle est validée, où elle est journalisée.",
              "Lancer la suite de tests et interpréter un compte de tests ignorés.",
              "Écrire une petite batterie de mutation autour de votre propre code.",
              "Dire pourquoi le projet n'a ni bus de messages ni cache distribué.",
            ]}
          />
        </section>

        <Lecon chapitres={PLAN}>
          <Chapitre id="principe" rang="Chapitre 1" titre="Choisir une dépendance">
            <p>
              Une bibliothèque de plus est une chose de plus à mettre à jour, à comprendre, et à
              expliquer au suivant. Le projet en compte peu, et chacune répond à une question
              simple : <b>qu&apos;est-ce qu&apos;il faudrait écrire et maintenir sans elle ?</b>
            </p>
            <p>
              Quand la réponse est « quelques dizaines de lignes », on écrit les lignes. Quand
              c&apos;est « une implémentation correcte d&apos;une fonction cryptographique », on
              prend la bibliothèque, parce qu&apos;une version maison est la faute la plus
              classique et la plus coûteuse du métier.
            </p>
          </Chapitre>

          <Chapitre id="fastapi" rang="Chapitre 2" titre="FastAPI et Pydantic">
            <p>
              FastAPI reçoit les requêtes, valide les corps, produit les codes d&apos;erreur et
              engendre la documentation de l&apos;API depuis le code lui-même, ce qui la rend
              impossible à périmer.
            </p>
            <pre>
              <code>{`class DemandeDEcart(BaseModel):
    model_config = ConfigDict(extra="forbid")   # une clé inconnue est refusée

    code_regle: str
    motif: str = Field(min_length=20)
    piece_appui: str | None = None


@routeur.post("/pieces/{reference}/ecarts", status_code=201)
def proposer_un_ecart(reference: str, corps: DemandeDEcart, acces: AccesRequis):
    exiger(acces, Permission.ECARTER_CONSTAT)      # l'autorisation, d'abord
    ecart = application.proposer(reference, corps, par=acces.compte)
    return {"ecart": ecart}`}</code>
            </pre>
            <h3>Le chemin d&apos;une requête, dans l&apos;ordre</h3>
            <div className="frise" role="list" aria-label="Chemin d'une requête">
              {[
                ["1", "Le sous-domaine donne le locataire"],
                ["2", "La session donne le compte"],
                ["3", "La permission est exigée"],
                ["4", "Le corps est validé"],
                ["5", "Le cas d'usage s'exécute"],
                ["6", "L'action est journalisée"],
                ["7", "La transaction est validée"],
              ].map(([rang, texte]) => (
                <div className="frise__etape" role="listitem" key={rang}>
                  <b>Étape {rang}</b>
                  {texte}
                </div>
              ))}
            </div>
            <Note titre="L'ordre porte un sens" ton="attention">
              <p>
                L&apos;autorisation vient <b>avant</b> la validation du corps. Un corps mal formé
                envoyé par quelqu&apos;un qui n&apos;a pas le droit d&apos;agir doit recevoir un
                refus d&apos;accès, pas un rapport détaillé sur les champs attendus : ce rapport
                est une description de l&apos;API offerte à qui n&apos;y a pas droit.
              </p>
              <p>
                Ce défaut a réellement existé dans ce projet : un cas d&apos;accès qui envoyait
                des lignes vides tombait en validation avant le contrôle d&apos;accès, et ne
                prouvait donc rien de ce qu&apos;il prétendait vérifier.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="persistance" rang="Chapitre 3" titre="SQLAlchemy, Alembic, PostgreSQL">
            <Tableau
              entetes={["Outil", "Ce qu'il fait ici", "Sans lui"]}
              lignes={[
                [
                  "SQLAlchemy",
                  "Les requêtes, et surtout le filtre du client posé automatiquement",
                  "Le filtre répété dans chaque requête, avec un oubli qui ne se voit pas",
                ],
                [
                  "Alembic",
                  "Les migrations versionnées, jouées avant le démarrage",
                  "Des scripts joués à la main, dans un ordre dont personne n'est sûr",
                ],
                [
                  "PostgreSQL",
                  "Les données, et les règles de cloisonnement écrites dans la base",
                  "Une confiance totale dans le programme qui interroge la base",
                ],
                [
                  "psycopg 3",
                  "Le pilote de connexion",
                  "La version 2, qui n'est plus la voie recommandée",
                ],
              ]}
            />
            <h3>L&apos;unité de travail</h3>
            <p>
              Une transaction par requête, ouverte au bord et validée à la sortie. Elle est
              ouverte <b>ici et nulle part ailleurs</b> : dix-huit routes qui valideraient chacune
              produiraient dix-huit transactions par requête, et une écriture partielle à la
              première erreur.
            </p>
            <Exercice
              enonce="Votre cas d'usage écrit une écriture comptable et une entrée de journal. La seconde échoue. Que se passe-t-il ?"
              reponse={
                <p>
                  Les deux sont annulées : elles sont dans la même transaction, et la sortie en
                  exception l&apos;annule. C&apos;est la propriété qui rend le journal
                  crédible : il n&apos;existe pas d&apos;action enregistrée sans sa trace, ni de
                  trace sans son action.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="tests" rang="Chapitre 4" titre="pytest, et la mutation">
            <pre>
              <code>{`python -m pytest -q          # tout, en silence
python -m pytest -q -rs      # tout, avec la RAISON des tests ignorés`}</code>
            </pre>
            <Note titre="Un test ignoré n'est pas un test qui passe" ton="piege">
              <p>
                Les cas qui ont besoin de PostgreSQL se taisent quand la base est injoignable, au
                lieu d&apos;échouer. La suite paraît alors verte et n&apos;a vérifié qu&apos;une
                partie du système. Un jour, trois cent huit cas ont ainsi été ignorés sans que
                personne le remarque.
              </p>
              <p>
                <b>Le compte attendu est zéro ignoré</b>, et <code>-rs</code> dit pourquoi
                quand ce n&apos;est pas le cas.
              </p>
            </Note>
            <h3>La mutation, en pratique</h3>
            <p>
              Une suite verte ne prouve pas que les tests vérifient quelque chose. On introduit
              donc volontairement un défaut, et on relance. Si les tests passent encore, la
              mutation a <b>survécu</b>, et c&apos;est le test qui est en cause.
            </p>
            <pre>
              <code>{`# Une batterie, écrite à la main autour du code qu'on vient d'ajouter
MUTATIONS = [
    # Le défaut d'origine, remis en place : il doit être tué.
    ("app/.../api.py", "valider(slug, noms_reserves())", "valider(slug)"),
    # La fenêtre devient stricte au lieu de large.
    ("app/.../repertoire.py", "ecart >= fenetre", "ecart > fenetre"),
    # L'instant n'est plus noté quand l'essai échoue.
    ("app/.../repertoire.py", "dernier = maintenant()\\n    try:", "try:"),
]`}</code>
            </pre>
            <Exercice
              enonce="Une mutation survit. Vous pensez qu'elle est équivalente, c'est-à-dire qu'elle ne change rien d'observable. Que faites-vous ?"
              reponse={
                <>
                  <p>
                    Vous le prouvez avant de le croire. Dans ce projet, une mutation retirait la
                    mise en minuscules d&apos;une clé et survivait. Elle paraissait équivalente
                    parce que tous les tests construisaient leurs objets par une fonction qui
                    refuse les capitales.
                  </p>
                  <p>
                    Or le modèle, lui, les accepte : une ligne écrite avant que la règle
                    n&apos;existe, ou par une migration, en porterait une. Le cas a été réécrit
                    sur <b>ce qui peut réellement se trouver en base</b>, et la mutation est
                    morte.
                  </p>
                </>
              }
            />
          </Chapitre>

          <Chapitre id="front" rang="Chapitre 5" titre="Next.js et React">
            <Tableau
              entetes={["Outil", "Ce qu'il fait ici"]}
              lignes={[
                [
                  "Next.js 16",
                  "Le routage par dossiers, le rendu serveur, la construction, les métadonnées",
                ],
                ["React 19", "Les composants, et l'interactivité là où elle est nécessaire"],
                [
                  "Tailwind CSS",
                  "Les styles de l'application de gestion. Ce site, lui, a sa propre feuille, parce qu'il partage la palette du document",
                ],
              ]}
            />
            <p>
              Le routage suit les dossiers : <code>app/prerequis/outils/page.tsx</code> répond à
              l&apos;adresse <code>/prerequis/outils</code>. Il n&apos;y a pas de table de routes
              à tenir à jour, donc pas de route oubliée.
            </p>
          </Chapitre>

          <Chapitre id="exploitation" rang="Chapitre 6" titre="Docker, orchestrateur, ordonnanceur">
            <Tableau
              entetes={["Outil", "Rôle", "État"]}
              lignes={[
                [
                  "Docker",
                  "La base de développement, et l'image de l'application",
                  "En service",
                ],
                [
                  "Kubernetes",
                  "Les manifestes : configuration, volume, migration, API, ordonnanceur, entrée TLS",
                  "Écrits et vérifiés contre la configuration, jamais appliqués sur un serveur",
                ],
                [
                  "L'ordonnanceur",
                  "Les travaux de fond : relais des messages, relances, veille, rappels d'échéance",
                  "En service, dans le processus ou par appel extérieur",
                ],
              ]}
            />
            <Note titre="Les manifestes sont vérifiés, pas seulement écrits">
              <p>
                Un test relit les manifestes et vérifie que chaque variable qu&apos;ils posent
                existe réellement dans la configuration de l&apos;application. Ce contrôle a
                trouvé deux défauts le jour où il a été écrit, dont une clé de secret nommée
                comme une variable d&apos;environnement : cela ne fait rien, en silence, et se
                découvre au premier démarrage en production.
              </p>
            </Note>
            <p>
              L&apos;ordonnanceur tourne en <b>un seul exemplaire</b>, tandis que l&apos;API en a
              plusieurs. C&apos;est une contrainte à connaître : un mécanisme qui compterait sur
              l&apos;ordonnanceur pour tenir à jour la mémoire des processus d&apos;API ne
              toucherait qu&apos;un processus sur trois.
            </p>
          </Chapitre>

          <Chapitre id="absents" rang="Chapitre 7" titre="Ce qui est absent, et pourquoi">
            <Tableau
              entetes={["Absent", "La raison", "Ce qui le ferait entrer"]}
              lignes={[
                [
                  "Un bus de messages dédié",
                  "La boîte d'envoi en base suffit au volume visé, et garantit qu'un message n'est jamais publié sans que la donnée soit écrite",
                  "Le jour où les services se déploieront séparément",
                ],
                [
                  "Un cache distribué",
                  "La seule donnée lue à chaque requête tient en mémoire dans chaque processus et se recharge toute seule",
                  "Un jeu de données partagé, volumineux et coûteux à recalculer",
                ],
                [
                  "Un moteur de recherche externe",
                  "La recherche est fédérée entre contextes, sur des volumes qui ne le justifient pas",
                  "Une recherche plein texte sur des millions de pièces",
                ],
                [
                  "Un registre de découverte de services",
                  "Il n'a de sens que lorsque les services sont réellement séparés et déployés indépendamment",
                  "La séparation effective des déploiements",
                ],
              ]}
            />
            <p>
              Chacune de ces absences est un choix daté, avec sa condition de sortie. C&apos;est
              la différence entre un manque et une décision : un manque se découvre, une décision
              s&apos;explique.
            </p>
            <p style={{ marginTop: 32 }}>
              <a className="site-bouton site-bouton--plein" href="/prerequis/poste">
                Cours suivant : le poste de travail
              </a>
            </p>
          </Chapitre>
        </Lecon>
      </main>
      <Pied />
    </>
  );
}
