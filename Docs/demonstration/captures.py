#!/usr/bin/env python3
"""Photographie les écrans du produit, profil par profil, contre la pile qui tourne.

─────────────────────────────────────────────────────────────────────────────────
POURQUOI CES CAPTURES SONT PRISES PAR UN SCRIPT, ET NON À LA MAIN

Une capture prise à la main vieillit sans prévenir. Elle montre un écran qui a
changé, un compteur qui n'existe plus, une colonne renommée, et personne ne s'en
aperçoit avant qu'un client ne pose la question devant témoin. Reprises par une
commande, elles se refont en une minute après chaque évolution, et le document
qui les porte reste vrai.

Surtout : elles sont prises **contre la pile réelle, sur des comptes réels, avec
les permissions réelles**. Un écran de refus photographié ici est un vrai refus,
pas une maquette de refus. C'est la différence entre montrer ce que le produit
fait et montrer ce qu'on aimerait qu'il fasse.

⚠️ CE QUI PEUT FAIRE ÉCHOUER CE SCRIPT, ET QUI N'EST PAS UN DÉFAUT DU PRODUIT

Le limiteur de connexions retient 30 tentatives par tranche de cinq minutes, en
mémoire. Ce script ouvre une session par profil : lancé deux fois de suite, il
épuise le compteur et les connexions suivantes sont refusées. Les captures
montrent alors un écran de refus là où on attendait un tableau de bord.

    Backend_erp_cga/outils/pile-de-demonstration.sh neuve

remet le compteur à zéro en redémarrant l'API. À faire avant chaque campagne.

    python3 Docs/demonstration/captures.py
─────────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "Docs" / "recette"))

from verifier_profils import MOT_DE_PASSE  # noqa: E402

FRONT = "http://localhost:3011"
SORTIE = RACINE / "Docs" / "demonstration" / "captures"

#: 1440 × 900 : l'écran d'un portable de bureau. Ni un mobile, ni un moniteur de
#: développeur. C'est la largeur sur laquelle le produit sera réellement employé,
#: et une capture prise à 2560 points de large donnerait une fausse idée de la
#: densité de l'interface.
FENETRE = {"width": 1440, "height": 900}

DIRECTION = "b.mballa@cga-brcg.cm"
COMPTABLE = "l.fotso@cga-brcg.cm"
ADHERENT = "jp.nkoa@batimentplus.cm"
REVISEUR = "a.bouba@cga-brcg.cm"

#: (fichier, compte ou None pour le public, chemin, légende, pleine hauteur)
ECRANS: list[tuple[str, str | None, str, str, bool]] = [
    # ── La vitrine, ce que voit un prospect ──────────────────────────────────
    ("00-vitrine-accueil", None, "/",
     "La vitrine publique, point d'entrée du prospect", False),
    ("01-vitrine-adherent", None, "/devenir-adherent",
     "L'offre d'adhésion et ses avantages fiscaux", False),
    ("02-connexion", None, "/connexion",
     "La connexion, commune au collaborateur et à l'adhérent", False),

    # ── Acte I · ce qu'un cabinet fait tous les jours ────────────────────────
    ("10-tableau-de-bord", COMPTABLE, "/tableau-de-bord",
     "Le tableau de bord du comptable : son portefeuille, et lui seul", True),
    ("11-portefeuille", COMPTABLE, "/portefeuille",
     "Les dossiers affectés, avec leur régime et leurs obligations", True),
    ("12-pieces", COMPTABLE, "/pieces",
     "La boîte de réception des pièces justificatives", True),
    ("13-piece-controlee", COMPTABLE, "/pieces/F-2026-0424",
     "Le rapport de conformité : deux constats, leur fondement, le paramètre employé",
     True),
    ("14-saisie", COMPTABLE, "/comptabilite/saisie",
     "La saisie d'écriture, et le journal des dernières saisies", True),
    ("15-balance", COMPTABLE, "/comptabilite",
     "La balance et le grand livre", True),

    # ── Acte II · le référentiel ─────────────────────────────────────────────
    ("20-referentiel", COMPTABLE, "/referentiel",
     "Le référentiel normatif : chaque valeur datée, sourcée, signée", True),

    # ── Acte III · ce qui protège le cabinet ─────────────────────────────────
    ("30-espace-adherent", ADHERENT, "/mon-espace",
     "L'espace de l'adhérent : son dossier, ses pièces, ses échéances", True),
    ("31-refus-adherent", ADHERENT, "/comptabilite",
     "Le même adhérent devant la comptabilité : refus nommant la permission", False),
    ("32-refus-reviseur", REVISEUR, "/pilotage",
     "Le réviseur devant le pilotage : voir les dossiers n'est pas piloter le cabinet",
     False),

    # ── Acte IV · ce que ça donne en haut ────────────────────────────────────
    ("40-pilotage", DIRECTION, "/pilotage",
     "Le pilotage : les dossiers rangés par risque, jamais par nom", True),
    ("41-obligations", DIRECTION, "/obligations",
     "L'échéancier fiscal, calculé et non ressaisi", True),
    ("42-declarations", DIRECTION, "/obligations/declarations",
     "La préparation d'une déclaration de TVA", True),
    ("43-social", COMPTABLE, "/social",
     "Le personnel et la paie", True),
    ("44-cloture", DIRECTION, "/cloture",
     "La clôture annuelle et la liasse fiscale", True),
    ("45-creation", DIRECTION, "/creation-entreprise",
     "Le tunnel de création d'entreprise", True),
    ("46-comptes", "s.onana@cga-brcg.cm", "/comptes",
     "Les comptes et leurs habilitations, réservés à l'administrateur", True),
]


def connecter(page: Page, adresse: str) -> None:
    """Ouvre une session par le vrai formulaire, comme un utilisateur.

    Pas d'injection de témoin ni d'appel direct à l'API : si la connexion ne
    passe pas par où passe un humain, les captures ne prouvent rien sur ce qu'un
    humain obtiendra.
    """
    page.goto(f"{FRONT}/connexion", wait_until="networkidle")
    page.fill('input[name="courriel"]', adresse)
    page.fill('input[name="motDePasse"]', MOT_DE_PASSE)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def capturer() -> int:
    SORTIE.mkdir(parents=True, exist_ok=True)
    prises, manquees = 0, []

    with sync_playwright() as pilote:
        navigateur = pilote.chromium.launch()
        session_ouverte: str | None = None
        contexte = navigateur.new_context(viewport=FENETRE, locale="fr-FR")
        page = contexte.new_page()

        for fichier, compte, chemin, legende, pleine in ECRANS:
            # Un contexte neuf par changement de compte : sans cela, le témoin de
            # session précédent survit et l'écran suivant est photographié sous
            # la mauvaise identité, ce qui ne se voit pas sur l'image.
            if compte != session_ouverte:
                contexte.close()
                contexte = navigateur.new_context(viewport=FENETRE, locale="fr-FR")
                page = contexte.new_page()
                if compte:
                    connecter(page, compte)
                session_ouverte = compte

            try:
                page.goto(f"{FRONT}{chemin}", wait_until="networkidle", timeout=30_000)
                page.wait_for_timeout(400)
                cible = SORTIE / f"{fichier}.png"
                page.screenshot(path=str(cible), full_page=pleine)
                poids = cible.stat().st_size // 1024
                print(f"  ✓ {fichier:<22} {chemin:<28} {poids:>5} Ko  {legende[:46]}")
                prises += 1
            except Exception as souci:  # noqa: BLE001
                manquees.append((fichier, chemin, str(souci)[:90]))
                print(f"  ✗ {fichier:<22} {chemin:<28} {str(souci)[:60]}")

        contexte.close()
        navigateur.close()

    print(f"\n  {prises}/{len(ECRANS)} écrans photographiés dans {SORTIE.relative_to(RACINE)}")
    if manquees:
        print("\n  ⚠️ Écrans manqués. Vérifier que la pile tourne et que le limiteur")
        print("     de connexions n'est pas épuisé : outils/pile-de-demonstration.sh neuve")
        for fichier, chemin, souci in manquees:
            print(f"     {fichier} ({chemin}) : {souci}")
    return 0 if not manquees else 1


if __name__ == "__main__":
    raise SystemExit(capturer())
