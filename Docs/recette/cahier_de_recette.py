"""Fabrique le cahier de recette, en PDF, depuis le registre qui vient de tourner.

─────────────────────────────────────────────────────────────────────────────────
POURQUOI UN GÉNÉRATEUR ET NON UN DOCUMENT ÉCRIT À LA MAIN

Un cahier de recette rédigé à la main vieillit le jour où il est imprimé. Celui-ci
se fabrique à partir de trois sources vivantes, et d'aucune autre :

    `cas_usage.REGISTRE`        les cas d'usage et leur preuve
    `verifier_profils.COMPTES`  les comptes, leurs rôles, leurs permissions
    l'exécution du registre     le constat réellement observé, ce jour-là

La colonne « constat » n'est donc jamais une promesse : c'est ce que la pile a
répondu au moment où le document a été fabriqué. Un cas qui tombe apparaît en
échec dans le PDF, et c'est le comportement voulu : un cahier de recette qui ne
peut pas afficher un échec ne prouve rien.

Le seul contenu écrit à la main est `COMPTE_DU_CAS` : quel compte employer pour
rejouer chaque cas à la main. Il est écrit ici, et non dans le registre, parce
qu'il s'adresse à un testeur humain et non au script.

USAGE

    python Docs/recette/cahier_de_recette.py               # exécute, puis édite
    python Docs/recette/cahier_de_recette.py --direct      # sans lancer pytest
    python Docs/recette/cahier_de_recette.py --sans-executer  # rendu à blanc

Le PDF sort dans `Docs/cahier-de-recette-cga.pdf`, via Chrome sans interface. Le
HTML intermédiaire est conservé à côté : c'est lui qu'on relit quand la mise en
page surprend.

⚠️ La pile doit tourner (front 3011, API 8010) pour que les preuves « direct »
s'exécutent, et `CGA_URL_BASE_DE_DONNEES_TEST` doit être exportée pour que les
preuves « suite » ne se sautent pas en silence. Voir `README.md`.

⚠️ DEUX FABRICATIONS DE SUITE FONT TOMBER LE LIMITEUR

Chaque exécution ouvre une session par compte, soit une dizaine de connexions.
Deux rendus rapprochés dépassent les trente connexions par cinq minutes, et
**tout** bascule en HTTP 401 : le cahier s'imprime alors avec trente cas en
échec qui n'ont rien à voir avec le produit. Le limiteur vit en mémoire dans
l'API : redémarrer uvicorn le remet à zéro, ce qui est plus rapide qu'attendre
la fenêtre. C'est le quatrième piège du `README.md`, rencontré en fabriquant ce
cahier.
─────────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import html
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ⚠️ `noqa: E402` : ces imports suivent `sys.path.insert` parce qu'ils désignent
# des modules voisins, introuvables avant. C'est la seule position qui marche.
from cas_usage import (  # noqa: E402
    API,
    FRONT,
    MOT_DE_PASSE,
    REGISTRE,
    CasUsage,
    RecetteLimitee,
    executer_suite,
)
from verifier_profils import (  # noqa: E402
    COMPTES,
    COMPTES_REFUSES,
    PERMISSIONS,
    permissions_de,
)

SORTIE_HTML = RACINE / "Docs" / "cahier-de-recette-cga.html"
SORTIE_PDF = RACINE / "Docs" / "cahier-de-recette-cga.pdf"


# ══ Ce qui s'adresse au testeur humain ════════════════════════════════════════
#: Le nom des contextes bornés, dans l'ordre où le cahier les présente.
CONTEXTES: dict[str, str] = {
    "K": "Accès, identité et exploitation",
    "M": "Souscription en ligne",
    "I": "Création d'entreprise",
    "C": "Collecte des pièces",
    "G": "Social et paie",
    "D": "Conformité",
    "H": "Clôture annuelle et DSF",
    "J": "Pilotage du cabinet",
    "E": "Comptabilité",
    "F": "Obligations fiscales",
}

#: Quel compte employer pour rejouer le cas à la main, et contre quel autre.
#: Écrit à la main, cas par cas : c'est la seule partie du cahier qui s'adresse
#: à un testeur et non à un script.
COMPTE_DU_CAS: dict[str, str] = {
    "UC-01": "b.mballa (ou tout collaborateur)",
    "UC-02": "jp.nkoa",
    "UC-03": "a.tchinda (suspendu)",
    "UC-04": "e.tchoumba (jamais activé)",
    "UC-05": "inconnu@nulle-part.cm",
    "UC-06": "aucun : visiteur anonyme",
    "UC-07": "aucun : 31 tentatives de suite",
    "UC-08": "aucun : lire l'en-tête Set-Cookie",
    "UC-09": "s.onana sur /comptabilite",
    "UC-10": "s.onana, en appelant l'API sans passer par l'écran",
    "UC-11": "s.onana",
    "UC-12": "l.fotso, puis c.ndongo sur le même dossier",
    "UC-13": "jp.nkoa sur un dossier qui n'est pas le sien",
    "UC-14": "aucun : la vitrine publique",
    "UC-15": "aucun : la vitrine publique",
    "UC-16": "aucun, puis le lien reçu par courriel",
    "UC-17": "le lien d'activation, puis le compte créé",
    "UC-18": "exploitant : configuration Tara réelle",
    "UC-19": "l.fotso, puis r.ebolo",
    "UC-20": "jp.nkoa",
    "UC-21": "jp.nkoa, puis a.bouba",
    "UC-22": "anonyme, s.onana, puis l.fotso",
    "UC-23": "l.fotso",
    "UC-24": "l.fotso, puis jp.nkoa",
    "UC-25": "l.fotso",
    "UC-26": "l.fotso",
    "UC-27": "l.fotso (refus), a.bouba (accord)",
    "UC-28": "b.mballa, puis l.fotso",
    "UC-29": "s.onana, puis b.mballa",
    "UC-30": "exploitant : GET /sante",
    "UC-31": "exploitant",
    "UC-32": "exploitant",
    "UC-33": "architecte",
    "UC-34": "p.moukouri, puis l.fotso",
    "UC-35": "p.moukouri",
    "UC-36": "p.moukouri",
    "UC-37": "p.moukouri",
    "UC-38": "p.moukouri, puis b.mballa au portefeuille",
    "UC-39": "p.moukouri",
    "UC-40": "r.ebolo",
    "UC-41": "l.fotso, puis s.onana et jp.nkoa",
    "UC-42": "l.fotso sur AGRO-NKOLO SA",
    "UC-43": "l.fotso sur AGRO-NKOLO SA",
    "UC-44": "l.fotso sur AGRO-NKOLO SA",
    "UC-45": "l.fotso",
    "UC-46": "l.fotso",
    "UC-47": "l.fotso, puis s.onana et jp.nkoa",
    "UC-48": "a.bouba",
    "UC-49": "l.fotso sur AGRO-NKOLO SA",
    "UC-50": "l.fotso",
    "UC-51": "l.fotso",
    "UC-52": "g.atangana",
    "UC-53": "b.mballa, puis a.bouba, l.fotso, jp.nkoa",
    "UC-54": "b.mballa",
    "UC-55": "b.mballa",
    "UC-56": "b.mballa",
    "UC-57": "b.mballa",
    "UC-58": "b.mballa",
    "UC-59": "l.fotso, puis p.moukouri et jp.nkoa",
    "UC-60": "l.fotso",
    "UC-61": "l.fotso",
    "UC-62": "l.fotso",
    "UC-63": "l.fotso",
    "UC-64": "l.fotso, formulaire posté sans JavaScript",
}

#: Les six dossiers du jeu de démonstration, et ce que chacun met en scène.
DOSSIERS = [
    ("M081234567890P", "SARL BATIMENT PLUS", "l.fotso", "jp.nkoa",
     "Le dossier de l'adhérent connecté : tout ce qu'il voit doit s'y limiter."),
    ("M071122334455J", "BOULANGERIE LA COLOMBE SARL", "l.fotso", "mc.essomba",
     "Le second adhérent : sert à prouver qu'un adhérent ne voit pas l'autre."),
    ("M065544332211L", "AGRO-NKOLO SA", "l.fotso", "aucun",
     "Le dossier de production : paie, liasse, TVA rejetée, mission d'inspection."),
    ("P019876543210K", "ETS TCHOUMBA & FILS", "c.ndongo", "e.tchoumba (non activé)",
     "Portefeuille du second comptable : l.fotso doit y recevoir 404."),
    ("P027788990011M", "CABINET NGUEMA CONSEIL", "c.ndongo", "aucun",
     "Profession libérale : régime et obligations différents."),
    ("M093344556677N", "CLINIQUE LE BON SAMARITAIN", "aucun", "aucun",
     "Dossier orphelin, délibérément : c'est l'anomalie que l'administration doit voir."),
]

#: Ce que le cahier ne prouve pas. Écrit ici pour être imprimé, et non tu.
RESERVES = [
    ("Neuf valeurs légales restent à confirmer",
     "Le référentiel porte 59 paramètres, dont 50 ont été confrontés aux textes le "
     "18 août 2026 et validés au nom du cabinet. Neuf restent au statut A_VALIDER "
     "faute d'avoir été confirmés : tout rapport qui s'en sert le signale. La fiche "
     "de contreseing les liste, valeur et source en regard, pour relecture."),
    ("Les validations ont été faites sur des fiches officielles, pas sur le code relié",
     "Le champ « source » de chaque paramètre dit ce qui a été réellement ouvert : "
     "fiches de la Direction Générale des Impôts, textes CNPS, actes uniformes "
     "OHADA. Aucune lecture n'a été faite sur le Code Général des Impôts relié ni "
     "sur la circulaire d'application de la loi de finances 2026. Un fiscaliste "
     "disposant du texte doit repasser sur les 50, et la fiche est faite pour cela."),
    ("Un seul cabinet est servi",
     "Le cloisonnement par locataire existe en base, mais 50 points d'appel "
     "emploient encore le locataire par défaut. Servir un second cabinet demande "
     "de propager le locataire depuis la session, pas de refaire le modèle."),
    ("La plateforme n'a jamais été déployée",
     "Elle tourne en développement et en recette. La configuration de production "
     "refuse de démarrer sans SMTP, sans identifiants de paiement réels et sans "
     "TLS : c'est voulu, et cela reste à faire."),
    ("Le mode démonstration fabrique les paiements",
     "CGA_MODE_DEMONSTRATION ouvre un accès sans encaissement et affiche les liens "
     "d'activation en clair. La route qui le permet répond 409 dès que des "
     "identifiants de paiement réels sont configurés."),
]

PIEGES = [
    ("Le type de contenu",
     "Les formulaires déclarent multipart/form-data. Postés en urlencoded, ils "
     "répondent 200 sans effet."),
    ("Les champs cachés de Next.js",
     "La référence de l'action serveur est sérialisée en JSON dans un champ caché. "
     "Une lecture par expression régulière renvoie des valeurs vides sans échouer, "
     "et toutes les connexions tombent en HTTP 500."),
    ("Le marqueur de refus",
     "La classe avertissement-ecran--reserve sert aussi de bandeau ordinaire sur "
     "cinq écrans qui s'ouvrent normalement. Seul le titre « Accès réservé » "
     "distingue un refus."),
    ("Le limiteur de débit",
     "Au-delà de 30 connexions par 5 minutes, la connexion est refusée. Une recette "
     "qui se reconnecte à chaque sonde se limite elle-même et fabrique des défauts "
     "qui n'existent pas."),
]


# ══ Rendu ═════════════════════════════════════════════════════════════════════
def e(texte: object) -> str:
    """Échappe, et remplace le tiret cadratin par une ponctuation ordinaire.

    Le cahier est destiné à être lu par des tiers : il emploie une ponctuation
    sobre. Le remplacement se fait au rendu plutôt qu'à la source pour ne pas
    dénaturer les constats produits par le registre.
    """
    texte = str(texte).replace(" — ", ", ").replace("—", ":").replace(" – ", ", ")
    return html.escape(texte)


def _verdicts(mode: str) -> dict[str, tuple[bool, str, str]]:
    """Rend, par référence, le triplet (validé, constat, genre de preuve)."""
    if mode == "sans-executer":
        return {}
    suite = {} if mode == "direct" else executer_suite(REGISTRE)
    resultats: dict[str, tuple[bool, str, str]] = {}
    for cas in REGISTRE:
        if cas.preuve is not None:
            try:
                ok, constat = cas.preuve()
            except RecetteLimitee:
                # ⚠️ Pas 119 : un cahier engendré pendant que le limiteur refuse la recette dirait
                # « quarante flux en échec » sur une pile saine, et il serait remis au cabinet.
                # Mieux vaut pas de cahier du tout.
                raise
            except Exception as erreur:  # noqa: BLE001 — un cas qui explose est un résultat
                ok, constat = False, f"exception : {type(erreur).__name__} {erreur}"
            resultats[cas.reference] = (ok, constat, "direct")
        elif cas.reference in suite:
            ok, constat = suite[cas.reference]
            resultats[cas.reference] = (ok, constat, "suite")
    return resultats


def _ligne_cas(cas: CasUsage, verdicts: dict[str, tuple[bool, str, str]]) -> str:
    verdict = verdicts.get(cas.reference)
    if verdict is None:
        marque, classe, constat, genre = "·", "attente", "non exécuté", "&nbsp;"
    else:
        ok, constat, genre = verdict
        marque = "✓" if ok else "✗"
        classe = "ok" if ok else "ko"
        genre = e(genre)
    cible = f"<div class=\"cible\">{e(cas.test)}</div>" if cas.test else ""
    return (
        f'<tr class="{classe}">'
        f'<td class="ref">{e(cas.reference)}</td>'
        f'<td class="acteur">{e(cas.acteur)}</td>'
        f'<td class="intitule">{e(cas.intitule)}{cible}</td>'
        f'<td class="compte">{e(COMPTE_DU_CAS.get(cas.reference, ""))}</td>'
        f'<td class="genre">{genre}</td>'
        f'<td class="constat"><span class="marque {classe}">{marque}</span>{e(constat)}</td>'
        f"</tr>"
    )


def _tableau_des_cas(verdicts: dict[str, tuple[bool, str, str]]) -> str:
    morceaux = [
        '<table class="cas">',
        "<thead><tr>"
        "<th>Réf.</th><th>Acteur</th><th>Cas d'usage</th>"
        "<th>Compte à employer</th><th>Preuve</th><th>Constat observé</th>"
        "</tr></thead><tbody>",
    ]
    for code, nom in CONTEXTES.items():
        cas_du_contexte = [c for c in REGISTRE if c.contexte == code]
        if not cas_du_contexte:
            continue
        morceaux.append(
            f'<tr class="groupe"><td colspan="6">'
            f'<span class="lettre">{e(code)}</span>{e(nom)}'
            f'<span class="compte-groupe">{len(cas_du_contexte)} cas</span>'
            f"</td></tr>"
        )
        morceaux += [_ligne_cas(cas, verdicts) for cas in cas_du_contexte]
    morceaux.append("</tbody></table>")
    return "\n".join(morceaux)


def _tableau_des_comptes() -> str:
    #: Ce que chaque compte sert à démontrer. La portée vient des habilitations
    #: de démonstration ; elle est rappelée ici pour que le testeur sache
    #: d'avance ce qu'il doit voir, et surtout ce qu'il ne doit pas voir.
    portees = {
        "b.mballa@cga-brcg.cm": ("tout le portefeuille",
                                 "Seule à détenir LIRE_PILOTAGE. Ne gère pas les comptes."),
        "s.onana@cga-brcg.cm": ("aucun dossier",
                                "Gère les comptes et ne lit aucun dossier. Le refus le plus "
                                "instructif du jeu."),
        "l.fotso@cga-brcg.cm": ("BATIMENT, COLOMBE, AGRO",
                                "Le comptable de référence : saisie, paie, liasse, TVA."),
        "c.ndongo@cga-brcg.cm": ("TCHOUMBA, NGUEMA",
                                 "Portefeuille disjoint du précédent : c'est là que se "
                                 "démontre le cloisonnement."),
        "a.bouba@cga-brcg.cm": ("tout le portefeuille",
                                "Seul à pouvoir déposer une déclaration et clore un exercice."),
        "r.ebolo@cga-brcg.cm": ("tout le portefeuille",
                                "Règle le référentiel et les règles. Ne saisit aucune écriture."),
        "p.moukouri@cga-brcg.cm": ("tous les adhérents",
                                   "Cumule clientèle et formalités : seul à ouvrir la "
                                   "création d'entreprise."),
        "jp.nkoa@batimentplus.cm": ("SARL BATIMENT PLUS",
                                    "L'adhérent qui a révélé le défaut de cloisonnement de "
                                    "la boîte de réception."),
        "mc.essomba@lacolombe.cm": ("BOULANGERIE LA COLOMBE",
                                    "Le second adhérent : sert à prouver qu'aucun ne voit "
                                    "l'autre."),
        "g.atangana@inspection.cm": ("AGRO-NKOLO SA",
                                     "Externe, en mission datée : lecture et avis seulement."),
    }
    lignes = []
    for courriel, role, roles in COMPTES:
        portee, propos = portees.get(courriel, ("", ""))
        lignes.append(
            f"<tr>"
            f'<td class="courriel">{e(courriel)}</td>'
            f"<td>{e(role)}</td>"
            f'<td class="portee">{e(portee)}</td>'
            f'<td class="propos">{e(propos)}</td>'
            f'<td class="nombre">{len(permissions_de(roles))}</td>'
            f"</tr>"
        )
    for courriel, motif in COMPTES_REFUSES:
        lignes.append(
            f'<tr class="refuse">'
            f'<td class="courriel">{e(courriel)}</td>'
            f"<td>{e(motif)}</td>"
            f'<td class="portee">sans objet</td>'
            f'<td class="propos">La connexion <strong>doit</strong> échouer, avec le '
            f"même message que les deux autres : sans quoi le formulaire dit qui "
            f"existe et qui n'existe pas.</td>"
            f'<td class="nombre">0</td>'
            f"</tr>"
        )
    return (
        '<table class="comptes"><thead><tr>'
        "<th>Identifiant de connexion</th><th>Profil</th><th>Portée</th>"
        "<th>Ce que ce compte sert à démontrer</th><th>Perm.</th>"
        "</tr></thead><tbody>" + "\n".join(lignes) + "</tbody></table>"
    )


def _tableau_des_dossiers() -> str:
    lignes = [
        f"<tr><td class=\"niu\">{e(niu)}</td><td><strong>{e(nom)}</strong></td>"
        f"<td>{e(comptable)}</td><td>{e(adherent)}</td><td class=\"propos\">{e(propos)}</td></tr>"
        for niu, nom, comptable, adherent, propos in DOSSIERS
    ]
    return (
        '<table class="dossiers"><thead><tr>'
        "<th>NIU</th><th>Dénomination</th><th>Comptable</th><th>Adhérent</th>"
        "<th>Ce que ce dossier met en scène</th>"
        "</tr></thead><tbody>" + "\n".join(lignes) + "</tbody></table>"
    )


def _matrice_des_permissions() -> str:
    """Les permissions par rôle, en colonnes.

    Le tableau est celui de `verifier_profils.PERMISSIONS`, recopié à la main
    depuis `roles.py`. Le dériver du code testé ne prouverait que la cohérence du
    code avec lui-même ; le recopier fait de la matrice un attendu indépendant.
    """
    roles = list(PERMISSIONS)
    toutes = sorted({p for jeu in PERMISSIONS.values() for p in jeu})
    entete = "".join(f'<th class="pivot"><span>{e(r.title())}</span></th>' for r in roles)
    lignes = []
    for permission in toutes:
        cases = "".join(
            f'<td class="{"oui" if permission in PERMISSIONS[r] else "non"}">'
            f'{"●" if permission in PERMISSIONS[r] else ""}</td>'
            for r in roles
        )
        lignes.append(f'<tr><td class="perm">{e(permission)}</td>{cases}</tr>')
    return (
        f'<table class="matrice"><thead><tr><th class="perm">Permission</th>{entete}</tr>'
        f"</thead><tbody>{''.join(lignes)}</tbody></table>"
    )


GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Cahier de recette : plateforme CGA Broad Range Consulting Group</title>

<!--
  ⚠️ CE FICHIER EST ENGENDRÉ. Ne pas le corriger à la main : la correction
  serait perdue au prochain rendu. La source est
  `Docs/recette/cahier_de_recette.py`.

      python Docs/recette/cahier_de_recette.py
-->

<style>
  @page {{ size: A4; margin: 13mm 12mm 11mm; }}
  @page :first {{ margin-top: 11mm; }}

  :root {{
    --encre:     #14232B;
    --encre-2:   #4B5C63;
    --encre-3:   #7C8D92;
    --trait:     #C6D0CD;
    --trait-fin: #E2E8E6;
    --fond:      #F4F7F6;
    --accent:    #0F6E5C;
    --accent-fd: #E2EDE9;
    --vert:      #1E7A4C;
    --rouge:     #A32D28;
    --ocre:      #8A5A18;
    --ocre-fd:   #F8F1E2;
    --serif: Georgia, "Iowan Old Style", "Times New Roman", serif;
    --sans:  "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif;
    --mono:  "DejaVu Sans Mono", ui-monospace, Menlo, Consolas, monospace;
  }}

  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  html, body {{ margin: 0; padding: 0; background: #FFFFFF; }}
  body {{ color: var(--encre); font-family: var(--sans); font-size: 8.2pt; line-height: 1.4; }}

  /* ── En-tête de la première page ──────────────────────────────────── */
  header {{
    display: flex; align-items: flex-end; justify-content: space-between;
    gap: 10mm; padding-bottom: 3mm; border-bottom: 1.6pt solid var(--encre);
  }}
  .eyebrow {{
    font-family: var(--mono); font-size: 6.6pt; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--accent); margin: 0 0 1.5mm;
  }}
  h1 {{ font-family: var(--serif); font-size: 19pt; line-height: 1.12;
       margin: 0; font-weight: 600; }}
  .sous-titre {{ font-size: 9pt; color: var(--encre-2); margin: 1.6mm 0 0; max-width: 118mm; }}
  .meta {{ text-align: right; font-family: var(--mono); font-size: 6.9pt;
           color: var(--encre-3); line-height: 1.7; white-space: nowrap; }}
  .meta strong {{ color: var(--encre); font-weight: 600; }}

  /* ── Bandeau de verdict ───────────────────────────────────────────── */
  .verdict {{
    margin-top: 4mm; padding: 3mm 4mm; border-radius: 1.2mm;
    border: 0.7pt solid {bord_verdict}; background: {fond_verdict};
    display: flex; align-items: baseline; gap: 5mm;
  }}
  .verdict .chiffre {{ font-family: var(--serif); font-size: 17pt; font-weight: 600;
                       color: {texte_verdict}; line-height: 1; }}
  .verdict .mot {{ font-family: var(--mono); font-size: 7.2pt; letter-spacing: 0.13em;
                   text-transform: uppercase; color: {texte_verdict}; }}
  .verdict p {{ margin: 0; font-size: 8pt; color: var(--encre-2); }}

  /* ── Titres de section ────────────────────────────────────────────── */
  section {{ margin-top: 5.5mm; }}
  h2 {{
    font-family: var(--mono); font-size: 7pt; letter-spacing: 0.17em;
    text-transform: uppercase; color: var(--encre-3); font-weight: 500;
    margin: 0 0 2mm; padding-bottom: 1.1mm; border-bottom: 0.6pt solid var(--trait-fin);
  }}
  h2 .numero {{ color: var(--accent); margin-right: 2mm; }}
  h3 {{ font-family: var(--sans); font-size: 8.4pt; font-weight: 600; margin: 3.2mm 0 1.2mm; }}
  p {{ margin: 0 0 1.8mm; }}
  .chapeau {{ color: var(--encre-2); max-width: 168mm; }}

  /* ── Tableaux, tous ───────────────────────────────────────────────── */
  table {{ width: 100%; border-collapse: collapse; font-size: 7.4pt; }}
  thead {{ display: table-header-group; }}
  h2 {{ break-after: avoid; }}
  .encadre {{ break-inside: avoid; }}
  thead th {{
    font-family: var(--mono); font-size: 6.2pt; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--encre-3); font-weight: 500;
    text-align: left; padding: 0 2mm 1.2mm; border-bottom: 0.7pt solid var(--trait);
  }}
  tbody td {{ padding: 1.35mm 2mm; border-bottom: 0.4pt solid var(--trait-fin);
              vertical-align: top; }}
  tbody tr {{ break-inside: avoid; }}

  /* ── Registre des cas d'usage ─────────────────────────────────────── */
  table.cas .ref {{ font-family: var(--mono); font-size: 6.9pt; white-space: nowrap;
                    color: var(--encre-2); width: 12mm; }}
  table.cas .acteur {{ width: 26mm; color: var(--encre-2); }}
  table.cas .intitule {{ width: 52mm; }}
  table.cas .compte {{ width: 34mm; font-family: var(--mono); font-size: 6.5pt;
                       color: var(--encre-2); }}
  table.cas .genre {{ width: 11mm; font-family: var(--mono); font-size: 6.3pt;
                      color: var(--encre-3); }}
  table.cas .constat {{ color: var(--encre-2); }}
  table.cas .cible {{ font-family: var(--mono); font-size: 6.1pt; color: var(--encre-3);
                      margin-top: 0.4mm; }}
  .marque {{ display: inline-block; width: 3.4mm; font-weight: 700; }}
  .marque.ok {{ color: var(--vert); }}
  .marque.ko {{ color: var(--rouge); }}
  .marque.attente {{ color: var(--encre-3); }}
  tr.ko td {{ background: #FBF0EF; }}
  tr.groupe td {{
    background: var(--fond); border-bottom: 0.4pt solid var(--trait);
    padding: 1.6mm 2mm; font-weight: 600; font-size: 7.6pt;
  }}
  tr.groupe .lettre {{
    display: inline-block; width: 4.2mm; height: 4.2mm; line-height: 4.2mm;
    text-align: center; border-radius: 0.8mm; background: var(--accent);
    color: #FFFFFF; font-family: var(--mono); font-size: 6.4pt; margin-right: 2.2mm;
  }}
  tr.groupe .compte-groupe {{ float: right; font-family: var(--mono); font-size: 6.4pt;
                              font-weight: 400; color: var(--encre-3); }}

  /* ── Comptes ──────────────────────────────────────────────────────── */
  .courriel {{ font-family: var(--mono); font-size: 6.9pt; white-space: nowrap; }}
  .portee {{ color: var(--encre-2); width: 34mm; }}
  .propos {{ color: var(--encre-2); }}
  .nombre {{ text-align: right; font-family: var(--mono); font-size: 6.9pt;
             color: var(--encre-3); width: 10mm; }}
  tr.refuse .courriel {{ color: var(--rouge); }}
  .niu {{ font-family: var(--mono); font-size: 6.9pt; white-space: nowrap; }}

  /* ── Matrice des permissions ──────────────────────────────────────── */
  table.matrice {{ font-size: 6.8pt; }}
  table.matrice .perm {{ font-family: var(--mono); font-size: 6.3pt; width: 44mm; }}
  table.matrice th.pivot {{ width: 15mm; text-align: center; vertical-align: bottom;
                            font-size: 5.9pt; letter-spacing: 0.04em; }}
  table.matrice td.oui, table.matrice td.non {{ text-align: center; }}
  table.matrice td.oui {{ color: var(--accent); }}
  table.matrice tbody tr:nth-child(odd) td {{ background: #FAFBFB; }}

  /* ── Encadrés ─────────────────────────────────────────────────────── */
  .encadres {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2.5mm 4mm; }}
  .encadre {{ border-left: 1.4pt solid var(--trait); padding: 0.6mm 0 0.6mm 3mm; }}
  .encadre strong {{ display: block; font-size: 8pt; margin-bottom: 0.5mm; }}
  .encadre span {{ color: var(--encre-2); }}
  .encadre.alerte {{ border-left-color: var(--ocre); }}
  .encadre.alerte strong {{ color: var(--ocre); }}

  pre {{
    font-family: var(--mono); font-size: 6.6pt; line-height: 1.55; margin: 0;
    background: var(--fond); border: 0.5pt solid var(--trait-fin);
    border-radius: 1mm; padding: 2.6mm 3mm; white-space: pre-wrap;
  }}
  pre .commentaire {{ color: var(--encre-3); }}

  .note {{ font-size: 7.4pt; color: var(--encre-2); margin-top: 2mm; }}
  .note strong {{ color: var(--encre); }}

  footer {{
    margin-top: 6mm; padding-top: 2.2mm; border-top: 0.7pt solid var(--trait);
    display: flex; justify-content: space-between;
    font-family: var(--mono); font-size: 6.3pt; color: var(--encre-3);
  }}

  .saut {{ break-before: page; }}
</style>
</head>
<body>

<header>
  <div>
    <p class="eyebrow">Cahier de recette</p>
    <h1>Plateforme CGA<br>Broad Range Consulting Group</h1>
    <p class="sous-titre">
      Les {total} cas d'usage du système, les comptes de démonstration qui
      permettent de les rejouer, et le constat relevé sur la pile au moment où ce
      document a été fabriqué.
    </p>
  </div>
  <div class="meta">
    <strong>Édition</strong> {jour}<br>
    Front {front}<br>
    API {api}<br>
    Mot de passe commun<br>
    <strong>{motdepasse}</strong>
  </div>
</header>

<div class="verdict">
  <span class="chiffre">{reussis}/{total}</span>
  <span class="mot">{mot_verdict}</span>
  <p>
    {commentaire_verdict}
  </p>
</div>

<section>
  <h2><span class="numero">1</span>Comment ce cahier se lit</h2>
  <p class="chapeau">
    Chaque cas d'usage porte sa preuve, et la preuve est de l'un des deux genres
    suivants, jamais d'un troisième. <strong>Direct</strong> : la sonde a été
    exécutée par HTTP contre la pile qui tourne, au moment de la fabrication de ce
    document. <strong>Suite</strong> : la vérification est déléguée à un test nommé
    de la suite automatisée, lancé par le même script. Rien n'est déclaré validé
    sur la foi d'une lecture de code.
  </p>
  <p class="chapeau">
    La colonne « constat observé » rapporte ce que la pile a répondu, et non ce
    qui était attendu. C'est elle qu'on relit six mois plus tard, quand la question
    n'est plus « est-ce que ça marche » mais « qu'est-ce qui a été vérifié
    exactement ».
  </p>
</section>

<section>
  <h2><span class="numero">2</span>Monter la pile de recette</h2>
  <pre>{pile}</pre>
  <p class="note">
    <strong>HOSTNAME=0.0.0.0 est obligatoire.</strong> Avec 127.0.0.1, le serveur
    autonome Next renvoie une redirection sur chaque page, et la recette conclut à
    un produit cassé. <strong>CGA_URL_BASE_DE_DONNEES_TEST</strong> l'est tout
    autant : sans elle, les tests de persistance se sautent, pytest sort 0, et un
    cahier naïf compterait le cas comme validé.
  </p>
</section>

<section>
  <h2><span class="numero">3</span>Les comptes de démonstration</h2>
  <p class="chapeau">
    Tous partagent le mot de passe <strong>{motdepasse}</strong>. Trois d'entre eux
    doivent échouer à la connexion, avec le même message que les autres : un
    formulaire qui distingue « compte inconnu » de « mot de passe erroné » indique
    à un attaquant quels comptes existent.
  </p>
  {comptes}
</section>

<section>
  <h2><span class="numero">4</span>Les dossiers du jeu de démonstration</h2>
  {dossiers}
  <p class="note">
    Le jeu met en scène deux portefeuilles disjoints, un dossier orphelin, une
    habilitation fermée en avril dont la ligne demeure, un adhérent jamais activé,
    et une mission d'inspection datée. Aucun de ces cas n'est décoratif : chacun
    est l'objet d'un cas d'usage du registre.
  </p>
</section>

<section>
  <h2><span class="numero">5</span>Le registre des cas d'usage</h2>
  {cas}
</section>

<section>
  <h2><span class="numero">6</span>Les permissions par profil</h2>
  <p class="chapeau">
    Cette matrice est recopiée à la main depuis le code des rôles, et c'est
    volontaire : la dériver du code qu'elle vérifie ne prouverait que la cohérence
    du code avec lui-même. Elle sert d'attendu indépendant à la passe
    d'autorisation.
  </p>
  {matrice}
</section>

<section>
  <h2><span class="numero">7</span>Quatre pièges qui font accuser le produit à tort</h2>
  <div class="encadres">
    {pieges}
  </div>
</section>

<section>
  <h2><span class="numero">8</span>Ce que ce cahier ne prouve pas</h2>
  <p class="chapeau">
    Un cahier de recette qui ne dit que ce qui marche n'est pas un document de
    recette, c'est une plaquette. Les réserves ci-dessous sont ouvertes, et aucune
    n'est masquée par un cas d'usage vert.
  </p>
  <div class="encadres">
    {reserves}
  </div>
</section>

<footer>
  <span>CGA Broad Range Consulting Group · agrément MINFI/DGI n° 00000048</span>
  <span>Engendré par Docs/recette/cahier_de_recette.py · {jour}</span>
</footer>

</body>
</html>
"""

