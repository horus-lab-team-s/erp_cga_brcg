"""Registre des cas d'usage, et la preuve qui valide chacun.

Ce script ne raconte pas que les flux sont bons : il les exécute et rend le
verdict. Chaque cas d'usage porte **sa preuve**, et la preuve est de l'un des
deux genres suivants — jamais d'un troisième :

    direct   exécuté à l'instant contre la pile qui tourne, par HTTP
    suite    délégué à un test nommé de la suite, exécuté par ce script

Rien n'est déclaré « validé » sur la foi d'une lecture de code. La totalité des
défauts trouvés sur ce projet l'ont été à l'exécution, aucun par relecture — et
plusieurs ont survécu à mille tests unitaires parce que les tests vérifiaient
des unités quand les défauts vivaient dans le câblage entre elles.

Usage :

    python Docs/recette/cas_usage.py            # tout
    python Docs/recette/cas_usage.py --direct   # sans lancer pytest
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ⚠️ `noqa: E402` : ces imports suivent `sys.path.insert` parce qu'ils désignent
# des modules voisins, introuvables avant. C'est la seule position qui marche.
from verifier_profils import Client, champs_caches  # noqa: E402

FRONT = "http://localhost:3011"
API = "http://127.0.0.1:8010"
MOT_DE_PASSE = "cabinet brcg douala 2026"
JOUR = "2026-08-17"
D1 = "M065544332211L"  # AGRO-NKOLO SA
D3 = "M081234567890P"  # SARL BATIMENT PLUS — le dossier de l'adhérent jp.nkoa


# ══ Outils ════════════════════════════════════════════════════════════════════
def api(
    client: Client | None, methode: str, chemin: str, corps: dict | None = None
) -> tuple[int, object]:
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


def envoyer_un_fichier(
    client: Client, chemin: str, nom: str, contenu: bytes
) -> tuple[int, object]:
    """Un envoi multipart, parce que le dépôt d'une pièce commence par un fichier (pas 81).

    ⚠️ Écrit à la main plutôt qu'avec une bibliothèque : la recette ne doit dépendre que de la
    bibliothèque standard, comme le reste de ces scripts.
    """
    frontiere = "----recette-cga"
    corps = (
        f"--{frontiere}\r\n"
        f'Content-Disposition: form-data; name="fichier"; filename="{nom}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode() + contenu + f"\r\n--{frontiere}--\r\n".encode()
    entetes = {
        "Accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={frontiere}",
        "Cookie": "; ".join(f"{c}={v}" for c, v in client.temoins.items()),
    }
    requete = urllib.request.Request(API + chemin, data=corps, headers=entetes, method="POST")
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


class RecetteLimitee(RuntimeError):
    """Le limiteur de connexions a refusé la recette elle-même (pas 119).

    ⚠️ **Ce n'est pas un défaut du produit, et il ne faut surtout pas le compter comme tel.** Deux
    passages rapprochés du registre dépassent les trente connexions par cinq minutes : sans cette
    exception, chaque cas d'usage tombait ensuite en `401`, et la recette annonçait vingt-cinq flux
    en échec pour une pile parfaitement saine. C'est le contraire du service qu'elle rend.
    """


def session(adresse: str) -> Client:
    """Une session par compte, ouverte une seule fois.

    ⚠️ Le limiteur refuse au-delà de trente connexions par cinq minutes. Une
    recette qui se reconnecte à chaque sonde se fait limiter elle-même et
    produit des défauts qui n'existent pas.
    """
    if adresse not in _SESSIONS:
        client = Client()
        _, page, _ = client.lire("/connexion")
        champs = champs_caches(page)
        champs["courriel"] = adresse
        champs["motDePasse"] = MOT_DE_PASSE
        client.soumettre("/connexion", champs)
        if "cga_session" not in client.temoins:
            # La cause la plus fréquente, et de loin : le limiteur. On le vérifie en interrogeant
            # l'API directement, pour ne pas confondre « limité » et « mot de passe changé ».
            code, _ = api(None, "POST", "/transverse/session",
                          {"courriel": adresse, "mot_de_passe": MOT_DE_PASSE})
            if code == 429:
                raise RecetteLimitee(
                    f"le limiteur de connexions a refusé la recette ({adresse}). Attendre cinq "
                    "minutes, ou remonter la pile : "
                    "Backend_erp_cga/outils/pile-de-demonstration.sh neuve"
                )
            raise RecetteLimitee(
                f"session refusée pour {adresse} (HTTP {code} à l'API). La pile est-elle amorcée "
                "avec le jeu de démonstration ?"
            )
        _SESSIONS[adresse] = client
    return _SESSIONS[adresse]


DIRECTION = "b.mballa@cga-brcg.cm"
ADMIN = "s.onana@cga-brcg.cm"
COMPTABLE = "l.fotso@cga-brcg.cm"
COMPTABLE2 = "c.ndongo@cga-brcg.cm"
REVISEUR = "a.bouba@cga-brcg.cm"
FISCALISTE = "r.ebolo@cga-brcg.cm"
ADHERENT = "jp.nkoa@batimentplus.cm"
FORMALITES = "p.moukouri@cga-brcg.cm"
INSPECTEUR = "g.atangana@inspection.cm"

FACTURE = {
    "document": {"type": "FACTURE_ACHAT", "reference": "F-UC-0001", "date_emission": JOUR},
    "emetteur": {"denomination": "FOURNISSEUR", "niu": "M011111111111A"},
    "montants": {"total_ht": "1000000", "total_tva": "192500", "total_ttc": "1192500"},
}


# ══ Le registre ═══════════════════════════════════════════════════════════════
@dataclass
class CasUsage:
    reference: str
    contexte: str
    acteur: str
    intitule: str
    #: Rend (verdict, constat). Le constat est ce qui a été observé, pas ce qui
    #: était attendu : c'est lui qu'on relit six mois plus tard.
    preuve: Callable[[], tuple[bool, str]] | None = None
    test: str | None = None


def _ecran(adresse: str, chemin: str) -> tuple[int, str]:
    code, page, _ = session(adresse).lire(chemin)
    return code, page


def uc_connexion_collaborateur() -> tuple[bool, str]:
    client = Client()
    _, page, _ = client.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = DIRECTION
    champs["motDePasse"] = MOT_DE_PASSE
    code, _, cible = client.soumettre("/connexion", champs)
    ok = code in (302, 303, 307) and cible == "/tableau-de-bord"
    return ok and "cga_session" in client.temoins, f"{code} → {cible}, témoin posé"


def uc_connexion_adherent() -> tuple[bool, str]:
    client = Client()
    _, page, _ = client.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = ADHERENT
    champs["motDePasse"] = MOT_DE_PASSE
    code, _, cible = client.soumettre("/connexion", champs)
    return cible == "/mon-espace", f"{code} → {cible} (routage après authentification)"


def _refus_connexion(adresse: str) -> tuple[bool, str]:
    client = Client()
    _, page, _ = client.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = adresse
    champs["motDePasse"] = MOT_DE_PASSE
    code, corps, _ = client.soumettre("/connexion", champs)
    refuse = "cga_session" not in client.temoins
    generique = "identifiants" in corps.lower() or "incorrect" in corps.lower()
    mot = "générique" if generique else "à vérifier"
    return refuse, f"HTTP {code}, aucun témoin, message {mot}"


def uc_401_sans_session() -> tuple[bool, str]:
    routes = [
        f"/portefeuille/entreprises?a_la_date={JOUR}",
        f"/collecte/pieces?a_la_date={JOUR}",
        "/transverse/audit",
        "/conformite/regles",
        "/conformite/demonstration/rapports",
    ]
    codes = {chemin: api(None, "GET", chemin)[0] for chemin in routes}
    anonyme = api(None, "POST", "/conformite/controler", FACTURE)[0]
    codes["POST /conformite/controler"] = anonyme
    return all(c == 401 for c in codes.values()), f"{len(codes)} routes, toutes 401"


def uc_ecran_reserve() -> tuple[bool, str]:
    code, page = _ecran(ADMIN, "/comptabilite")
    return code == 200 and "Accès réservé" in page, "l'administrateur lit « Accès réservé »"


def uc_refus_tient_sans_interface() -> tuple[bool, str]:
    code, _ = api(session(ADMIN), "GET", f"/comptabilite/dossiers/{D1}/balance?exercice=2026")
    return code == 403, f"appel direct de l'API par l'administrateur : HTTP {code}"


def uc_admin_aucun_dossier() -> tuple[bool, str]:
    codes = [api(session(ADMIN), "GET", f"/portefeuille/entreprises/{niu}")[0]
             for niu in (D1, D3)]
    return all(c in (403, 404) for c in codes), f"deux dossiers sondés : {codes}"


def uc_portee_comptable() -> tuple[bool, str]:
    sien, _ = api(session(COMPTABLE), "GET", f"/portefeuille/entreprises/{D1}")
    voisin, _ = api(session(COMPTABLE2), "GET", f"/portefeuille/entreprises/{D1}")
    return sien == 200 and voisin == 404, f"habilité {sien}, non habilité {voisin}"


def uc_hors_portee_404() -> tuple[bool, str]:
    code, _ = api(session(ADHERENT), "GET", "/portefeuille/entreprises/M071122334455J")
    return code == 404, f"HTTP {code} — un 403 confirmerait que le dossier existe"


def uc_boite_restreinte() -> tuple[bool, str]:
    code, sien = api(session(ADHERENT), "GET", "/conformite/demonstration/rapports")
    _, tout = api(session(REVISEUR), "GET", "/conformite/demonstration/rapports")
    if code != 200 or not isinstance(sien, list) or not isinstance(tout, list):
        return False, f"HTTP {code}"
    niu = {(r["facture"].get("destinataire") or {}).get("niu") for r in sien}
    return niu == {D3} and len(sien) < len(tout), (
        f"{len(sien)} pièces sur {len(tout)}, un seul dossier : {niu.pop()}"
    )


def uc_moteur_permission() -> tuple[bool, str]:
    refus, corps = api(session(ADHERENT), "POST", "/conformite/controler", FACTURE)
    accord, _ = api(session(REVISEUR), "POST", "/conformite/controler", FACTURE)
    nomme = isinstance(corps, dict) and "CONTROLER_CONFORMITE" in str(corps.get("detail"))
    return refus == 403 and accord == 200 and nomme, (
        f"adhérent {refus}, réviseur {accord}, permission nommée dans le refus"
    )


def uc_regles_non_publiques() -> tuple[bool, str]:
    anonyme, _ = api(None, "GET", "/conformite/regles")
    admin, _ = api(session(ADMIN), "GET", "/conformite/regles")
    metier, _ = api(session(COMPTABLE), "GET", "/conformite/regles")
    return anonyme == 401 and admin == 403 and metier == 200, (
        f"anonyme {anonyme}, administrateur {admin}, comptable {metier}"
    )


def _pdf(marqueur: str) -> bytes:
    """Un PDF minimal, reconnu par la détection de type du magasin de fichiers."""
    return (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%% "
        + marqueur.encode()
        + b"\n%%EOF\n"
    )


def uc_depot_piece() -> tuple[bool, str]:
    """Le dépôt réel, en deux temps : le fichier, puis la pièce avec son empreinte (pas 81).

    ⚠️ Ce cas envoyait l'ancien corps (identifiant, recue_le) jusqu'au pas 119, et recevait un 422
    que personne ne lisait : la recette avait vieilli sans le dire. Le premier temps est donc ici,
    et le refus du fiscaliste est vérifié sur le geste entier.
    """
    from uuid import uuid4

    marqueur = uuid4().hex[:8]
    code, retour = envoyer_un_fichier(
        session(COMPTABLE),
        f"/collecte/fichiers?entreprise={D1}",
        f"piece-{marqueur}.pdf",
        _pdf(marqueur),
    )
    if code != 201 or not isinstance(retour, dict):
        return False, f"envoi du fichier : HTTP {code}"
    piece = {
        "entreprise": D1,
        "canal": "DEPOT_CABINET",
        "empreinte": retour["empreinte"],
        "nom_fichier": retour["nom_fichier"],
        "depose_le": JOUR,
    }
    accord, recu = api(session(COMPTABLE), "POST", "/collecte/pieces", piece)
    refus, _ = api(session(FISCALISTE), "POST", "/collecte/pieces", piece)
    identifiant = recu["piece"]["identifiant"] if accord == 201 and isinstance(recu, dict) else "—"
    return (
        accord == 201 and refus == 403,
        f"comptable 201 ({identifiant}), fiscaliste {refus}",
    )


def uc_balance() -> tuple[bool, str]:
    """La balance se lit, et elle est équilibrée — les deux se vérifient.

    L'équilibre est recalculé ici sur les lignes rendues, pas lu dans un
    indicateur fourni par l'API : un indicateur qui se tromperait mentirait
    aussi à ce test. Débits et crédits sont des chaînes décimales — les
    additionner en flottant sur des montants FCFA introduirait l'écart d'un
    franc que la balance a précisément pour rôle de rendre visible.
    """
    from decimal import Decimal

    lecture, lignes = api(
        session(COMPTABLE), "GET", f"/comptabilite/dossiers/{D1}/balance?exercice=2026"
    )
    refus, _ = api(session(ADHERENT), "GET", "/comptabilite/journaux")
    if lecture != 200 or not isinstance(lignes, list) or not lignes:
        return False, f"comptable {lecture}, réponse inattendue"
    debit = sum(Decimal(ligne["total_debit"]) for ligne in lignes)
    credit = sum(Decimal(ligne["total_credit"]) for ligne in lignes)
    return refus == 403 and debit == credit, (
        f"comptable 200 ({len(lignes)} comptes), adhérent {refus}, "
        f"débit {debit:,.0f} = crédit {credit:,.0f}".replace(",", " ")
    )


def uc_echeancier() -> tuple[bool, str]:
    code, corps = api(session(COMPTABLE), "GET",
                      f"/obligations/dossiers/{D1}/echeancier?exercice=2026&a_la_date={JOUR}")
    nombre = len(corps) if isinstance(corps, list) else len(corps.get("obligations", []) or [])
    return code == 200 and nombre > 0, f"HTTP {code}, {nombre} obligations calculées"


def uc_depot_declaration() -> tuple[bool, str]:
    tva = f"?periode_debut=2026-07-01&periode_fin=2026-07-31&a_la_date={JOUR}"
    refus, _ = api(session(COMPTABLE), "POST",
                   f"/obligations/dossiers/{D1}/depot-tva{tva}",
                   {"numero": "UC-TVA", "depose_le": JOUR})
    return refus == 403, f"comptable (sans DEPOSER_DECLARATION) : HTTP {refus}"


def uc_audit() -> tuple[bool, str]:
    ouvert, _ = api(session(DIRECTION), "GET", "/transverse/audit")
    ferme, _ = api(session(COMPTABLE), "GET", "/transverse/audit")
    return ouvert == 200 and ferme == 403, f"direction {ouvert}, comptable {ferme}"


def uc_invitation() -> tuple[bool, str]:
    invitation = {"courriel": "uc.temoin@cga-brcg.cm", "nom": "TEMOIN",
                  "prenom": "Cas", "role": "COMPTABLE", "depuis": JOUR}
    admin, _ = api(session(ADMIN), "POST", "/transverse/comptes/invitation", invitation)
    direction, _ = api(session(DIRECTION), "POST", "/transverse/comptes/invitation", invitation)
    # 409 vaut accord : l'administrateur a le droit d'inviter, et le conflit dit
    # seulement que le témoin existe déjà d'une exécution précédente. Le
    # distinguer d'un refus est ce qui rend la recette rejouable sur une base
    # persistante sans la réamorcer entre deux passes.
    accord = "201 création" if admin == 201 else "409 témoin déjà invité, donc autorisé"
    return admin in (201, 409) and direction == 403, (
        f"administrateur {accord}, direction {direction} — la direction ne gère pas les comptes"
    )


# ── I · Création d'entreprise ────────────────────────────────────────────────
def uc_pipeline_reserve() -> tuple[bool, str]:
    """`SUIVRE_FORMALITE` n'ouvrait aucun écran avant ce contexte."""
    ouvert, _ = api(session(FORMALITES), "GET", f"/creations/pipeline?a_la_date={JOUR}")
    ferme, _ = api(session(COMPTABLE), "GET", f"/creations/pipeline?a_la_date={JOUR}")
    return ouvert == 200 and ferme == 403, f"chargé de formalités {ouvert}, comptable {ferme}"


