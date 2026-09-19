# 09 · Questions ouvertes

Ce qui doit être tranché par le cabinet ou par son fiscaliste. Aucune de ces questions ne
bloque le socle livré.

Les questions **bloquantes** empêchent une mise en production. Les questions
**structurantes** ne l'empêchent pas : le code a choisi, pour chacune, une approximation
qui s'annule proprement plutôt qu'un choix pris à la place du cabinet, et elle est nommée
là où elle est faite. Elles décident de la finesse du système, pas de sa mise en route.

---

## Bloquantes pour la production

### Q1 · Seuil de règlement en espèces excluant la déduction de TVA — TRANCHÉE LE 18/08/2026

**Le cadrage avait raison, la maquette avait tort, et c'est la maquette qui l'avait emporté.**

| Source | Valeur | Sort |
|---|---|---|
| Document de cadrage, § 2.4 | **100 000 FCFA** | confirmée par le texte |
| Maquette `Prototype cliquable`, constat `FAC-ACH-007` | 500 000 FCFA | écartée |

Le CGI art. 143 dit, littéralement : « Pour les opérations taxables d'une valeur au moins
égale à cent mille (100 000) F CFA, le droit à déduction n'est autorisé qu'à condition que
les dites opérations n'aient pas été payées en espèces. » Le texte a été lu sur la fiche
« La Taxe sur la Valeur Ajoutée » publiée par la DGI, consultée le 18 août 2026.

`SEUIL_ESPECES_DEDUCTIBILITE_TVA` est passé de 500 000 à **100 000 FCFA**, statut `VALIDE`.
La règle `FAC-ACH-007` est validée sur le même fondement.

**Ce que l'erreur coûtait.** Cinq fois trop permissif : toute facture réglée en espèces entre
100 000 et 500 000 FCFA passait comme ouvrant droit à déduction. Le sens de l'erreur était le
pire des deux — elle ne gênait personne à la saisie, ne produisait aucun constat, et se
serait découverte au contrôle, en rappel de TVA sur trois exercices. Un contrôle de
conformité passé avant le 18 août 2026 doit être rejoué.

**La borne est stricte.** À exactement 100 000 FCFA, la déduction est refusée : le texte vise
les opérations « au moins égales ». Le prédicat est écrit `< seuil`, et un test dédié tient
cette borne, parce que 100 000 rond est précisément le montant que choisit un fournisseur
qui cherche la limite.

### Q1 bis · Interopérabilité avec le portail de télédéclaration de la DGI ⚠

**C'est la question la plus importante du dossier, et je n'ai aucun élément pour y
répondre.**

La DGI ne publie, à ma connaissance, ni interface programmatique documentée, ni format
d'échange, ni jeu d'essai, ni environnement de recette. Le portail de télédéclaration est
un site que l'on remplit à la main.

Le socle livré en tient compte : le port `PortailDeclaratif` existe, l'adaptateur manuel
fonctionne, et l'adaptateur automatique sera une substitution le jour où il y aura quelque
chose à brancher. **Rien n'a été inventé** — une charge utile imaginaire aurait produit un
adaptateur qui compile, qui se teste contre lui-même, et qui ne fonctionnera jamais.

Cinq questions à poser au cabinet, puis à la DGI par son intermédiaire :

| # | Question | Ce qu'elle décide |
|---|---|---|
| a | Le portail accepte-t-il un **import de fichier** — tableur, XML, texte positionnel — ou faut-il saisir champ par champ ? | Si oui, la plateforme produit le fichier et le cabinet le dépose : dix minutes par déclaration au lieu d'une heure. |
| b | Existe-t-il un **compte de rattachement CGA** permettant de déposer *pour* un adhérent ? | **La plus lourde.** Elle décide si la plateforme peut déposer, ou seulement préparer. Sans elle, il faut les identifiants de chaque adhérent — ce qu'aucun cabinet sérieux ne veut détenir. |
| c | Que contient exactement l'**accusé de réception** ? Numéro, horodatage, montant repris, empreinte ? | Ce qui peut être confronté automatiquement, et ce qui restera déclaratif. |
| d | La **DSF** se dépose-t-elle en liasse structurée, et sous quel format ? | Le contexte H · Clôture tout entier. |
| e | La **facturation électronique** instituée par la LF 2026 : quel calendrier, quelles spécifications, quel périmètre d'entreprises ? | Le port `FiscalInvoiceGateway`, à concevoir avant d'être implémenté. |

**Ce que la plateforme apporte déjà sans aucune de ces réponses**, et qu'il ne faut pas
sous-estimer : elle produit des chiffres contrôlés, elle **refuse** de préparer un dossier
irrecevable, elle conserve l'accusé et son empreinte, et elle sait dire trois ans plus tard
ce qui a été déposé et par qui. Le portail, lui, ne sait rien de tout cela.

