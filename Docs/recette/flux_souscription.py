"""Le flux M · Souscription, de bout en bout, comme un prospect le vit.

Devis → engagement → encaissement → activation → première connexion. C'est le
seul parcours qui traverse la frontière entre le site public et l'ERP : on y
entre sans compte, on en sort adhérent. Un défaut ici ne se rattrape pas — le
prospect a payé et n'a pas d'accès.

Le mode démonstration valide le paiement d'office ; la route de simulation est
refusée dès que des identifiants Tara réels sont configurés, ce qui a été
vérifié séparément.
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
JOUR = "2026-08-17"
FRONT = "http://localhost:3011"


def appeler(methode: str, chemin: str, corps: dict | None = None) -> tuple[int, dict | str]:
    donnees = json.dumps(corps).encode() if corps is not None else None
    entetes = {"Accept": "application/json"}
    if corps is not None:
        entetes["Content-Type"] = "application/json"
    requete = urllib.request.Request(API + chemin, data=donnees, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            brut = reponse.read().decode()
            return reponse.status, json.loads(brut) if brut else {}
    except urllib.error.HTTPError as erreur:
        brut = erreur.read().decode()
        try:
            return erreur.code, json.loads(brut)
        except json.JSONDecodeError:
            return erreur.code, brut[:300]


def etape(numero: int, libelle: str, code: int, attendu: tuple[int, ...], detail: str = "") -> bool:
    ok = code in attendu
    print(f"  {'✓' if ok else '✗'} {numero}. {libelle:<46} HTTP {code}  {detail}")
    return ok


def main() -> int:
    echecs: list[str] = []
    # ⚠️ Une adresse et un NIU neufs à chaque exécution. Rejoué avec les mêmes,
    # le parcours s'arrête à l'activation : le compte existe déjà, la
    # souscription reste `PAYEE` avec `a_activer=True`. C'est le bon
    # comportement du produit — on ne crée pas deux comptes pour un adhérent —
    # mais un script non rejouable finit par se lire comme une régression.
    marque = uuid.uuid4().hex[:8]
    courriel = f"prospect.recette+{marque}@exemple.cm"
    niu = f"M{marque.upper()[:6]}{marque.upper()[6:8]}0011Q"[:14]

    print("═" * 96)
    print("FLUX M · SOUSCRIPTION — DU PROSPECT À L'ADHÉRENT")
    print("═" * 96)

    # 1 · Le catalogue, tel que le site public le lit ─────────────────────────
    code, services = appeler("GET", f"/souscription/services?a_la_date={JOUR}")
    if not etape(1, "Catalogue des services (public)", code, (200,),
                 f"{len(services) if isinstance(services, list) else 0} services"):
        echecs.append("catalogue")
        return bilan(echecs)
    adhesion = next((s for s in services if s["code"] == "ADHESION"), services[0])
    formule = (adhesion.get("formules") or [{}])[0]

    # 2 · Le devis ────────────────────────────────────────────────────────────
    demande = {
        "prospect": {
            "nom": "NGOUNOU",
            "prenom": "Aline",
            "courriel": courriel,
            "telephone": "699000111",
            "denomination": "ALINE DISTRIBUTION SARL",
            "niu": niu,
            "chiffre_affaires_declare": "45000000",
        },
        "lignes": [
            {
                "service": adhesion["code"],
                "libelle": adhesion["libelle"],
                "formule": formule.get("code"),
                "montant": str(formule.get("montant") or "35000"),
                "periodicite": "MENSUELLE",
                "nature": "ABONNEMENT",
                "chiffree": True,
            }
        ],
    }
    code, devis = appeler("POST", f"/souscription/devis?a_la_date={JOUR}", demande)
    reference = devis.get("reference") if isinstance(devis, dict) else None
    if not etape(2, "Création du devis", code, (200, 201), f"référence {reference}"):
        echecs.append(f"devis : {devis}")
        return bilan(echecs)

    # 3 · Relecture du devis, sans session ────────────────────────────────────
    code, _ = appeler("GET", f"/souscription/devis/{reference}?a_la_date={JOUR}")
    if not etape(3, "Relecture du devis par sa référence", code, (200,)):
        echecs.append("relecture devis")

    # 4 · L'engagement — c'est lui qui crée le paiement ───────────────────────
    code, engagement = appeler(
        "POST",
        f"/souscription/devis/{reference}/engagement?a_la_date={JOUR}",
        {"niu": niu},
    )
    detail = ""
    if isinstance(engagement, dict):
        detail = " ".join(
            f"{c}={engagement[c]}" for c in ("etat", "souscription") if c in engagement
        )
    if not etape(4, "Engagement (paiement validé d'office en démo)", code, (200, 201), detail):
        echecs.append(f"engagement : {engagement}")
        return bilan(echecs)

    # 5 · Le courriel d'activation, tel que la recette peut le lire ───────────
    code, courriels = appeler("GET", "/transverse/courriels")
    lien = None
    if isinstance(courriels, list):
        for message in reversed(courriels):
            texte = json.dumps(message)
            if courriel in texte:
                for cle in ("lien", "url"):
                    if cle in message:
                        lien = message[cle]
                        break
                if lien is None:
                    debut = texte.find("/activation")
                    if debut != -1:
                        lien = texte[debut : texte.find('"', debut)]
                break
    if not etape(5, "Courriel d'activation produit", code, (200,),
                 f"lien {'trouvé' if lien else 'INTROUVABLE'}"):
        echecs.append("courriels")
    if lien is None:
        echecs.append("aucun lien d'activation dans le courriel")
        return bilan(echecs)

    # 6 · L'écran d'activation, atteint par le lien du courriel ───────────────
    chemin = lien if lien.startswith("/") else lien.split(FRONT, 1)[-1]
    client = Client()
    code, page, _ = client.lire(chemin)
    if not etape(6, "Ouverture du lien d'activation", code, (200,), chemin[:52]):
        echecs.append(f"page d'activation : HTTP {code}")
        return bilan(echecs)

    # 7 · La définition du mot de passe, par le vrai formulaire ───────────────
    champs = champs_caches(page)
    champs["motDePasse"] = "Recette Souscription 2026 !"
    champs["confirmation"] = "Recette Souscription 2026 !"
    code, _corps, cible = client.soumettre(chemin, champs)
    if not etape(7, "Définition du mot de passe", code, (200, 302, 303, 307),
                 f"→ {cible or 'aucune redirection'}"):
        echecs.append("définition du mot de passe")

    # 8 · La première connexion de l'adhérent tout neuf ───────────────────────
    neuf = Client()
    _, page, _ = neuf.lire("/connexion")
    champs = champs_caches(page)
    champs["courriel"] = courriel
    champs["motDePasse"] = "Recette Souscription 2026 !"
    code, _, cible = neuf.soumettre("/connexion", champs)
    ouverte = "cga_session" in neuf.temoins
    if not etape(8, "Première connexion du nouvel adhérent", code, (302, 303, 307),
                 f"→ {cible}  témoin {'posé' if ouverte else 'ABSENT'}"):
        echecs.append("première connexion")
    if not ouverte:
        echecs.append("aucun témoin de session après activation")
        return bilan(echecs)

    # 9 · Son espace s'ouvre ──────────────────────────────────────────────────
    code, page, _ = neuf.lire("/mon-espace")
    if not etape(9, "Accès à /mon-espace", code, (200,),
                 "refus affiché" if "Accès réservé" in page else "contenu rendu"):
        echecs.append("mon-espace")

    # 10 · Et il ne voit rien du portefeuille du cabinet ──────────────────────
    entetes = {"Cookie": "; ".join(f"{c}={v}" for c, v in neuf.temoins.items())}
    requete = urllib.request.Request(
        API + "/transverse/comptes?a_la_date=2026-08-17", headers=entetes
    )
    try:
        with urllib.request.urlopen(requete, timeout=20) as reponse:
            code = reponse.status
    except urllib.error.HTTPError as erreur:
        code = erreur.code
    if not etape(10, "Refus sur les comptes du cabinet", code, (401, 403, 404)):
        echecs.append("le nouvel adhérent atteint les comptes du cabinet")

    return bilan(echecs)


def bilan(echecs: list[str]) -> int:
    print()
    print("═" * 96)
    if echecs:
        print(f"FLUX INTERROMPU — {len(echecs)} échec(s)")
        for e in echecs:
            print(f"  ⚠ {e}")
    else:
        print("FLUX COMPLET — les dix étapes passent")
    print("═" * 96)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
