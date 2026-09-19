import type { Metadata } from "next";

import { Etiquette, Note, Tableau } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";

export const metadata: Metadata = {
  title: "Mise en œuvre",
  description:
    "Ce qu'il faut faire pour lancer la plateforme : ce qui est prêt, ce qui bloque, et dans quel ordre.",
};

/**
 * La mise en œuvre : du dépôt à la première déclaration déposée pour un adhérent réel.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ CETTE PAGE DIT CE QUI MANQUE, ET C'EST SA RAISON D'ÊTRE
 *
 * Une page de lancement qui n'énumère que ce qui est prêt se lit agréablement et
 * laisse découvrir les obstacles un par un, au pire moment, c'est-à-dire devant le
 * client. Chaque étape porte donc son état, et les trois qui bloquent le disent.
 * ─────────────────────────────────────────────────────────────────────────────
 */
export default function MiseEnOeuvre() {
  return (
    <>
      <Entete courant="/mise-en-oeuvre" />
      <main className="page page--etroite">
        <section className="bandeau">
          <p className="bandeau__oeil">Du dépôt au premier adhérent servi</p>
          <h1>Mise en œuvre</h1>
          <p className="bandeau__chapo">
            Le produit est construit et éprouvé. Le mettre en service demande trois choses que
            le code ne peut pas fournir seul : des valeurs légales contresignées, des réponses
            de l&apos;administration, et un serveur. Voici l&apos;ordre, et ce qui bloque.
          </p>
        </section>

        <section className="bloc" id="etat">
          <h2 className="bloc__titre">L&apos;état, en une table</h2>
          <p className="bloc__intro">
            Mesuré sur le dépôt, et non recopié d&apos;une version précédente.
          </p>
          <Tableau
            entetes={["Volet", "État", "Ce qui manque"]}
            lignes={[
              [
                "Le produit",
                <Etiquette key="p" ton="fait">
                  prêt
                </Etiquette>,
                "3 727 tests sur base réelle, 225 gestes d'écran sur 225, 74 cas d'usage rejoués sur la pile qui tourne",
              ],
              [
                "Les valeurs légales",
                <Etiquette key="v" ton="bloquant">
                  bloquant
                </Etiquette>,
                "40 valeurs sur 91 attendent le contreseing d'un fiscaliste nommé. Aucun chiffre n'est opposable avant.",
              ],
              [
                "La télédéclaration",
                <Etiquette key="t" ton="attente">
                  en attente
                </Etiquette>,
                "L'administration n'expose aucune interface documentée. Le dépôt reste manuel, et la plateforme prépare.",
              ],
              [
                "L'hébergement",
                <Etiquette key="h" ton="attente">
                  en attente
                </Etiquette>,
                "Les manifestes de déploiement sont écrits et vérifiés. Aucun serveur ne les porte encore.",
              ],
              [
                "Le canal de conversation",
                <Etiquette key="c" ton="attente">
                  partiel
                </Etiquette>,
                "Le courriel et le prestataire de paiement sont branchés. La messagerie instantanée est modélisée, sans connecteur.",
              ],
              [
                "L'application mobile",
                <Etiquette key="m" ton="attente">
                  non commencée
                </Etiquette>,
                "Prévue pour l'usage de terrain hors ligne. Le serveur l'attend déjà, avec sa file de synchronisation.",
              ],
            ]}
          />
        </section>

        <section className="bloc" id="ordre">
          <h2 className="bloc__titre">L&apos;ordre des opérations</h2>
          <p className="bloc__intro">
            Neuf étapes. Les trois premières ne demandent aucun serveur et conditionnent tout
            le reste : les commencer tard est la façon la plus courante de retarder un
            lancement de plusieurs mois.
          </p>

          <ol className="etapes">
            <Etape titre="Faire contresigner le référentiel" etat="bloquant">
              <p>
                Chaque taux, seuil, délai et pénalité porte son fondement et sa source. Un
                fiscaliste nommé les confronte au texte en vigueur, et son nom ainsi que la
                date sont inscrits dans le fichier. Le modèle refuse une valeur déclarée exacte
                sans ces deux champs.
              </p>
              <p>
                Une fiche de contreseing est engendrée depuis le référentiel pour cette
                séance : elle liste les valeurs, leur source et l&apos;espace où porter la
                décision.
              </p>
              <p>
                <b>Sans cette étape</b>, la plateforme reste une maquette exacte dans ses
                mécanismes et sans valeur devant l&apos;administration.
              </p>
            </Etape>

            <Etape titre="Obtenir les réponses de l'administration" etat="bloquant">
              <p>Cinq questions, posées par le cabinet, décident de tout un pan du produit :</p>
              <ul>
                <li>
                  le portail accepte-t-il un <b>dépôt de fichier</b>, ou faut-il saisir champ
                  par champ ;
                </li>
                <li>
                  existe-t-il un <b>compte de rattachement</b> permettant au centre de déposer
                  pour un adhérent, ce qui évite de détenir les identifiants de chacun ;
                </li>
                <li>
                  que contient exactement l&apos;<b>accusé de réception</b>, et qu&apos;est-ce
                  qui peut donc être rapproché automatiquement ;
                </li>
                <li>
                  sous quel format se dépose la <b>liasse annuelle</b> ;
                </li>
                <li>
                  quel est le calendrier et le périmètre de la <b>facturation
                  électronique</b>.
                </li>
              </ul>
              <Note titre="Ce que la plateforme apporte sans aucune de ces réponses">
                <p>
                  Elle produit des chiffres contrôlés, elle <b>refuse</b> de préparer un
                  dossier irrecevable, elle conserve l&apos;accusé et son empreinte, et elle
                  sait dire trois ans plus tard ce qui a été déposé et par qui. Le transport
                  est une demi-journée de travail le jour où les spécifications existent ; la
                  recevabilité, elle, est déjà écrite.
                </p>
              </Note>
            </Etape>

            <Etape titre="Trancher les questions d'organisation" etat="attente">
              <p>
                Le rattachement des collaborateurs aux agences, la pondération de la charge, le
                référent de validation des règles, l&apos;hébergement et la protection des
                données. Ce sont des décisions du cabinet, pas des choix techniques, et
                chacune est posée avec ses conséquences sur le produit.
              </p>
            </Etape>

            <Etape titre="Préparer le serveur et la base" etat="attente">
              <ul>
                <li>PostgreSQL 16, sauvegardé, avec une restauration réellement testée.</li>
                <li>
                  <b>Deux rôles distincts</b> : un pour les migrations, propriétaire des
                  tables ; un pour l&apos;application. C&apos;est une condition de sécurité,
                  pas une préférence, et l&apos;encadré ci-dessous dit pourquoi.
                </li>
                <li>
                  Un volume pour les pièces déposées, sauvegardé lui aussi. Sans copie, une
                  panne disque fait perdre les justificatifs de tous les adhérents, et la
                  comptabilité qui s&apos;appuie dessus devient indéfendable.
                </li>
                <li>Les secrets créés hors du dépôt, et jamais versionnés.</li>
              </ul>
              <Note titre="Le piège des rôles" ton="piege">
                <p>
                  Le cloisonnement des données repose en partie sur des règles écrites dans la
                  base. Ces règles <b>ne s&apos;appliquent pas au propriétaire des tables</b>.
                  Une installation qui emploierait le même compte pour les migrations et pour
                  l&apos;application aurait donc des règles visibles, correctes, et sans aucun
                  effet. La plateforme le constate au démarrage et le publie sur sa sonde de
                  santé, mais c&apos;est à l&apos;installation que cela se règle.
                </p>
              </Note>
            </Etape>

            <Etape titre="Déployer, dans l'ordre imposé" etat="attente">
              <p>
                Les manifestes sont versionnés avec le code, et un test vérifie à chaque
                relecture que les variables qu&apos;ils posent existent réellement dans la
                configuration. Ce contrôle a trouvé deux défauts le jour où il a été écrit,
                dont une clé de secret nommée comme une variable d&apos;environnement, ce qui
                ne fait rien, en silence.
              </p>
              <Tableau
                entetes={["Ordre", "Ce qui est posé"]}
                lignes={[
                  ["1", "L'espace de noms, la configuration, et le gabarit de secret"],
                  ["2", "Le volume des justificatifs"],
                  ["3", "Les migrations de schéma, avant tout le reste"],
                  ["4", "L'API, en plusieurs exemplaires, et son service"],
                  ["5", "L'ordonnanceur des travaux de fond, en un seul exemplaire"],
                  ["6", "L'entrée réseau et le certificat générique"],
                ]}
              />
              <p>
                Le secret ne figure pas dans cette liste : il se crée hors du dépôt, et le
                gabarit sert seulement à dire quelles clés sont attendues.
              </p>
            </Etape>

            <Etape titre="Ouvrir le domaine et les sous-domaines" etat="attente">
              <p>
                Chaque client dispose de son sous-domaine. Il faut donc un enregistrement
                générique vers l&apos;entrée réseau, et un certificat générique. Le nom réservé
                de la plateforme et les noms techniques sont refusés à l&apos;attribution, par
                une liste qui vit au référentiel et qui grandit sans livraison.
              </p>
            </Etape>

            <Etape titre="Jouer la recette d'installation" etat="attente">
              <p>
                Le registre des cas d&apos;usage rejoue soixante-quatorze parcours contre la
                pile qui tourne, et produit un cahier daté, imprimable, qui dit pour chacun ce
                qui a été exécuté et le verdict obtenu. C&apos;est ce cahier que le cabinet
                reçoit, et c&apos;est lui qui atteste que l&apos;installation fonctionne, pas
                une capture d&apos;écran.
              </p>
            </Etape>

            <Etape titre="Reprendre l'existant" etat="attente">
              <p>
                Les adhérents ont un passé. La plateforme sait reprendre un exercice antérieur
                sans le dupliquer, inscrire un changement de régime à sa date, et constater
                l&apos;abattement plutôt que de le supposer. La reprise se fait dossier par
                dossier, et chaque reprise est journalisée.
              </p>
            </Etape>

            <Etape titre="Exploiter" etat="fait">
              <p>Ce qui est déjà prévu pour le jour où la plateforme tourne :</p>
              <ul>
                <li>
                  une route qui dit, pour chaque service, s&apos;il répond et ce qui tombe avec
                  lui ;
                </li>
                <li>
                  des sondes de santé par service, avec trois nuances plutôt que deux : répond,
                  suspect, en panne. Une sonde qui crie au loup finit ignorée ;
                </li>
                <li>
                  un journal chaîné, vérifiable, qui dit qui a fait quoi, quand, et au nom de
                  qui ;
                </li>
                <li>
                  des travaux de fond qui se reprennent seuls après incident, avec un recul
                  progressif et une borne.
                </li>
              </ul>
            </Etape>
          </ol>
        </section>

        <section className="bloc" id="reste">
          <h2 className="bloc__titre">Ce qui reste au produit lui-même</h2>
          <p className="bloc__intro">
            Le chantier du socle multi-tenant est <b>clos</b> : le répertoire des clients se
            tient à jour, le jeton de session est confronté au domaine, le mandat est branché
            de bout en bout, et le script des deux rôles est joué à chaque passage de la
            suite de tests. Reste ce qui suit.
          </p>
          <Tableau
            entetes={["Chantier", "Pourquoi il compte"]}
            lignes={[
              [
                "L'application mobile hors ligne",
                "Le serveur l'attend : la file de synchronisation est écrite et testée, et elle n'a pas encore de client.",
              ],
              [
                "Le connecteur de messagerie instantanée",
                "Le canal est modélisé, la conversation aussi. Il manque le lien avec le fournisseur, et le choix de ce fournisseur.",
              ],
              [
                "Le dépôt automatisé des déclarations",
                "Le port existe et l'adaptateur manuel fonctionne. Le reste dépend de réponses que l'administration seule peut donner.",
              ],
            ]}
          />
        </section>

        <section className="bloc" id="honnetete">
          <h2 className="bloc__titre">La réponse courte</h2>
          <Note titre="Est-ce que la solution est prête ?" ton="attention">
            <p>
              <b>Le logiciel, oui.</b> Il est construit, éprouvé sur une base réelle, et chacun
              de ses parcours est rejoué automatiquement contre la pile qui tourne.
            </p>
            <p>
              <b>La solution, pas encore.</b> Il manque le contreseing des valeurs légales, les
              réponses de l&apos;administration, et un serveur. Les deux premières ne
              s&apos;achètent pas et ne se codent pas : elles se demandent, et il vaut mieux
              les demander tôt.
            </p>
          </Note>
        </section>
      </main>
      <Pied />
    </>
  );
}

function Etape({
  titre,
  etat,
  children,
}: {
  titre: string;
  etat: "fait" | "bloquant" | "attente";
  children: React.ReactNode;
}) {
  const mots = { fait: "en place", bloquant: "bloquant", attente: "à faire" };
  return (
    <li>
      <div>
        <h3>
          {titre} <Etiquette ton={etat}>{mots[etat]}</Etiquette>
        </h3>
        {children}
      </div>
    </li>
  );
}