Le transport est une demi-journée de travail le jour où les spécifications existent. La
recevabilité, elle, est déjà écrite.

### Q1 ter · Le cabinet a-t-il un compte de test sur le portail ?

Sans environnement de recette, le premier dépôt automatisé sera un dépôt réel, sur un
dossier réel, avec une pénalité réelle en cas d'erreur. À obtenir avant toute
implémentation d'adaptateur.

### Q2 · Qui est le référent de validation des règles fiscales ? — RÉPONDUE LE 18/08/2026

Le référent est **CGA Broad Range Consulting Group**, agrément MINFI/DGI n° 00000048. C'est
ce nom que porte le champ `valide_par` des 50 paramètres et de la règle validés ce jour, avec
la date en `valide_le`.

Le modèle refuse une version `VALIDE` sans ces deux champs — la règle de conformité aussi,
depuis ce jour : une règle porte une *interprétation* du texte, donc à plus forte raison.
Aucun chiffre ne peut donc être déclaré exact sans que quelqu'un de nommé en réponde.

⚠️ **Une personne physique reste à désigner.** Signer au nom de la personne morale suffit à
l'opposabilité mais pas à la traçabilité interne : le jour où une valeur est contestée, il
faut savoir qui l'a relue. À compléter dans `valide_par` sans changer le reste.

### Q3 · Le cabinet dispose-t-il du CGI 2026 à jour et de la circulaire d'application de la LF 2026 ?

Partiellement résolue le 18 août 2026 : 50 des 59 paramètres ont été confrontés à des
sources primaires ou officielles, et le champ `source` de chacun dit **ce qui a été
réellement consulté**, page par page. Neuf restent `A_VALIDER` faute d'avoir été confirmés.

Il reste que rien n'a été lu sur le CGI relié lui-même, ni sur la circulaire d'application de
la LF 2026. Les fiches de la DGI et les textes OHADA en tiennent lieu. Un fiscaliste
disposant du texte doit repasser sur les 50, et la fiche de contreseing existe pour cela.

### Q4 · Taux de l'impôt sur les sociétés — TRANCHÉE LE 18/08/2026

La divergence des sources venait de ce qu'il n'y a pas **un** taux mais deux, commandés par
le régime, auxquels s'ajoutent les centimes additionnels :

| Régime | Taux | Avec CAC (+10 %) |
|---|---|---|
| Réel normal | 30 % | **33 %** |
| Simplifié | 25 % | **27,5 %** |

Deux paramètres ont été créés — `TAUX_IS_REEL_NORMAL` et `TAUX_IS_SIMPLIFIE` —, tous deux
`VALIDE`. Ils s'entendent hors CAC ; `CAC_TAUX` les majore, comme il majore la TVA.

Le taux n'existait pas du tout au référentiel jusqu'ici : aucun calcul d'acompte n'était donc
possible. Il l'est désormais, mais **aucun écran ne le consomme encore**.

### Q5 · Hébergement et protection des données

Existe-t-il une obligation d'hébergement local des données fiscales au Cameroun ? Quel cadre
de protection des données personnelles s'applique au traitement, par un CGA, de données
concernant les fournisseurs et clients de ses adhérents ?

---

## En veille — décision du 16 août 2026

Ces quatre points sont **connus, tranchés et mis de côté**. Ils ne dépendent pas du
code et ne bloquent plus le travail en cours. Ils restent écrits ici pour qu'aucun
ne se perde, et pour qu'on n'ait pas à les redécouvrir le jour de la mise en
service.

| Point | Ce qu'il faut | Conséquence tant qu'il dort |
|---|---|---|
| **Validation du référentiel** | Un fiscaliste nommé qui confirme chaque paramètre sur le CGI | Aucun chiffre produit n'est opposable |
| **Identifiants Tara de production** | Ouvrir le compte marchand, faire une transaction réelle | Le code n'a jamais parlé au vrai prestataire |
| **Relais de messagerie + DNS** | Un compte SMTP, puis SPF, DKIM et DMARC sur `cga-brcg.cm` | Aucun courriel ne part ; s'il partait, il serait classé indésirable |
| **Extraction automatique** | Choisir un moteur, réaliser `ServiceExtraction` | Chaque champ de chaque facture se saisit à la main |

⚠️ Le premier n'est pas de même nature que les trois autres. Les trois sont des
démarches ; celui-là est une **responsabilité professionnelle**, et c'est le seul qui
décide si la plateforme peut produire autre chose que des chiffres indicatifs.

## Structurantes pour la conception

### Q6 · Organisation du cabinet