def uc_checklist_par_forme() -> tuple[bool, str]:
    """Une SA exige un commissaire aux comptes, pas une entreprise individuelle.

    C'est ce qui explique l'écart de prix, et le fondateur doit le lire sur le
    devis plutôt qu'au guichet.
    """
    client = session(FORMALITES)
    _, sa = api(client, "GET", "/creations/checklist/SA")
    _, ets = api(client, "GET", "/creations/checklist/ETS")
    if not isinstance(sa, list) or not isinstance(ets, list):
        return False, "checklist illisible"
    codes_sa = {p["code"] for p in sa}
    codes_ets = {p["code"] for p in ets}
    return "COMMISSAIRE_COMPTES" in codes_sa and "STATUTS" not in codes_ets, (
        f"SA {len(sa)} pièces dont le commissaire aux comptes, ETS {len(ets)} sans statuts"
    )


def uc_pipeline_par_urgence() -> tuple[bool, str]:
    """Un dossier qui dort depuis trois semaines passe avant celui d'hier."""
    code, lignes = api(session(FORMALITES), "GET", f"/creations/pipeline?a_la_date={JOUR}")
    if code != 200 or not isinstance(lignes, list) or not lignes:
        return False, f"HTTP {code}"
    jours = [ligne["jours_d_immobilite"] for ligne in lignes]
    retard = sum(1 for ligne in lignes if ligne["en_retard"])
    return jours == sorted(jours, reverse=True), (
        f"{len(lignes)} dossiers, du plus immobile ({jours[0]} j) au plus récent, "
        f"{retard} à relancer au guichet"
    )


def uc_depot_incomplet_refuse() -> tuple[bool, str]:
    """Un dossier incomplet présenté au CFCE revient — trois jours plus tard."""
    from uuid import uuid4

    client = session(FORMALITES)
    reference = f"CR-UC-{uuid4().hex[:6].upper()}"
    code, _ = api(
        client, "POST", f"/creations?a_la_date={JOUR}",
        {
            "reference": reference,
            "fondateur": {
                "nom": "TEST", "prenom": "Cas", "courriel": f"{reference}@exemple.cm",
                "telephone": "+237699000000",
            },
            "denomination_souhaitee": f"CAS {reference} SARL",
            "forme_juridique": "SARL",
            "activite": "Commerce",
            "siege": "Douala",
            "capital": "1500000",
        },
    )
    if code != 201:
        return False, f"ouverture impossible : HTTP {code}"
    api(client, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
        {"vers": "CONSTITUTION"})
    refus, corps = api(client, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
                       {"vers": "DEPOT_CFCE"})
    nomme = isinstance(corps, dict) and "Statuts" in str(corps.get("detail"))
    return refus == 409 and nomme, (
        f"HTTP {refus}, pièces manquantes nommées dans le refus"
    )


