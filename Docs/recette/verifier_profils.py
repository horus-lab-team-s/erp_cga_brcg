"""Vérification systématique : chaque profil, sur chaque écran.

Le principe est de ne rien simuler. On ouvre une session par le **vrai
formulaire** de connexion — lu, puis re-soumis en `multipart/form-data` comme le
ferait un navigateur sans JavaScript — et on parcourt ensuite chaque écran avec
le témoin obtenu. Un client qui fabriquerait lui-même le témoin ne prouverait
rien : c'est précisément la fabrication du témoin qui a caché un défaut réel
lors de la session précédente.

Chaque réponse est classée en quatre états seulement, parce qu'un jury de
recette ne sait pas quoi faire d'une nuance :

    ouvert    l'écran rend son contenu
    reserve   l'écran refuse poliment, en nommant le profil qui l'ouvrirait
    renvoi    redirection (typiquement vers /connexion)
    panne     5xx, ou une erreur de rendu

La matrice attendue est écrite à la main d'après `roles.py` et les gardes
`detient(...)` relevées dans les pages. Écrire l'attendu à la main est
volontaire : le dériver du même code que celui qu'on teste ne prouverait que la
cohérence du code avec lui-même.
"""

from __future__ import annotations

import html.parser as _parser
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field

BASE = "http://localhost:3011"
MOT_DE_PASSE = "cabinet brcg douala 2026"

# ── Les comptes de démonstration, et le ou les rôles qu'ils portent ───────────
COMPTES: list[tuple[str, str, tuple[str, ...]]] = [
    ("b.mballa@cga-brcg.cm", "Direction", ("DIRECTION",)),
    ("s.onana@cga-brcg.cm", "Administrateur", ("ADMINISTRATEUR",)),
    ("l.fotso@cga-brcg.cm", "Comptable", ("COMPTABLE",)),
    ("c.ndongo@cga-brcg.cm", "Comptable (2e portefeuille)", ("COMPTABLE",)),
    ("a.bouba@cga-brcg.cm", "Réviseur", ("REVISEUR",)),
    ("r.ebolo@cga-brcg.cm", "Fiscaliste", ("FISCALISTE",)),
    ("p.moukouri@cga-brcg.cm", "Clientèle + formalités", ("CHARGE_CLIENTELE", "CHARGE_FORMALITES")),
    ("jp.nkoa@batimentplus.cm", "Adhérent", ("ADHERENT",)),
    ("mc.essomba@lacolombe.cm", "Adhérent (2e dossier)", ("ADHERENT",)),
    ("g.atangana@inspection.cm", "Inspecteur", ("INSPECTEUR",)),
]

#: Ceux dont la connexion **doit** échouer, et avec le message générique.
COMPTES_REFUSES: list[tuple[str, str]] = [
    ("a.tchinda@cga-brcg.cm", "Compte suspendu"),
    ("e.tchoumba@tchoumbaetfils.cm", "Compte jamais activé"),
    ("inconnu@nulle-part.cm", "Compte inexistant"),
]

# ── Les écrans, et la permission que chacun exige ────────────────────────────
ECRANS: list[tuple[str, str]] = [
    ("/tableau-de-bord", "LIRE_DOSSIER"),
    ("/portefeuille", "LIRE_DOSSIER"),
    ("/pieces", "LIRE_PIECE"),
    ("/pieces/PJ-2026-0001", "LIRE_PIECE"),
    ("/comptabilite", "LIRE_COMPTABILITE"),
    ("/comptabilite/grand-livre", "LIRE_COMPTABILITE"),
    ("/obligations", "LIRE_DOSSIER"),
    ("/obligations/declarations", "LIRE_COMPTABILITE"),
    ("/referentiel", "LIRE_DOSSIER"),
    ("/comptes", "GERER_COMPTES"),
    ("/mon-espace", "LIRE_DOSSIER"),
]