- Combien d'adhérents aujourd'hui, quelle répartition par régime, quelle croissance visée ?
  *(Le jeu de démonstration indique 128 adhérents, 84 au réel et 44 à l'IGS — à confirmer.)*
- Qui saisit, qui révise, qui valide, qui déclare ? **Y a-t-il une double validation avant
  dépôt ?**
- Le CGA tient-il lui-même la comptabilité, ou l'adhérent peut-il passer par son propre
  comptable ?
- Quel outil aujourd'hui — Excel, Sage, autre ? **Faut-il reprendre l'historique ?**
- Quelle est l'implication concrète de l'inspecteur assistant rattaché au CGA ?

### Q7 · Métier

- **Quels sont les cinq motifs de redressement les plus fréquents chez vos adhérents ?**
  Ce sont les cinq premières règles à écrire.
- Le CGA a-t-il déjà une checklist de contrôle de facture, même sur papier ?
- Comment sont réellement collectées les pièces aujourd'hui ?
- Le CGA gère-t-il la paie et les DIPE ?
- Quelles prestations sont facturées, à quel prix, à quelle fréquence ?

### Q8 · Création d'entreprise

Volume annuel, formes juridiques les plus fréquentes, CFCE utilisés, taux de conversion en
adhésion ?

### Q13 · Le formulaire public doit-il demander la région du visiteur ?

⚠️ **Aucune urgence, et une conséquence précise.** Le parcours fonctionne sans elle, et
le référentiel l'a anticipé : une région non déclarée pénalise tous les collaborateurs
également, ce qui annule le critère de proximité sans le fausser.

La région **est** collectée, mais au questionnaire de qualification, donc **après**
l'affectation. Le premier collaborateur est donc choisi sans tenir compte de la
distance.

- Le cabinet veut-il que la proximité pèse dès la première affectation ? Cela demande
  un septième champ au formulaire public, et *chaque champ de plus est un visiteur de
  moins*.
- Ou préfère-t-il **réaffecter** après qualification, quand la région est connue ? Le
  domaine sait déjà réaffecter, dans la limite de trois fois.

*Recommandation : la seconde. Elle ne coûte aucun champ au visiteur et emploie une
donnée sûre plutôt qu'une donnée saisie à la volée.*

### Q14 · Les collaborateurs sont-ils rattachés à une agence ?

Le critère de proximité compare la région du prospect à **l'agence du responsable**.
Aucune des deux n'est renseignée aujourd'hui : un compte ne porte pas d'agence.

- Le cabinet a-t-il plusieurs agences, et lesquelles ?
- Un collaborateur est-il rattaché à une seule, ou intervient-il sur plusieurs ?
- Le rattachement change-t-il dans le temps ? *(Si oui, il sera daté comme les
  habilitations, et non écrit en dur sur le compte.)*

⚠️ Tant que la réponse manque, le critère de proximité **ne départage personne**, et
c'est écrit dans le code plutôt que masqué.

### Q15 · Comment pondérer la charge d'un collaborateur ?

L'affectation choisit le moins chargé. Aujourd'hui la charge vaut le **nombre de
dossiers en cours**, ce qui est une approximation nommée : elle ordonne correctement,
elle ne prétend rien de plus.

- Un dossier de création de SARL pèse-t-il autant qu'une adhésion simple ?
- Faut-il pondérer par service, par chiffre d'affaires du client, par ancienneté du
  dossier ?
- Un dossier bloqué depuis trois semaines pèse-t-il encore ?

*La section 26 du document de conception prévoit une matrice d'évaluation de charge.
Elle attend ces trois réponses ; sans elles, l'inventer produirait un classement qui
paraît savant et ne repose sur rien.*

### Q16 · Existe-t-il un référentiel de compétences, distinct des rôles ?

L'affectation exige que le responsable détienne la **compétence requise** par le service
demandé. Faute de référentiel, le code dérive les compétences des **rôles tenus** : un
chargé de formalités *a* la compétence « formalités », parce que rien ne le dit ailleurs.

- Un collaborateur peut-il tenir un rôle sans en avoir la compétence, ou l'inverse ? *(Un
  junior en formation tient le rôle avant de tenir la compétence.)*
- Y a-t-il des niveaux — junior, confirmé, référent — et faut-il qu'un dossier complexe
  aille au référent ?
- Une compétence s'acquiert et se perd. Faut-il la dater, comme les habilitations ?

*La dérivation actuelle est assumée et écrite dans le code. Elle tient tant qu'un rôle
vaut une compétence ; le jour où le centre distingue les deux, il faudra un annuaire de
compétences et non une déduction.*

### Q17 · Une adhésion prise en cours d'exercice ouvre-t-elle l'abattement pour cet exercice ?

⚠️ **Conséquence fiscale directe, et elle se chiffre.** L'abattement CGA réduit le bénéfice
imposable de l'adhérent, et c'est le Centre qui atteste l'adhésion.

