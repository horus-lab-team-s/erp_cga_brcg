# 09 · Questions ouvertes

Ce qui doit être tranché par le cabinet ou par son fiscaliste. Aucune de ces questions ne
bloque le socle livré ; toutes bloquent une mise en production.

---

## Bloquantes pour la production

### Q1 · Seuil de règlement en espèces excluant la déduction de TVA ⚠

**Deux sources fournies se contredisent d'un facteur cinq.**

| Source | Valeur | Fondement cité |
|---|---|---|
| Document de cadrage, § 2.4 | **100 000 FCFA** | « pour les opérations ≥ 100 000 FCFA, la déduction n'est admise que si l'opération n'a pas été payée en espèces » |
| Maquette `Prototype cliquable`, constat `FAC-ACH-007` | **500 000 FCFA** | CGI art. 143 |

La règle `FAC-ACH-007` est celle qui produit le plus gros enjeu du jeu de démonstration :
47 constats, 5 593 560 FCFA cumulés. Se tromper de seuil, c'est soit rater des rejets, soit
en produire à tort sur des factures conformes.

Le paramètre `SEUIL_ESPECES_DEDUCTIBILITE_TVA` porte aujourd'hui la valeur 500 000 — celle
des maquettes, donc celle que le cabinet a validée visuellement — au statut `A_VALIDER`, avec
la divergence documentée dans le YAML.

**À trancher sur le texte du CGI par le fiscaliste.**

### Q2 · Qui est le référent de validation des règles fiscales ?

Ce rôle doit être **nommé et engagé**. C'est la protection juridique du projet : c'est lui qui
répond de l'exactitude des valeurs, pas l'éditeur. Sans lui, aucun paramètre ne peut passer
de `A_VALIDER` à `VALIDE`, et aucun chiffre produit par la plateforme n'est opposable.

### Q3 · Le cabinet dispose-t-il du CGI 2026 à jour et de la circulaire d'application de la LF 2026 ?

Les quinze paramètres du référentiel proviennent tous de sources secondaires. Ils doivent
être confrontés au texte.

### Q4 · Taux de l'impôt sur les sociétés

Les sources consultées divergent : 30 % + CAC, 25 %, 28 % selon les régimes et les années.
À faire trancher avant tout calcul d'acompte.

### Q5 · Hébergement et protection des données

Existe-t-il une obligation d'hébergement local des données fiscales au Cameroun ? Quel cadre
de protection des données personnelles s'applique au traitement, par un CGA, de données
concernant les fournisseurs et clients de ses adhérents ?

---

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

### Q9 · Pondération du score de risque

La vue Risque de la maquette Direction décompose le score en cinq composantes — anomalies non
résolues 35 points, complétude 25, échéances 20, volumétrie 20, relation et paiement 20. Ces
pondérations sont une proposition. **La direction doit les arbitrer**, ainsi que le seuil
au-delà duquel un dossier remonte automatiquement en comité.

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