PILE = (
    '<span class="commentaire">'
    "# 1 · PostgreSQL local, données de démonstration uniquement</span>\n"
    """cd Backend_erp_cga &amp;&amp; eval "$(bash outils/postgres-local.sh start)"

<span class="commentaire"># 2 · Schéma et jeu de démonstration</span>
export CGA_PERSISTANCE=postgresql
python -m alembic upgrade head
CGA_MODE_DEMONSTRATION=true python -c "from app.amorcage import amorcer; print(amorcer())"

<span class="commentaire"># 3 · L'API, en mode recette</span>
CGA_MODE_DEMONSTRATION=true CGA_ADRESSE_PUBLIQUE_SITE=http://localhost:3011 \\
CGA_ORIGINES_CORS='["http://localhost:3011"]' \\
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010

<span class="commentaire"># 4 · Le front, build autonome</span>
cd Frontend_erp_cga &amp;&amp; npx next build
cd .next/standalone
API_URL=http://127.0.0.1:8010 PORT=3011 HOSTNAME=0.0.0.0 node Frontend_erp_cga/server.js

<span class="commentaire"># 5 · Rejouer les cas d'usage, et refaire ce cahier</span>
python Docs/recette/cas_usage.py
python Docs/recette/cahier_de_recette.py"""
)