Le code répond **non** : il exige qu'une **même** adhésion couvre l'exercice du premier au
dernier jour. Le dossier de démonstration `M093344556677N`, réadhérent au 1er juillet 2022,
n'a donc pas droit à l'abattement pour 2022.

- Une adhésion signée en mars ouvre-t-elle l'abattement de l'exercice en cours, ou
  seulement du suivant ?
- Une résiliation suivie d'une réadhésion sans interruption rompt-elle le droit ?
- Le seuil d'adhésion de l'article 118 s'apprécie-t-il sur le chiffre d'affaires de
  l'exercice, ou sur celui de l'exercice précédent ?

*La lecture prudente a été retenue parce que l'erreur inverse expose le Centre : accorder à
tort est une attestation fausse, refuser à tort se rattrape par réclamation. Si le cabinet
établit le contraire, une seule méthode change :
`Entreprise.adherente_sur_toute_la_periode`.*

### Q18 · Comment corriger un régime fiscal mal saisi à l'origine ?

L'inscription d'un changement de régime refuse la cause « correction » dans les deux sens :
un tel acte ne se distingue pas d'un retour à l'IGS déguisé, qui contournerait la période
probatoire.

- Qui peut corriger un régime saisi à tort, et sur quelle pièce ?
- Une correction peut-elle toucher un exercice clos, puisqu'elle ne change pas la réalité
  fiscale mais ce que le cabinet en avait enregistré ?

*Tant que la réponse manque, un régime faux se corrige hors du produit, et c'est visible.
Mieux vaut cela qu'une porte que tout le monde emprunterait.*

### Q29 · Que montre l'espace adhérent, et comment l'adhérent paie-t-il ?

La maquette « Espace adhérent CGA » laisse elle-même une question ouverte (vue F, note 4), et le pas
112 en révèle trois autres en construisant les vues B et C.

1. **Le paiement par Mobile Money** (vue D) passe-t-il par un **agrégateur** encaissant pour le
   compte de l'adhérent, ou l'adhérent paie-t-il **directement** l'administration fiscale ? La
   maquette suppose le second cas (« le cabinet ne détient jamais votre argent »). Rien n'est
   construit tant que ce n'est pas tranché : un parcours de paiement faux engage le cabinet.
2. **La facture refusée, dans les mots de l'adhérent.** La maquette veut « un motif, une conséquence
   chiffrée en impôt, une consigne exécutable », sans code de règle. Aujourd'hui, l'adhérent lit le
   motif **écrit par le collaborateur** à la demande de rectificative, et une consigne commune
   (« demandez à votre fournisseur une nouvelle facture corrigée »). Faut-il une **phrase par règle**,
   rédigée pour l'adhérent au référentiel des règles, et le **coût en impôt** calculé par le moteur ?
   Qui les valide ?
3. **Les attentes déduites** (relevé bancaire absent, série de factures interrompue) ne sont pas
   montrées à l'adhérent tant que le cabinet ne les a pas demandées : elles font seulement dire
   « le cabinet vérifie » plutôt que « complet ». Le cabinet veut-il les montrer d'emblée, au risque
   de demander une pièce qu'il sait inutile ?
4. **L'accès par téléphone** (vue A : code reçu par WhatsApp ou SMS, code à quatre chiffres,
   empreinte). Le produit ouvre aujourd'hui l'espace par courriel et mot de passe. L'accès par
   téléphone attend le compte d'envoi WhatsApp ou SMS, et une décision sur la réinitialisation
   (« par le chargé de clientèle, jamais en autonomie »).

5. **Les explications des échéances** (pas 113, `obligations/explications_adherent.yaml`) sont une
   proposition rédigée à partir de la maquette. Le fiscaliste les relit-il telles quelles, et qui
   signe la validation ? L'écran dit « explication en cours de validation par le cabinet » tant
   qu'elles ne le sont pas.
6. **Le montant à régler** d'une échéance hors TVA : aujourd'hui, seule une estimation existe quand le
   calcul la permet, sinon « le cabinet vous indique le montant ». Le cabinet veut-il saisir le
   montant arrêté avant l'échéance, pour que l'adhérent le lise ?

7. **Les attestations** (pas 114). La maquette montre une « attestation de non-redevance » et une
   « attestation d'adhésion », « documents officiels émis par le cabinet », dont « une banque peut
   vérifier l'authenticité auprès du CGA ». La plateforme n'en émet aucune. Il faut arrêter : le
   modèle de chaque attestation, qui la signe, sa durée de validité, et **le moyen de vérification**
   (un numéro et une page publique de contrôle, un QR code). Tant que ce n'est pas fait, « Mes
   documents » ne montre que les reçus de dépôt, relevés des accusés consignés, et dit que les
   attestations se demandent à l'interlocuteur.
