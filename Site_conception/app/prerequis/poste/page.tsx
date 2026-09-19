import type { Metadata } from "next";

import { Note, Tableau } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";
import { Chapitre, Lecon } from "@/app/composants/Lecon";
import { Exercice, Faits, FilDAriane, Objectifs } from "@/app/composants/Pedagogie";

export const metadata: Metadata = {
  title: "Cours · Le poste de travail",
  description:
    "Séance pratique : monter son poste, faire tourner la plateforme, lire le code dans le bon ordre, et livrer une modification prouvée.",
};

const PLAN = [
  { id: "outillage", titre: "1 · Ce qu'il faut avoir" },
  { id: "base", titre: "2 · La base de données" },
  { id: "pile", titre: "3 · La pile de démonstration" },
  { id: "tests", titre: "4 · La suite de tests" },
  { id: "introspection", titre: "5 · Ce que la plateforme dit d'elle-même" },
  { id: "lecture", titre: "6 · Lire le code dans le bon ordre" },
  { id: "modifier", titre: "7 · Faire une modification, et la prouver" },
  { id: "pannes", titre: "8 · Quand ça ne marche pas" },
  { id: "site", titre: "9 · Ce site, en local" },
];

export default function CoursPoste() {
  return (
    <>
      <Entete courant="/prerequis" />
      <main className="page">
        <section className="cours-tete">
          <FilDAriane
            pieces={[
              { libelle: "Prérequis", href: "/prerequis" },
              { libelle: "Le poste de travail" },
            ]}
          />
          <h1>Séance pratique : votre poste, en une heure</h1>
          <p className="cours-tete__chapo">
            À faire dans l&apos;ordre, commandes comprises. À la fin, la plateforme tourne sur
            votre machine avec un jeu de démonstration, la suite de tests passe, et vous savez où
            regarder quand quelque chose ne va pas.
          </p>
          <Faits
            faits={[
              { mot: "durée", valeur: "environ 60 minutes" },
              { mot: "chapitres", valeur: "9" },
              { mot: "format", valeur: "à faire, pas à lire" },
            ]}
          />
          <Objectifs
            points={[
              "Faire tourner la plateforme complète sur votre machine.",
              "Reconnaître une suite de tests qui ment, et la faire dire la vérité.",
              "Interroger la plateforme sur son propre état.",
              "Remonter d'un comportement observé jusqu'à la règle qui le produit.",
              "Livrer une modification accompagnée de la preuve qu'elle vérifie ce qu'elle prétend.",
            ]}
          />
        </section>

        <Lecon chapitres={PLAN}>
          <Chapitre id="outillage" rang="Étape 1" titre="Ce qu'il faut avoir">
            <Tableau
              entetes={["Outil", "Version", "À quoi il sert ici"]}
              lignes={[
                ["Python", "3.11 ou plus", "Tout le serveur"],
                ["Node.js", "20 ou plus", "Les interfaces et ce site"],
                ["Docker", "récent", "Uniquement PostgreSQL en local"],
                ["Git", "récent", "Le dépôt"],
              ]}
            />
            <pre>
              <code>{`python --version
node --version
docker --version
git --version`}</code>
            </pre>
            <p>
              <b>Ce que vous devez voir</b> : quatre versions affichées, et aucune commande
              introuvable.
            </p>
          </Chapitre>

          <Chapitre id="base" rang="Étape 2" titre="La base de données">
            <pre>
              <code>{`cd Backend_erp_cga
eval "$(outils/postgres-local.sh start)"`}</code>
            </pre>
            <p>
              Le script démarre une instance PostgreSQL dédiée au projet et affiche les variables
              d&apos;environnement à poser. Il ne touche pas à une base que vous auriez déjà, et
              il emploie un port qui n&apos;est pas le port habituel, pour la même raison.
            </p>
            <p>
              <b>Ce que vous devez voir</b> : une ligne d&apos;URL de connexion, et un port
              inhabituel.
            </p>
            <Note titre="Pourquoi « eval » et non un simple appel" ton="attention">
              <p>
                Un script enfant ne peut pas modifier l&apos;environnement de son parent. Il
                affiche donc les variables, et <code>eval</code> les pose dans votre terminal.
                Sans cela, le script s&apos;exécute correctement et votre terminal ne sait
                toujours rien de la base.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="pile" rang="Étape 3" titre="La pile de démonstration">
            <pre>
              <code>{`outils/pile-de-demonstration.sh neuve`}</code>
            </pre>
            <p>
              Une base recréée, les migrations jouées, l&apos;API et l&apos;interface démarrées,
              et un cabinet fictif garni : des adhérents, des pièces, des constats de conformité,
              des échéances, des écritures.
            </p>
            <p>
              <b>Ce que vous devez voir</b> : deux adresses locales, une pour l&apos;API et une
              pour l&apos;interface, et un compte de démonstration.
            </p>
            <Note titre="Le mot « neuve » compte" ton="piege">
              <p>
                Il <b>recrée</b> la base. C&apos;est ce qu&apos;on veut pour une découverte, et
                ce qu&apos;on ne veut surtout pas sur une base qui porte du travail. Sans ce mot,
                la pile démarre sur l&apos;existant.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="tests" rang="Étape 4" titre="La suite de tests">
            <pre>
              <code>{`python -m pytest -q -rs`}</code>
            </pre>
            <p>
              <b>Ce que vous devez voir</b> : 3 727 tests passés, et <b>aucun ignoré</b>. Un
              compte de tests ignorés qui n&apos;est pas nul signifie presque toujours que
              PostgreSQL n&apos;est pas joignable : les cas qui en dépendent se taisent au lieu
              d&apos;échouer, et la suite paraît verte alors qu&apos;elle n&apos;a pas tout
              vérifié.
            </p>
            <Exercice
              enonce="La suite affiche « 3 419 passed, 308 skipped ». Que faites-vous ?"
              reponse={
                <p>
                  Vous ne continuez pas. L&apos;option <code>-rs</code> donne la raison : la base
                  est injoignable. Vous relancez l&apos;étape 2, et vous relancez la suite. Un
                  code livré sur une suite à trois cents cas ignorés n&apos;a pas été vérifié sur
                  la persistance, c&apos;est-à-dire sur la moitié qui casse le plus souvent.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="introspection" rang="Étape 5" titre="Ce que la plateforme dit d'elle-même">
            <pre>
              <code>{`GET /transverse/services`}</code>
            </pre>
            <p>
              Cette route répond, pour chacun des quatorze services : jusqu&apos;où il est écrit,
              s&apos;il répond à l&apos;instant, et <b>ce qui tombe avec lui</b>. C&apos;est la
              question qu&apos;on se pose pendant un incident, et c&apos;est celle à laquelle un
              tableau écrit à la main ne répond jamais correctement, parce qu&apos;il dérive.
            </p>
            <Tableau
              entetes={["Ce que la route distingue", "Pourquoi les séparer"]}
              lignes={[
                [
                  "Construction : est-ce écrit ?",
                  "Constaté sur le disque et sur l'application montée",
                ],
                [
                  "Exécution : répond-il maintenant ?",
                  "Constaté par une sonde, quand le service en a une",
                ],
                [
                  "Dépendance : qu'est-ce qui tombe avec lui ?",
                  "Calculé sur le graphe, la seule chose déclarée",
                ],
              ]}
            />
            <p>
              Les fondre en un seul état ferait passer un service complet dont la base est tombée
              pour « incomplet », et un service à peine commencé mais qui répond pour
              « opérationnel ». Le second mensonge est le plus coûteux.
            </p>
            <p>
              <b>Ce que vous devez voir</b> : treize services en service, un encore au stade des
              cas d&apos;usage, et trois sans sonde, ce qui est dit plutôt que masqué.
            </p>
          </Chapitre>

          <Chapitre id="lecture" rang="Étape 6" titre="Lire le code dans le bon ordre">
            <p>
              Pour comprendre un comportement, on remonte toujours dans le même sens. Prenez un
              exemple réel : « pourquoi ce constat majeur reste-t-il en attente après que je
              l&apos;ai écarté ? »
            </p>
            <ol>
              <li>
                <code>adaptateurs/entrant/routes_*.py</code> : ce que l&apos;écran appelle, et
                qui a le droit de l&apos;appeler.
              </li>
              <li>
                <code>application/</code> : l&apos;enchaînement des gestes, et ce qui est
                journalisé.
              </li>
              <li>
                <code>domaine/</code> : la règle elle-même et ses transitions. <b>La réponse est
                là dans la plupart des cas</b> : ici, la politique du cabinet exige un second
                regard sur les écarts majeurs, donc l&apos;écart reste en attente jusqu&apos;à
                l&apos;accord d&apos;un second habilité.
              </li>
              <li>
                <code>tests/</code> : le fichier de test porte souvent, dans son en-tête, la
                raison d&apos;être du mécanisme et les erreurs commises avant d&apos;arriver à
                cette forme.
              </li>
            </ol>
            <Exercice
              enonce="Un adhérent dit que sa pièce déposée n'apparaît pas dans sa liste. Par où commencez-vous ?"
              reponse={
                <p>
                  Par la route que l&apos;écran appelle, pour vérifier <b>sur quel périmètre</b>{" "}
                  elle lit. Neuf fois sur dix, une donnée qui « disparaît » est une donnée lue
                  avec un filtre différent de celui qui l&apos;a écrite : un autre dossier, un
                  autre mois, un autre statut. Le domaine vient ensuite.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="modifier" rang="Étape 7" titre="Faire une modification, et la prouver">
            <ol>
              <li>Écrire le cas de test qui échoue, et vérifier qu&apos;il échoue vraiment.</li>
              <li>Écrire le code qui le fait passer.</li>
              <li>Relancer toute la suite, pas seulement le fichier concerné.</li>
              <li>
                <b>Muter votre code volontairement</b> : inverser une comparaison, retirer une
                garde, changer un seuil. Si les tests passent encore, le cas que vous venez
                d&apos;écrire ne vérifie pas ce que vous croyez.
              </li>
              <li>
                Lancer <code>ruff check</code> et <code>ruff format</code>.
              </li>
              <li>
                Écrire, au-dessus du code, <b>pourquoi</b> il est ainsi, et le piège qu&apos;il
                évite s&apos;il y en a un.
              </li>
            </ol>
            <Note titre="Le geste numéro quatre est celui qu'on saute">
              <p>
                C&apos;est pourtant celui qui trouve le plus souvent quelque chose. Plusieurs cas
                de ce projet semblaient solides et ne vérifiaient rien : la mutation les a
                démasqués en trois secondes.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="pannes" rang="Étape 8" titre="Quand ça ne marche pas">
            <Tableau
              entetes={["Symptôme", "Cause la plus fréquente", "Geste"]}
              lignes={[
                [
                  "Des centaines de tests ignorés",
                  "PostgreSQL n'est pas joignable",
                  "Relancer le script de base, puis la suite",
                ],
                [
                  "Toutes les routes répondent 401",
                  "Le limiteur de connexions a été atteint par vos essais",
                  "Attendre quelques minutes, ou repartir sur une pile neuve",
                ],
                [
                  "Un sous-domaine répond introuvable",
                  "Le répertoire des clients n'a pas encore rechargé",
                  "Attendre la fenêtre de fraîcheur, trente secondes par défaut",
                ],
                [
                  "Un écran vide sans erreur",
                  "Le périmètre lu n'est pas celui attendu",
                  "Vérifier le locataire établi et le dossier demandé",
                ],
                [
                  "Une valeur légale absente",
                  "La date demandée n'est couverte par aucune version",
                  "Regarder le paramètre dans le référentiel, et ses périodes",
                ],
              ]}
            />
          </Chapitre>

          <Chapitre id="site" rang="Étape 9" titre="Ce site, en local">
            <pre>
              <code>{`cd Site_conception
npm install
npm run dev`}</code>
            </pre>
            <p>
              La construction relit le document de conception et engendre la page servie. Si vous
              modifiez le document pendant que le serveur tourne, rejouez{" "}
              <code>npm run importer</code> : le serveur de développement ne surveille pas un
              fichier qui vit hors du projet.
            </p>
            <p style={{ marginTop: 32 }}>
              <a className="site-bouton site-bouton--plein" href="/document">
                Vous êtes prêt : ouvrir le document de conception
              </a>
            </p>
          </Chapitre>
        </Lecon>
      </main>
      <Pied />
    </>
  );
}