def _aujourd_hui() -> str:
    """La date d'édition, en heure universelle.

    `date.today()` lit le fuseau du poste : deux fabrications simultanées à
    Douala et ailleurs dateraient le même cahier de deux jours différents.
    """
    return datetime.now(UTC).strftime("%d/%m/%Y")


def rendre(verdicts: dict[str, tuple[bool, str, str]]) -> str:
    executes = len(verdicts)
    reussis = sum(1 for ok, _, _ in verdicts.values() if ok)
    total = len(REGISTRE)
    tout_vert = executes == total and reussis == total

    if executes == 0:
        mot, bord, fond, texte = "rendu à blanc", "#C6D0CD", "#F4F7F6", "#4B5C63"
        commentaire = (
            "Ce cahier a été rendu sans exécuter les preuves. Les constats sont "
            "absents, et aucun cas ne doit être considéré comme validé."
        )
    elif tout_vert:
        mot, bord, fond, texte = "tous les flux validés", "#BFDCCC", "#EDF6F1", "#1E7A4C"
        commentaire = (
            "Chaque cas a été rejoué contre la pile au moment de la fabrication de ce "
            "document. Les constats ci-après sont les réponses effectivement reçues, "
            "et non des attendus recopiés."
        )
    else:
        mot, bord, fond, texte = "des flux restent en échec", "#E8C7C4", "#FBF0EF", "#A32D28"
        commentaire = (
            f"{total - reussis} cas sur {total} ne passent pas. Ils figurent au "
            "registre, en rouge, avec le constat exact : un cahier qui ne peut pas "
            "afficher un échec ne prouve rien."
        )

    return GABARIT.format(
        jour=_aujourd_hui(),
        front=FRONT,
        api=API,
        motdepasse=MOT_DE_PASSE,
        total=total,
        reussis=reussis,
        mot_verdict=mot,
        bord_verdict=bord,
        fond_verdict=fond,
        texte_verdict=texte,
        commentaire_verdict=commentaire,
        pile=PILE,
        comptes=_tableau_des_comptes(),
        dossiers=_tableau_des_dossiers(),
        cas=_tableau_des_cas(verdicts),
        matrice=_matrice_des_permissions(),
        pieges="\n".join(
            f'<div class="encadre alerte"><strong>{e(titre)}</strong>'
            f"<span>{e(propos)}</span></div>"
            for titre, propos in PIEGES
        ),
        reserves="\n".join(
            f'<div class="encadre"><strong>{e(titre)}</strong><span>{e(propos)}</span></div>'
            for titre, propos in RESERVES
        ),
    )