8. **Le numéro de l'interlocuteur.** « Appeler » n'apparaît que si le compte du chargé de clientèle
   porte un téléphone ; dans la démonstration, Patricia MOUKOURI n'en a pas. Faut-il un numéro de
   cabinet par défaut, ou exiger le téléphone des chargés de clientèle ?

*Tant que la réponse manque, l'espace montre ce qui est sûr : ce qui est demandé, ce qui est reçu,
les achats d'un seul mois déjà revu, « réglez au guichet, puis envoyez la quittance », et des reçus
de dépôt qui disent ce qu'ils sont.*

### Q28 · Qui rouvre un mois verrouillé, et qu'est-ce qui empêche de le transmettre ?

La maquette du parcours comptable (vue G) laisse la question ouverte : « le verrouillage est-il
réversible par le réviseur seul, ou faut-il l'accord de la direction ? Le parcours suppose le
réviseur. » Le pas 107 suit la maquette, **par le référentiel** (`cloture_mensuelle/reglages.yaml`) :

| Réglage livré | Effet |
| --- | --- |
| `statuts_qui_verrouillent: [TRANSMISE, VALIDEE]` | un mois transmis ou validé refuse toute saisie, correction, validation et contre-passation datée du mois |
| renvoi du réviseur | rouvre le mois, pour que le comptable corrige ce qu'on lui demande |
| mois validé | reste verrouillé ; une erreur se corrige par une contre-passation datée d'un mois ouvert |
| points bloquants | pièces du mois non traitées, brouillons, rapprochement, caisse négative, balance, numérotation, écarts en attente du second regard |
| point informatif | pièces attendues de l'adhérent (« le mois sera transmis sans elles ») |

Questions à trancher :

1. Un mois **validé** doit-il pouvoir se rouvrir, et par qui : le réviseur, la direction, les deux ?
   Aujourd'hui, personne : retirer `VALIDEE` de la liste rouvrirait tous les mois validés à la fois.
2. La liste des points bloquants convient-elle ? En particulier, le rapprochement bancaire doit-il
   bloquer un mois dont le relevé n'est pas encore arrivé ?
3. **Classer une pièce sans écriture** (un doublon, un relevé rapproché) est permis au comptable, avec
   un motif inscrit au journal d'audit, sans second regard. Faut-il un second regard, comme pour
   écarter un constat (Q26) ?

*Tant que la réponse manque, les réglages livrés s'appliquent, et chaque transmission, renvoi et
classement porte son auteur au journal.*

### Q27 · Quelles mesures la direction peut-elle décider sur un dossier à risque ?

La maquette du parcours direction (vue B) se termine par des actions et une note : « les décisions
sont datées, signées, visibles dans la chronologie de la fiche adhérent ». Le pas 100 construit le
geste, et **ne fixe pas la liste à la place de la direction** : le catalogue est lu dans
`Docs/referentiel/pilotage/mesures.yaml`. Le fichier livré reprend les quatre actions de la maquette,
en **proposition** :

| Mesure livrée | Niveaux où elle est permise | Échéance |
| --- | --- | --- |
| Renforcer le suivi du dossier | à surveiller, à traiter | non |
| Exiger une régularisation datée | à surveiller, à traiter | exigée |
| Convoquer un rendez-vous de cadrage | à traiter | non |
| Envisager la fin d'adhésion | à traiter | non |

Motif d'au moins 30 caractères à la prise et à la clôture. Sans fichier, **aucune mesure** ne peut
être décidée ; la vue risque reste lisible.

Questions à trancher :

1. La liste convient-elle, et dans quel ordre (de la plus légère à la plus lourde) ?
2. **Qui est prévenu** d'une décision ? Aujourd'hui : les collaborateurs qui travaillent sur le dossier
   (saisie ou relance), jamais l'adhérent ni l'inspecteur. Le chargé de clientèle doit-il écrire à
   l'adhérent dès « Exiger une régularisation datée », et par quel canal ?
3. **Le seuil de remontée en comité**, que la maquette laisse « à arbitrer » : faut-il qu'un score
   au-delà d'une valeur inscrive d'office le dossier au comité, ou la direction reste-t-elle seule
   juge ?
4. La maquette compose le score de **cinq rubriques** (dont « relation et paiement » et « volumétrie
   et complexité »). Le score réel en compte quatre, faute de relevé du paiement des honoraires et du
   temps passé. Faut-il ouvrir ces relevés, et avec quel poids ?

*Tant que la réponse manque, le catalogue livré s'applique, et chaque décision porte son auteur, son
motif, son échéance et le score qui l'a fondée au journal d'audit.*

### Q26 · Que le cabinet permet-il d'écarter, et qui donne le second regard ?

