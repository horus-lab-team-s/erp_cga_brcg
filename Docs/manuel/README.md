# Manuel — Comptabilité et fiscalité camerounaises

Manuel de référence pour comprendre les rouages du métier et défendre la
plateforme devant des professionnels de la comptabilité et de la fiscalité.

**Livrable : `Manuel-comptabilite-fiscalite-CGA.pdf`** — 92 pages.

## Régénérer le PDF

Les sources sont découpées en fragments HTML, assemblés dans cet ordre :

    00_tete.html            couverture, styles, mode d'emploi
    01_sommaire_partie1.html sommaire + Partie I  (le cadre)
    02_partie2.html          Partie II  (comptabilité)
    03_partie3.html          Partie III (fiscalité)
    04a_partie4_AB.html      Partie IV  (scénarios A et B)
    04b_partie4_CDEF.html    Partie IV  (scénarios C à F)
    05_partie5_6.html        Parties V (DSF) et VI (stratagèmes)
    06_partie7_annexes.html  Partie VII et annexes

Assemblage et rendu :

    head -n -2 00_tete.html > _t.tmp
    cat _t.tmp 01_*.html 02_*.html 03_*.html 04a_*.html 04b_*.html 05_*.html 06_*.html > manuel.html
    rm _t.tmp
    google-chrome --headless=new --no-pdf-header-footer \
      --print-to-pdf=sortie.pdf manuel.html

La pagination et les signets sont ajoutés ensuite par un script `pypdf` +
`reportlab` (voir l'historique de session).

## Avertissement

Aucune valeur légale citée dans ce manuel n'a été validée sur le Code Général
des Impôts. Les mécanismes décrits sont structurels ; les chiffres portent le
statut `A_VALIDER` du référentiel ou sont signalés comme absents.