def imprimer() -> bool:
    """Rend le PDF par Chrome sans interface, ou explique pourquoi il ne peut pas."""
    navigateur = next(
        (
            chemin
            for nom in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable")
            if (chemin := shutil.which(nom))
        ),
        None,
    )
    if navigateur is None:
        print("Chrome introuvable : le HTML est écrit, le PDF ne l'est pas.", file=sys.stderr)
        return False
    subprocess.run(
        [
            navigateur,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={SORTIE_PDF}",
            str(SORTIE_HTML),
        ],
        check=True,
        capture_output=True,
        timeout=180,
    )
    return True


def main() -> int:
    mode = "complet"
    if "--sans-executer" in sys.argv:
        mode = "sans-executer"
    elif "--direct" in sys.argv:
        mode = "direct"

    try:
        verdicts = _verdicts(mode)
    except RecetteLimitee as limite:
        # Le cahier n'est pas réécrit : celui d'hier, juste, vaut mieux qu'un cahier d'aujourd'hui
        # qui accuse le produit d'échecs que la recette a provoqués elle-même.
        print(f"CAHIER NON ENGENDRÉ : {limite}", file=sys.stderr)
        return 2
    SORTIE_HTML.write_text(rendre(verdicts), encoding="utf-8")
    print(f"HTML : {SORTIE_HTML.relative_to(RACINE)}")
    if imprimer():
        print(f"PDF  : {SORTIE_PDF.relative_to(RACINE)}")

    executes = len(verdicts)
    reussis = sum(1 for ok, _, _ in verdicts.values() if ok)
    print(f"{reussis}/{len(REGISTRE)} cas validés ({executes} exécutés)")
    return 0 if executes == len(REGISTRE) and reussis == executes else 1


if __name__ == "__main__":
    sys.exit(main())