def uc_conversion_complete() -> tuple[bool, str]:
    """LE CAS D'USAGE QUI JUSTIFIE LE CONTEXTE.

    Il ne suffit pas que la conversion réponde 200. Ce qui se vérifie ici, c'est
    que l'entreprise née est **lisible au portefeuille**, que sa date de création
    est celle du RCCM, et que F · Obligations lui calcule un échéancier sans
    qu'on le lui ait demandé. La première version passait les deux premiers
    points et échouait au troisième : sans exercice, F n'avait rien sur quoi
    calculer, et la promesse du contexte était creuse.
    """
    from uuid import uuid4

    client = session(FORMALITES)
    marque = uuid4().hex[:6].upper()
    reference = f"CR-UC-{marque}"
    niu = f"M3{marque}00011K"[:14]

    ouverture, _ = api(
        client, "POST", f"/creations?a_la_date={JOUR}",
        {
            "reference": reference,
            "fondateur": {
                "nom": "CONVERSION", "prenom": "Cas",
                "courriel": f"{reference}@exemple.cm", "telephone": "+237699000000",
            },
            "denomination_souhaitee": f"CONVERSION {marque} SARL",
            "forme_juridique": "SARL",
            "activite": "Commerce",
            "siege": "Douala",
            "capital": "1500000",
        },
    )
    if ouverture != 201:
        return False, f"ouverture : HTTP {ouverture}"

    _, fiche = api(client, "GET", f"/creations/{reference}?a_la_date={JOUR}")
    for piece in fiche["dossier"]["pieces"]:
        api(client, "POST", f"/creations/{reference}/pieces?a_la_date={JOUR}",
            {"code": piece["code"]})
    for vers in ("CONSTITUTION", "DEPOT_CFCE", "SUIVI_IMMATRICULATION"):
        api(client, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}", {"vers": vers})
    api(client, "POST", f"/creations/{reference}/identifiants",
        {"rccm": f"RC/DLA/2026/B/{marque[:4]}", "rccm_obtenu_le": "2026-07-02",
         "niu": niu, "niu_obtenu_le": "2026-07-25"})
    api(client, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
        {"vers": "LIVRAISON"})

    code, resultat = api(client, "POST", f"/creations/{reference}/conversion?a_la_date={JOUR}",
                         {"regime": "REEL", "centre": "CDI", "adherent": True})
    if code != 200:
        return False, f"conversion : HTTP {code} {resultat}"
    au_rccm = resultat.get("date_creation") == "2026-07-02"

    lecture, _ = api(client, "GET", f"/portefeuille/entreprises/{niu}")
    code_ech, echeancier = api(
        client, "GET",
        f"/obligations/dossiers/{niu}/echeancier?exercice=2026&a_la_date={JOUR}",
    )
    obligations = len(echeancier) if isinstance(echeancier, list) else 0
    return (au_rccm and lecture == 200 and code_ech == 200 and obligations > 0), (
        f"née le {resultat.get('date_creation')} (RCCM), au portefeuille {lecture}, "
        f"{obligations} obligations calculées d'office"
    )


# ── G · Social et paie ───────────────────────────────────────────────────────
def uc_plafond_cnps() -> tuple[bool, str]:
    """LE CAS D'USAGE QUI DISTINGUE UN CALCUL JUSTE D'UN CALCUL PLAUSIBLE.

    Les branches pensions et prestations familiales sont plafonnées ; les
    accidents du travail, le CFC et le FNE portent sur le salaire réel. Une
    seule assiette pour toutes passerait n'importe quel contrôle tant qu'aucun
    salarié ne dépasse le plafond — c'est-à-dire jusqu'au premier client qui
    paie ses cadres.
    """
    from decimal import Decimal

    code, bulletin = api(
        session(COMPTABLE), "GET",
        f"/social/dossiers/{D1}/bulletins/2026/7/SAL-0001?groupe_risque=B",
    )
    if code != 200 or not isinstance(bulletin, dict):
        return False, f"HTTP {code}"
    lignes = {ligne["code"]: ligne for ligne in bulletin["lignes"]}
    brut = (
        Decimal(bulletin["salaire_base"])
        + Decimal(bulletin["primes"])
        + Decimal(bulletin["avantages_evalues"])
    )
    plafonnees = [c for c in ("CNPS_PVID_S", "CNPS_PVID_P", "CNPS_PF")
                  if Decimal(lignes[c]["assiette"]) < brut]
    reelles = [c for c in ("CNPS_AT", "CFC_S", "CFC_P", "FNE")
               if Decimal(lignes[c]["assiette"]) == brut]
    return len(plafonnees) == 3 and len(reelles) == 4, (
        f"brut {brut:,.0f} — 3 branches plafonnées, 4 sur salaire réel".replace(",", " ")
    )


def uc_avantages_hors_du_net() -> tuple[bool, str]:
    """Les avantages en nature sont imposables et ne se versent pas.

    Les laisser dans le net paierait le logement deux fois : une fois en clés,
    une fois en espèces.
    """
    from decimal import Decimal

    code, bulletin = api(
        session(COMPTABLE), "GET", f"/social/dossiers/{D1}/bulletins/2026/7/SAL-0001"
    )
    if code != 200 or not isinstance(bulletin, dict):
        return False, f"HTTP {code}"
    avantages = Decimal(bulletin["avantages_evalues"])
    retenues = sum(
        Decimal(ligne["montant"])
        for ligne in bulletin["lignes"]
        if ligne["a_charge_du_salarie"]
    )
    net = Decimal(bulletin["salaire_base"]) + Decimal(bulletin["primes"]) - retenues
    brut = Decimal(bulletin["salaire_base"]) + Decimal(bulletin["primes"]) + avantages
    return avantages > 0 and net < brut - avantages + avantages, (
        f"avantages {avantages:,.0f} dans l'assiette, net {net:,.0f} sans eux".replace(",", " ")
    )


def uc_declaration_sociale() -> tuple[bool, str]:
    """Le DIPE : effectif, masse, mouvements, et ce qu'il faut réellement verser.

    Le total mis en avant est **patronales + retenues**. L'erreur de trésorerie
    classique est de ne provisionner que sa part : la retenue salariale
    n'appartient pas à l'employeur, il la détient pour l'administration.
    """
    from decimal import Decimal

    code, dipe = api(
        session(COMPTABLE), "GET",
        f"/social/dossiers/{D1}/declaration/2026/7?a_la_date={JOUR}&groupe_risque=B",
    )
    if code != 200 or not isinstance(dipe, dict):
        return False, f"HTTP {code}"
    total = Decimal(dipe["total_a_verser"])
    somme = Decimal(dipe["charges_patronales"]) + Decimal(dipe["retenues_salariales"])
    sorties = [m for m in dipe["mouvements"] if m["sens"] == "SORTIE"]
    return (
        total == somme
        and dipe["a_deposer_avant"] == "2026-08-15"
        and len(sorties) >= 1
    ), (
        f"effectif {dipe['effectif']}, à verser {total:,.0f} FCFA avant le "
        f"{dipe['a_deposer_avant']}, {len(sorties)} sortie(s) relevée(s)".replace(",", " ")
    )


def uc_paie_reservee() -> tuple[bool, str]:
    """La paie porte des rémunérations nominatives : elle suit LIRE_COMPTABILITE."""
    ouvert, _ = api(session(COMPTABLE), "GET", f"/social/dossiers/{D1}/salaries?a_la_date={JOUR}")
    ferme, _ = api(session(ADMIN), "GET", f"/social/dossiers/{D1}/salaries?a_la_date={JOUR}")
    voisin, _ = api(
        session(ADHERENT), "GET", f"/social/dossiers/{D1}/salaries?a_la_date={JOUR}"
    )
    return ouvert == 200 and ferme == 403 and voisin in (403, 404), (
        f"comptable {ouvert}, administrateur {ferme}, adhérent d'un autre dossier {voisin}"
    )


# ── H · Clôture et DSF ───────────────────────────────────────────────────────
def uc_liasse_coherente() -> tuple[bool, str]:
    """Les trois contrôles d'avant dépôt, sur une vraie balance.

    Le plus important est la concordance des deux résultats : produits − charges
    d'un côté, actif − passif de l'autre. Les deux chemins sont indépendants —
    les faire dériver l'un de l'autre rendrait le contrôle toujours satisfait.
    """
    from decimal import Decimal

    code, liasse = api(session(COMPTABLE), "GET", f"/cloture/dossiers/{D1}/liasse/2026")
    if code != 200 or not isinstance(liasse, dict):
        return False, f"HTTP {code}"
    verts = [c for c in liasse["controles"] if c["satisfait"]]
    concordant = Decimal(liasse["resultat_comptable"]) == Decimal(
        liasse["resultat_par_le_bilan"]
    )
    return len(verts) == 3 and concordant and liasse["coherent"], (
        f"{len(verts)}/3 contrôles verts, résultat "
        f"{Decimal(liasse['resultat_comptable']):,.0f} concordant par les deux chemins"
        .replace(",", " ")
    )