# ── Les permissions par rôle, recopiées de roles.py ──────────────────────────
LECTURE_DOSSIER = {"LIRE_DOSSIER", "LIRE_PIECE"}
PERMISSIONS: dict[str, set[str]] = {
    "ADHERENT": LECTURE_DOSSIER | {"DEPOSER_PIECE"},
    "CHARGE_CLIENTELE": LECTURE_DOSSIER
    | {"LIRE_COMPTABILITE", "RELANCER_ADHERENT", "DEPOSER_PIECE"},
    "COMPTABLE": LECTURE_DOSSIER
    | {
        "LIRE_COMPTABILITE", "DEPOSER_PIECE", "IDENTIFIER_PIECE", "ARBITRER_DOUBLON",
        "CONTROLER_CONFORMITE", "SAISIR_ECRITURE", "VALIDER_ECRITURE", "CONTRE_PASSER",
    },
    "REVISEUR": LECTURE_DOSSIER
    | {
        "LIRE_COMPTABILITE", "LIRE_AUDIT", "DEPOSER_PIECE", "IDENTIFIER_PIECE",
        "ARBITRER_DOUBLON", "CONTROLER_CONFORMITE", "SAISIR_ECRITURE",
        "VALIDER_ECRITURE", "CONTRE_PASSER", "ECARTER_CONSTAT",
        "DEPOSER_DECLARATION", "CLOTURER_EXERCICE",
    },
    "FISCALISTE": LECTURE_DOSSIER
    | {"LIRE_COMPTABILITE", "MODIFIER_PARAMETRE", "MODIFIER_REGLE", "CONTROLER_CONFORMITE"},
    "CHARGE_FORMALITES": {"LIRE_DOSSIER", "SUIVRE_FORMALITE"},
    "DIRECTION": LECTURE_DOSSIER
    | {
        "LIRE_COMPTABILITE", "LIRE_PILOTAGE", "LIRE_AUDIT", "AFFECTER_DOSSIER",
        "CLOTURER_EXERCICE", "EDITER_VITRINE",
    },
    "ADMINISTRATEUR": {"GERER_COMPTES", "AFFECTER_DOSSIER", "LIRE_AUDIT", "EDITER_VITRINE"},
    "INSPECTEUR": LECTURE_DOSSIER | {"LIRE_COMPTABILITE", "LIRE_AUDIT", "EMETTRE_AVIS"},
}


def permissions_de(roles: tuple[str, ...]) -> set[str]:
    reunion: set[str] = set()
    for role in roles:
        reunion |= PERMISSIONS[role]
    return reunion


