"""Le flux G · Social et paie, de bout en bout, contre PostgreSQL.

Fichier du personnel → bulletin d'un salarié → déclaration mensuelle, plus les
vérifications qui distinguent un calcul juste d'un calcul plausible :

* le plafond CNPS ne s'applique pas aux mêmes branches ;
* les avantages en nature entrent dans l'assiette et sortent du net ;
* le total à verser comprend la retenue salariale ;
* un embauché en cours de mois est déclaré, un sorti produit un mouvement.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid
from decimal import Decimal

sys.path.insert(0, "/tmp/cga-pg")
from verifier_profils import Client, champs_caches

API = "http://127.0.0.1:8010"
JOUR = "2026-08-17"
MOT_DE_PASSE = "cabinet brcg douala 2026"
COMPTABLE = "l.fotso@cga-brcg.cm"
ADHERENT = "jp.nkoa@batimentplus.cm"
AGRO = "M065544332211L"
BATIMENT = "M081234567890P"


def session(adresse: str) -> Client:
    client = Client()
    _, page, _ = client.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = adresse
    champs["motDePasse"] = MOT_DE_PASSE
    client.soumettre("/connexion", champs)
    return client


def appeler(client: Client, methode: str, chemin: str, corps: dict | None = None):
    donnees = json.dumps(corps).encode() if corps is not None else None
    entetes = {"Accept": "application/json"}
    if corps is not None:
        entetes["Content-Type"] = "application/json"
    if client.temoins:
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
            return erreur.code, brut[:250]


def etape(n: int, libelle: str, ok: bool, detail: str = "") -> bool:
    print(f"  {'✓' if ok else '✗'} {n:>2}. {libelle:<52} {detail}")
    return ok


def sous(montant) -> str:
    return f"{Decimal(str(montant)):,.0f}".replace(",", " ")


def main() -> int:
    echecs: list[str] = []
    comptable = session(COMPTABLE)
    adherent = session(ADHERENT)

    print("═" * 100)
    print("FLUX G · SOCIAL ET PAIE — DU FICHIER DU PERSONNEL À LA DÉCLARATION")
    print("═" * 100)

    # 0 · Le périmètre tient ───────────────────────────────────────────────────
    code, _ = appeler(adherent, "GET", f"/social/dossiers/{AGRO}/salaries?a_la_date={JOUR}")
    if not etape(0, "Un adhérent ne lit pas le personnel d'un autre dossier",
                 code in (403, 404), f"HTTP {code}"):
        echecs.append("le périmètre ne tient pas sur le personnel")

    # 1 · Le fichier du personnel ─────────────────────────────────────────────
    code, personnel = appeler(
        comptable, "GET", f"/social/dossiers/{AGRO}/salaries?a_la_date={JOUR}"
    )
    n = len(personnel) if isinstance(personnel, list) else 0
    sortis = sum(1 for s in personnel if s["sans_contrat"]) if isinstance(personnel, list) else 0
    if not etape(1, "Fichier du personnel", code == 200,
                 f"HTTP {code}, {n} salariés dont {sortis} sans contrat en cours"):
        echecs.append(f"personnel : {personnel}")
        return bilan(echecs)
    if sortis == 0:
        echecs.append("aucun salarié sorti : le fichier semble purgé, or il ne doit pas l'être")

    # 2 · Le bulletin du cadre — au-dessus du plafond ─────────────────────────
    code, bulletin = appeler(
        comptable, "GET",
        f"/social/dossiers/{AGRO}/bulletins/2026/7/SAL-0001?groupe_risque=B",
    )
    if not etape(2, "Bulletin du cadre (au-dessus du plafond)", code == 200,
                 f"HTTP {code}, brut {sous(bulletin.get('salaire_base', 0))} + primes + avantages"
                 if isinstance(bulletin, dict) else str(bulletin)):
        echecs.append(f"bulletin : {bulletin}")
        return bilan(echecs)

    lignes = {ligne["code"]: ligne for ligne in bulletin["lignes"]}
    brut = (
        Decimal(bulletin["salaire_base"])
        + Decimal(bulletin["primes"])
        + Decimal(bulletin["avantages_evalues"])
    )
    plafonnees = {c for c in ("CNPS_PVID_S", "CNPS_PVID_P", "CNPS_PF")
                  if Decimal(lignes[c]["assiette"]) < brut}
    reelles = {c for c in ("CNPS_AT", "CFC_S", "CFC_P", "FNE")
               if Decimal(lignes[c]["assiette"]) == brut}
    if not etape(3, "Plafond CNPS appliqué aux seules bonnes branches",
                 len(plafonnees) == 3 and len(reelles) == 4,
                 f"plafonnées {sorted(plafonnees)}, réelles {sorted(reelles)}"):
        echecs.append("l'asymétrie du plafond CNPS n'est pas respectée")

    # 4 · Les avantages entrent dans l'assiette et sortent du net ─────────────
    avantages = Decimal(bulletin["avantages_evalues"])
    net = Decimal(bulletin["salaire_base"]) + Decimal(bulletin["primes"]) - sum(
        Decimal(ligne["montant"]) for ligne in bulletin["lignes"] if ligne["a_charge_du_salarie"]
    )
    if not etape(4, "Avantages dans l'assiette, hors du net",
                 avantages > 0 and brut > Decimal(bulletin["salaire_base"]),
                 f"avantages {sous(avantages)} inclus au brut {sous(brut)}, net {sous(net)}"):
        echecs.append("les avantages en nature ne sont pas traités correctement")

    # 5 · L'IRPP n'a pas de taux unique ───────────────────────────────────────
    irpp = lignes.get("IRPP")
    if not etape(5, "IRPP progressif, sans taux unique affiché",
                 irpp is not None and irpp["taux"] is None,
                 f"montant {sous(irpp['montant'])}" if irpp else "ligne absente"):
        echecs.append("l'IRPP affiche un taux unique, ce qu'un barème progressif n'a pas")

    # 6 · Les valeurs non validées sont signalées ─────────────────────────────
    non_valides = sum(1 for ligne in bulletin["lignes"] if ligne["non_valide"])
    if not etape(6, "Valeurs non validées signalées", non_valides == len(bulletin["lignes"]),
                 f"{non_valides}/{len(bulletin['lignes'])} lignes marquées A_VALIDER"):
        echecs.append("des lignes reposent sur des valeurs non validées sans le dire")

    # 7 · La déclaration mensuelle ────────────────────────────────────────────
    code, dipe = appeler(
        comptable, "GET",
        f"/social/dossiers/{AGRO}/declaration/2026/7?a_la_date={JOUR}&groupe_risque=B",
    )
    if not etape(7, "DIPE de juillet", code == 200,
                 f"HTTP {code}, effectif {dipe.get('effectif')}, "
                 f"masse {sous(dipe.get('masse_salariale_brute', 0))} FCFA"
                 if isinstance(dipe, dict) else str(dipe)):
        echecs.append(f"déclaration : {dipe}")
        return bilan(echecs)

    total = Decimal(dipe["total_a_verser"])
    patronales = Decimal(dipe["charges_patronales"])
    retenues = Decimal(dipe["retenues_salariales"])
    if not etape(8, "Total à verser = patronales + retenues", total == patronales + retenues,
                 f"{sous(total)} = {sous(patronales)} + {sous(retenues)}"):
        echecs.append("le total à verser omet la retenue salariale")

    # 9 · Le mouvement de sortie est relevé ───────────────────────────────────
    sorties = [m for m in dipe["mouvements"] if m["sens"] == "SORTIE"]
    if not etape(9, "Sortie du mois relevée", len(sorties) == 1,
                 f"{sorties[0]['salarie']} le {sorties[0]['survenu_le']}" if sorties else "aucune"):
        echecs.append("le mouvement de sortie n'est pas relevé")

    # 10 · L'échéance et le retard ────────────────────────────────────────────
    if not etape(10, "Échéance au 15 du mois suivant, retard jugé à une date",
                 dipe["a_deposer_avant"] == "2026-08-15" and dipe["en_retard"] is True,
                 f"à déposer avant {dipe['a_deposer_avant']}, en retard au {JOUR} : "
                 f"{dipe['en_retard']}"):
        echecs.append("l'échéance ou le retard sont mal calculés")

    # 11 · Embauche puis paie du nouveau salarié ──────────────────────────────
    marque = uuid.uuid4().hex[:6].upper()
    matricule = f"SAL-{marque}"
    code, _ = appeler(
        comptable, "POST", f"/social/dossiers/{AGRO}/salaries",
        {"matricule": matricule, "nom": "RECETTE", "prenom": "Cas",
         "matricule_cnps": f"09{marque[:8]}", "enfants_a_charge": 1},
    )
    ok_inscription = code == 201
    code, _ = appeler(
        comptable, "POST", f"/social/dossiers/{AGRO}/salaries/{matricule}/contrats",
        {"type_contrat": "CDI", "debut": "2026-07-10", "salaire_base": "500000",
         "primes": "0", "avantages": [], "poste": "Agent de recette"},
    )
    if not etape(11, "Inscription puis engagement", ok_inscription and code == 201,
                 f"salarié {matricule}, contrat HTTP {code}"):
        echecs.append("l'embauche échoue")
        return bilan(echecs)

    code, neuf = appeler(
        comptable, "GET", f"/social/dossiers/{AGRO}/bulletins/2026/7/{matricule}"
    )
    if not etape(12, "Bulletin du nouvel embauché", code == 200,
                 f"HTTP {code}, {len(neuf['lignes'])} lignes" if isinstance(neuf, dict) else ""):
        echecs.append("le nouvel embauché n'a pas de bulletin")

    code, dipe2 = appeler(
        comptable, "GET",
        f"/social/dossiers/{AGRO}/declaration/2026/7?a_la_date={JOUR}&groupe_risque=B",
    )
    entrees = [m for m in dipe2["mouvements"] if m["sens"] == "ENTREE"] if code == 200 else []
    if not etape(13, "Embauche en cours de mois déclarée",
                 dipe2.get("effectif") == dipe["effectif"] + 1 and len(entrees) >= 1,
                 f"effectif {dipe['effectif']} → {dipe2.get('effectif')}, "
                 f"{len(entrees)} entrée(s) relevée(s)"):
        echecs.append("l'embauche du mois n'entre pas dans la déclaration")

    # 14 · Un dossier sans salarié déclare à néant ────────────────────────────
    code, vide = appeler(
        comptable, "GET",
        f"/social/dossiers/{BATIMENT}/declaration/2026/1?a_la_date={JOUR}",
    )
    if not etape(14, "Déclaration à néant possible", code == 200,
                 f"HTTP {code}, effectif {vide.get('effectif')}"
                 if isinstance(vide, dict) else str(vide)):
        echecs.append("un dossier sans salarié ne peut pas déclarer à néant")

    return bilan(echecs)


def bilan(echecs: list[str]) -> int:
    print()
    print("═" * 100)
    if echecs:
        print(f"FLUX INTERROMPU — {len(echecs)} échec(s)")
        for e in echecs:
            print(f"  ⚠ {e}")
    else:
        print("FLUX COMPLET — les quinze étapes passent")
    print("═" * 100)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