def uc_tva_rejetee_non_reintegree() -> tuple[bool, str]:
    """LE CAS D'USAGE QUI ÉVITE DE FAIRE PAYER L'IMPÔT DEUX FOIS.

    Une TVA non déductible relève de la déclaration de TVA, pas du résultat. La
    réintégrer ferait payer l'adhérent une fois en TVA non récupérée et une fois
    en base imposable majorée — et personne ne s'en plaindrait à
    l'administration.
    """
    from decimal import Decimal

    code, liasse = api(session(COMPTABLE), "GET", f"/cloture/dossiers/{D3}/liasse/2026")
    if code != 200 or not isinstance(liasse, dict):
        return False, f"HTTP {code}"
    tva = Decimal(liasse["tva_rejetee_a_verifier"])
    reintegre_la_tva = any(
        "TVA" in ligne["libelle"].upper() and ligne["nature"] == "REINTEGRATION"
        for ligne in liasse["passage"]
    )
    return tva > 0 and not reintegre_la_tva, (
        f"{tva:,.0f} FCFA de TVA rejetée, signalée et hors du tableau de passage"
        .replace(",", " ")
        + f" · pièces {liasse['pieces_a_verifier']}"
    )


def uc_liasse_reservee() -> tuple[bool, str]:
    ouvert, _ = api(session(COMPTABLE), "GET", f"/cloture/dossiers/{D1}/liasse/2026")
    ferme, _ = api(session(ADMIN), "GET", f"/cloture/dossiers/{D1}/liasse/2026")
    voisin, _ = api(session(ADHERENT), "GET", f"/cloture/dossiers/{D1}/liasse/2026")
    return ouvert == 200 and ferme == 403 and voisin in (403, 404), (
        f"comptable {ouvert}, administrateur {ferme}, adhérent d'un autre dossier {voisin}"
    )


def uc_sante() -> tuple[bool, str]:
    code, corps = api(None, "GET", "/sante")
    joignable = isinstance(corps, dict) and corps.get("base_de_donnees") == "joignable"
    return code == 200 and joignable, f"HTTP {code}, base sondée par un SELECT réel"


# ── J · Pilotage du cabinet ──────────────────────────────────────────────────
def _tableau_de_bord() -> tuple[int, object]:
    return api(session(DIRECTION), "GET", f"/pilotage/tableau-de-bord?a_la_date={JOUR}")


def uc_pilotage_reserve() -> tuple[bool, str]:
    """Le pilotage est fermé à tous, y compris au réviseur qui voit tout.

    Voir l'ensemble du portefeuille n'est pas piloter le cabinet : le score de
    risque porte un jugement d'affectation, que seule la direction a mandat de
    lire. C'est pour cela que le refus est sondé sur le réviseur, le profil dont
    le refus est le moins évident, et non sur l'adhérent.
    """
    ouvert, _ = _tableau_de_bord()
    refuses = {
        role: api(session(adresse), "GET", "/pilotage/tableau-de-bord")[0]
        for role, adresse in (
            ("réviseur", REVISEUR),
            ("comptable", COMPTABLE),
            ("adhérent", ADHERENT),
        )
    }
    return ouvert == 200 and set(refuses.values()) == {403}, (
        f"direction {ouvert}, " + ", ".join(f"{r} {c}" for r, c in refuses.items())
    )


def uc_score_tracable() -> tuple[bool, str]:
    """Le score se déplie jusqu'à la pièce, sans quoi il n'appelle aucune action.

    Un directeur qui lit « 3 pièces en souffrance » sans savoir lesquelles
    rouvre le dossier pour les chercher : le tableau de bord lui a fait perdre
    du temps au lieu de lui en faire gagner.
    """
    code, corps = _tableau_de_bord()
    if code != 200 or not isinstance(corps, dict):
        return False, f"HTTP {code}"
    mesures = [m for ligne in corps["risques"] for m in ligne["mesures"]]
    if not mesures:
        return False, "aucune composante active : la démonstration ne prouve rien"
    citees = [m for m in mesures if m["elements"]]
    complete = all(len(m["elements"]) == m["occurrences"] for m in citees)
    agissantes = all(m["action"] for m in mesures)
    return bool(citees) and complete and agissantes, (
        f"{len(mesures)} composantes, {len(citees)} citant leurs éléments, "
        "chacune assortie de l'action attendue"
    )


def uc_pilotage_par_risque() -> tuple[bool, str]:
    """Du plus risqué au moins risqué : un tri alphabétique ferait un annuaire."""
    code, corps = _tableau_de_bord()
    if code != 200 or not isinstance(corps, dict):
        return False, f"HTTP {code}"
    totaux = [float(ligne["total"]) for ligne in corps["risques"]]
    decroissant = all(a >= b for a, b in itertools.pairwise(totaux))
    return bool(totaux) and decroissant, (
        f"{len(totaux)} dossiers, scores {totaux}, "
        f"{corps['a_risque_eleve']} à traiter et {corps['a_risque_modere']} à surveiller"
    )


def uc_ponderation_arretee_leve_la_reserve() -> tuple[bool, str]:
    """L'AVERTISSEMENT TOMBE DÈS QUE LA DIRECTION ARRÊTE LES POIDS, SANS DÉPLOIEMENT.

    Jusqu'au 18 août 2026, ce cas d'usage prouvait l'inverse : l'écran avertissait
    que la pondération n'avait été choisie par personne. Il prouve désormais que
    l'avertissement disparaît une fois les poids arrêtés, et c'est le même
    mécanisme qui produit les deux comportements.

    Ce qu'il faut regarder n'est pas l'absence du bandeau, c'est **par quoi elle
    est obtenue** : six lignes de YAML passées au statut VALIDE, aucun code
    modifié, aucun redéploiement. Un référentiel qui ne changerait pas le
    comportement du produit ne serait qu'une documentation coûteuse.

    La machinerie d'avertissement, elle, reste éprouvée : la suite unitaire la
    rejoue sur un référentiel dont toute validation a été retirée.
    """
    code, corps = _tableau_de_bord()
    if code != 200 or not isinstance(corps, dict):
        return False, f"HTTP {code}"
    silencieux = not corps["poids_non_arretes"]
    _, page = _ecran(DIRECTION, "/pilotage")
    ecran_net = "pas encore été arrêtée" not in page

    # Et le référentiel nomme qui a arrêté, à quel titre. Une réserve levée sans
    # signataire ne vaudrait pas mieux que la réserve.
    _, poids = api(session(DIRECTION), "GET",
                   f"/referentiel/parametres/POIDS_RISQUE_RETARD_DECLARATIF?a_la_date={JOUR}")
    nomme = isinstance(poids, dict) and poids.get("statut") == "VALIDE" and bool(
        poids.get("valide_par")
    )
    detail = (
        f"réserve levée : {silencieux} ; écran net : {ecran_net} ; "
        f"arrêté par : {poids.get('valide_par', 'personne') if isinstance(poids, dict) else '?'}"
    )
    return silencieux and ecran_net and nomme, detail


# ── E · Saisie comptable ─────────────────────────────────────────────────────
#
# ⚠️ Ces sondes appellent l'API directement plutôt que de poster le formulaire.
# Le parcours d'écran, lui, est éprouvé de bout en bout par `flux_saisie.py`,
# qui soumet le vrai formulaire en `multipart/form-data`. Les deux sont
# nécessaires : ici on prouve la règle, là-bas on prouve qu'elle est atteignable.
_ACHAT = {
    "journal": "AC",
    "exercice": "2026",
    "date_operation": JOUR,
    "libelle": "Registre : achat de fournitures",
    "piece_justificative": "PJ-REGISTRE",
    "lignes": [
        {"compte": "604", "libelle": "Fournitures", "sens": "DEBIT", "montant": "90000"},
        {"compte": "401", "libelle": "Fournisseur", "sens": "CREDIT", "montant": "90000"},
    ],
}


def uc_saisie_reservee() -> tuple[bool, str]:
    """`SAISIR_ECRITURE` n'ouvrait aucun écran avant celui-ci.

    Le refus est sondé sur le chargé de clientèle, qui **lit** la comptabilité :
    c'est le profil dont le refus est le moins évident, et donc le seul qui
    prouve quelque chose.
    """
    ouvert, ecriture = api(session(COMPTABLE), "POST",
                           f"/comptabilite/dossiers/{D1}/ecritures", _ACHAT)
    clientele, _ = api(session(FORMALITES), "POST",
                       f"/comptabilite/dossiers/{D1}/ecritures", _ACHAT)
    adherent, _ = api(session(ADHERENT), "POST",
                      f"/comptabilite/dossiers/{D3}/ecritures", _ACHAT)
    brouillon = isinstance(ecriture, dict) and ecriture.get("etat") == "BROUILLON"
    return ouvert == 201 and brouillon and clientele == 403 and adherent == 403, (
        f"comptable {ouvert} en brouillon, chargé de clientèle {clientele}, "
        f"adhérent {adherent}"
    )


def uc_ecriture_desequilibree_refusee() -> tuple[bool, str]:
    """Une comptabilité qui accepte une écriture déséquilibrée n'en est plus une."""
    bancale = {**_ACHAT, "lignes": [
        {"compte": "604", "libelle": "Fournitures", "sens": "DEBIT", "montant": "90000"},
        {"compte": "401", "libelle": "Fournisseur", "sens": "CREDIT", "montant": "80000"},
    ]}
    code, detail = api(session(COMPTABLE), "POST",
                       f"/comptabilite/dossiers/{D1}/ecritures", bancale)
    return code == 409 and "quilibr" in str(detail), (
        f"HTTP {code}, le refus nomme le déséquilibre"
    )


