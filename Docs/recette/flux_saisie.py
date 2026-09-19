"""Le parcours E : saisir une écriture, la valider, la contre-passer.

─────────────────────────────────────────────────────────────────────────────────
CE QUE CE SCRIPT ÉTABLIT, ET QU'AUCUN TEST UNITAIRE N'ÉTABLIT

Que le cabinet peut **produire**. Jusqu'à cet écran, l'espace de travail était en
lecture seule : seize écrans, une seule action serveur — la connexion. L'API
savait écrire depuis longtemps, et aucune de ses trente routes d'écriture n'était
atteignable autrement qu'en ligne de commande.

Le formulaire est donc soumis **comme le ferait un navigateur sans JavaScript** :
`multipart/form-data`, champs cachés relus dans la page, y compris la référence
d'action serveur de Next. C'est la seule façon de prouver que la chaîne entière
tient — écran, action serveur, témoin de session, API, base — et c'est là que
vivent les défauts que les tests d'unité ne voient pas.

⚠️ TROIS DÉFAUTS ONT ÉTÉ TROUVÉS EN ÉCRIVANT CE SCRIPT, DONT UN DE L'OUTIL

1. **L'API tournait sans les routes d'écriture.** Le formulaire recevait un
   « Method Not Allowed » et l'affichait proprement. Rien n'était cassé : le
   serveur n'avait pas été redémarré. Le symptôme est indiscernable d'un défaut
   de produit, d'où cette note.
2. **Le type `Ecriture` du front décrivait des champs qui n'existent pas.** Il
   déclarait `debit` et `credit` par ligne, quand l'API rend `sens` et `montant`.
   Personne ne l'avait exécuté : le compilateur ne pouvait rien dire, et le
   premier écran à s'en servir affichait des montants vides.
3. **Mon propre lecteur de formulaire postait la mauvaise action.** L'écran porte
   plusieurs formulaires ; lire les champs cachés de la page entière fait gagner
   la référence d'action du dernier. La soumission validait donc une écriture
   existante au lieu d'en créer une, sans le moindre message. Voir `_formulaire`
   — c'est le cinquième piège du `README.md`.

USAGE

    python Docs/recette/flux_saisie.py

Code de sortie 1 si une étape échoue.
─────────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verifier_profils import Client, champs_caches

FRONT = "http://localhost:3011"
API = "http://127.0.0.1:8010"
MOT_DE_PASSE = "cabinet brcg douala 2026"
EXERCICE = "2026"

COMPTABLE = "l.fotso@cga-brcg.cm"
CLIENTELE = "p.moukouri@cga-brcg.cm"
ADHERENT = "jp.nkoa@batimentplus.cm"

#: AGRO-NKOLO SA, au portefeuille de L. FOTSO.
DOSSIER = "M065544332211L"


def api(client: Client | None, methode: str, chemin: str, corps: dict | None = None):
    donnees = json.dumps(corps).encode() if corps is not None else None
    entetes = {"Accept": "application/json"}
    if corps is not None:
        entetes["Content-Type"] = "application/json"
    if client is not None and client.temoins:
        entetes["Cookie"] = "; ".join(f"{c}={v}" for c, v in client.temoins.items())
    requete = urllib.request.Request(API + chemin, data=donnees, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            brut = reponse.read().decode()
            return reponse.status, (json.loads(brut) if brut else None)
    except urllib.error.HTTPError as erreur:
        brut = erreur.read().decode()
        try:
            return erreur.code, json.loads(brut)
        except json.JSONDecodeError:
            return erreur.code, brut[:200]


_SESSIONS: dict[str, Client] = {}


def session(adresse: str) -> Client:
    """Une session par compte : le limiteur refuse au-delà de 30 connexions / 5 min."""
    if adresse not in _SESSIONS:
        client = Client()
        _, page, _ = client.lire("/connexion")
        champs = champs_caches(page)
        champs["courriel"] = adresse
        champs["motDePasse"] = MOT_DE_PASSE
        client.soumettre("/connexion", champs)
        _SESSIONS[adresse] = client
    return _SESSIONS[adresse]


def ecritures(client: Client) -> list[dict]:
    _, corps = api(client, "GET", f"/comptabilite/dossiers/{DOSSIER}/ecritures?exercice={EXERCICE}")
    return corps if isinstance(corps, list) else []


def _echec_affiche(page: str) -> str | None:
    trouve = re.search(r'class="saisie__echec"[^>]*>([^<]{0,300})', page)
    return trouve.group(1).strip() if trouve else None


def _formulaire(page: str, marqueur: str) -> str:
    """Isole le formulaire qui contient `marqueur`.

    ─────────────────────────────────────────────────────────────────────────
    ⚠️ LE PIÈGE QUI M'A FAIT VALIDER UNE ÉCRITURE EN CROYANT EN SAISIR UNE

    `champs_caches` lit la page **entière**. L'écran de saisie porte plusieurs
    formulaires : celui de la saisie, et un par écriture listée en dessous, pour
    la valider ou la contre-passer. Chacun a sa propre référence d'action
    serveur dans un champ caché, et la dernière lue écrase les précédentes.

    Résultat observé : la soumission part avec la référence de l'action
    « valider », le journal ne gagne aucune écriture, et un brouillon existant
    passe en validé. Aucune erreur, aucun message : le formulaire répond 200 et
    l'on conclut que la saisie ne fonctionne pas.

    Un navigateur, lui, n'envoie que les champs du formulaire soumis. Cette
    fonction rétablit ce périmètre, et c'est un défaut de l'outil de recette,
    jamais du produit.
    ─────────────────────────────────────────────────────────────────────────
    """
    fin = page.index(marqueur)
    debut = page.rindex("<form", 0, fin)
    ferme = page.index("</form>", fin)
    return page[debut:ferme]


def soumettre_une_ecriture(client: Client, lignes: list[tuple[str, str, str, str]], **entete):
    """Remplit le vrai formulaire et le poste, comme un navigateur sans script.

    ⚠️ `champs_caches` ne relève que les `<input>`. Le journal et le sens de
    chaque ligne sont des `<select>` : il faut les poser à la main, sinon le
    formulaire part sans journal et le refus qu'on observe n'est pas celui qu'on
    croit tester.
    """
    _, page, _ = client.lire("/comptabilite/saisie")
    champs = champs_caches(_formulaire(page, "saisie__lignes"))
    champs["journal"] = entete.get("journal", "AC")
    champs["date_operation"] = entete.get("date_operation", str(date(2026, 8, 18)))
    champs["libelle"] = entete.get("libelle", "Recette : achat de fournitures")
    champs["piece_justificative"] = entete.get("piece", "PJ-RECETTE")
    for rang in range(8):
        champs[f"sens-{rang}"] = "DEBIT"
    for rang, (compte, libelle, sens, montant) in enumerate(lignes):
        champs[f"compte-{rang}"] = compte
        champs[f"libelle-{rang}"] = libelle
        champs[f"sens-{rang}"] = sens
        champs[f"montant-{rang}"] = montant
    return client.soumettre("/comptabilite/saisie", champs)


ACHAT = [
    ("604", "Fournitures de bureau", "DEBIT", "150000"),
    ("401", "Fournisseur BUROTIC", "CREDIT", "150000"),
]


# ══ Les étapes ════════════════════════════════════════════════════════════════
def etape_ecran_reserve() -> tuple[bool, str]:
    """L'écran de saisie exige `SAISIR_ECRITURE`, pas la simple lecture.

    Le chargé de clientèle lit la comptabilité et ne saisit pas. Lui ouvrir le
    formulaire produirait un envoi refusé en 403 : un bouton qui échoue est pire
    qu'un bouton absent.
    """
    ouvert = "saisie__lignes" in session(COMPTABLE).lire("/comptabilite/saisie")[1]
    refuses = {
        role: "Accès réservé" in session(adresse).lire("/comptabilite/saisie")[1]
        for role, adresse in (("chargé de clientèle", CLIENTELE), ("adhérent", ADHERENT))
    }
    return ouvert and all(refuses.values()), (
        "comptable : formulaire rendu ; " + ", ".join(f"{r} : refusé" for r in refuses)
    )


def etape_saisie_sans_javascript() -> tuple[bool, str]:
    """LE TEST QUI PORTE TOUT LE RESTE.

    Le formulaire est posté en `multipart/form-data`, sans une ligne de script.
    Si cette étape passe, un cabinet peut tenir sa comptabilité.
    """
    client = session(COMPTABLE)
    avant = len(ecritures(client))
    _, page, _ = soumettre_une_ecriture(client, ACHAT)
    echec = _echec_affiche(page)
    apres = ecritures(client)
    gagnee = len(apres) - avant
    if echec:
        return False, f"le formulaire a refusé : {echec}"
    derniere = apres[-1] if apres else {}
    return gagnee == 1 and derniere.get("etat") == "BROUILLON", (
        f"{avant} → {len(apres)} écritures ; "
        f"{derniere.get('journal')} n° {derniere.get('numero')} en {derniere.get('etat')}"
    )


def etape_ecriture_relisible() -> tuple[bool, str]:
    """Ce qui a été saisi doit se relire tel quel, ligne par ligne.

    C'est la vérification qui a démasqué le type faux : l'écriture était bien
    enregistrée, et l'écran affichait des montants vides parce qu'il lisait des
    champs qui n'existaient pas.
    """
    derniere = ecritures(session(COMPTABLE))[-1]
    lignes = derniere.get("lignes", [])
    formees = all(
        set(ligne) >= {"compte", "libelle", "sens", "montant"} and ligne["montant"]
        for ligne in lignes
    )
    debits = sum(float(ligne["montant"]) for ligne in lignes if ligne["sens"] == "DEBIT")
    credits = sum(float(ligne["montant"]) for ligne in lignes if ligne["sens"] == "CREDIT")
    return formees and debits == credits and debits > 0, (
        f"{len(lignes)} lignes, débit {debits:.0f} = crédit {credits:.0f}, "
        "chacune porte compte, libellé, sens et montant"
    )


def etape_equilibre_refuse() -> tuple[bool, str]:
    """Une écriture déséquilibrée est refusée, et le refus se lit à l'écran.

    Le compteur du navigateur ne bloque rien : c'est le backend qui juge, et son
    verdict revient au comptable en toutes lettres.
    """
    client = session(COMPTABLE)
    avant = len(ecritures(client))
    _, page, _ = soumettre_une_ecriture(
        client,
        [("604", "Fournitures", "DEBIT", "150000"), ("401", "Fournisseur", "CREDIT", "140000")],
        libelle="Recette : écriture bancale",
    )
    echec = _echec_affiche(page)
    inchange = len(ecritures(client)) == avant
    return bool(echec) and "quilibr" in (echec or "") and inchange, (
        f"refus affiché : « {(echec or 'aucun')[:80]} » ; journal inchangé : {inchange}"
    )


def etape_compte_hors_plan_refuse() -> tuple[bool, str]:
    """Un compte absent du plan ne s'ouvre pas par faute de frappe.

    Un plan qui s'enrichit tout seul produit des comptes jumeaux — 601 et 6011 —
    dont la balance ne fait plus la somme, et personne ne s'en aperçoit avant la
    clôture.
    """
    client = session(COMPTABLE)
    avant = len(ecritures(client))
    _, page, _ = soumettre_une_ecriture(
        client,
        [("60199", "Achat", "DEBIT", "1000"), ("401", "Fournisseur", "CREDIT", "1000")],
        libelle="Recette : compte inventé",
    )
    echec = _echec_affiche(page) or ""
    return "60199" in echec and len(ecritures(client)) == avant, (
        f"refus nommant le compte : « {echec[:90]} »"
    )


def etape_validation() -> tuple[bool, str]:
    """Valider engage l'écriture, qui devient immuable et nomme son valideur."""
    client = session(COMPTABLE)
    brouillon = next(
        (e for e in reversed(ecritures(client)) if e["etat"] == "BROUILLON"), None
    )
    if brouillon is None:
        return False, "aucun brouillon à valider"
    cle = f"{brouillon['exercice']}/{brouillon['journal']}/{brouillon['numero']}"
    code, corps = api(
        client, "POST", f"/comptabilite/dossiers/{DOSSIER}/ecritures/{cle}/validation"
    )
    if code != 200 or not isinstance(corps, dict):
        return False, f"HTTP {code}"
    rejoue, _ = api(
        client, "POST", f"/comptabilite/dossiers/{DOSSIER}/ecritures/{cle}/validation"
    )
    return corps["etat"] == "VALIDEE" and bool(corps["validee_par"]) and rejoue == 409, (
        f"{cle} validée par {corps['validee_par']} ; seconde validation refusée en {rejoue}"
    )


