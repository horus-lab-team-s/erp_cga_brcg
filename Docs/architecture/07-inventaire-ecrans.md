# 07 · Inventaire des écrans

Référence : § 7 et § 8 du dossier de design.

## Les quatorze écrans

| Réf. | Écran | Espace | Support | Priorité | Maquette livrée |
|---|---|---|---|---|---|
| E00 | Structure générale et navigation | Collaborateur | Bureau | 1 | `Wireframes CGA.dc.html` (distant) |
| **E02** | **Détail d'une pièce et rapport de conformité** | Collaborateur | Bureau | **1** | `Prototype cliquable CGA.html` |
| E03 | Boîte de réception des pièces | Collaborateur | Bureau | 2 | `Prototype cliquable CGA.html` |
| E06 | Accueil adhérent | Adhérent | Mobile d'abord | 2 | `Espace adherent CGA.html` |
| E07 | Dépôt d'un justificatif | Adhérent | Mobile | 2 | `Prototype cliquable CGA.html` |
| E01 | Tableau de bord collaborateur | Collaborateur | Bureau | 3 | — |
| E05 | Échéancier consolidé | Collaborateur | Bureau | 3 | — |
| E08 | File de synchronisation | Adhérent | Mobile | 3 | `Espace adherent CGA.html` |
| E09 | Mes échéances | Adhérent | Mobile | 3 | `Espace adherent CGA.html` |
| E04 | Fiche adhérent 360° | Collaborateur | Bureau | 4 | — |
| E13 | Pipeline création d'entreprise | Collaborateur | Bureau | 4 | — |
| E10 | Saisie et imputation comptable | Collaborateur | Bureau | 5 | `Prototype cliquable CGA.html` |
| E11 | Constructeur de règle de conformité | Fiscaliste | Bureau | 5 | — |
| E12 | Assistant de clôture et liasse | Collaborateur | Bureau | 5 | — |

Ordre de production recommandé par le dossier de design :
**E00, E02, E03, E01, E05, E06, E07, E08, E04, E10, E11, E12, E13.**

## E02 — l'écran le plus important du produit

> À concevoir en premier et soigner plus que tous les autres.

**Deux colonnes.** À gauche, environ 45 % : visionneuse du document, zoom, rotation,
ajustement. Quand un constat est sélectionné à droite, **la zone correspondante du document
est surlignée**.

À droite, environ 55 %, dans cet ordre exact :

1. **Bandeau de verdict** — gravité maximale rencontrée et conséquence fiscale chiffrée, en
   langage clair : « Anomalie majeure — TVA non déductible : 379 350 FCFA ».
2. **Données extraites** — fournisseur, NIU, RCCM, numéro, date, HT, TVA, TTC, mode de
   règlement. Chaque champ porte un **indice de confiance** ; les champs peu fiables sont
   signalés pour vérification. Tous sont modifiables.
3. **Liste des constats** — un par anomalie, dépliable, avec gravité, libellé, code,
   **référence légale**, message explicatif et consigne de régularisation.
4. **Actions** — valider et comptabiliser ; demander une facture rectificative ; écarter un
   constat avec motif obligatoire, réservé au réviseur.

**Contrainte forte** : la référence légale est visible sur chaque constat. C'est ce qui
distingue cet outil d'un validateur de formulaire, et ce qui permet au comptable de justifier
un rejet auprès d'un adhérent mécontent.

Trois variantes à produire : facture conforme, facture avec deux anomalies majeures, facture
avec une anomalie bloquante.

## Contraintes transversales

- **Tout tient en 1440 × 900 sans défilement** sur les écrans de production collaborateur.
- E03 : au moins 25 lignes visibles sans défilement, navigation complète au clavier.
- Chaque écran existe en état **vide, chargement, erreur**, et **hors ligne** sur mobile.
- E11 : aucune syntaxe technique visible, aucun code, aucune expression à taper — voir
  [03-moteur-conformite.md](03-moteur-conformite.md) § 12.

## Ce que les maquettes livrées couvrent en plus de l'inventaire

Les cinq maquettes de `Docs/` documentent des parcours par profil, plus larges que les fiches
d'écran :

| Maquette | Contenu |
|---|---|
| `Bibliotheque de composants CGA.html` | Jetons, typographie, gravité, actions, densité, formats, espacement |
| `Prototype cliquable CGA.html` | E03 → E02 → E10 côté bureau ; E06 → E07 côté mobile, avec coupure réseau simulée |
| `Parcours comptable CGA.html` | Plan de travail, rapprochement bancaire, grand livre, préparation TVA, contre-passation, relance, clôture mensuelle |
| `Parcours reviseur CGA.html` | File d'anomalies, traitement en masse par règle, journal des dérogations, revue de dossier, dépôt, qualité des règles |
| `Pilotage direction CGA.html` | Tableau de bord, vue risque avec score décomposé, charge et production, portefeuille et rentabilité, qualité et rapport mensuel |

Ces parcours introduisent des écrans absents de l'inventaire E00–E13 — journal des
dérogations, statistiques de règles, vue risque. Ils sont à intégrer à l'inventaire lors de
la prochaine révision du dossier de design.

## Ce qui est construit : une mesure, plus un tableau

⚠️ **Rectificatif du pas 80.** Cette section portait un tableau « ce qui est construit — 18 août 2026 ».
Il affirmait encore, bien des pas plus tard, que les indicateurs du tableau de bord étaient fictifs, que
l'écran des comptes était en lecture seule, et il ignorait les écrans construits depuis. Un état écrit
à la main vieillit sans le dire : c'est la faute des simulations des pas 75 et 76.

