# Recette par profil — la matrice complète

Huit scripts qui vérifient, contre une pile qui tourne, ce qu'aucun test
unitaire ne vérifie : **le comportement réel d'un profil donné devant un écran
donné**. Les défauts trouvés depuis le début de ce projet l'ont tous été à
l'exécution, jamais par la suite de tests — non parce que les tests sont
mauvais, mais parce qu'ils testent des unités et que ces défauts vivent dans le
câblage entre elles.

| Script | Ce qu'il établit |
|---|---|
| `cas_usage.py` | **Le registre des cas d'usage** — soixante-quinze cas, chacun avec sa preuve exécutée. À montrer. |
| `cahier_de_recette.py` | **Le cahier de recette en PDF** — le registre, les comptes et les réserves, mis en page. À remettre. |
| `recette_complete.py` | Les cinq passes A→E, en matrices. À lire quand un cas d'usage tombe. |
| `flux_souscription.py` | Le parcours M, du prospect anonyme à l'adhérent connecté. |
| `flux_creation.py` | Le parcours I, du porteur de projet à l'entreprise adhérente — la dernière étape vérifie que F lui calcule un échéancier sans qu'on l'ait généré. |
| `flux_saisie.py` | Le parcours E, de la saisie d'écriture à la contre-passation : le seul qui prouve que le cabinet peut **produire**. |
| `flux_social.py` | Le parcours G, du fichier du personnel à la déclaration mensuelle — dont l'asymétrie du plafond CNPS, invisible sous le plafond. |
| `verifier_profils.py` | Le socle : comptes, permissions par rôle, client HTTP, classement des réponses. |

⚠️ Exporter `CGA_URL_BASE_DE_DONNEES_TEST` avant `cas_usage.py`. Sans lui, les
tests de persistance et de concurrence se **sautent** au lieu de tourner. Le
registre le détecte et refuse de compter le cas comme validé — un cas validé
par des tests qui ne se sont pas exécutés éteint la seule alarme qui aurait pu
sonner — mais mieux vaut la base montée que le cas manquant.

Depuis le pas 129, le cahier **dit pourquoi** rien n'a tourné : la raison
d'ignorance rapportée par pytest suit le verdict. « Aucun test exécuté » est
exact et parfaitement inutile à celui qui doit corriger ; « base injoignable
sur telle adresse » se répare en une commande.

## Les cinq passes

    A  connexion            qui entre, qui doit être refusé
    B  écrans               ce que chaque profil peut ouvrir
    C  autorisations API    le refus tient-il sans l'interface
    D  portée par dossier   un habilité voit-il le dossier voisin
    E  flux d'écriture      les actes qui modifient l'état

**La passe C est celle qui compte.** Une garde écrite dans une page Next protège
l'écran, pas la donnée : le front transmet le même témoin `cga_session` à l'API.
Tout refus constaté à l'écran doit donc être rejoué directement contre le
backend, faute de quoi on a mesuré une politesse d'interface et non une
autorisation.

**La passe D est celle qui engage.** Un comptable habilité sur trois dossiers
qui lit le quatrième n'est pas une gêne d'ergonomie, c'est une violation du
secret professionnel.

**La passe E vérifie aussi des accords.** Une recette qui ne constate que des
refus valide tout aussi bien un système qui refuse tout.

## Monter la pile

**Une commande suffit désormais**, et c'est celle qu'il faut employer avant toute
séance :

```bash
Backend_erp_cga/outils/pile-de-demonstration.sh neuve
```

Quatre secondes : la base est **recréée**, le jeu de démonstration versé, l'API et
le front démarrés, et le limiteur de connexions remis à zéro. Voir
`Docs/seance-de-demonstration.md` pour la séance elle-même, conduite dans un ordre
où chaque acte s'appuie sur le précédent.

⚠️ `amorcer()` **refuse** de rejouer sur une base qui contient déjà des comptes :
un réamorçage écraserait des mots de passe réels par ceux de la démonstration. La
seule façon de repartir propre est de recréer la base, et c'est ce que fait `neuve`.

Le détail, pour qui veut monter la pile à la main :