def etape_contrepassation() -> tuple[bool, str]:
    """L'annulation passe par l'inverse, motivée, datée du jour du constat.

    ⚠️ Un motif vide reçoit **403 et non 409** : `CONTRE_PASSER` figure parmi les
    actes qui se justifient, et le contrôle d'accès refuse avant que le domaine
    ne voie l'acte.
    """
    client = session(COMPTABLE)
    validee = next((e for e in reversed(ecritures(client)) if e["etat"] == "VALIDEE"), None)
    if validee is None:
        return False, "aucune écriture validée à contre-passer"
    cle = f"{validee['exercice']}/{validee['journal']}/{validee['numero']}"
    chemin = f"/comptabilite/dossiers/{DOSSIER}/ecritures/{cle}/contre-passation"

    sans_motif, _ = api(client, "POST", chemin, {"motif": "   "})
    code, inverse = api(client, "POST", chemin, {"motif": "Facture reçue en double"})
    if code != 201 or not isinstance(inverse, dict):
        return False, f"HTTP {code} — {inverse}"

    origine_debits = {ligne["compte"]: ligne["sens"] for ligne in validee["lignes"]}
    inversee = all(
        ligne["sens"] != origine_debits.get(ligne["compte"], ligne["sens"])
        for ligne in inverse["lignes"]
    )
    _, relue = api(client, "GET", f"/comptabilite/dossiers/{DOSSIER}/ecritures/{cle}")
    intacte = isinstance(relue, dict) and relue.get("etat") == "VALIDEE"
    return sans_motif == 403 and inversee and intacte, (
        f"motif vide {sans_motif} ; inverse {inverse['journal']} n° {inverse['numero']} "
        f"en {inverse['etat']} ; l'originale demeure validée : {intacte}"
    )