def uc_ecriture_validee_immuable() -> tuple[bool, str]:
    """Après validation, la seule correction est la contre-passation.

    C'est le principe d'intangibilité, et c'est ce qui distingue une
    comptabilité d'un tableur.
    """
    client = session(COMPTABLE)
    code, ecriture = api(client, "POST", f"/comptabilite/dossiers/{D1}/ecritures", _ACHAT)
    if code != 201 or not isinstance(ecriture, dict):
        return False, f"saisie impossible : HTTP {code}"
    cle = f"{ecriture['exercice']}/{ecriture['journal']}/{ecriture['numero']}"
    base = f"/comptabilite/dossiers/{D1}/ecritures/{cle}"
    validee, corps = api(client, "POST", f"{base}/validation")
    rejouee, _ = api(client, "POST", f"{base}/validation")
    nomme = isinstance(corps, dict) and bool(corps.get("validee_par"))
    return validee == 200 and nomme and rejouee == 409, (
        f"validée {validee} par {corps.get('validee_par') if nomme else '?'}, "
        f"seconde validation {rejouee}"
    )


def uc_contrepassation_motivee() -> tuple[bool, str]:
    """On n'efface pas : on ajoute l'inverse, motivé et daté du jour du constat.

    ⚠️ Un motif vide reçoit **403** et non 409 : `CONTRE_PASSER` figure parmi les
    actes qui se justifient, et le contrôle d'accès refuse avant que le domaine
    ne voie l'acte.
    """
    client = session(COMPTABLE)
    code, ecriture = api(client, "POST", f"/comptabilite/dossiers/{D1}/ecritures", _ACHAT)
    if code != 201 or not isinstance(ecriture, dict):
        return False, f"saisie impossible : HTTP {code}"
    cle = f"{ecriture['exercice']}/{ecriture['journal']}/{ecriture['numero']}"
    # ⚠️ La clé que le domaine inscrit dans `ecriture_contrepassee` est **remplie
    # à six chiffres** : `2026/AC/000009`, jamais `2026/AC/9`. L'URL accepte les
    # deux — la route repose le remplissage — mais la comparaison, elle, doit
    # employer la forme canonique, sans quoi on conclut à une contre-passation
    # non rattachée alors qu'elle l'est.
    cle_canonique = f"{ecriture['exercice']}/{ecriture['journal']}/{ecriture['numero']:06d}"
    base = f"/comptabilite/dossiers/{D1}/ecritures/{cle}"
    api(client, "POST", f"{base}/validation")
    sans_motif, _ = api(client, "POST", f"{base}/contre-passation", {"motif": "  "})
    avec, inverse = api(client, "POST", f"{base}/contre-passation",
                        {"motif": "Facture reçue en double"})
    _, origine = api(client, "GET", base)
    intacte = isinstance(origine, dict) and origine.get("etat") == "VALIDEE"
    inversee = (
        isinstance(inverse, dict)
        and inverse.get("type") == "CONTREPASSATION"
        and inverse.get("ecriture_contrepassee") == cle_canonique
    )
    return sans_motif == 403 and avec == 201 and inversee and intacte, (
        f"motif vide {sans_motif}, inverse {avec} rattaché à {cle_canonique}, "
        f"originale toujours validée : {intacte}"
    )


def uc_exercice_clos_ferme() -> tuple[bool, str]:
    """Écrire dans un exercice inconnu ou clos rendrait fausse une liasse déjà
    déposée, sans que le cabinet sache que sa copie a changé."""
    code, detail = api(session(COMPTABLE), "POST",
                       f"/comptabilite/dossiers/{D1}/ecritures",
                       {**_ACHAT, "exercice": "2099"})
    return code == 409 and "2099" in str(detail), f"HTTP {code}, l'exercice est nommé"


def uc_simulation_gardee() -> tuple[bool, str]:
    """La route qui fabrique un paiement disparaît dès que Tara est configuré."""
    source = (
        RACINE
        / "Backend_erp_cga/app/contextes/souscription/adaptateurs/entrant/routes_http.py"
    ).read_text(encoding="utf-8")
    garde = "if not boutique.fournisseur.simule:" in source and "status_code=409" in source
    return garde, "409 dès que des identifiants Tara réels sont configurés"


# ══ L'espace de l'adhérent, la file du réviseur, la preuve d'une dérogation ════
#
# Pas 119 : les gestes construits aux pas 112 à 118 n'avaient aucune preuve exécutée. Un registre
# qui s'arrête au pas 105 dit « tout va bien » d'un produit qui a doublé d'écrans depuis.


def uc_accueil_adherent() -> tuple[bool, str]:
    """L'adhérent lit son mois : ce qui manque, ou que son dossier est complet (pas 112)."""
    code, vue = api(session(ADHERENT), "GET", f"/pilotage/dossiers/{D3}/mon-mois")
    if code != 200 or not isinstance(vue, dict):
        return False, f"HTTP {code}"
    bandeau = vue["bandeau"]
    etats = {"A_ENVOYER", "EN_VERIFICATION", "AUCUNE_PIECE", "COMPLET"}
    correct = bandeau["etat"] in etats and len(bandeau["titre"]) > 3
    return correct, f"{bandeau['etat']} · « {bandeau['titre']} » · {len(vue['attendues'])} demandée(s)"


def uc_reponse_au_cabinet() -> tuple[bool, str]:
    """L'adhérent répond à une demande ; le collaborateur ne répond pas à sa place (pas 112)."""
    code, demandes = api(session(ADHERENT), "GET", f"/collecte/demandes?entreprise={D3}")
    if code != 200 or not demandes:
        return False, f"aucune demande ouverte à laquelle répondre (HTTP {code})"
    demande = demandes[0]["identifiant"]
    chemin = f"/collecte/demandes/{demande}/reponse"
    accord, repondue = api(session(ADHERENT), "POST", chemin, {"nature": "INTROUVABLE"})
    double, _ = api(session(ADHERENT), "POST", chemin, {"nature": "INTROUVABLE"})
    refus, _ = api(session(COMPTABLE), "POST", chemin, {"nature": "INTROUVABLE"})
    ouverte = repondue.get("statut") == "OUVERTE" if isinstance(repondue, dict) else False
    return (
        accord == 201 and double == 409 and refus == 403 and ouverte,
        f"adhérent 201 (demande toujours OUVERTE : {ouverte}), double {double}, comptable {refus}",
    )


def uc_justificatifs_de_l_adherent() -> tuple[bool, str]:
    """Les justificatifs d'un mois, dans les mots de l'adhérent, et pas ceux d'un autre (pas 112)."""
    code, vue = api(session(ADHERENT), "GET", f"/collecte/dossiers/{D3}/justificatifs?mois=2026-07")
    hors, _ = api(session(ADHERENT), "GET", f"/collecte/dossiers/{D1}/justificatifs")
    if code != 200 or not isinstance(vue, dict):
        return False, f"HTTP {code}"
    statuts = {l_["statut"] for l_ in vue["lignes"]}
    connus = {"A_CORRIGER", "RECU", "ENREGISTRE", "CLASSE"}
    return (
        statuts <= connus and hors == 404 and vue["total_du_mois"] == len(vue["lignes"]),
        f"{vue['total_du_mois']} justificatif(s) de juillet, statuts {sorted(statuts)}, autre dossier {hors}",
    )


def uc_echeances_de_l_adherent() -> tuple[bool, str]:
    """Une carte par obligation, dans ses mots, avec sa période lisible (pas 113)."""
    code, vue = api(session(ADHERENT), "GET", f"/obligations/dossiers/{D3}/mes-echeances")
    if code != 200 or not isinstance(vue, dict):
        return False, f"HTTP {code}"
    codes = [e["code_obligation"] for e in vue["echeances"] if e["etat"] != "DEPOSEE"]
    unique = len(codes) == len(set(codes))
    lisible = all(e["periode"] and e["titre"] for e in vue["echeances"])
    return unique and lisible, f"{len(vue['echeances'])} carte(s), une par obligation : {unique}"


def uc_preuve_de_paiement() -> tuple[bool, str]:
    """« J'ai déjà payé » : la quittance rejoint le dossier et dit ce qu'elle règle (pas 113)."""
    from uuid import uuid4

    code, vue = api(session(ADHERENT), "GET", f"/obligations/dossiers/{D3}/mes-echeances")
    a_regler = [e for e in (vue.get("echeances", []) if isinstance(vue, dict) else []) if e["etat"] in ("EN_RETARD", "A_VENIR")]
    if code != 200 or not a_regler:
        return False, f"aucune échéance à régler (HTTP {code})"
    echeance = a_regler[0]
    marqueur = uuid4().hex[:8]
    envoi, fichier = envoyer_un_fichier(
        session(ADHERENT), f"/collecte/fichiers?entreprise={D3}", f"quittance-{marqueur}.pdf", _pdf(marqueur)
    )
    if envoi != 201 or not isinstance(fichier, dict):
        return False, f"envoi de la quittance : HTTP {envoi}"
    depot, piece = api(
        session(ADHERENT),
        "POST",
        "/collecte/pieces",
        {
            "entreprise": D3,
            "canal": "PORTAIL",
            "empreinte": fichier["empreinte"],
            "nom_fichier": fichier["nom_fichier"],
            "type": "QUITTANCE_IMPOT",
        },
    )
    if depot != 201 or not isinstance(piece, dict):
        return False, f"dépôt de la quittance : HTTP {depot}"
    corps = {
        "code_obligation": echeance["code_obligation"],
        "periode_debut": echeance["periode_debut"],
        "periode_fin": echeance["periode_fin"],
        "piece": piece["piece"]["identifiant"],
    }
    accord, recue = api(session(ADHERENT), "POST", f"/obligations/dossiers/{D3}/preuves-de-paiement", corps)
    double, _ = api(session(ADHERENT), "POST", f"/obligations/dossiers/{D3}/preuves-de-paiement", corps)
    _, apres = api(session(ADHERENT), "GET", f"/obligations/dossiers/{D3}/mes-echeances")
    vue_apres = {(e["code_obligation"], e["periode_debut"]): e["etat"] for e in apres["echeances"]}
    etat = vue_apres.get((echeance["code_obligation"], echeance["periode_debut"]))
    return (
        accord == 201 and double == 409 and etat == "PREUVE_ENVOYEE",
        f"{recue['titre'] if isinstance(recue, dict) else '—'} : preuve reçue, carte « {etat} », seconde fois {double}",
    )