```bash
# 1 · PostgreSQL local — données de démonstration uniquement
export PATH=/usr/lib/postgresql/16/bin:$PATH
initdb -D /tmp/cga/pgdata --auth=trust -U cga -E UTF8 --locale=C
mkdir -p /tmp/cga-sock
pg_ctl -D /tmp/cga/pgdata -o "-p 55432 -k /tmp/cga-sock -c listen_addresses=127.0.0.1" start
createdb -h 127.0.0.1 -p 55432 -U cga cga_dev

# 2 · Schéma et jeu de démonstration
cd Backend_erp_cga
export CGA_PERSISTANCE=postgresql
export CGA_URL_BASE_DE_DONNEES="postgresql+psycopg://cga@127.0.0.1:55432/cga_dev"
python -m alembic upgrade head
CGA_MODE_DEMONSTRATION=true python -c "from app.amorcage import amorcer; print(amorcer())"

# 3 · L'API, en mode recette
CGA_MODE_DEMONSTRATION=true \
CGA_ADRESSE_PUBLIQUE_SITE=http://localhost:3011 \
CGA_ORIGINES_CORS='["http://localhost:3011"]' \
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

# 4 · Le front, build autonome
cd Frontend_erp_cga/.next/standalone
API_URL=http://127.0.0.1:8010 PORT=3011 HOSTNAME=0.0.0.0 node Frontend_erp_cga/server.js
```

⚠️ `HOSTNAME=0.0.0.0`. Avec `127.0.0.1`, le serveur autonome renvoie une
redirection sur chaque page et la recette conclut à un produit cassé.

## Lancer

```bash
python Docs/recette/cas_usage.py            # le registre, à montrer
python Docs/recette/recette_complete.py     # A→E, à lire quand un cas tombe
python Docs/recette/flux_souscription.py    # le parcours M
python Docs/recette/flux_creation.py        # le parcours I
python Docs/recette/flux_social.py          # le parcours G
python Docs/recette/flux_saisie.py          # le parcours E, écriture comptable
python Docs/recette/cahier_de_recette.py    # le PDF, depuis le registre qui vient de tourner
```

Code de sortie 1 s'il reste une anomalie.

## ⚠️ Quatre pièges qui font accuser le produit à tort

Chacun a été rencontré. Chacun produit exactement le symptôme d'un logiciel
cassé, et chacun venait de l'outil de test.

1. **Le type de contenu.** Les formulaires déclarent
   `encType="multipart/form-data"`. Postés en `application/x-www-form-urlencoded`,
   ils répondent 200 sans effet.

2. **La lecture des champs cachés.** Next.js sérialise la référence de son action
   serveur en JSON dans un champ caché. Une expression régulière qui suppose
   `name` avant `value` renvoie des valeurs **vides** sans jamais échouer, et
   l'action serveur devient irrésolvable : HTTP 500 sur toutes les connexions.
   D'où le parseur HTML dans `verifier_profils.py`.

3. **Le marqueur de refus.** La classe `avertissement-ecran--reserve` sert aussi
   de bandeau de mise en garde ordinaire sur cinq écrans qui s'ouvrent
   normalement. Seul le titre **« Accès réservé »** distingue un refus.

4. **Les champs cachés de plusieurs formulaires sur une même page.** L'écran de
   saisie comptable en porte un par écriture listée, en plus du sien. Lire les
   champs cachés de la page entière fait gagner la **référence d'action du
   dernier** : la soumission a alors validé une écriture existante au lieu d'en
   créer une, sans le moindre message, et le journal restait à son compte
   d'avant. Un navigateur n'envoie que les champs du formulaire soumis ; voir
   `_formulaire` dans `flux_saisie.py`.

Et un cinquième, qui n'est pas un piège mais une bonne nouvelle : le limiteur de
débit refuse au-delà de **trente connexions par cinq minutes**. Une recette qui
se reconnecte à chaque sonde se fait limiter elle-même et produit des faux
défauts. Les scripts ouvrent une session par compte et la réutilisent.

⚠️ Cela vaut aussi **entre deux exécutions**. Chaque passe ouvre une dizaine de
sessions ; deux passes rapprochées franchissent la fenêtre et **tout** bascule en
401. Le cahier de recette a été imprimé une fois dans cet état, avec trente cas
en échec qui n'accusaient que l'outil. Le limiteur vit en mémoire dans l'API :
redémarrer uvicorn le remet à zéro, plus vite qu'attendre les cinq minutes.

**Depuis le pas 119, l'outil s'en aperçoit.** `session()` lève `RecetteLimitee`
quand la connexion est refusée : le registre **s'arrête** avec un bandeau
« RECETTE INTERROMPUE » plutôt que d'aligner des faux défauts, et le cahier
**n'est pas réécrit** — celui d'hier, juste, vaut mieux qu'un cahier
d'aujourd'hui qui accuse le produit d'échecs provoqués par la recette. C'est
arrivé de nouveau ce jour-là, à l'identique : vingt-cinq cas « en échec » sur une
pile parfaitement saine.

## Les comptes

Voir [`../cahier-de-recette-cga.pdf`](../cahier-de-recette-cga.pdf), section 3, ou [`../recette.md`](../recette.md). Tous partagent le mot de passe
`cabinet brcg douala 2026`, et trois d'entre eux **doivent** échouer à la
connexion — suspendu, jamais activé, inexistant — avec le même message, pour ne
pas rouvrir l'oracle d'énumération.