def etape_adherent_ne_saisit_pas() -> tuple[bool, str]:
    """LE REFUS QUI PROTÈGE L'AGRÉMENT.

    Un centre de gestion agréé engage son agrément sur les comptes qu'il produit.
    Laisser l'adhérent écrire dans son propre journal ferait du cabinet le témoin
    de ses écritures plutôt que leur auteur.
    """
    corps = {
        "journal": "AC",
        "exercice": EXERCICE,
        "date_operation": "2026-08-18",
        "libelle": "Tentative",
        "lignes": [
            {"compte": "604", "libelle": "X", "sens": "DEBIT", "montant": "1000"},
            {"compte": "401", "libelle": "Y", "sens": "CREDIT", "montant": "1000"},
        ],
    }
    sien = "M081234567890P"
    code, detail = api(
        session(ADHERENT), "POST", f"/comptabilite/dossiers/{sien}/ecritures", corps
    )
    nomme = "SAISIR_ECRITURE" in str(detail)
    return code == 403 and nomme, f"HTTP {code}, permission nommée dans le refus : {nomme}"


ETAPES = [
    ("L'écran n'ouvre qu'à qui peut saisir", etape_ecran_reserve),
    ("Le formulaire enregistre sans JavaScript", etape_saisie_sans_javascript),
    ("L'écriture se relit ligne par ligne", etape_ecriture_relisible),
    ("Une écriture déséquilibrée est refusée", etape_equilibre_refuse),
    ("Un compte hors plan est refusé", etape_compte_hors_plan_refuse),
    ("La validation engage et fige", etape_validation),
    ("La contre-passation annule sans effacer", etape_contrepassation),
    ("L'adhérent n'écrit pas dans son journal", etape_adherent_ne_saisit_pas),
]


def main() -> int:
    print()
    print("  PARCOURS E · SAISIE COMPTABLE".center(96))
    print(f"  front {FRONT}   ·   API {API}   ·   dossier {DOSSIER}")
    print("─" * 96)
    echecs = 0
    for intitule, etape in ETAPES:
        try:
            ok, constat = etape()
        except Exception as erreur:  # noqa: BLE001 — une étape qui explose est un résultat
            ok, constat = False, f"exception : {type(erreur).__name__} {erreur}"
        echecs += not ok
        print(f"{'✓' if ok else '✗'} {intitule:<48} {constat}")
    print("─" * 96)
    verdict = "PARCOURS COMPLET" if echecs == 0 else f"{echecs} ÉTAPE(S) EN ÉCHEC"
    print(f"  {len(ETAPES) - echecs}/{len(ETAPES)} — {verdict}")
    print()
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