L'état réel se **mesure** désormais :

- la cible est déclarée, écran par écran et geste par geste, dans
  [avancement/grille-des-ecrans.yaml](avancement/grille-des-ecrans.yaml) ;
- `Backend_erp_cga/outils/avancement_des_ecrans.py` la confronte au backend et au frontend, et rend le
  pourcentage par écran, par priorité et global.

```
cd Backend_erp_cga
CGA_PERSISTANCE=memoire python -m outils.avancement_des_ecrans --detail
```

Mesure du pas 118 : **100 % des gestes attendus sont branchés** (225 sur 225). La **pièce d'appui d'une dérogation**
(maquettes réviseur vue B et direction vue E) se joint à la décision, et le journal des dérogations compte ce qui reste
« à régulariser » passé le délai du référentiel. ⚠️ **Cent pour cent de la grille n'est pas un produit fini** : restent de
l'espace adhérent l'accès par téléphone, le paiement en ligne et les attestations (Q29) ; du pilotage, la rentabilité par
dossier (grille d'honoraires et coût horaire à fournir) et « Envoyer au comité » ; du parcours comptable, les codes du
formulaire de TVA et WhatsApp ; et les questions ouvertes (Q24 à Q29) et la validation des paramètres légaux et des textes
adressés à l'adhérent par un professionnel nommé. Le détail est au journal
([13-parcours-d-acquisition.md](13-parcours-d-acquisition.md), pas 80 à 118). Ce chiffre date du pas 118 : **rejouer la
mesure plutôt que le recopier.**

⚠️ `/comptabilite/saisie` exige `SAISIR_ECRITURE`, que son parent n'exige pas : un
chargé de clientèle lit la balance et n'écrit pas. Une entrée de menu dont chaque
envoi finirait en 403 serait pire qu'une entrée absente.

⚠️ L'entrée « Pilotage » n'apparaît que pour la direction : `LIRE_PILOTAGE` n'est
détenue par personne d'autre, réviseur compris. Voir tout le portefeuille n'est pas
piloter le cabinet, et le score porte un jugement d'affectation. Depuis le pas 100, chaque
dossier du tableau de bord s'ouvre sur sa vue risque (`/pilotage/[niu]`), où la direction
décide ; les décisions, sans la vue risque, sont lisibles sur la fiche adhérent par le cabinet
qui porte le dossier, jamais par l'adhérent.

### Décisions d'affichage à tenir

**Le référentiel est lisible par tous les rôles internes**, pas seulement par le
fiscaliste — permission `LIRE_DOSSIER`, non `MODIFIER_PARAMETRE`. Le réserver au fiscaliste
empêcherait un comptable de répondre à « sur quoi repose ce chiffre ? », qui est précisément
la question qu'on lui posera.

**Un sous-menu ne liste que ses enfants construits.** Une entrée de sous-menu qui tombe en
404 est plus déroutante qu'une entrée absente, parce qu'on la découvre après avoir cliqué.

**Un tiret, jamais un zéro, pour une valeur inconnue.** Sur une échéance fiscale, « on ne
sait pas » et « rien à payer » ne se confondent pas.

**Le ton d'alerte est réservé à ce qui bloque.** Une échéance dépassée le porte ; un compte
non lettré est du travail restant, pas une anomalie.

**Chaque écran vérifie la permission avant d'appeler l'API.** Sans ce garde, un
refus d'habilitation remontait en `500` : « le logiciel est cassé » là où la réponse
juste était « ce n'est pas pour vous ». Un `500` fait appeler le cabinet, ouvrir un
incident, chercher une panne inexistante — et il noie les vrais `500`.

| Écran | Permission exigée |
|---|---|
| Tableau de bord, Portefeuille, Référentiel | `LIRE_DOSSIER` |
| Comptabilité, Grand livre, Déclaration TVA | `LIRE_COMPTABILITE` |
| Obligations | `LIRE_DOSSIER` |
| Comptes et habilitations | `GERER_COMPTES` |

⚠️ **La coquille elle-même conditionne ses lectures.** L'administrateur n'a
délibérément aucune permission sur les dossiers — il distribue les droits, il ne s'en
sert pas. Le gabarit l'avait oublié et appelait `lireDossiers()` sans condition :
`403` dans le gabarit, donc `500` sur **chaque écran**, y compris celui des comptes
qui est le sien. Le seul rôle capable de réparer une habilitation était le seul à ne
pouvoir ouvrir aucune page.

**Le refus nomme le profil qui ouvrirait l'écran.** L'API, elle, tait tout et rend
`404` plutôt que `403` sur un dossier hors périmètre — le dire apprendrait à un
adhérent quels dossiers le cabinet suit. Ici rien de tel : une permission est
attachée à un rôle, pas à un dossier. Nommer le profil ne révèle aucune donnée et
évite un appel au support.

**Une frontière d'erreur double le garde**, pour ce qu'aucune vérification de
permission ne peut anticiper : un refus qui dépend du **dossier** demandé. ⚠️ Elle
n'affiche jamais le message, seulement le `digest` — et se replie sur « panne »
plutôt que « refus » en cas de doute, parce qu'annoncer un refus sur une vraie panne
enverrait chercher une habilitation au lieu d'un incident.

**Les gestes d'administration exigent une confirmation explicite.** Suspendre un compte coupe
les sessions ouvertes, fermer une habilitation n'est pas réversible : ces gestes portent une case à
cocher (pas 69 et 70), parce qu'une confirmation bâclée vaut moins que pas de bouton. ⚠️ Cette
phrase disait « les écrans d'administration ne modifient rien pour l'instant » ; c'était vrai
jusqu'au pas 68.