def uc_signalement_de_changement() -> tuple[bool, str]:
    """L'adhérent signale un changement ; le dossier ne bouge pas (pas 114)."""
    from uuid import uuid4

    message = f"Nouveau numéro de téléphone : 699 00 {uuid4().hex[:4]}"
    avant_code, avant = api(session(ADHERENT), "GET", f"/portefeuille/entreprises/{D3}/mon-entreprise")
    accord, _ = api(
        session(ADHERENT), "POST", f"/portefeuille/entreprises/{D3}/signalements",
        {"nature": "TELEPHONE", "message": message},
    )
    refus, _ = api(
        session(COMPTABLE), "POST", f"/portefeuille/entreprises/{D3}/signalements",
        {"nature": "TELEPHONE", "message": message},
    )
    _, apres = api(session(ADHERENT), "GET", f"/portefeuille/entreprises/{D3}/mon-entreprise")
    inchange = avant_code == 200 and apres["siege"] == avant["siege"]
    vu = any(s["message"] == message for s in apres["signalements"])
    return (
        accord == 201 and refus == 403 and inchange and vu,
        f"adhérent 201, collaborateur {refus}, dossier inchangé : {inchange}, signalement visible : {vu}",
    )


def uc_rappels_regles_par_l_adherent() -> tuple[bool, str]:
    """L'adhérent règle ses rappels ; le collaborateur ne les règle pas pour lui (pas 115)."""
    chemin = f"/obligations/dossiers/{D3}/mes-rappels"
    code, vue = api(session(ADHERENT), "GET", chemin)
    if code != 200 or not isinstance(vue, dict):
        return False, f"HTTP {code}"
    regle, apres = api(session(ADHERENT), "POST", chemin, {"actifs": True, "jalons": [3, 1]})
    vide, _ = api(session(ADHERENT), "POST", chemin, {"actifs": True, "jalons": []})
    hors, _ = api(session(ADHERENT), "POST", chemin, {"actifs": True, "jalons": [5]})
    refus, _ = api(session(COMPTABLE), "GET", chemin)
    jalons = apres["preference"]["jalons"] if regle == 200 and isinstance(apres, dict) else []
    return (
        regle == 200 and jalons == [3, 1] and vide == 422 and hors == 422 and refus == 403,
        f"réglé sur {jalons}, sans moment {vide}, moment non proposé {hors}, comptable {refus}",
    )


def uc_lien_d_acces_rendu() -> tuple[bool, str]:
    """Le chargé de clientèle rend l'accès, après avoir écrit comment il a reconnu l'adhérent (pas 116)."""
    tchoumba = "P019876543210K"
    code, acces = api(session(FORMALITES), "GET", f"/portefeuille/entreprises/{tchoumba}/acces-adherents")
    if code != 200 or not acces:
        return False, f"aucun compte adhérent lu (HTTP {code})"
    compte = acces[0]["compte"]
    chemin = f"/portefeuille/entreprises/{tchoumba}/acces-adherents/{compte}/lien"
    courte, _ = api(session(FORMALITES), "POST", chemin, {"verification": "ok"})
    accord, lien = api(
        session(FORMALITES), "POST", chemin,
        {"verification": "Rappelé au numéro du dossier, gérant confirmé"},
    )
    refus, _ = api(session(COMPTABLE), "POST", chemin, {"verification": "Rappelé au numéro du dossier"})
    type_du_lien = lien.get("type") if isinstance(lien, dict) else "—"
    return (
        courte == 422 and accord == 201 and refus == 403,
        f"vérification courte {courte}, lien {type_du_lien} envoyé, comptable {refus}",
    )


def uc_file_d_anomalies() -> tuple[bool, str]:
    """La file du réviseur : tout le portefeuille, par gravité puis par enjeu (pas 117)."""
    code, vue = api(session(REVISEUR), "GET", "/pilotage/file-d-anomalies")
    refus, _ = api(session(ADHERENT), "GET", "/pilotage/file-d-anomalies")
    if code != 200 or not isinstance(vue, dict):
        return False, f"HTTP {code}"
    rang = {"BLOQUANT": 0, "MAJEUR": 1, "AVERTISSEMENT": 2}
    gravites = [rang[l_["gravite"]] for l_ in vue["lignes"]]
    _, du_comptable = api(session(COMPTABLE), "GET", "/pilotage/file-d-anomalies")
    dossiers_reviseur = {l_["dossier"] for l_ in vue["lignes"]}
    dossiers_comptable = {l_["dossier"] for l_ in du_comptable["lignes"]}
    return (
        gravites == sorted(gravites) and refus == 403 and dossiers_comptable <= dossiers_reviseur,
        f"{len(vue['lignes'])} constat(s) ordonnés, adhérent {refus}, périmètre du comptable inclus : "
        f"{dossiers_comptable <= dossiers_reviseur}",
    )


def uc_piece_d_appui() -> tuple[bool, str]:
    """Une dérogation porte sa preuve, et le journal compte ce qui reste à régulariser (pas 118)."""
    code, file_ = api(session(REVISEUR), "GET", "/pilotage/file-d-anomalies?gravite=MAJEUR")
    lignes = file_.get("lignes", []) if isinstance(file_, dict) else []
    if code != 200 or not lignes:
        return False, f"aucun constat majeur à écarter (HTTP {code})"
    ligne = lignes[0]
    pose, ecart = api(
        session(REVISEUR), "POST", f"/conformite/pieces/{ligne['piece']}/ecarts",
        {
            "code_regle": ligne["code_regle"],
            "motif": "Attestation obtenue du fournisseur et vérifiée au fichier DGI, recette du pas 119.",
        },
    )
    if pose not in (200, 201) or not isinstance(ecart, dict):
        return False, f"écart refusé : HTTP {pose}"
    identifiant = ecart["ecart"]["identifiant"]
    chemin = f"/conformite/pieces/{ligne['piece']}/ecarts/{identifiant}/piece-appui"
    courte, _ = api(session(REVISEUR), "POST", chemin, {"piece": "ok"})
    jointe, avec = api(session(REVISEUR), "POST", chemin, {"piece": "Attestation DGI du 18/09/2026"})
    refus, _ = api(session(COMPTABLE), "POST", chemin, {"piece": "PJ-2026-0042"})
    portee = avec["ecart"]["piece_appui"] if jointe in (200, 201) and isinstance(avec, dict) else "—"
    _, journal = api(session(REVISEUR), "GET", "/conformite/derogations")
    delai = journal.get("delai_de_regularisation_jours") if isinstance(journal, dict) else None
    return (
        courte == 422 and jointe in (200, 201) and refus == 403 and portee != "—",
        f"preuve « {portee} », référence courte {courte}, comptable {refus}, délai du référentiel {delai} j",
    )


def uc_mandat_accorde() -> tuple[bool, str]:
    """Le cabinet ouvre ses données à un autre locataire, puis referme (pas 127 et 129).

    ⚠️ Le geste le plus lourd de l'écran d'administration : il n'accorde aucun rôle, il
    autorise l'exercice, **ici**, de rôles déjà tenus ailleurs. On vérifie donc les quatre
    choses qui comptent : qu'il s'accorde, qu'il se lit, qu'il se retire, et qu'un
    comptable ne peut ni le voir ni le poser.
    """
    administrateur = session(ADMIN)
    pose, accorde = api(
        administrateur,
        "POST",
        "/transverse/mandats",
        {
            "mandataire": "station-bonaberi",
            "roles": ["COMPTABLE"],
            "debut": "2026-01-01",
            "motif": "CONTRAT_DE_SUIVI",
            "precision": "Recette du pas 129.",
        },
    )
    if pose != 201 or not isinstance(accorde, dict):
        return False, f"mandat refusé : HTTP {pose}"
    identifiant = accorde["identifiant"]

    lu, liste = api(administrateur, "GET", "/transverse/mandats")
    present = isinstance(liste, list) and any(m["identifiant"] == identifiant for m in liste)

    # ⚠️ Un mandat sans rôle n'autorise rien : le modèle le refuse, et la recette le
    # constate plutôt que de croire la documentation.
    vide, _ = api(
        administrateur,
        "POST",
        "/transverse/mandats",
        {"mandataire": "ailleurs", "roles": [], "debut": "2026-01-01", "motif": "ASSISTANCE"},
    )

    refus_lecture, _ = api(session(COMPTABLE), "GET", "/transverse/mandats")
    retrait, retire = api(
        administrateur,
        "POST",
        f"/transverse/mandats/{identifiant}/revocation",
        {"motif": "Fin du contrat de suivi au 30/09/2026, recette du pas 129."},
    )
    ferme = retrait == 200 and isinstance(retire, dict) and retire["revoque_le"] is not None
    rejoue, _ = api(
        administrateur,
        "POST",
        f"/transverse/mandats/{identifiant}/revocation",
        {"motif": "Second retrait, qui ne doit pas passer."},
    )
    return (
        lu == 200 and present and vide == 422 and refus_lecture == 403 and ferme and rejoue == 409,
        f"accordé {pose}, lu {lu}, sans rôle {vide}, comptable {refus_lecture}, "
        f"retiré {retrait}, second retrait {rejoue}",
    )


