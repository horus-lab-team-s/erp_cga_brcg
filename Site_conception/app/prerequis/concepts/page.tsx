import type { Metadata } from "next";

import { Note, Tableau } from "@/app/composants/Bouts";
import { Entete, Pied } from "@/app/composants/Coquille";
import { Chapitre, Lecon } from "@/app/composants/Lecon";
import { Exercice, Faits, FilDAriane, Objectifs } from "@/app/composants/Pedagogie";
import { ControleFacture } from "@/app/composants/simulations/ControleFacture";
import { JournalChaine } from "@/app/composants/simulations/JournalChaine";
import { ResolutionTenant } from "@/app/composants/simulations/ResolutionTenant";
import { SagaOuverture } from "@/app/composants/simulations/SagaOuverture";

export const metadata: Metadata = {
  title: "Cours · Les concepts",
  description:
    "Le métier, le découpage en contextes, les ports et adaptateurs, le moteur et sa configuration, le cloisonnement, le journal chaîné et les sagas, avec des simulations.",
};

const PLAN = [
  { id: "metier", titre: "1 · Le métier commande tout" },
  { id: "contexte", titre: "2 · Le contexte borné" },
  { id: "hexagone", titre: "3 · Ports et adaptateurs" },
  { id: "moteur", titre: "4 · Le moteur et sa configuration" },
  { id: "cloisonnement", titre: "5 · Plusieurs clients, une seule base" },
  { id: "journal", titre: "6 · Le journal chaîné" },
  { id: "saga", titre: "7 · Ce qu'une transaction ne couvre pas" },
  { id: "refus", titre: "8 · Ce que le code refuse" },
  { id: "rythme", titre: "9 · Comment le projet avance" },
];

