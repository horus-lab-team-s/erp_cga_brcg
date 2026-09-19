import type { Metadata } from "next";

import { Note, Tableau } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";
import { Chapitre, Lecon } from "@/app/composants/Lecon";
import { Exercice, Faits, FilDAriane, Objectifs } from "@/app/composants/Pedagogie";
import { ParametreDate } from "@/app/composants/simulations/ParametreDate";

export const metadata: Metadata = {
  title: "Cours · Les langages",
  description:
    "Python, TypeScript, SQL, YAML et HTML tels qu'ils sont employés dans ce projet, avec les conventions et les pièges.",
};

const PLAN = [
  { id: "choix", titre: "1 · Pourquoi ces langages" },
  { id: "python-modeles", titre: "2 · Python : des modèles qui refusent" },
  { id: "python-style", titre: "3 · Python : le style du projet" },
  { id: "yaml", titre: "4 · YAML : le référentiel" },
  { id: "sql", titre: "5 · SQL : deux ceintures" },
  { id: "typescript", titre: "6 · TypeScript et React" },
  { id: "html", titre: "7 · HTML et CSS" },
  { id: "pieges", titre: "8 · Les pièges par langage" },
];

export default function CoursLangages() {
  return (
    <>
      <Entete courant="/prerequis" />
      <main className="page">
        <section className="cours-tete">
          <FilDAriane
            pieces={[{ libelle: "Prérequis", href: "/prerequis" }, { libelle: "Les langages" }]}
          />
          <h1>Les langages, tels qu&apos;ils sont employés ici</h1>
          <p className="cours-tete__chapo">
            Ce n&apos;est pas un cours de langage : c&apos;est la part de chacun qui sert
            réellement dans ce projet, les conventions qu&apos;on y suit, et les pièges qui ont
            déjà coûté quelque chose. Apprendre Python se fait ailleurs ; savoir ce qu&apos;on
            en attend ici ne se trouve qu&apos;ici.
          </p>
          <Faits
            faits={[
              { mot: "durée", valeur: "environ 40 minutes" },
              { mot: "chapitres", valeur: "8" },
              { mot: "simulations", valeur: "1" },
              { mot: "prérequis", valeur: "le cours des concepts" },
            ]}
          />
          <Objectifs
            points={[
              "Écrire un modèle de domaine qui refuse d'exister dans un état impossible.",
              "Reconnaître, dans une revue, les trois formes qu'un projet refuse.",
              "Lire un fichier du référentiel et dire ce que le code en fera.",
              "Expliquer pourquoi une requête SQL de ce projet n'écrit jamais son filtre de client.",
              "Choisir entre un composant rendu sur le serveur et un composant interactif.",
            ]}
          />
        </section>

        <Lecon chapitres={PLAN}>
          <Chapitre id="choix" rang="Chapitre 1" titre="Pourquoi ces langages">
            <p>
              Cinq langages en service, un sixième prévu. Chacun est là pour une raison, et aucun
              n&apos;est employé pour ce qu&apos;un autre ferait mieux.
            </p>
            <Tableau
              entetes={["Langage", "Où", "Pourquoi celui-là"]}
              lignes={[
                [
                  "Python 3.11+",
                  "Tout le serveur",
                  "Le typage progressif et les modèles validés donnent au domaine fiscal une forme qu'un comptable peut relire par-dessus l'épaule.",
                ],
                [
                  "TypeScript",
                  "Les deux interfaces web",
                  "Le type d'une réponse se déclare une fois, et une route renommée casse la compilation plutôt qu'un écran en production.",
                ],
                [
                  "SQL",
                  "La base et ses règles",
                  "Le cloisonnement est écrit dans la base elle-même, et pas seulement dans le programme qui l'interroge.",
                ],
                [
                  "YAML",
                  "Le référentiel légal",
                  "Un fiscaliste doit relire un taux et son fondement sans lire de code.",
                ],
                [
                  "HTML et CSS",
                  "Le document et ce site",
                  "Un document qui doit survivre dix ans ne dépend d'aucun outil de rendu : il s'ouvre dans un navigateur, et il s'imprime.",
                ],
                [
                  "Dart, prévu",
                  "L'application de terrain",
                  "Un usage qui doit survivre à une coupure réseau, avec une seule base de code pour les deux systèmes.",
                ],
              ]}
            />
          </Chapitre>

          <Chapitre id="python-modeles" rang="Chapitre 2" titre="Python : des modèles qui refusent">
            <p>
              Le projet emploie des modèles de données validés à la construction. Un objet mal
              formé <b>n&apos;existe pas</b> : il lève à l&apos;endroit où on tente de le
              fabriquer, et non trois couches plus loin quand quelqu&apos;un lit un champ nul.
            </p>
            <pre>
              <code>{`class EcartDeConstat(BaseModel):
    """Une dérogation accordée sur un constat de conformité."""

    # frozen : l'objet ne change pas. Un changement d'état produit un nouvel objet.
    model_config = ConfigDict(frozen=True)

    identifiant: str
    dossier: str
    severite: Severite
    motif: str = Field(min_length=20)      # un motif de trois mots ne défend rien
    propose_par: str
    propose_le: datetime
    statut: StatutEcart = StatutEcart.EN_ATTENTE
    piece_appui: str | None = None`}</code>
            </pre>
            <h3>Trois propriétés, et ce que chacune évite</h3>
            <Tableau
              entetes={["Propriété", "Ce qu'elle évite"]}
              lignes={[
                [
                  "Validé à la construction",
                  "Un champ nul découvert par l'écran, chez le client, au lieu du test",
                ],
                [
                  "Figé après création",
                  "Un objet partagé modifié discrètement par une fonction qui devait seulement le lire",
                ],
                [
                  "Fermé aux clés inconnues",
                  "Un réglage mal orthographié dans un fichier, ignoré en silence, et un comportement que personne n'explique",
                ],
              ]}
            />
            <h3>Un changement d&apos;état produit un nouvel objet</h3>
            <pre>
              <code>{`def joindre_une_piece_d_appui(self, reference, *, par, le):
    if self.statut in (StatutEcart.LEVE, StatutEcart.REFUSE):
        raise EcartRefuse("un écart sans effet n'accepte plus de pièce")
    reference = reference.strip()
    if len(reference) < 3:
        raise EcartRefuse("la pièce d'appui se désigne : un numéro, un intitulé")
    return self.model_copy(update={
        "piece_appui": reference, "piece_appui_le": le, "piece_appui_par": par,
    })`}</code>
            </pre>
            <p>
              La méthode appartient au <b>domaine</b>. Elle ne connaît ni la base, ni
              l&apos;heure : la date lui est donnée. C&apos;est ce qui permet de l&apos;éprouver
              en quelques millisecondes, et de rejouer un scénario daté de l&apos;an dernier.
            </p>
            <Exercice
              enonce="Vous devez ajouter un champ « commentaire du réviseur » sur cet écart. Quel est le risque si vous le rendez modifiable après coup ?"
              reponse={
                <p>
                  Un objet figé garantit qu&apos;une fonction qui reçoit un écart ne peut pas le
                  changer sous les pieds de son appelant. Rendre un seul champ modifiable ouvre
                  la porte à des modifications à distance, impossibles à retrouver dans une pile
                  d&apos;appels. On ajoute donc un champ, et une méthode qui rend une copie,
                  comme ci-dessus.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="python-style" rang="Chapitre 3" titre="Python : le style du projet">
            <h3>Les noms sont en français</h3>
            <p>
              Y compris les fonctions, les classes et les variables. Le domaine est français, ses
              lois sont écrites en français, et traduire chaque terme métier ajouterait une
              chance de se tromper à chaque ligne. <code>ecart</code> et <code>derogation</code>{" "}
              ne sont pas la même chose ; <code>waiver</code> les confond.
            </p>
            <h3>Les en-têtes expliquent pourquoi, pas quoi</h3>
            <pre>
              <code>{`"""La file d'anomalies du réviseur : tout le portefeuille, par gravité et par enjeu.

D'OÙ VIENT CE MODULE
  Le produit savait traiter dossier par dossier et règle par règle. Il ne savait pas
  dire « voici les six constats bloquants de votre portefeuille, le plus coûteux
  d'abord ». Or c'est ainsi que travaille un réviseur.

⚠️ Un constat qui dort passe devant DANS SA GRAVITÉ, jamais au-dessus. Un premier
   essai le faisait monter d'un cran : un avertissement de deux mois passait alors
   devant un bloquant du jour à 500 000 F. Un bloquant interdit la comptabilisation.
"""`}</code>
            </pre>
            <p>
              Le <b>⚠️</b> signale un piège concret, c&apos;est-à-dire une manière de faire qui
              paraît raisonnable et qui casse à l&apos;usage. Quand il raconte un essai
              précédent, il empêche quelqu&apos;un de refaire la même erreur dans six mois, en
              croyant améliorer le code.
            </p>
            <h3>Les trois formes que le projet refuse</h3>
            <Tableau
              entetes={["Refusé", "Pourquoi"]}
              lignes={[
                [
                  "Une valeur légale écrite dans le code",
                  "Le code devient faux à la prochaine loi de finances, et faux rétroactivement",
                ],
                [
                  "Une valeur par défaut qui masque une absence",
                  "Un locataire non établi servirait les lignes de n'importe qui, sans signal",
                ],
                [
                  "Un « except » qui avale l'erreur",
                  "L'incident devient invisible, et se manifeste plus tard sous une autre forme",
                ],
              ]}
            />
          </Chapitre>

          <Chapitre id="yaml" rang="Chapitre 4" titre="YAML : le référentiel">
            <p>
              Le référentiel est un ensemble de fichiers versionnés dans le dépôt, relus et
              commentés comme du code, mais lisibles par quelqu&apos;un qui n&apos;en écrit pas.
            </p>
            <pre>
              <code>{`- code: SEUIL_ESPECES_DEDUCTIBILITE_TVA
  libelle: Seuil de règlement en espèces excluant la déduction de TVA
  unite: FCFA
  versions:
    - valeur: 100000
      borne: AU_MOINS_EGALE       # « au moins égale » et « supérieure » diffèrent
      applicable_du: 2024-01-01
      applicable_au: 2025-12-31
      statut: VALIDE
      valide_par: CGA Broad Range Consulting Group
      valide_le: 2026-08-18
      fondement:
        texte: Exclusion du droit à déduction pour les règlements en espèces
        source: Fiche DGI consultée le 18/08/2026, page 4`}</code>
            </pre>
            <h3>Trois champs qui ne sont pas décoratifs</h3>
            <ul>
              <li>
                <b>La borne.</b> « Au moins égale à cent mille » et « supérieure à cent mille »
                ne comparent pas pareil, et la différence se voit sur une facture à exactement
                cent mille. La borne est une donnée légale, pas un opérateur choisi par le
                développeur.
              </li>
              <li>
                <b>Le statut.</b> Tant qu&apos;une valeur porte <code>A_VALIDER</code>, le
                chiffre qu&apos;elle produit illustre le mécanisme et n&apos;engage personne.
              </li>
              <li>
                <b>Le fondement et sa source.</b> Sans eux, personne ne sait quoi mettre à jour
                à la loi de finances suivante, ni justifier un rejet auprès d&apos;un client
                mécontent.
              </li>
            </ul>

            <ParametreDate />

            <Note titre="Le modèle refuse une valeur qui se déclare exacte sans répondant" ton="attention">
              <p>
                Une version au statut <code>VALIDE</code> sans <code>valide_par</code> ni{" "}
                <code>valide_le</code> est rejetée au chargement. Aucun chiffre ne peut donc être
                déclaré exact sans que quelqu&apos;un de nommé en réponde. C&apos;est une règle
                de modèle, pas une consigne.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="sql" rang="Chapitre 5" titre="SQL : deux ceintures">
            <p>
              Les requêtes ordinaires ne sont pas écrites à la main : une couche de correspondance
              objet les produit. Son intérêt principal n&apos;est pas d&apos;éviter d&apos;écrire
              du SQL, c&apos;est de <b>poser le filtre du client sans que personne ait à y
              penser</b>.
            </p>
            <pre>
              <code>{`# Ce que le développeur écrit
pieces = depot.lister(mois="2026-04")

# Ce que la base reçoit : le filtre est ajouté par la session, pas par l'appelant
SELECT ... FROM piece WHERE mois = '2026-04' AND locataire = 'station-bonaberi'`}</code>
            </pre>
            <p>
              Le filtre est posé par un écouteur, à l&apos;ouverture de la session. Il
              s&apos;applique aux entités chargées, y compris par relation, et{" "}
              <b>il ne peut pas être oublié puisqu&apos;il n&apos;est jamais écrit</b>.
            </p>
            <h3>La seconde ceinture, dans la base</h3>
            <p>
              La sécurité au niveau des lignes est une règle écrite dans PostgreSQL : même une
              requête tapée à la main dans une console, avec le compte de l&apos;application, ne
              voit que les lignes de son client.
            </p>
            <Note titre="Le piège qui rend la seconde ceinture inutile" ton="piege">
              <p>
                Ces règles <b>ne s&apos;appliquent pas au propriétaire des tables</b>. Une
                installation qui emploierait le même compte pour les migrations et pour
                l&apos;application aurait des règles visibles, correctes, et sans aucun effet.
                Deux rôles distincts sont donc nécessaires, et la plateforme publie ce constat
                sur sa sonde de santé plutôt que de le supposer.
              </p>
            </Note>
            <h3>Les migrations</h3>
            <p>
              Un changement de schéma est une migration versionnée, jouée <b>avant</b> le
              démarrage de l&apos;application, jamais par elle. Une application qui migre au
              démarrage, en trois exemplaires, tente trois migrations concurrentes sur la même
              base.
            </p>
            <Exercice
              enonce="Vous devez compter les pièces de tous les clients pour un tableau interne. Comment faites-vous ?"
              reponse={
                <p>
                  Pas avec la session ordinaire : elle est cloisonnée, et elle a raison de
                  l&apos;être. Une lecture transversale est un besoin du plan de contrôle, qui
                  passe par un chemin distinct, explicitement nommé, et journalisé. Si vous vous
                  surprenez à vouloir désactiver le filtre, c&apos;est presque toujours que le
                  besoin appartient à un autre contexte.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="typescript" rang="Chapitre 6" titre="TypeScript et React">
            <p>
              Les composants sont rendus sur le serveur par défaut. Un composant ne devient
              interactif que s&apos;il en a besoin, et il le déclare alors explicitement, par une
              première ligne <code>&quot;use client&quot;</code>.
            </p>
            <Tableau
              entetes={["Rendu sur le serveur", "Rendu interactif"]}
              lignes={[
                [
                  "Du texte, un tableau, une carte, une mise en page",
                  "Un onglet, un champ de saisie, une simulation",
                ],
                [
                  "Rien à télécharger : le navigateur reçoit du HTML",
                  "Le code du composant part avec la page",
                ],
                [
                  "Peut lire des fichiers et appeler l'API directement",
                  "Ne peut pas : il s'exécute chez le lecteur",
                ],
              ]}
            />
            <h3>Le coût mesuré, et la leçon</h3>
            <p>
              Un composant rendu sur le serveur envoie son contenu <b>deux fois</b> : une fois en
              HTML, et une fois dans la charge que le navigateur rejoue pour reprendre la main.
              Sur le document de conception, 966 Ko de texte, cela faisait 2,17 Mo servis au lieu
              de 970 Ko.
            </p>
            <p>
              Le document est donc assemblé à la construction et servi comme fichier, tandis que
              les pages que vous lisez restent des pages React. <b>C&apos;est la taille du
              contenu qui décide, pas une préférence de principe.</b>
            </p>
            <h3>Le type d&apos;une réponse se déclare une fois</h3>
            <pre>
              <code>{`export type EcartDeConstat = {
  identifiant: string;
  severite: "BLOQUANT" | "MAJEUR" | "AVERTISSEMENT" | "INFORMATION";
  statut: "EN_ATTENTE" | "EFFECTIF" | "REFUSE" | "LEVE";
  piece_appui: string | null;
};

// Une seule fonction par lecture : les écrans ne connaissent qu'elle.
export async function lireLesEcarts(dossier: string): Promise<EcartDeConstat[]> { … }`}</code>
            </pre>
            <p>
              Un champ renommé côté serveur casse alors la compilation de l&apos;interface, ce
              qui est exactement le moment où on veut l&apos;apprendre.
            </p>
          </Chapitre>

          <Chapitre id="html" rang="Chapitre 7" titre="HTML et CSS">
            <p>
              Le document de conception est un seul fichier HTML, avec ses styles à
              l&apos;intérieur et ses figures dessinées en SVG. Aucun outil n&apos;est nécessaire
              pour l&apos;ouvrir, et aucun ne le sera dans dix ans.
            </p>
            <h3>Trois règles suivies partout</h3>
            <ul>
              <li>
                <b>Les couleurs sont des variables</b>, déclarées une fois et redéclarées pour le
                thème sombre. Une couleur écrite en dur quelque part est une couleur qui ne
                suivra pas la bascule.
              </li>
              <li>
                <b>Rien ne dépasse.</b> Tout ce qui peut être large, un tableau, un bloc de code,
                un schéma, vit dans une enveloppe qui défile, et qui le dit par une ombre. Un
                tableau large sans enveloppe pousse la page entière, et le lecteur croit que la
                page est fautive.
              </li>
              <li>
                <b>Le clavier passe partout.</b> Un contour de focus visible, un ordre de
                tabulation qui suit la lecture, et des onglets qui répondent aux flèches.
              </li>
            </ul>
            <Note titre="Un défaut trouvé en mesurant, pas en regardant" ton="attention">
              <p>
                Le code en ligne du document était déclaré insécable. Un identifiant long
                débordait la colonne de texte et élargissait la page entière : au téléphone, tout
                le document défilait de travers à cause d&apos;un mot. Il a fallu mesurer
                quarante combinaisons de page et de largeur pour le voir, parce qu&apos;à
                l&apos;œil, sur un grand écran, la page est parfaite.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="pieges" rang="Chapitre 8" titre="Les pièges par langage">
            <Tableau
              entetes={["Langage", "Le piège", "Ce qu'il faut faire"]}
              lignes={[
                [
                  "Python",
                  "Une valeur par défaut mutable, ou un « except » sans motif",
                  "Des modèles figés, et des exceptions nommées qui disent quoi corriger",
                ],
                [
                  "Python",
                  "Lire l'heure dans le domaine",
                  "La recevoir en argument, toujours",
                ],
                [
                  "SQL",
                  "Écrire le filtre du client à la main",
                  "Ne jamais l'écrire : la session le pose",
                ],
                [
                  "SQL",
                  "Migrer au démarrage de l'application",
                  "Une étape de migration distincte, avant tout le reste",
                ],
                [
                  "YAML",
                  "Un fichier mal formé chargé à moitié",
                  "Un chargement qui échoue franchement : un réglage à moitié lu est pire qu'absent",
                ],
                [
                  "TypeScript",
                  "Rendre interactif ce qui n'a pas d'état",
                  "Laisser le serveur rendre : le navigateur ne télécharge rien",
                ],
                [
                  "CSS",
                  "Un élément large sans enveloppe qui défile",
                  "Une enveloppe, et une ombre qui dit qu'elle défile",
                ],
              ]}
            />
            <p style={{ marginTop: 32 }}>
              <a className="site-bouton site-bouton--plein" href="/prerequis/outils">
                Cours suivant : les outils
              </a>
            </p>
          </Chapitre>
        </Lecon>
      </main>
      <Pied />
    </>
  );
}