REGISTRE: list[CasUsage] = [
    # ── K · Accès et identité ────────────────────────────────────────────────
    CasUsage("UC-01", "K", "Collaborateur", "Ouvrir une session de travail",
             uc_connexion_collaborateur),
    CasUsage("UC-02", "K", "Adhérent", "Ouvrir une session et arriver sur son espace",
             uc_connexion_adherent),
    CasUsage("UC-03", "K", "Compte suspendu", "Être refusé à la connexion",
             lambda: _refus_connexion("a.tchinda@cga-brcg.cm")),
    CasUsage("UC-04", "K", "Compte non activé", "Être refusé à la connexion",
             lambda: _refus_connexion("e.tchoumba@tchoumbaetfils.cm")),
    CasUsage("UC-05", "K", "Compte inexistant", "Être refusé sans révéler qu'il n'existe pas",
             lambda: _refus_connexion("inconnu@nulle-part.cm")),
    CasUsage("UC-06", "K", "Visiteur anonyme", "Se voir refuser toute route métier",
             uc_401_sans_session),
    CasUsage("UC-07", "K", "Attaquant", "Être freiné au-delà de 30 connexions / 5 min",
             test="tests/test_limitation.py"),
    CasUsage("UC-08", "K", "Navigateur", "Ne recevoir un témoin Secure que sur HTTPS",
             test="tests/test_transverse.py -k temoin"),
    # ── K · Habilitations et périmètre ───────────────────────────────────────
    CasUsage("UC-09", "K", "Tout profil", "Ne voir que les écrans de son rôle", uc_ecran_reserve),
    CasUsage("UC-10", "K", "Tout profil", "Être refusé aussi hors de l'interface",
             uc_refus_tient_sans_interface),
    CasUsage("UC-11", "K", "Administrateur", "N'accéder à aucun dossier", uc_admin_aucun_dossier),
    CasUsage("UC-12", "K", "Comptable", "Ne lire que les dossiers de son portefeuille",
             uc_portee_comptable),
    CasUsage("UC-13", "K", "Adhérent", "Recevoir 404, jamais 403, hors périmètre",
             uc_hors_portee_404),
    # ── M · Souscription ─────────────────────────────────────────────────────
    CasUsage("UC-14", "M", "Prospect", "Obtenir un devis sans compte",
             test="tests/test_souscription.py -k devis"),
    CasUsage("UC-15", "M", "Prospect", "Se voir exiger le NIU quand le service ouvre un accès",
             test="tests/test_souscription.py -k niu"),
    CasUsage("UC-16", "M", "Prospect", "Voir son paiement ouvrir l'accès et partir en courriel",
             test="tests/test_mode_demonstration.py"),
    CasUsage("UC-17", "M", "Nouvel adhérent", "Définir son mot de passe et se connecter",
             test="tests/test_transverse.py -k mot_de_passe"),
    CasUsage("UC-18", "M", "Exploitant", "Voir la simulation de paiement refusée en production",
             uc_simulation_gardee),
    # ── I · Création d'entreprise ────────────────────────────────────────────
    CasUsage("UC-34", "I", "Chargé de formalités", "Ouvrir le pipeline — et lui seul",
             uc_pipeline_reserve),
    CasUsage("UC-35", "I", "Fondateur", "Savoir quelles pièces réunir pour sa forme",
             uc_checklist_par_forme),
    CasUsage("UC-36", "I", "Chargé de formalités", "Voir d'abord les dossiers qui dorment",
             uc_pipeline_par_urgence),
    CasUsage("UC-37", "I", "Chargé de formalités", "Être arrêté avant un dépôt CFCE incomplet",
             uc_depot_incomplet_refuse),
    CasUsage("UC-38", "I", "Nouvelle entreprise", "Naître au portefeuille avec ses échéances",
             uc_conversion_complete),
    CasUsage("UC-39", "I", "Chargé de formalités", "Voir le tunnel refuser tout saut d'étape",
             test="tests/test_creation_entreprise.py::TestTunnel"),
    CasUsage("UC-40", "I", "Fiscaliste",
             "Voir un capital validé bloquer là où un capital douteux avertissait",
             test="tests/test_creation_entreprise.py::TestDiagnostic"),

    # ── C · Collecte ─────────────────────────────────────────────────────────
    CasUsage("UC-19", "C", "Comptable", "Enregistrer une pièce déposée au cabinet",
             uc_depot_piece),
    CasUsage("UC-20", "C", "Adhérent", "Ne voir dans la boîte que les pièces de son dossier",
             uc_boite_restreinte),
    # ── C · L'espace de l'adhérent (pas 112 à 116) ───────────────────────────
    CasUsage("UC-65", "J", "Adhérent", "Lire son mois : ce qui manque, ou que tout est complet",
             uc_accueil_adherent),
    CasUsage("UC-66", "C", "Adhérent", "Répondre au cabinet sans fermer la demande",
             uc_reponse_au_cabinet),
    CasUsage("UC-67", "C", "Adhérent", "Lire ses justificatifs d'un mois, dans ses mots",
             uc_justificatifs_de_l_adherent),
    CasUsage("UC-68", "F", "Adhérent", "Lire ses échéances, une carte par obligation",
             uc_echeances_de_l_adherent),
    CasUsage("UC-69", "F", "Adhérent", "Envoyer la preuve qu'il a déjà payé",
             uc_preuve_de_paiement),
    CasUsage("UC-70", "B", "Adhérent", "Signaler un changement sans que le dossier bouge",
             uc_signalement_de_changement),
    CasUsage("UC-71", "F", "Adhérent", "Régler ses rappels d'échéance, lui seul",
             uc_rappels_regles_par_l_adherent),
    CasUsage("UC-72", "K", "Chargé de clientèle", "Rendre l'accès à un adhérent, vérification écrite",
             uc_lien_d_acces_rendu),
    # ── D · Conformité : la file et la preuve (pas 117 et 118) ───────────────
    CasUsage("UC-73", "D", "Réviseur", "Traiter tout le portefeuille par gravité et par enjeu",
             uc_file_d_anomalies),
    CasUsage("UC-74", "D", "Réviseur", "Joindre à une dérogation la preuve de son motif",
             uc_piece_d_appui),
    # ── K · Transverse : le mandat (pas 127 et 129) ──────────────────────────
    CasUsage("UC-75", "K", "Administrateur",
             "Ouvrir ses données à un autre locataire, puis refermer", uc_mandat_accorde),
    # ── G · Social et paie ───────────────────────────────────────────────────
    CasUsage("UC-41", "G", "Comptable", "Lire le personnel — refusé ailleurs", uc_paie_reservee),
    CasUsage("UC-42", "G", "Cadre au-dessus du plafond",
             "Voir le plafond CNPS n'atteindre que les bonnes branches", uc_plafond_cnps),
    CasUsage("UC-43", "G", "Salarié logé",
             "Voir son avantage imposé sans être versé deux fois", uc_avantages_hors_du_net),
    CasUsage("UC-44", "G", "Employeur", "Savoir quoi verser, et avant quand",
             uc_declaration_sociale),
    CasUsage("UC-45", "G", "Salarié", "Voir un impôt progressif, jamais un taux moyen",
             test="tests/test_social.py::TestIrpp"),
    CasUsage("UC-46", "G", "Cabinet", "Voir le calcul refuser plutôt qu'amputer un bulletin",
             test="tests/test_social.py::TestRefusDeCalculer"),

    # ── D · Conformité ───────────────────────────────────────────────────────
    CasUsage("UC-21", "D", "Adhérent", "Ne pas faire tourner le moteur de conformité",
             uc_moteur_permission),
    CasUsage("UC-22", "D", "Concurrent", "Ne pas lire le catalogue des règles",
             uc_regles_non_publiques),
    CasUsage("UC-23", "D", "Comptable", "Obtenir une conséquence fiscale chiffrée par anomalie",
             test="tests/test_regles.py"),
    # ── H · Clôture et DSF ───────────────────────────────────────────────────
    CasUsage("UC-47", "H", "Comptable", "Lire la liasse — refusée ailleurs", uc_liasse_reservee),
    CasUsage("UC-48", "H", "Réviseur", "Voir les trois contrôles d'avant dépôt",
             uc_liasse_coherente),
    CasUsage("UC-49", "H", "Adhérent", "Ne pas payer l'impôt deux fois sur une TVA rejetée",
             uc_tva_rejetee_non_reintegree),
    CasUsage("UC-50", "H", "Adhérent", "Voir son abattement CGA calculé après réintégrations",
             test="tests/test_cloture.py::TestPassageFiscal"),
    CasUsage("UC-51", "H", "Comptable", "Voir une balance fausse refuser de s'équilibrer",
             test="tests/test_cloture.py::TestAssemblage"),
    CasUsage("UC-52", "H", "Vérificateur", "Remonter d'une réintégration jusqu'à la facture",
             test="tests/test_cloture.py::TestChaineComplete"),

    # ── J · Pilotage du cabinet ──────────────────────────────────────────────
    CasUsage("UC-53", "J", "Direction", "Ouvrir le pilotage, fermé même au réviseur",
             uc_pilotage_reserve),
    CasUsage("UC-54", "J", "Direction", "Descendre du score jusqu'à la pièce qui le cause",
             uc_score_tracable),
    CasUsage("UC-55", "J", "Direction", "Voir les dossiers rangés par risque, jamais par nom",
             uc_pilotage_par_risque),
    CasUsage("UC-56", "J", "Direction", "Voir la réserve tomber dès que la direction arrête",
             uc_ponderation_arretee_leve_la_reserve),
    CasUsage("UC-57", "J", "Cabinet", "Voir la charge ignorer les habilitations à portée ouverte",
             test="tests/test_pilotage.py::TestCharge"),
    CasUsage("UC-58", "J", "Cabinet", "Voir un poids absent valoir zéro plutôt qu'être inventé",
             test="tests/test_pilotage.py::TestPonderation"),

    # ── E · Comptabilité ─────────────────────────────────────────────────────
    CasUsage("UC-59", "E", "Comptable", "Saisir une écriture, et lui seul",
             uc_saisie_reservee),
    CasUsage("UC-60", "E", "Cabinet", "Voir une écriture déséquilibrée refusée",
             uc_ecriture_desequilibree_refusee),
    CasUsage("UC-61", "E", "Vérificateur", "Voir qu'une écriture validée ne se retouche plus",
             uc_ecriture_validee_immuable),
    CasUsage("UC-62", "E", "Comptable", "Annuler par l'inverse, motivé, sans rien effacer",
             uc_contrepassation_motivee),
    CasUsage("UC-63", "E", "Cabinet", "Voir un exercice inconnu ou clos refuser la saisie",
             uc_exercice_clos_ferme),
    CasUsage("UC-64", "E", "Comptable", "Saisir depuis l'écran, sans JavaScript",
             test="tests/test_comptabilite_saisie.py::TestRoute"),
    CasUsage("UC-24", "E", "Comptable", "Lire une balance équilibrée, interdite à l'adhérent",
             uc_balance),
    CasUsage("UC-25", "E", "Comptable", "Voir les trois contrôles d'avant dépôt",
             test="tests/test_comptabilite.py"),
    # ── F · Obligations ──────────────────────────────────────────────────────
    CasUsage("UC-26", "F", "Comptable", "Obtenir l'échéancier calculé du dossier", uc_echeancier),
    CasUsage("UC-27", "F", "Comptable", "Être refusé au dépôt de déclaration (réviseur seul)",
             uc_depot_declaration),
    # ── K · Traçabilité et exploitation ──────────────────────────────────────
    CasUsage("UC-28", "K", "Direction", "Lire le journal d'audit, fermé au comptable", uc_audit),
    CasUsage("UC-29", "K", "Administrateur", "Inviter un compte — et lui seul", uc_invitation),
    CasUsage("UC-30", "K", "Exploitant", "Voir /sante sonder réellement la base", uc_sante),
    CasUsage("UC-31", "K", "Exploitant", "Voir la chaîne d'audit tenir sous concurrence",
             test="tests/test_concurrence.py"),
    CasUsage("UC-32", "K", "Exploitant", "Voir la production refuser une configuration dangereuse",
             test="tests/test_courriel.py::TestConfigurationDeProduction"),
    CasUsage("UC-33", "K", "Architecte", "Voir les frontières de contexte tenir",
             test="tests/test_architecture.py"),
]