export default function CoursConcepts() {
  return (
    <>
      <Entete courant="/prerequis" />
      <main className="page">
        <section className="cours-tete">
          <FilDAriane
            pieces={[{ libelle: "Prérequis", href: "/prerequis" }, { libelle: "Les concepts" }]}
          />
          <h1>Les concepts qui tiennent ce projet</h1>
          <p className="cours-tete__chapo">
            Neuf chapitres, quatre simulations, et aucun prérequis autre que savoir ce
            qu&apos;est un programme. Chaque notion part d&apos;un problème concret du métier,
            et se termine par l&apos;endroit du dépôt où elle vit.
          </p>
          <Faits
            faits={[
              { mot: "durée", valeur: "environ 50 minutes" },
              { mot: "chapitres", valeur: "9" },
              { mot: "simulations", valeur: "4" },
              { mot: "niveau", valeur: "débutant accepté" },
            ]}
          />
          <Objectifs
            points={[
              "Expliquer pourquoi un centre de gestion agréé ne se conçoit pas comme un logiciel de facturation ordinaire.",
              "Dire où va un nouveau bout de code, et pourquoi il ne va pas ailleurs.",
              "Lire un rapport de conformité et comprendre pourquoi il ne répond pas par oui ou par non.",
              "Expliquer à quelqu'un pourquoi la plateforme répond « introuvable » à un client suspendu.",
              "Reconnaître les trois situations où une transaction de base de données ne suffit plus.",
            ]}
          />
        </section>

        <Lecon chapitres={PLAN}>
          <Chapitre id="metier" rang="Chapitre 1" titre="Le métier commande tout">
            <p>
              Un centre de gestion agréé n&apos;est pas un cabinet comptable ordinaire.
              C&apos;est une structure <b>agréée par l&apos;administration fiscale</b>, inscrite
              à un répertoire public, et dont l&apos;adhésion ouvre au contribuable des
              avantages fiscaux qu&apos;il n&apos;aurait pas seul. Quatre conséquences
              découlent de ce statut, et chacune se retrouve dans le code.
            </p>
            <Tableau
              entetes={["Conséquence du statut", "Ce que cela impose au logiciel"]}
              lignes={[
                [
                  "Le centre répond de ses chiffres",
                  "Chaque valeur produite doit être explicable : quelle règle, quelle version, quel fondement, quelle date. Ce n'est pas du confort documentaire, c'est la condition d'exercice.",
                ],
                [
                  "L'adhérent bénéficie d'un abattement sous conditions",
                  "Le système doit savoir dire si un adhérent reste éligible, donc suivre son chiffre d'affaires et son régime dans le temps, et pas seulement à l'instant présent.",
                ],
                [
                  "Le centre peut perdre son agrément",
                  "La traçabilité protège l'activité elle-même. D'où un journal qu'on ne peut pas réécrire.",
                ],
                [
                  "Le centre détient les données de dizaines d'entreprises",
                  "Le cloisonnement n'est pas une bonne pratique, c'est une obligation dont le manquement se paie devant un tribunal.",
                ],
              ]}
            />
            <h3>Le rythme du droit, et pourquoi il tue les logiciels</h3>
            <p>
              Une loi de finances par an, systématiquement, qui touche des taux, des seuils et
              parfois des régimes entiers. Un droit comptable régional qui bouge par réformes,
              plus rarement mais plus profondément. Des barèmes sociaux qui suivent leur propre
              calendrier.
            </p>
            <p>
              Un logiciel qui écrit ces valeurs dans son code demande une livraison à chaque
              changement, sur trois calendriers qu&apos;il ne maîtrise pas. <b>Il ne meurt pas
              d&apos;un défaut, il meurt de ne plus suivre.</b> Retenez cette phrase : la moitié
              des décisions d&apos;architecture de ce projet en découlent.
            </p>
            <h3>La ligne de conduite du produit</h3>
            <p>
              La plateforme ne remplace pas l&apos;expertise humaine, elle l&apos;assiste. Son
              enchaînement est toujours le même : collecter, analyser, proposer, permettre la
              modification, faire valider par l&apos;expert, générer, transmettre, faire payer,
              suivre.
            </p>
            <p>
              L&apos;étape de modification n&apos;est pas un rattrapage, c&apos;est une fonction
              du produit. Un montant proposé par le système reste un montant qu&apos;un expert
              engage de sa signature, et cette phrase se traduit techniquement : <b>aucun montant
              ne devient opposable sans passer par une action habilitée et journalisée</b>.
            </p>
            <Exercice
              enonce="Le cabinet vous demande d'ajouter le taux de la taxe de développement local, 0,5 %, qui vient d'être institué. Où écrivez-vous ce nombre ?"
              reponse={
                <>
                  <p>
                    Nulle part dans le code. Il devient une entrée du référentiel, avec sa date
                    d&apos;entrée en vigueur, son fondement et son statut de validation. Le code
                    qui l&apos;emploie le lit <b>à la date de la pièce contrôlée</b>, jamais « à
                    aujourd&apos;hui ».
                  </p>
                  <p>
                    Si vous l&apos;écrivez dans le code, votre programme devient faux le jour où
                    le taux change, et il le devient <b>rétroactivement</b> : les pièces de
                    l&apos;année passée seraient recontrôlées avec la valeur nouvelle.
                  </p>
                </>
              }
            />
          </Chapitre>

          <Chapitre id="contexte" rang="Chapitre 2" titre="Le contexte borné">
            <p>
              Tout logiciel de gestion finit par avoir un mot qui veut dire deux choses.
              Prenez « dossier » : pour le commercial, c&apos;est une affaire en cours de
              négociation, avec un prix et une probabilité ; pour le comptable, c&apos;est une
              entreprise dont il tient les comptes, avec un exercice et un plan de comptes.
            </p>
            <p>
              Les fondre dans une seule table produit une entité à quarante colonnes dont la
              moitié est vide selon qui la lit, et dont personne n&apos;ose plus rien retirer.
              C&apos;est la façon la plus courante dont un logiciel de gestion devient
              impossible à modifier.
            </p>
            <h3>La réponse : des zones, chacune avec son vocabulaire</h3>
            <p>
              On découpe le système en zones. À l&apos;intérieur d&apos;une zone, un mot a un
              seul sens. Entre deux zones, on traduit explicitement. Le projet en compte
              quatorze, nommées de A à N.
            </p>
            <Tableau
              entetes={["Lettre", "Contexte", "Ce dont il est maître"]}
              lignes={[
                ["A", "Référentiel", "Les paramètres légaux datés, les barèmes, les textes"],
                ["B", "Portefeuille", "Les entreprises, leurs exercices, leurs mandats"],
                ["C", "Collecte", "Les pièces déposées et leur file de traitement"],
                ["D", "Conformité", "Les règles de contrôle et leurs constats"],
                ["E", "Comptabilité", "Les écritures, les journaux, le lettrage"],
                ["F", "Obligations", "Les échéances déclaratives et les dépôts"],
                ["J", "Pilotage", "Les vues de direction. Il lit tout le monde, personne ne le lit"],
                ["N", "Tenants", "L'ouverture et le cycle de vie des espaces clients"],
              ]}
            />
            <h3>La règle qui tient le découpage</h3>
            <p>
              Un contexte ne lit jamais la table d&apos;un autre. Il l&apos;appelle par sa
              façade, le fichier <code>api.py</code>, qui est la seule chose qu&apos;un voisin a
              le droit d&apos;employer. Tout le reste appartient au contexte et peut changer sans
              prévenir.
            </p>
            <Note titre="Une règle qu'un document ne suffit pas à tenir" ton="attention">
              <p>
                Cette règle n&apos;est pas écrite dans un document que personne ne relit : un
                test parcourt les importations réellement écrites et refuse celles qui traversent
                une frontière. Une règle d&apos;architecture qui n&apos;est pas exécutable se
                perd au troisième nouveau venu, et c&apos;est toujours le plus pressé qui la
                franchit en premier.
              </p>
            </Note>
            <Exercice
              enonce="L'écran des échéances doit afficher la raison sociale de l'entreprise. Les échéances vivent dans Obligations, la raison sociale dans Portefeuille. Que faites-vous ?"
              reponse={
                <>
                  <p>
                    Obligations appelle <code>portefeuille.api</code>, qui rend ce qu&apos;il a
                    décidé d&apos;exposer. Il ne lit jamais la table des entreprises, même si
                    elle est dans la même base et que la requête serait plus rapide.
                  </p>
                  <p>
                    La raison est le jour d&apos;après : le jour où Portefeuille change sa
                    colonne, il doit pouvoir le faire sans chercher qui d&apos;autre la lisait.
                    C&apos;est ce que la façade garantit, et c&apos;est ce qu&apos;une jointure
                    directe détruit pour toujours.
                  </p>
                </>
              }
            />
          </Chapitre>

          <Chapitre id="hexagone" rang="Chapitre 3" titre="Ports et adaptateurs">
            <p>
              Une règle fiscale écrite au milieu d&apos;une requête HTTP ne se teste
              qu&apos;en montant un serveur, et ne se réutilise nulle part. Le jour où la même
              règle doit servir dans un traitement de nuit, on la recopie, et les deux copies
              divergent. La troisième fois, plus personne ne sait laquelle fait foi.
            </p>
            <h3>Trois couches, et ce que chacune a le droit de connaître</h3>
            <Tableau
              entetes={["Couche", "Connaît", "Ne connaît pas", "Exemple ici"]}
              lignes={[
                [
                  "domaine",
                  "Ses propres règles",
                  "Ni base, ni réseau, ni horloge, ni requête",
                  "Un écart de conformité, ses statuts, ses transitions autorisées",
                ],
                [
                  "application",
                  "Le domaine, et des ports décrits comme des interfaces",
                  "La technique qui réalise ces ports",
                  "Proposer un écart, exiger un second regard, le lever",
                ],
                [
                  "adaptateurs entrants",
                  "L'application et le cadre web",
                  "Les règles elles-mêmes",
                  "Les routes HTTP, les sondes de santé, les travaux périodiques",
                ],
                [
                  "adaptateurs sortants",
                  "Les ports, et la technique",
                  "L'application",
                  "PostgreSQL, les fichiers du référentiel, le relais de courriel",
                ],
              ]}
            />
            <p>
              Le domaine ne connaît même pas l&apos;heure. Une règle qui a besoin de la date la
              reçoit en argument, ce qui a deux effets : elle se teste sans attendre minuit, et
              surtout elle devient capable de répondre à la question qui compte dans ce métier,
              à savoir <b>ce que disait la règle à la date de la pièce</b>.
            </p>
            <pre>
              <code>{`# domaine : la règle, sans rien du monde extérieur
def a_regulariser(ecart, politique, aujourd_hui):
    if ecart.piece_appui is not None:
        return False
    return (aujourd_hui - ecart.propose_le.date()).days > politique.delai_jours

# adaptateur entrant : c'est lui, et lui seul, qui va chercher la date
retard = a_regulariser(ecart, politique_du_cabinet(), maintenant().date())`}</code>
            </pre>
            <Exercice
              enonce="Vous devez envoyer un courriel quand un écart dépasse son délai. Dans quelle couche écrivez-vous l'envoi ?"
              reponse={
                <p>
                  Dans un adaptateur sortant, derrière un port. Le domaine dit « cet écart est à
                  régulariser », l&apos;application décide « alors on prévient », et
                  l&apos;adaptateur sait seul comment un courriel part. Écrire l&apos;envoi dans
                  le domaine rendrait impossible de tester la règle sans serveur de messagerie,
                  et rendrait impossible de la réutiliser pour un rapport imprimé.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="moteur" rang="Chapitre 4" titre="Le moteur et sa configuration">
            <p>
              C&apos;est le cœur intellectuel du projet, et la réponse directe au « il meurt de
              ne plus suivre » du premier chapitre. Le principe tient en une phrase : <b>le code
              porte les mécanismes, la configuration porte les décisions</b>.
            </p>
            <p>
              Un taux, un seuil, un barème, une règle de contrôle, un critère de charge, un
              modèle de message : tout cela change plusieurs fois par an, et rien de tout cela ne
              doit demander un déploiement.
            </p>
            <h3>Une règle n&apos;est pas un booléen</h3>
            <p>
              C&apos;est l&apos;idée la plus contre-intuitive du projet. On attend d&apos;un
              contrôle qu&apos;il réponde conforme ou non conforme. Ici, il rend un{" "}
              <b>rapport de constats gradués</b>, chacun portant une gravité, un message et,
              quand la règle sait la chiffrer, une conséquence fiscale en francs.
            </p>
            <p>
              La règle <b>décrit</b>, elle n&apos;agit pas. Un service en aval lit les gravités
              et décide. C&apos;est ce qui permet au même moteur de servir quatre usages : le
              contrôle de facture, la tarification, l&apos;évaluation de la charge d&apos;un
              dossier et le contrôle interne.
            </p>

            <ControleFacture />

            <h3>Pourquoi aucune lecture sans date</h3>
            <p>
              Il n&apos;existe volontairement <b>aucune</b> façon de lire la valeur courante
              d&apos;un paramètre. Une facture de 2024 se contrôle avec les règles de 2024, sans
              quoi un contrôle refait deux ans plus tard donnerait un résultat différent du
              premier, et le cabinet serait incapable de dire lequel est juste.
            </p>
            <pre>
              <code>{`# Interdit : la valeur est en dur
if montant >= 100_000 and mode == "ESPECES":

# Interdit aussi : la valeur vient du référentiel, mais l'opérateur est resté en dur
seuil = parametres.valeur("SEUIL_ESPECES", facture.date_emission)
if montant >= seuil and mode == "ESPECES":

# Attendu : la valeur, ET ce que le texte dit de la valeur
seuil = parametres.resoudre("SEUIL_ESPECES", facture.date_emission)
if seuil.atteint(montant) and mode is ModeReglement.ESPECES:`}</code>
            </pre>
            <Note titre="Le détail qui sépare un outil fiscal d'un validateur de formulaire">
              <p>
                « Au moins égale à cent mille » et « supérieur à cent mille » ne comparent pas de
                la même façon, et la différence se voit sur une facture à exactement cent mille.
                La <b>borne</b> d&apos;un seuil est donc une donnée légale, portée par le
                référentiel à côté de sa valeur, et non un opérateur choisi par celui qui écrit
                la ligne.
              </p>
            </Note>
            <Exercice
              enonce="Un fiscaliste vous dit : « le seuil passe à 500 000 au 1er janvier prochain ». Que livrez-vous ?"
              reponse={
                <p>
                  Rien. Vous ajoutez une <b>version</b> au paramètre existant, avec sa date
                  d&apos;entrée en vigueur, son fondement et le nom du fiscaliste. L&apos;ancienne
                  version reste, parce que les pièces de l&apos;an passé doivent continuer
                  d&apos;être contrôlées avec elle. Aucun code ne change, aucun déploiement
                  n&apos;a lieu.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="cloisonnement" rang="Chapitre 5" titre="Plusieurs clients, une seule base">
            <p>
              Un cabinet et ses adhérents, plus des entreprises autonomes, partagent le même
              programme et la même base. Une requête mal écrite qui oublie un filtre montre les
              données d&apos;un client à un autre, <b>et rien ne le signale</b> : la page
              s&apos;affiche normalement, avec des lignes qui paraissent plausibles.
            </p>
            <h3>Le locataire est établi une fois, au bord</h3>
            <p>
              Le sous-domaine désigne le client. L&apos;intergiciel qui reçoit la requête le
              résout, l&apos;établit, et tout le reste du programme le lit sans jamais le
              demander. Aucune fonction ne le prend en argument, donc personne ne peut
              l&apos;oublier.
            </p>
            <p>
              Deux ceintures plutôt qu&apos;une : un filtre posé automatiquement par la couche de
              persistance, et une règle écrite dans la base elle-même, qui s&apos;applique même à
              une requête qui contournerait le programme.
            </p>

            <ResolutionTenant />

            <h3>Le mandat, quand le cabinet travaille chez son client</h3>
            <p>
              Le cas le plus courant est celui-ci : le centre tient la comptabilité d&apos;une
              entreprise qui dispose aussi de son propre accès. Deux espaces, deux jeux de
              données, et pourtant les mêmes écritures.
            </p>
            <p>
              La réponse n&apos;est ni de fondre les deux espaces, ni de dupliquer les données,
              mais un <b>mandat</b> : un objet explicite, daté, révocable, que l&apos;entreprise
              accorde et peut retirer. Chaque action exercée sous mandat est journalisée comme
              telle, et le retrait fait tomber l&apos;accès à la requête suivante.
            </p>
            <Exercice
              enonce="Pourquoi ne pas simplement donner aux comptables du cabinet un accès à tous les espaces ?"
              reponse={
                <p>
                  Parce que le jour d&apos;un litige, d&apos;un départ fâché ou d&apos;un
                  contrôle, personne ne saurait dire qui a touché quoi ni au nom de qui. Le
                  mandat rend cette question triviale, et il est presque gratuit tant qu&apos;on
                  le pose <b>avant</b> d&apos;écrire le premier contrôle d&apos;accès. Ajouté
                  après, il oblige à relire chaque route.
                </p>
              }
            />
          </Chapitre>

          <Chapitre id="journal" rang="Chapitre 6" titre="Le journal chaîné">
            <p>
              Un centre de gestion agréé répond de ses chiffres devant l&apos;administration. Un
              historique qu&apos;on peut modifier après coup ne prouve rien, et un administrateur
              de base de données peut toujours modifier une ligne.
            </p>
            <p>
              La réponse est un chaînage : chaque entrée porte l&apos;empreinte de la précédente.
              Modifier une ligne ancienne casse la chaîne de toutes celles qui suivent, ce qui
              rend l&apos;altération détectable <b>sans avoir à faire confiance à qui que ce
              soit</b>.
            </p>

            <JournalChaine />

            <h3>Le journal sert aussi de mémoire</h3>
            <p>
              Au-delà de l&apos;audit, il enregistre les petits faits datés dont un état
              séparé serait excessif : une preuve de paiement déposée par un adhérent, un
              signalement de changement d&apos;adresse, un réglage de rappel, une pièce
              d&apos;appui jointe à une dérogation. Ce sont des <b>faits</b>, pas des états, et
              un journal est exactement fait pour cela.
            </p>
          </Chapitre>

          <Chapitre id="saga" rang="Chapitre 7" titre="Ce qu'une transaction ne couvre pas">
            <p>
              Ouvrir un espace client touche plusieurs systèmes : réserver un sous-domaine, créer
              un espace de données, ouvrir un stockage de fichiers, créer un compte et envoyer un
              lien d&apos;activation. Aucune transaction de base de données ne couvre ces gestes.
              Si le quatrième échoue, les trois premiers ont déjà eu lieu.
            </p>

            <SagaOuverture />

            <h3>La boîte d&apos;envoi, et les deux ordres fautifs</h3>
            <p>
              Deuxième mécanisme, jumeau du premier. Quand une donnée est écrite et qu&apos;un
              message doit partir, deux ordres sont possibles, et les deux sont faux :
            </p>
            <Tableau
              entetes={["Ordre", "Ce qui casse"]}
              lignes={[
                [
                  "Écrire, puis publier",
                  "Le programme s'arrête entre les deux : la donnée existe, personne n'est prévenu. Le client a payé et son espace ne s'ouvre pas.",
                ],
                [
                  "Publier, puis écrire",
                  "L'écriture échoue : un message circule à propos d'une donnée qui n'existe pas, et le reste du système agit sur du vide.",
                ],
                [
                  "Écrire le message avec la donnée, dans la même transaction, puis le relayer",
                  "Rien. On ne peut pas avoir écrit sans avoir enregistré le message, ni l'inverse.",
                ],
              ]}
            />
            <Note titre="La conséquence à connaître avant d'écrire un abonné" ton="attention">
              <p>
                Le relais publie <b>au moins une fois</b>. Un rappel rejoué, une reprise après
                incident, deux instances derrière un répartiteur : le même message arrive
                plusieurs fois, et c&apos;est le régime normal, pas le cas limite.
              </p>
              <p>
                Tout traitement doit donc être <b>idempotent</b> : produire le même effet
                qu&apos;il soit joué une fois ou trois. Et la garde n&apos;est pas un test
                d&apos;existence suivi d&apos;une création, parce qu&apos;entre les deux
                l&apos;autre instance a écrit : c&apos;est une clé unique tenue par la base.
              </p>
            </Note>
          </Chapitre>

          <Chapitre id="refus" rang="Chapitre 8" titre="Ce que le code refuse">
            <p>
              Les règles d&apos;un projet vivent souvent dans un document que personne ne relit.
              Ici, celles qui peuvent être vérifiées le sont, et les autres sont écrites en
              commentaire, au-dessus du code concerné, avec la raison.
            </p>
            <Tableau
              entetes={["La règle", "Ce qui la tient", "Ce qui arriverait sans elle"]}
              lignes={[
                [
                  "Aucune valeur légale en dur",
                  "Les lectures datées du référentiel, et la relecture",
                  "Une livraison à chaque loi de finances, sur trois calendriers",
                ],
                [
                  "Aucun contexte n'importe l'intérieur d'un autre",
                  "Un test qui parcourt les importations écrites",
                  "Un monolithe dont les frontières ne veulent plus rien dire",
                ],
                [
                  "Hors périmètre rend introuvable, jamais interdit",
                  "La résolution du locataire, et la revue",
                  "La liste des clients du cabinet, découvrable au hasard",
                ],
                [
                  "Aucune lecture sans locataire établi",
                  "Une exception levée plutôt qu'une valeur par défaut",
                  "Les données d'un client servies à un autre, en silence",
                ],
                [
                  "Aucun réglage qui ment",
                  "Des modèles fermés qui refusent une clé inconnue",
                  "Un réglage mal orthographié, ignoré, et un comportement inexpliqué",
                ],
                [
                  "Aucune sonde complaisante",
                  "Trois états plutôt que deux, et « sans sonde » dit plutôt que masqué",
                  "Un tableau de bord au vert pendant que les clients reçoivent des erreurs",
                ],
              ]}
            />
          </Chapitre>

          <Chapitre id="rythme" rang="Chapitre 9" titre="Comment le projet avance">
            <p>
              Le projet progresse par <b>pas</b>. Un pas confronte une maquette ou un document à
              ce que le code fait réellement, construit ce qui manque, corrige ce qui est faux,
              vérifie sur une base réelle, et s&apos;écrit dans un journal daté. Le document de
              conception porte un chapitre par pas, dans l&apos;ordre.
            </p>
            <h3>La discipline de vérification</h3>
            <ol>
              <li>Écrire le cas de test qui échoue, et vérifier qu&apos;il échoue vraiment.</li>
              <li>Écrire le code qui le fait passer.</li>
              <li>Relancer toute la suite, pas seulement le fichier concerné.</li>
              <li>
                <b>Muter son propre code volontairement</b> : inverser une comparaison, retirer
                une garde, changer un seuil. Si les tests passent encore, c&apos;est le test qui
                est en cause, pas le code.
              </li>
            </ol>
            <p>
              Le quatrième geste est celui qu&apos;on saute quand on est pressé, et c&apos;est
              celui qui a le plus souvent trouvé quelque chose : plusieurs cas de ce projet
              semblaient solides et ne vérifiaient rien.
            </p>
            <Note titre="Le commentaire est une partie du code, pas une décoration">
              <p>
                Les en-têtes de fichier expliquent <b>pourquoi</b> le code est ainsi, et souvent
                ce qui a été essayé avant. Les marques <b>⚠️</b> signalent un piège concret :
                une manière de faire qui paraît raisonnable et qui casse à l&apos;usage. Les
                lire fait gagner des heures, et les écrire évite de refaire la même erreur dans
                six mois.
              </p>
            </Note>
            <p style={{ marginTop: 32 }}>
              <a className="site-bouton site-bouton--plein" href="/prerequis/langages">
                Cours suivant : les langages
              </a>
            </p>
          </Chapitre>
        </Lecon>
      </main>
      <Pied />
    </>
  );
}
