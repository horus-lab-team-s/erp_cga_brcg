"""Le flux I · Création d'entreprise, de bout en bout, contre PostgreSQL.

Qualification → constitution → dépôt CFCE → suivi → livraison → conversion, puis
la vérification qui compte : l'entreprise créée apparaît-elle au portefeuille, et
F · Obligations lui calcule-t-il un échéancier sans qu'on le lui ait demandé ?

C'est cette dernière question qui valide la promesse du contexte. Le reste peut
passer et la promesse rester creuse.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, "/tmp/cga-pg")
from verifier_profils import Client, champs_caches

API = "http://127.0.0.1:8010"
FRONT = "http://localhost:3011"
JOUR = "2026-08-17"
MOT_DE_PASSE = "cabinet brcg douala 2026"
#: Le chargé de formalités — seul détenteur de SUIVRE_FORMALITE.
FORMALITES = "p.moukouri@cga-brcg.cm"
#: Un comptable, qui ne détient pas cette permission. Sert au contre-test.
COMPTABLE = "l.fotso@cga-brcg.cm"


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


def etape(n: int, libelle: str, code: int, attendus: tuple[int, ...], detail: str = "") -> bool:
    ok = code in attendus
    print(f"  {'✓' if ok else '✗'} {n:>2}. {libelle:<52} HTTP {code}  {detail}")
    return ok


def main() -> int:
    echecs: list[str] = []
    marque = uuid.uuid4().hex[:6].upper()
    reference = f"CR-RECETTE-{marque}"
    niu = f"M2{marque}00011K"[:14]
    rccm = f"RC/DLA/2026/B/{marque[:4]}"

    print("═" * 100)
    print("FLUX I · CRÉATION D'ENTREPRISE — DU PORTEUR DE PROJET À L'ADHÉRENT")
    print("═" * 100)

    chargee = session(FORMALITES)
    comptable = session(COMPTABLE)

    # 0 · Le contre-test : la permission barre-t-elle vraiment ? ──────────────
    code, _ = appeler(comptable, "GET", f"/creations/pipeline?a_la_date={JOUR}")
    if not etape(0, "Un comptable est refusé sur le pipeline", code, (403,),
                 "SUIVRE_FORMALITE exigée"):
        echecs.append("la permission SUIVRE_FORMALITE ne barre pas le pipeline")

    # 1 · La checklist, avant même qu'un dossier existe ───────────────────────
    code, pieces = appeler(chargee, "GET", "/creations/checklist/SARL")
    nb = len(pieces) if isinstance(pieces, list) else 0
    if not etape(1, "Checklist d'une SARL", code, (200,), f"{nb} pièces"):
        echecs.append("checklist")

    # 2 · Le pipeline de démonstration ────────────────────────────────────────
    code, pipeline = appeler(chargee, "GET", f"/creations/pipeline?a_la_date={JOUR}")
    n0 = len(pipeline) if isinstance(pipeline, list) else 0
    if not etape(2, "Pipeline lisible", code, (200,), f"{n0} dossiers"):
        echecs.append("pipeline")

    # 3 · Ouvrir un dossier ───────────────────────────────────────────────────
    code, dossier = appeler(
        chargee, "POST", f"/creations?a_la_date={JOUR}",
        {
            "reference": reference,
            "fondateur": {
                "nom": "KAMGA", "prenom": "Sylvie",
                "courriel": f"s.kamga+{marque}@exemple.cm", "telephone": "+237699887766",
            },
            "denomination_souhaitee": f"SYLVIE NEGOCE {marque} SARL",
            "forme_juridique": "SARL",
            "activite": "Négoce de matériaux",
            "siege": "Douala, Akwa",
            "capital": "1500000",
        },
    )
    attendues = len(dossier.get("pieces", [])) if isinstance(dossier, dict) else 0
    if not etape(3, "Ouverture du dossier", code, (201,),
                 f"{reference}, {attendues} pièces attendues"):
        echecs.append(f"ouverture : {dossier}")
        return bilan(echecs)

    # 4 · Le dépôt est refusé tant que le dossier est incomplet ───────────────
    appeler(chargee, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
            {"vers": "CONSTITUTION"})
    code, refus = appeler(chargee, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
                          {"vers": "DEPOT_CFCE"})
    nomme = isinstance(refus, dict) and "Statuts" in str(refus.get("detail"))
    if not etape(4, "Dépôt refusé, pièces manquantes nommées", code, (409,),
                 "pièces citées" if nomme else "⚠ refus muet"):
        echecs.append("le dépôt d'un dossier incomplet n'est pas refusé")

    # 5 · Fournir toutes les pièces ───────────────────────────────────────────
    _, fiche = appeler(chargee, "GET", f"/creations/{reference}?a_la_date={JOUR}")
    codes = [p["code"] for p in fiche["dossier"]["pieces"]]
    for code_piece in codes:
        appeler(chargee, "POST", f"/creations/{reference}/pieces?a_la_date={JOUR}",
                {"code": code_piece})
    code, fiche = appeler(chargee, "GET", f"/creations/{reference}?a_la_date={JOUR}")
    if not etape(5, "Dossier complet et déposable", code, (200,),
                 f"déposable={fiche.get('deposable')}"):
        echecs.append("diagnostic")
    if not fiche.get("deposable"):
        echecs.append("le dossier complet n'est pas déclaré déposable")

    # 6 · Le tunnel jusqu'au suivi ────────────────────────────────────────────
    for vers in ("DEPOT_CFCE", "SUIVI_IMMATRICULATION"):
        code, _ = appeler(chargee, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
                          {"vers": vers})
        if code != 200:
            echecs.append(f"franchissement {vers}")
    etape(6, "Dépôt CFCE puis suivi d'immatriculation", code, (200,))

    # 7 · Le RCCM seul ne suffit pas à livrer ─────────────────────────────────
    appeler(chargee, "POST", f"/creations/{reference}/identifiants",
            {"rccm": rccm, "rccm_obtenu_le": "2026-07-02"})
    code, refus = appeler(chargee, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
                          {"vers": "LIVRAISON"})
    if not etape(7, "Livraison refusée sans NIU", code, (409,),
                 "sans NIU il n'y a pas de contribuable"):
        echecs.append("la livraison est possible sans NIU")

    # 8 · Le NIU arrive, la livraison passe ───────────────────────────────────
    appeler(chargee, "POST", f"/creations/{reference}/identifiants",
            {"niu": niu, "niu_obtenu_le": "2026-07-25"})
    code, _ = appeler(chargee, "POST", f"/creations/{reference}/etape?a_la_date={JOUR}",
                      {"vers": "LIVRAISON"})
    if not etape(8, "Livraison", code, (200,)):
        echecs.append("livraison")

    # 9 · La conversion ───────────────────────────────────────────────────────
    code, resultat = appeler(
        chargee, "POST", f"/creations/{reference}/conversion?a_la_date={JOUR}",
        {"regime": "REEL", "centre": "CDI", "adherent": True},
    )
    detail = ""
    if isinstance(resultat, dict):
        detail = (f"NIU {resultat.get('niu')}, née le {resultat.get('date_creation')}, "
                  f"portefeuille={resultat.get('enregistree_au_portefeuille')}")
    if not etape(9, "Conversion en entreprise du portefeuille", code, (200,), detail):
        echecs.append(f"conversion : {resultat}")
        return bilan(echecs)

    # 10 · La date de création est celle du RCCM, pas celle du jour ───────────
    juste = isinstance(resultat, dict) and resultat.get("date_creation") == "2026-07-02"
    if not etape(10, "Date de création = date du RCCM", 200 if juste else 0, (200,),
                 f"{resultat.get('date_creation')} (RCCM du 2026-07-02)"):
        echecs.append("la date de création n'est pas celle du RCCM")

    # 11 · L'entreprise est réellement au portefeuille ────────────────────────
    code, fiche_entreprise = appeler(chargee, "GET", f"/portefeuille/entreprises/{niu}")
    denomination = (
        fiche_entreprise.get("denomination", "") if isinstance(fiche_entreprise, dict) else ""
    )
    if not etape(11, "Entreprise lisible au portefeuille", code, (200,), denomination):
        echecs.append("l'entreprise convertie est absente du portefeuille")

    # 12 · LA PROMESSE DU CONTEXTE : l'échéancier existe sans qu'on l'ait demandé
    code, echeancier = appeler(
        chargee, "GET",
        f"/obligations/dossiers/{niu}/echeancier?exercice=2026&a_la_date={JOUR}",
    )
    nb = 0
    if isinstance(echeancier, list):
        nb = len(echeancier)
    elif isinstance(echeancier, dict):
        nb = len(echeancier.get("obligations", []) or [])
    if not etape(12, "Échéancier fiscal calculé d'office", code, (200,),
                 f"{nb} obligations, sans qu'on l'ait généré"):
        echecs.append("aucun échéancier pour l'entreprise créée")
    if nb == 0:
        echecs.append("l'échéancier est vide : la promesse du contexte n'est pas tenue")

    # 13 · On ne convertit pas deux fois ──────────────────────────────────────
    code, _ = appeler(chargee, "POST", f"/creations/{reference}/conversion?a_la_date={JOUR}",
                      {"regime": "REEL", "centre": "CDI"})
    if not etape(13, "Seconde conversion refusée", code, (409,)):
        echecs.append("un dossier converti se reconvertit")

    return bilan(echecs)


def bilan(echecs: list[str]) -> int:
    print()
    print("═" * 100)
    if echecs:
        print(f"FLUX INTERROMPU — {len(echecs)} échec(s)")
        for e in echecs:
            print(f"  ⚠ {e}")
    else:
        print("FLUX COMPLET — les quatorze étapes passent")
    print("═" * 100)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