Écarter un constat de conformité, c'est décider qu'une anomalie détectée par le moteur n'en est pas
une sur cette facture. Le pas 92 construit le geste, et **ne décide pas à la place du cabinet** :
la politique est lue dans `Docs/referentiel/ecarts/politique.yaml`. Le fichier livré est une
**proposition**, choisie dans le sens prudent, qui attend la décision de la direction :

| Réglage livré | Pourquoi ce choix par défaut |
| --- | --- |
| BLOQUANT non écartable | un bloquant interdit la comptabilisation ; l'écarter reviendrait à comptabiliser ce que la loi refuse |
| MAJEUR écartable avec second regard | il coûte de l'argent au dossier et se répercute jusqu'à la liasse |
| AVERTISSEMENT et INFORMATION écartables sans second regard | aucune conséquence chiffrée |
| Second regard par le réviseur (autre que l'auteur) ou le fiscaliste | le cabinet de démonstration n'a qu'un réviseur ; le fiscaliste écrit les règles |
| Motif d'au moins 20 caractères | « ok » ne répond pas à la question du vérificateur |

Sans fichier, **rien n'est écartable**, et l'écran le dit.

Questions à trancher :

1. Un **bloquant** peut-il jamais être écarté (erreur de lecture de la facture, par exemple), ou la
   seule voie est-elle la rectificative ?
2. La **direction** doit-elle pouvoir donner le second regard, alors qu'elle ne détient aujourd'hui
   aucune permission de conformité ?
3. Certaines règles doivent-elles être déclarées **non écartables** quelle que soit leur sévérité ?
4. Un écart posé **après** la validation de l'écriture doit-il déclencher une contre-passation
   proposée ? Aujourd'hui il ne change que les propositions suivantes : une écriture validée garde
   son attribut fiscal.

*Tant que la réponse manque, la politique livrée s'applique et chaque écart porte son auteur, son
motif et son second regard au journal d'audit.*

### Q25 · Où vit le groupe de risque professionnel d'un employeur ?

La cotisation « accidents du travail » dépend du **groupe de risque** (A, B ou C) que la CNPS
**notifie** à chaque employeur. Il ne se déduit pas de l'activité. Aujourd'hui, les routes de
paie le reçoivent en paramètre, avec « A » par défaut, et le dossier ne le porte pas.

Essai du pas 89, même salarié (SARL BATIMENT PLUS, août 2026) : **coût employeur de 571 478 FCFA
en groupe A, 587 565 FCFA en groupe C**. Un écran qui oublie de le demander, ou un défaut qui
passe inaperçu, sous-estime la cotisation d'un employeur classé B ou C, et c'est l'adhérent qui
paie la régularisation.

Le pas 89 le rend visible sans le trancher : l'écran du bulletin demande le groupe et affiche
« à confirmer sur la notification CNPS du dossier ».

Options :

1. **Un statut daté du dossier**, comme le régime ou le centre : le groupe notifié, sa date
   d'effet, la référence de la notification. La paie le lit à la date du mois, et un changement
   de classement ne réécrit pas les paies passées.
2. **Un paramètre par dossier au référentiel** : plus simple, mais le référentiel porte des
   règles communes, pas des faits propres à un adhérent.
3. Garder le paramètre de requête, et refuser le calcul sans groupe explicite (plus de défaut).

*Tant que la réponse manque, aucun bulletin produit n'est opposable (les taux sont d'ailleurs
tous à valider), et l'écran dit que le groupe est supposé.*

### Q24 · Comment prouver en ligne qu'on représente l'entreprise ?

La souscription publique demande un NIU, **déclaré** par le visiteur. Jusqu'au pas 83, l'encaissement
ouvrait aussitôt un compte adhérent portant ce NIU. Essai réel : un inconnu règle une adhésion au NIU de
SARL BATIMENT PLUS, reçoit le lien, définit son mot de passe, et lit la fiche du dossier, ses pièces avec
fournisseurs et montants, son échéancier, et y dépose un fichier.

Le pas 83 ferme la porte sans trancher la question : **le paiement n'ouvre plus d'accès à un dossier**. La
souscription reste payée, apparaît dans l'écran « Souscriptions en ligne », et l'administration des
comptes ouvre l'accès après avoir vérifié l'identité, en décrivant sa vérification (inscrite au journal
avec son auteur).

Refuser seulement les NIU déjà au portefeuille ne suffirait pas : un NIU est imprimé sur chaque facture.
Un concurrent souscrirait avec celui d'une entreprise qui n'est pas encore cliente, et serait habilité le
jour où elle le deviendrait.

Options pour une preuve en ligne, à arbitrer par le cabinet :

