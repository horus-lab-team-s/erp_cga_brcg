# Vérifier les parcours à la main

📄 **Le document à remettre est ailleurs.** Le cahier de recette complet, avec les
58 cas d'usage, les comptes de démonstration et les réserves ouvertes, est en PDF :
[`cahier-de-recette-cga.pdf`](cahier-de-recette-cga.pdf). Il se refabrique par
`python Docs/recette/cahier_de_recette.py`. Ce document-ci reste le mode d'emploi
du parcours manuel.

⚠️ **Ce document décrit un mode qui fabrique des encaissements sans argent et
expose les liens d'activation en clair.** La production refuse de démarrer avec
— voir `_exigences_production` dans `app/infrastructure/config.py`.

## Démarrer

```bash
# 1 · La base de développement
cd Backend_erp_cga
eval "$(outils/postgres-local.sh start)"
alembic upgrade head
python -c "from app.amorcage import amorcer; print(amorcer())"

# 2 · L'API, en mode recette
CGA_MODE_DEMONSTRATION=true CGA_PERSISTANCE=postgresql \
  uvicorn app.main:app --reload --port 8000

# 3 · Le site
cd ../Frontend_erp_cga && pnpm dev
```

Vérifier que le mode est bien actif : `curl localhost:8000/sante` doit contenir
`"mode_demonstration": true`.

## Ce que le mode change, et rien d'autre

| | Sans le mode | Avec |
|---|---|---|
| Paiement | Attend la notification du prestataire — donc n'arrive jamais en développement | **Validé d'office**, en empruntant exactement le chemin d'une vraie notification |
| Courriels | Retenus en mémoire, illisibles | Retenus **et lisibles** sur `/courriels` |
| `/transverse/courriels` | `404` | Rend les messages, liens compris |

Le reste est inchangé : mêmes règles, mêmes contrôles, mêmes refus. Ce qui est
simulé, c'est **l'appel du prestataire de paiement**, pas la logique métier.

## Parcours 1 · De la souscription à l'espace adhérent

C'est le parcours qui n'avait jamais été exécuté en entier, et c'est ainsi que la
page d'activation a pu manquer sans que rien ne le signale.

1. **`/estimation`** → renseigner une entreprise, choisir un service, obtenir un devis.
2. **Payer** — le paiement se valide seul. Le message le dit en toutes lettres.
3. **`/courriels`** → le courriel d'activation apparaît. Cliquer « Ouvrir le lien ».
4. **`/activation?jeton=…`** → choisir un mot de passe.
   ⚠️ Il ne doit contenir ni le nom, ni le prénom, ni l'adresse : la politique
   refuse, et le message dit pourquoi. Ce refus est correct, pas un défaut.
5. **`/connexion`** → se connecter. On arrive sur `/mon-espace`, avec le seul
   dossier souscrit.

Le lien ne fonctionne **qu'une fois** : le rouvrir rend `410`.

## Parcours 2 · Mot de passe oublié

1. `/connexion` → **« Mot de passe oublié ? »** → saisir une adresse de test.
2. `/courriels` → le message `compte.reinitialisation` apparaît.
3. Suivre le lien → `/reinitialisation?jeton=…`, choisir un nouveau mot de passe.
4. Se reconnecter.

⚠️ La confirmation est **la même** que l'adresse existe ou non — essayez avec
`inconnu@nulle-part.cm` pour le vérifier. La différencier donnerait la liste des
adhérents du cabinet à qui essaierait mille adresses.

⚠️ Après envoi, le formulaire disparaît. Chaque nouvelle demande **invalide le
lien précédent** — celui qui est peut-être en train d'arriver.

## Parcours 3 · Le travail du cabinet

Se connecter avec un compte du tableau ci-dessous, puis :

`/portefeuille` → `/pieces` → ouvrir une pièce (rapport de conformité, constats
chiffrés) → `/comptabilite` (balance, grand livre) → `/obligations` (échéancier)
→ `/obligations/declarations` (la TVA écartée par le contrôle).

Pour voir un rejet, choisir le dossier **M081234567890P** : `FAC-ACH-007`,
379 350 F de TVA non déductible.

## Les comptes de test

Tous partagent le même mot de passe :

```
cabinet brcg douala 2026
```

| Adresse | Rôle | Ce qu'il sert à vérifier |
|---|---|---|
| `b.mballa@cga-brcg.cm` | Direction | Tout voir |
| `s.onana@cga-brcg.cm` | Administrateur | ⚠️ **Aucun droit sur les dossiers** — seul rôle à ne voir que `/comptes` |
| `l.fotso@cga-brcg.cm` | Comptable | Le parcours de travail ordinaire |
| `c.ndongo@cga-brcg.cm` | Comptable | Un second portefeuille |
| `a.bouba@cga-brcg.cm` | Réviseur | Écarter un constat, arbitrer un doublon |
| `r.ebolo@cga-brcg.cm` | Fiscaliste | Le référentiel |
| `p.moukouri@cga-brcg.cm` | Chargé de clientèle + formalités | Deux rôles simultanés |
| `jp.nkoa@batimentplus.cm` | Adhérent | `/mon-espace`, et le refus poli ailleurs |
| `mc.essomba@lacolombe.cm` | Adhérent | Un second dossier |
| `g.atangana@inspection.cm` | Inspecteur | Lecture seule, jamais d'écriture |
| `a.tchinda@cga-brcg.cm` | **Suspendu** | La connexion doit être refusée |
| `e.tchoumba@tchoumbaetfils.cm` | **Jamais activé** | La connexion doit être refusée |

⚠️ Les deux derniers **doivent** échouer à la connexion, avec le même message que
pour un compte inexistant. C'est le comportement attendu : différencier les
motifs rouvrirait l'oracle d'énumération.

## ⚠️ Servir en clair, et le témoin de session

Le témoin de session est marqué `Secure` **uniquement quand la connexion est
chiffrée** — déterminé sur `x-forwarded-proto`, jamais sur `NODE_ENV`.

C'est ce qui permet de faire tourner la **compilation de production** sur
`http://localhost` sans que la connexion ne rebondisse indéfiniment sur l'écran
de connexion. Le symptôme, avant correctif, était muet : connexion réussie,
redirection partie, page suivante qui redemande de se connecter.

⚠️ En production, le mandataire inverse **doit** poser `x-forwarded-proto`. Sans
lui, le témoin circulerait sans `Secure`. C'est la même exigence que pour l'API,
dont la limitation de débit lit l'adresse qu'il reconstitue.

## Ce qu'il faut regarder de près

**Les refus.** Un rôle qui ouvre un écran qui ne le concerne pas doit voir
« cet écran n'est pas ouvert à votre rôle », jamais une page cassée.

**Les tirets.** Un montant inconnu s'affiche `—`, jamais `0`. Sur une échéance
fiscale, la différence est celle d'une pénalité.

**Les avertissements.** Trois sont écrits dans l'interface : le référentiel n'est
pas validé, l'échéancier suppose un dossier sans salariés, un accusé sans
justificatif archivé ne repose que sur la saisie du numéro.

## Ce que ce mode ne prouve pas

* **que le paiement fonctionne** — Tara n'a jamais été appelé pour de vrai ;
* **que les courriels arrivent** — ils ne partent pas ; il y faut SPF, DKIM, DMARC ;
* **que les chiffres sont justes** — le référentiel n'est pas validé, et aucun
  montant produit n'est opposable.