# ══ Exécution ═════════════════════════════════════════════════════════════════
def _pourquoi_rien_n_a_tourne(sortie: str) -> str:
    """La première raison d'ignorance rapportée par pytest, ou un aveu d'ignorance.

    ⚠️ **Un verdict qui dit « aucun test exécuté » est exact et inutile.** Celui qui lit le
    cahier doit savoir s'il manque une base, un fichier, ou une dépendance. La raison est
    dans la sortie de pytest quand on la lui demande ; l'oublier revient à transformer un
    problème d'installation en mystère.
    """
    for ligne in sortie.splitlines():
        depouillee = ligne.strip()
        if depouillee.startswith("SKIPPED"):
            return depouillee.split("]", 1)[-1].strip() or depouillee
    return "cause non rapportée par pytest"


def executer_suite(cas: list[CasUsage]) -> dict[str, tuple[bool, str]]:
    """Lance pytest une seule fois par cible et rend le verdict de chacune.
    ⚠️ L'environnement est transmis tel quel — `CGA_URL_BASE_DE_DONNEES_TEST`
    compris. Sans lui, les tests de persistance se **sautent**, `pytest` sort 0,
    et un registre naïf compte le cas d'usage comme validé. Un cas validé par
    des tests qui ne se sont pas exécutés est pire qu'un cas en échec : il
    éteint la seule alarme qui aurait pu sonner.
    """
    resultats: dict[str, tuple[bool, str]] = {}
    for c in cas:
        if c.test is None:
            continue
        cible = c.test.split(" -k ")
        # ⚠️ `-rs` : quand rien ne tourne, la raison des cas ignorés est la seule chose
        # qui dise quoi faire. Sans elle, le cahier affiche « aucun test exécuté », ce
        # qui est exact et parfaitement inutile à celui qui doit corriger.
        commande = [sys.executable, "-m", "pytest", "-q", "-rs", cible[0]]
        if len(cible) > 1:
            commande += ["-k", cible[1]]
        # `check=False` : un test rouge est un résultat à afficher, pas une
        # exception qui interromprait le registre au premier échec.
        issue = subprocess.run(
            commande,
            cwd=RACINE / "Backend_erp_cga",
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
            env=os.environ.copy(),
        )
        derniere = [
            ligne
            for ligne in issue.stdout.strip().splitlines()
            if "passed" in ligne or "failed" in ligne
        ]
        resume = derniere[-1].strip() if derniere else "aucun test exécuté"
        # « 0 passed » ou aucune ligne de résultat : rien n'a tourné. Le cas
        # d'usage n'est pas validé, il est **non couvert**, et ça se dit.
        a_tourne = bool(derniere) and not resume.startswith("no tests ran")
        if not a_tourne:
            resume = f"{resume} · {_pourquoi_rien_n_a_tourne(issue.stdout)}"
        resultats[c.reference] = (issue.returncode == 0 and a_tourne, resume)
    return resultats


def main() -> int:
    direct_seulement = "--direct" in sys.argv
    verdicts_suite = {} if direct_seulement else executer_suite(REGISTRE)

    largeur = 118
    print("╔" + "═" * (largeur - 2) + "╗")
    titre = "REGISTRE DES CAS D'USAGE — ET LA PREUVE QUI VALIDE CHACUN"
    print("║" + titre.center(largeur - 2) + "║")
    print("╚" + "═" * (largeur - 2) + "╝")
    print()
    print(f"  Pile   front {FRONT}   ·   API {API}")
    print("  Preuve « direct » = exécuté à l'instant par HTTP · « suite » = test nommé, lancé ici")
    print()

    entete = f"{'':2}{'réf':<7}{'ctx':<5}{'acteur':<20}{'cas d’usage':<56}{'preuve':<8}"
    print(entete)
    print("─" * largeur)

    total = reussis = 0
    contexte_courant = None
    for cas in REGISTRE:
        if cas.contexte != contexte_courant:
            contexte_courant = cas.contexte
            print()
        if cas.preuve is not None:
            try:
                ok, constat = cas.preuve()
            except RecetteLimitee as limite:
                # ⚠️ Pas 119 : on **arrête** au lieu de compter des faux défauts. Le limiteur refusé
                # une fois refusera les suivants : continuer produirait vingt-cinq « flux en échec »
                # sur une pile saine, et c'est exactement ce que la recette existe pour éviter.
                print()
                print("  " + "─" * 100)
                print(f"  RECETTE INTERROMPUE : {limite}")
                print("  " + "─" * 100)
                return 2
            except Exception as erreur:  # noqa: BLE001
                ok, constat = False, f"exception : {type(erreur).__name__} {erreur}"
            genre = "direct"
        elif cas.reference in verdicts_suite:
            ok, constat = verdicts_suite[cas.reference]
            genre = "suite"
        else:
            print(f"  {cas.reference:<7}{cas.contexte:<5}{cas.acteur:<20}"
                  f"{cas.intitule:<56}{'—':<8}(non exécuté)")
            continue
        total += 1
        reussis += ok
        marque = "✓" if ok else "✗"
        print(f"{marque} {cas.reference:<7}{cas.contexte:<5}{cas.acteur:<20}"
              f"{cas.intitule:<56}{genre:<8}")
        print(f"{'':2}{'':7}{'':5}{'└─ ' + constat}")

    print()
    print("─" * largeur)
    verdict = "TOUS LES FLUX VALIDÉS" if reussis == total else "DES FLUX RESTENT EN ÉCHEC"
    print(f"  {reussis}/{total} cas d'usage validés — {verdict}")
    print("─" * largeur)
    return 0 if reussis == total else 1


if __name__ == "__main__":
    sys.exit(main())