1. **Vérification humaine systématique** (l'état du pas 83) : RCCM et pièce d'identité du représentant,
   présentés au cabinet ou envoyés. Sûre, lente, et elle suppose que le cabinet rappelle chaque client
   dans un délai annoncé.
2. **Un code envoyé à un contact déjà connu de l'entreprise** : téléphone ou adresse figurant au dossier
   fiscal ou au RCCM. Rapide, mais le cabinet ne détient ces contacts que pour ses clients existants, et
   aucune source officielle en ligne n'est aujourd'hui interrogeable.
3. **Un dépôt de pièces dans le tunnel** (RCCM, carte du contribuable, CNI) avant paiement, contrôlé par le
   cabinet : la vérification reste humaine, mais elle ne demande plus de rendez-vous.

Questions liées :

- Quel délai le cabinet s'engage-t-il à tenir entre le paiement et l'ouverture, et que dit-on au client
  qui attend ?
- Qu'advient-il d'un paiement dont l'identité ne peut pas être vérifiée : remboursement, ou conversion en
  prestation sans accès ?

*Tant que la réponse manque, aucun accès à un dossier ne s'ouvre sans un humain qui signe sa
vérification. L'attente d'un client légitime est visible et se mesure ; une fuite de comptabilité ne se
rattrape pas.*

### Q23 · Que faire d'un brouillon qui n'aurait jamais dû exister ?

Une écriture reçoit son numéro **à la saisie**, en brouillon. Depuis le pas 72, un brouillon se
**corrige** à son numéro. Mais aucun geste ne le fait disparaître, et c'est voulu : une suppression
laisserait un trou dans la séquence, que la clôture refuse (`SEQUENCE_TROUEE`) et que
l'administration cherche en premier. Or la clôture refuse aussi tout brouillon qui subsiste.

Deux cas restent donc sans issue raisonnable :

- un brouillon saisi par erreur (mauvais dossier, doublon) : il faut le corriger en écriture
  plausible, avec une pièce, le **valider** puis le **contre-passer**. Deux écritures au journal pour
  un geste qui n'a jamais eu lieu, et un comptable qui valide sous son nom une écriture qu'il sait
  fausse ;
- une **reprise** appliquée sur le mauvais fichier : quatre mille brouillons, même traitement.
  Depuis le pas 85, le cas le plus probable est fermé : le **même** fichier appliqué deux fois,
  ou l'export d'un dossier réimporté chez lui, est refusé écriture par écriture (une écriture
  identique existe déjà). Reste le fichier d'un autre dossier ou d'un autre exercice.

Options :

1. Un état **ABANDONNÉ** : le numéro reste au journal avec son libellé et le motif de l'abandon, hors
   des soldes, sans bloquer la clôture ni créer de trou. L'entité dit aujourd'hui « il n'y a pas de
   troisième état » ; l'exception porterait sur le brouillon seul, jamais sur une écriture validée.
   La colonne `etat` est une chaîne de vingt caractères : aucune migration de type n'est nécessaire.
2. Numéroter **à la validation** plutôt qu'à la saisie : un brouillon n'aurait pas de numéro, et se
   supprimerait sans trou. Changement plus profond : les brouillons se désignent aujourd'hui par leur
   clé, dans l'écran comme dans les rapports de clôture.
3. Assumer valider puis contre-passer, et prévoir pour la reprise une annulation de lot.

*Tant que la réponse manque, un brouillon se corrige, se valide ou se contre-passe, et la reprise
reste en mode contrôle par défaut (pas 72). Un expert-comptable du cabinet doit trancher : c'est une
question de pratique comptable avant d'être une question de code.*

### Q22 · Qui peut accorder un rôle qui dépose ou qui clôt ?

Le rôle **administrateur** est volontairement privé de toute permission comptable ou déclarative :
il gère les comptes, il ne dépose pas. Mais il peut **inviter n'importe quel rôle**, réviseur
compris. Rien ne l'empêche donc de s'inviter lui-même sous une seconde adresse, avec le rôle de
réviseur, et de déposer des déclarations ou de clore un exercice sous un autre nom. La séparation
des tâches tient à la bonne foi de l'administrateur.

- Un rôle portant `DEPOSER_DECLARATION`, `CLOTURER_EXERCICE` ou `VALIDER_ECRITURE` doit-il être
  accordé par la **direction**, ou validé par elle après coup ?
- Ou le cabinet assume-t-il cette confiance, le journal d'audit gardant la trace de qui a invité qui ?

*Tant que la réponse manque, l'administrateur invite tous les rôles, et chaque invitation est au
journal avec son auteur (pas 69).*

### Q21 · Comment mesurer la charge d'un prospect avant de le chiffrer ?

Depuis le pas 65, le prix se calcule sur la qualification enregistrée, sauf un fait : le
**score de charge**, que les règles `TAR-CHG-001` et `TAR-CHG-002` emploient pour majorer la
prestation au-delà de 46 et 76 points. La matrice de charge existe au portefeuille, pour une
entreprise suivie, sur des faits qu'un prospect n'a pas encore (volume de pièces, régime,
nombre d'établissements).

- Le cabinet veut-il une matrice propre au prospect, lue sur les réponses du questionnaire ?
- Ou le score reste-t-il une appréciation du responsable, et alors qui la valide ?

*Tant que la réponse manque, le score est déclaré par le responsable et conservé avec les faits
de la proforma : un score minoré pour baisser le prix se lit sur le document émis.*

### Q20 · À quel guichet se déposent les retenues sur salaires ?

Depuis le pas 59, chaque obligation du catalogue porte le guichet où elle se dépose, et le
constat de dépôt le reprend. La CNPS est rattachée au guichet CNPS. Les **retenues IRPP sur
salaires** sont rattachées à la DGI, et ce choix n'est pas vérifié : le DIPE réunit retenues
et cotisations sur une même déclaration.

- Où le cabinet dépose-t-il réellement les retenues sur salaires, et quel accusé en reçoit-il ?
- Si c'est un seul DIPE pour les deux, faut-il un seul accusé pour deux obligations, ou une
  seule obligation « DIPE » au catalogue ?

*Tant que la réponse manque, un accusé DIPE consigné sur les retenues IRPP le sera au guichet
DGI. La valeur est une donnée du catalogue : la corriger ne demande aucun changement de règle.*

### Q19 · Quel consentement recueillir sur la vitrine ?

Depuis le pas 51, le formulaire de contact enregistre la demande dans le parcours
d'acquisition **et** ouvre WhatsApp. Sa case dit « me recontacter au sujet de ma demande » :
ce n'est pas un consentement à recevoir des messages WhatsApp du cabinet. La demande est
donc enregistrée avec un rappel **par téléphone**.

- Le cabinet veut-il recueillir le consentement WhatsApp sur la vitrine ? Il faut alors un
  texte validé, versionné comme `consentement-whatsapp-v1`, et une seconde case.
- **Le formulaire de la bannière n'a aucune case de consentement.** Il ouvre WhatsApp sans
  rien enregistrer. L'y brancher suppose d'ajouter une case à un écran validé par le cabinet.

*Tant que la réponse manque, les demandes de la bannière passent par WhatsApp sans trace
dans le produit. Mieux vaut cela qu'enregistrer des données personnelles sans accord.*

### Q9 · Pondération du score de risque — ARRÊTÉE LE 18/08/2026

La maquette Direction proposait cinq composantes ; le référentiel en porte quatre, plus deux
seuils de classement. La direction les a arrêtés le 18 août 2026 : ils portent
`nature: POLITIQUE_CABINET` et le statut `VALIDE`.

**Ce que la nature du paramètre a levé.** Ces six réglages attendaient jusqu'ici la signature
d'un fiscaliste, qui n'avait aucune qualité pour les donner : rien dans le CGI ne dit ce que
vaut un retard déclaratif dans une note interne. Ils attendaient une signature que personne
ne pouvait apposer. `LOI` contre `POLITIQUE_CABINET` dit désormais *qui* est compétent, là où
le statut ne disait que *si* c'était validé.

Reste ouvert : **le seuil au-delà duquel un dossier remonte automatiquement en comité**. Le
score classe, il ne convoque pas. C'est une décision d'organisation, pas de paramétrage.

---

## Matériel manquant

### Q10 · Logo monochrome blanc — partiellement résolu

La bibliothèque de composants signalait en rouge l'absence d'une version blanche pour la
barre latérale en `brand-indigo-900`. **Vérification faite : elle existe**, en PNG blanc sur
transparent, dans le projet Claude Design sous `uploads/CGA-logo-blanc.png`. Elle est
désormais versionnée dans `Frontend_erp_cga/public/marque/` et employée par E00.

Reste à obtenir une **version SVG** : le PNG se dégrade sur écran à haute densité et pèse
14 Ko là où un tracé vectoriel en pèserait moins d'un — ce qui compte sur les connexions
visées.

### Q11 · Autres éléments attendus du cabinet

- Le jeu d'icônes linéaires retenu.
- Les gabarits de messages de relance, portail et WhatsApp.
- La liste officielle des paramètres du référentiel : seuils, taux.
- La liste annuelle des entités habilitées à opérer la retenue à la source, publiée par
  arrêté — nécessaire aux règles de catégorie 6.

### Q12 · Documents non dépouillés

Trois cahiers des charges existent dans le projet Claude Design distant et n'ont pas été lus.
Ils peuvent contenir des exigences contractuelles qui contredisent ou complètent ce dossier.

- `uploads/Cahier_des_charges_TECHNIQUE_CGA_BRC_Group.pdf`
- `uploads/Cahier_des_charges_Plateforme_CGA_BRC_Group.pdf`
- `uploads/Cahier_des_charges_CGA_BRC_Group_version_synthetique.pdf`

**À traiter en priorité au prochain jalon.**
