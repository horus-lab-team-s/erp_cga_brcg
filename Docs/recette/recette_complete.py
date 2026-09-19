"""Recette complète : profils, écrans, autorisations API, portée, écritures.

Cinq passes, dans l'ordre où un défaut coûte le plus cher :

    A  connexion            qui entre, qui doit être refusé
    B  écrans               ce que chaque profil peut ouvrir
    C  autorisations API    le refus tient-il sans l'interface
    D  portée par dossier   un profil habilité voit-il un dossier voisin
    E  flux d'écriture      les actes qui modifient l'état

Le point le plus important est **C**. Une garde qui ne vit que dans la page
Next protège l'écran, pas la donnée : il suffit d'appeler l'API avec le même
témoin pour la contourner. Chaque refus constaté en B est donc rejoué en C,
directement contre le backend.

La passe D vaut pour un centre de gestion ce que vaut l'isolation dans une
banque : un comptable habilité sur trois dossiers qui lit le quatrième n'est pas
un défaut d'ergonomie, c'est une violation du secret professionnel.

Une seule session est ouverte par compte, puis réutilisée partout. Le limiteur
de débit refuse au-delà de 30 connexions par cinq minutes, et une recette qui se
fait limiter elle-même produit des faux défauts.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/tmp/cga-pg")
from verifier_profils import (
    COMPTES,
    COMPTES_REFUSES,
    ECRANS,
    Client,
    champs_caches,
    classer,
    permissions_de,
)

FRONT = "http://localhost:3011"
API = "http://127.0.0.1:8010"
MOT_DE_PASSE = "cabinet brcg douala 2026"

#: Les dossiers de démonstration, et qui est censé les voir.
DOSSIERS = {
    "M065544332211L": "AGRO-NKOLO SA",
    "M071122334455J": "BOULANGERIE LA COLOMBE",
    "M081234567890P": "SARL BATIMENT PLUS",
    "M093344556677N": "CLINIQUE LE BON SAMARITAIN",
    "P019876543210K": "ETS TCHOUMBA & FILS",
    "P027788990011M": "CABINET NGUEMA CONSEIL",
}

#: La portée relevée en base, par compte. `None` vaut « tout le portefeuille ».
PORTEE: dict[str, set[str] | None] = {
    "b.mballa@cga-brcg.cm": None,
    "s.onana@cga-brcg.cm": None,
    "l.fotso@cga-brcg.cm": {"M065544332211L", "M071122334455J", "M081234567890P"},
    "c.ndongo@cga-brcg.cm": {"P019876543210K", "P027788990011M"},
    "a.bouba@cga-brcg.cm": None,
    "r.ebolo@cga-brcg.cm": None,
    "p.moukouri@cga-brcg.cm": None,
    "jp.nkoa@batimentplus.cm": {"M081234567890P"},
    "mc.essomba@lacolombe.cm": {"M071122334455J"},
    "g.atangana@inspection.cm": {"M065544332211L"},
}

#: Routes de lecture de l'API, et la permission que chacune devrait exiger.
#: ⚠️ Les paramètres obligatoires sont fournis. Sans eux, l'API répond 422 —
#: et un 422 ne dit **pas** si la permission aurait refusé : il dit seulement
#: que la requête n'a pas passé la validation. Une recette qui s'arrête au 422
#: conclut « refusé » là où l'appel n'a jamais été jugé.
JOUR = "2026-08-17"
D1 = "M065544332211L"
ROUTES_LECTURE: list[tuple[str, str, str]] = [
    ("GET", f"/portefeuille/entreprises?a_la_date={JOUR}", "LIRE_DOSSIER"),
    ("GET", f"/collecte/pieces?a_la_date={JOUR}", "LIRE_PIECE"),
    ("GET", "/collecte/demandes", "LIRE_PIECE"),
    ("GET", "/collecte/doublons", "ARBITRER_DOUBLON"),
    ("GET", "/comptabilite/journaux", "LIRE_COMPTABILITE"),
    ("GET", f"/comptabilite/dossiers/{D1}/balance?exercice=2026", "LIRE_COMPTABILITE"),
    ("GET", f"/obligations/dossiers/{D1}/echeancier?exercice=2026&a_la_date={JOUR}",
     "LIRE_DOSSIER"),
    (
        "GET",
        (
            f"/obligations/dossiers/{D1}/declaration-tva"
            "?periode_debut=2026-07-01&periode_fin=2026-07-31"
        ),
        "LIRE_COMPTABILITE",
    ),
    ("GET", f"/transverse/comptes?a_la_date={JOUR}", "GERER_COMPTES"),
    ("GET", "/transverse/audit", "LIRE_AUDIT"),
]


# ── Appels directs à l'API, avec le témoin obtenu par le formulaire ──────────
def appeler(
    client: Client, methode: str, chemin: str, corps: dict | None = None
) -> tuple[int, str]:
    donnees = json.dumps(corps).encode() if corps is not None else None
    entetes = {"Accept": "application/json", "User-Agent": "recette-cga/1.0"}
    if corps is not None:
        entetes["Content-Type"] = "application/json"
    if client.temoins:
        entetes["Cookie"] = "; ".join(f"{c}={v}" for c, v in client.temoins.items())
    requete = urllib.request.Request(API + chemin, data=donnees, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return reponse.status, reponse.read().decode("utf-8", "replace")[:400]
    except urllib.error.HTTPError as erreur:
        return erreur.code, erreur.read().decode("utf-8", "replace")[:400]
    except urllib.error.URLError as erreur:
        return 0, str(erreur)


def ouvrir(adresse: str) -> tuple[Client, bool]:
    client = Client()
    _, page, _ = client.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = adresse
    champs["motDePasse"] = MOT_DE_PASSE
    client.soumettre("/connexion", champs)
    return client, "cga_session" in client.temoins


def titre(numero: str, libelle: str) -> None:
    print()
    print("═" * 104)
    print(f"{numero} · {libelle}")
    print("═" * 104)


def main() -> int:
    anomalies: list[str] = []
    sessions: dict[str, Client] = {}

    # ── A · Connexion ────────────────────────────────────────────────────────
    titre("A", "CONNEXION PAR PROFIL")
    for adresse, libelle, _roles in COMPTES:
        client, ouverte = ouvrir(adresse)
        if ouverte:
            sessions[adresse] = client
        else:
            anomalies.append(f"[A] connexion impossible pour {libelle} ({adresse})")
        print(f"  {'✓' if ouverte else '✗'} {libelle:<28} {adresse:<32}"
              f" {'session ouverte' if ouverte else 'REFUSÉ ⚠'}")
    print()
    for adresse, libelle in COMPTES_REFUSES:
        _, ouverte = ouvrir(adresse)
        if ouverte:
            anomalies.append(f"[A] {libelle} ({adresse}) a ouvert une session — devait être refusé")
        print(f"  {'✗' if ouverte else '✓'} {libelle:<28} {adresse:<32}"
              f" {'ACCEPTÉ ⚠' if ouverte else 'refusé'}")

    # ── B · Écrans ───────────────────────────────────────────────────────────
    titre("B", "ÉCRANS × PROFILS")
    entete = f"{'écran':<28}{'permission':<20}" + "".join(
        f"{lib.split()[0][:10]:<11}" for _a, lib, _r in COMPTES
    )
    print(entete)
    print("─" * len(entete))
    for chemin, permission in ECRANS:
        ligne = f"{chemin:<28}{permission:<20}"
        for adresse, libelle, roles in COMPTES:
            client = sessions.get(adresse)
            if client is None:
                ligne += f"{'—':<11}"
                continue
            code, page, cible = client.lire(chemin)
            etat = classer(code, page, cible).split("→")[0]
            attendu = permission in permissions_de(roles)
            conforme = (etat == "ouvert") == attendu and etat != "panne"
            if not conforme:
                anomalies.append(
                    f"[B] {chemin} · {libelle} ({'/'.join(roles)}) : {etat}, "
                    f"attendu {'ouvert' if attendu else 'refusé'}"
                )
            ligne += f"{(etat + ('' if conforme else ' ⚠'))[:10]:<11}"
        print(ligne)

    # ── C · Autorisations côté API ───────────────────────────────────────────
    titre("C", "AUTORISATIONS API — LE REFUS TIENT-IL SANS L'INTERFACE")
    entete = f"{'route':<52}{'permission':<20}" + "".join(
        f"{lib.split()[0][:10]:<11}" for _a, lib, _r in COMPTES
    )
    print(entete)
    print("─" * len(entete))
    for methode, chemin, permission in ROUTES_LECTURE:
        ligne = f"{methode + ' ' + chemin:<52}{permission:<20}"
        for adresse, libelle, roles in COMPTES:
            client = sessions.get(adresse)
            if client is None:
                ligne += f"{'—':<11}"
                continue
            code, _ = appeler(client, methode, chemin)
            attendu = permission in permissions_de(roles)
            # Un dossier hors portée se refuse aussi : on ne juge ici que le
            # couple (permission, code), la portée est la passe D.
            hors_portee = (
                D1 in chemin
                and (p := PORTEE[adresse]) is not None
                and "M065544332211L" not in p
            )
            if hors_portee:
                attendu = False
            accorde = code == 200
            conforme = accorde == attendu
            if not conforme:
                anomalies.append(
                    f"[C] {methode} {chemin} · {libelle} ({'/'.join(roles)}) : "
                    f"HTTP {code}, attendu {'200' if attendu else 'refus'}"
                )
            ligne += f"{(str(code) + ('' if conforme else ' ⚠')):<11}"
        print(ligne)

    # ── D · Portée par dossier ───────────────────────────────────────────────
    titre("D", "PORTÉE — UN PROFIL HABILITÉ VOIT-IL LE DOSSIER VOISIN")
    entete = f"{'compte':<30}{'portée':<8}" + "".join(f"{niu[:12]:<15}" for niu in DOSSIERS)
    print(entete)
    print("─" * len(entete))
    for adresse, libelle, roles in COMPTES:
        client = sessions.get(adresse)
        if client is None:
            continue
        portee = PORTEE[adresse]
        ligne = f"{libelle:<30}{('tout' if portee is None else str(len(portee))):<8}"
        for niu, denomination in DOSSIERS.items():
            code, _ = appeler(client, "GET", f"/portefeuille/entreprises/{niu}")
            lisible = "LIRE_DOSSIER" in permissions_de(roles)
            attendu = lisible and (portee is None or niu in portee)
            accorde = code == 200
            conforme = accorde == attendu
            if not conforme:
                anomalies.append(
                    f"[D] {libelle} ({'/'.join(roles)}, portée "
                    f"{'tout' if portee is None else sorted(portee)}) lit {niu} "
                    f"({denomination}) : HTTP {code}, attendu {'200' if attendu else 'refus'}"
                )
            marque = "·" if not accorde else "LIT"
            ligne += f"{(marque + ('' if conforme else ' ⚠')):<15}"
        print(ligne)

    # ── E · Flux d'écriture ──────────────────────────────────────────────────
    titre("E", "FLUX D'ÉCRITURE")
    # Charges utiles **valides** : c'est la seule façon de savoir si la
    # permission barre l'appel. Avec un corps invalide, le 422 masque le verdict.
    piece = {
        "identifiant": "PJ-RECETTE-0001",
        "entreprise": D1,
        "canal": "DEPOT_CABINET",
        "depose_le": JOUR,
        "recue_le": JOUR,
    }
    controle = {
        "document": {
            "type": "FACTURE_ACHAT",
            "reference": "F-2026-9001",
            "date_emission": JOUR,
        },
        "emetteur": {"denomination": "FOURNISSEUR TEST", "niu": "M011111111111A"},
        "montants": {"total_ht": "1000000", "total_tva": "192500", "total_ttc": "1192500"},
    }
    invitation = {
        "courriel": "recette.temoin@cga-brcg.cm",
        "nom": "TEMOIN",
        "prenom": "Recette",
        "role": "COMPTABLE",
        "depuis": JOUR,
    }
    depot = {"numero": "TVA-RECETTE-01", "depose_le": JOUR}
    tva = f"?periode_debut=2026-07-01&periode_fin=2026-07-31&a_la_date={JOUR}"
    ecritures: list[tuple[str, str, str, dict | None, str]] = [
        # (compte, méthode, route, corps, attendu)
        ("s.onana@cga-brcg.cm", "POST", "/collecte/pieces", piece, "refus"),
        ("g.atangana@inspection.cm", "POST", "/collecte/pieces", piece, "refus"),
        ("r.ebolo@cga-brcg.cm", "POST", "/collecte/pieces", piece, "refus"),
        ("jp.nkoa@batimentplus.cm", "POST", "/conformite/controler", controle, "refus"),
        ("g.atangana@inspection.cm", "POST", "/transverse/comptes/invitation",
         invitation, "refus"),
        ("l.fotso@cga-brcg.cm", "POST", "/transverse/comptes/invitation", invitation, "refus"),
        ("b.mballa@cga-brcg.cm", "POST", "/transverse/comptes/invitation", invitation, "refus"),
        ("l.fotso@cga-brcg.cm", "POST", f"/obligations/dossiers/{D1}/depot-tva{tva}",
         depot, "refus"),
        ("g.atangana@inspection.cm", "POST", f"/obligations/dossiers/{D1}/depot-tva{tva}",
         depot, "refus"),
        # Ceux-là doivent **passer** : c'est le contre-test. Une recette qui ne
        # vérifie que des refus valide aussi bien un système qui refuse tout.
        ("l.fotso@cga-brcg.cm", "POST", "/collecte/pieces", piece, "accord"),
        ("a.bouba@cga-brcg.cm", "POST", "/conformite/controler", controle, "accord"),
        ("s.onana@cga-brcg.cm", "POST", "/transverse/comptes/invitation",
         invitation, "accord"),
    ]
    for adresse, methode, chemin, corps, attendu in ecritures:
        client = sessions.get(adresse)
        if client is None:
            continue
        code, contenu = appeler(client, methode, chemin, corps)
        # 422 = la permission est passée, seule la charge utile est invalide.
        # C'est un accord déguisé : la recette doit le compter comme tel.
        refuse = code in (401, 403, 404)
        # 422 après une charge utile valide signale un désaccord de contrat,
        # pas une autorisation : on le signale au lieu de le compter d'un côté.
        conforme = refuse if attendu == "refus" else code in (200, 201, 202, 204, 409)
        libelle = next(lib for a, lib, _ in COMPTES if a == adresse)
        if not conforme:
            anomalies.append(
                f"[E] {methode} {chemin} · {libelle} : HTTP {code} — "
                f"attendu {attendu}, la permission n'a pas barré l'appel"
            )
        print(f"  {'✓' if conforme else '✗'} {libelle:<26} {attendu:<7} "
              f"{methode} {chemin.split('?')[0]:<46} HTTP {code}"
              f"{'' if conforme else '  ⚠ ' + contenu[:90]}")

    # ── Bilan ────────────────────────────────────────────────────────────────
    titre("F", f"ANOMALIES — {len(anomalies)}")
    for anomalie in anomalies:
        print(f"  ⚠ {anomalie}")
    if not anomalies:
        print("  aucune")
    return 1 if anomalies else 0


if __name__ == "__main__":
    sys.exit(main())