# ── Un client HTTP qui ne suit pas les redirections et retient ses témoins ────
class SansRedirection(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


@dataclass
class Client:
    temoins: dict[str, str] = field(default_factory=dict)

    def _ouvreur(self):
        return urllib.request.build_opener(SansRedirection)

    def _entetes(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        entetes = {"User-Agent": "recette-cga/1.0", "Accept": "text/html"}
        if self.temoins:
            entetes["Cookie"] = "; ".join(f"{c}={v}" for c, v in self.temoins.items())
        entetes.update(extra or {})
        return entetes

    def _retenir(self, reponse) -> None:
        for brut in reponse.headers.get_all("Set-Cookie") or []:
            nom, _, reste = brut.partition("=")
            self.temoins[nom.strip()] = reste.split(";")[0]

    def lire(self, chemin: str) -> tuple[int, str, str]:
        requete = urllib.request.Request(BASE + chemin, headers=self._entetes())
        try:
            with self._ouvreur().open(requete, timeout=30) as reponse:
                self._retenir(reponse)
                return reponse.status, reponse.read().decode("utf-8", "replace"), ""
        except urllib.error.HTTPError as erreur:
            self._retenir(erreur)
            cible = erreur.headers.get("Location", "")
            return erreur.code, erreur.read().decode("utf-8", "replace"), cible

    def soumettre(self, chemin: str, champs: dict[str, str]) -> tuple[int, str, str]:
        """Poste un formulaire en `multipart/form-data`.

        Le type compte : les formulaires de l'application le déclarent
        explicitement, et un `urlencoded` est accepté avec un 200 sans effet —
        exactement le symptôme d'un produit cassé, pour un client mal réglé.
        """
        limite = f"----cga{uuid.uuid4().hex}"
        corps = bytearray()
        for nom, valeur in champs.items():
            corps += f"--{limite}\r\n".encode()
            corps += f'Content-Disposition: form-data; name="{nom}"\r\n\r\n'.encode()
            corps += f"{valeur}\r\n".encode()
        corps += f"--{limite}--\r\n".encode()
        requete = urllib.request.Request(
            BASE + chemin,
            data=bytes(corps),
            headers=self._entetes(
                {
                    "Content-Type": f"multipart/form-data; boundary={limite}",
                    "Origin": BASE,
                    "Referer": BASE + chemin,
                }
            ),
            method="POST",
        )
        try:
            with self._ouvreur().open(requete, timeout=30) as reponse:
                self._retenir(reponse)
                return reponse.status, reponse.read().decode("utf-8", "replace"), ""
        except urllib.error.HTTPError as erreur:
            self._retenir(erreur)
            return erreur.code, erreur.read().decode("utf-8", "replace"), erreur.headers.get(
                "Location", ""
            )


class LecteurDeFormulaire(_parser.HTMLParser):
    """Relève les couples nom/valeur de tous les `<input>` d'une page.

    Un parseur plutôt qu'une expression régulière : l'ordre des attributs varie
    d'un champ à l'autre — `name` avant `value` sur les champs cachés de Next,
    après sur les champs visibles — et une regex qui suppose un ordre renvoie
    des valeurs vides sans jamais échouer. C'est le pire mode de panne pour un
    outil de recette : il accuse le produit.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.champs: dict[str, str] = {}

    def handle_starttag(self, balise: str, attributs: list[tuple[str, str | None]]) -> None:
        if balise != "input":
            return
        table = dict(attributs)
        nom = table.get("name")
        if nom:
            self.champs[nom] = table.get("value") or ""


def champs_caches(page: str) -> dict[str, str]:
    """Les champs du formulaire, valeurs par défaut comprises.

    Les entités HTML sont résolues par le parseur : Next.js sérialise la
    référence de son action serveur en JSON dans un champ caché, donc avec des
    `&quot;`. Les reposter tels quels fait échouer la résolution de l'action
    côté serveur avec un 500 — indiscernable, dans un journal, d'un produit
    cassé.
    """
    lecteur = LecteurDeFormulaire()
    lecteur.feed(page)
    return lecteur.champs


def classer(code: int, html: str, cible: str) -> str:
    if code >= 500:
        return "panne"
    if code in (301, 302, 303, 307, 308):
        return f"renvoi→{cible or '?'}"
    # ⚠️ Ne pas se fier à la classe `avertissement-ecran--reserve` : elle sert
    # aussi de bandeau de mise en garde ordinaire sur cinq écrans qui, eux,
    # s'ouvrent normalement. Seul le titre du panneau de refus est probant.
    if "Accès réservé" in html:
        return "reserve"
    if code == 404:
        return "absent"
    if code == 200:
        return "ouvert"
    return f"http{code}"


def ouvrir_session(adresse: str) -> tuple[Client, str]:
    client = Client()
    _, html, _ = client.lire("/connexion")
    champs = champs_caches(html)
    champs["courriel"] = adresse
    champs["motDePasse"] = MOT_DE_PASSE
    code, _corps, cible = client.soumettre("/connexion", champs)
    if code in (302, 303, 307) and "cga_session" in client.temoins:
        return client, f"ok →{cible}"
    if "cga_session" in client.temoins:
        return client, "témoin sans redirection ⚠"
    motif = "refus" if code == 200 else f"http{code}"
    return client, motif


def main() -> int:
    anomalies: list[str] = []

    print("═" * 100)
    print("A · CONNEXION PAR PROFIL")
    print("═" * 100)
    sessions: dict[str, Client] = {}
    for adresse, libelle, _roles in COMPTES:
        client, etat = ouvrir_session(adresse)
        drapeau = "✓" if etat.startswith("ok") else "✗"
        if not etat.startswith("ok"):
            anomalies.append(f"connexion refusée pour {libelle} ({adresse}) : {etat}")
        else:
            sessions[adresse] = client
        print(f"  {drapeau} {libelle:<28} {adresse:<32} {etat}")

    print()
    for adresse, libelle in COMPTES_REFUSES:
        client, etat = ouvrir_session(adresse)
        refuse = not etat.startswith("ok")
        drapeau = "✓" if refuse else "✗"
        if not refuse:
            anomalies.append(f"{libelle} ({adresse}) a OUVERT une session — il devait être refusé")
        print(f"  {drapeau} {libelle:<28} {adresse:<32} {'refusé' if refuse else 'ACCEPTÉ ⚠'}")

    print()
    print("═" * 100)
    print("B · MATRICE ÉCRANS × PROFILS")
    print("═" * 100)
    entete = f"{'écran':<28}{'permission':<20}" + "".join(
        f"{libelle.split()[0][:11]:<12}" for _, libelle, _ in COMPTES
    )
    print(entete)
    print("─" * len(entete))

    for chemin, permission in ECRANS:
        ligne = f"{chemin:<28}{permission:<20}"
        for adresse, libelle, roles in COMPTES:
            client = sessions.get(adresse)
            if client is None:
                ligne += f"{'—':<12}"
                continue
            code, html, cible = client.lire(chemin)
            etat = classer(code, html, cible)
            attendu_ouvert = permission in permissions_de(roles)
            # /mon-espace ne porte pas de garde propre : il se contente de
            # conditionner la lecture des dossiers à LIRE_DOSSIER. L'attendu
            # suit donc la permission, et la question « un interne devrait-il
            # atteindre l'espace adhérent » est traitée à part, comme un choix
            # de conception et non comme un défaut.
            court = etat.split("→")[0]
            conforme = (court == "ouvert") == attendu_ouvert
            if etat == "panne":
                conforme = False
            marque = "" if conforme else " ⚠"
            if not conforme:
                anomalies.append(
                    f"{chemin} pour {libelle} ({'/'.join(roles)}) : {etat}, "
                    f"attendu {'ouvert' if attendu_ouvert else 'refusé'}"
                )
            affiche = (court + marque)[:11]
            ligne += f"{affiche:<12}"
        print(ligne)

    print()
    print("═" * 100)
    print(f"C · ANOMALIES — {len(anomalies)}")
    print("═" * 100)
    for anomalie in anomalies:
        print(f"  ⚠ {anomalie}")
    if not anomalies:
        print("  aucune")
    return 1 if anomalies else 0


if __name__ == "__main__":
    sys.exit(main())
