/**
 * Importe le document de conception dans le site, sans le réécrire.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * UNE SEULE SOURCE, ET ELLE N'EST PAS ICI
 *
 * Le document vit dans `Docs/architecture/document-de-conception/`. Ce script le
 * découpe en morceaux que le site assemble :
 *
 *     contenu/document.css     les styles du document, tels quels
 *     contenu/theme.css        les seules variables de couleur, pour les pages du site
 *     contenu/document.html    le corps, tel quel
 *     contenu/document.json    le titre, la version, le nombre de sections, le sommaire
 *     public/document.html     la page complète du document, servie telle quelle
 *
 * ⚠️ **Rien n'est reformulé, rien n'est coupé.** Le seul retrait est celui des
 * balises que la page HTML possède déjà.
 *
 * ⚠️ **`theme.css` existe pour qu'il n'y ait qu'une palette.** Les pages du site
 * (accueil, prérequis, mise en œuvre) sont écrites en React et ne partagent pas
 * la feuille du document, qui met en forme un texte long. Elles partagent en
 * revanche ses couleurs, et les recopier à la main aurait produit deux identités
 * qui divergent au premier ajustement.
 *
 * ⚠️ **Le fichier engendré est versionné.** L'hébergeur construit depuis une copie
 * du dépôt : la source est là, et la réimportation tourne avant chaque
 * construction. Mais si elle venait à manquer, le site doit se construire quand
 * même, avec le dernier contenu importé, plutôt que d'échouer et de ne rien
 * servir. Le script le dit alors, fort, sur la sortie d'erreur.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ICI = dirname(fileURLToPath(import.meta.url));
const PROJET = resolve(ICI, "..");
const SOURCE = resolve(
  PROJET,
  "..",
  "Docs/architecture/document-de-conception/architecture-multitenant-cga.html",
);
const DOSSIER = join(PROJET, "contenu");
const SITE = JSON.parse(readFileSync(join(PROJET, "donnees", "site.json"), "utf8"));

/** Le sommaire, lu dans le document lui-même : numéro, titre, ancre. */
function sommaire(html) {
  const sections = [];
  const motif = /<section id="(s\d+)">\s*<h2>(?:<span class="num">(\d+)<\/span>)?([\s\S]*?)<\/h2>/g;
  let trouve;
  while ((trouve = motif.exec(html)) !== null) {
    const titre = trouve[3]
      .replace(/<[^>]+>/g, "")
      .replace(/\s+/g, " ")
      .trim();
    sections.push({ ancre: trouve[1], numero: trouve[2] ?? null, titre });
  }
  return sections;
}

/** Le bloc qui commence à `depuis`, accolades équilibrées comprises. */
function bloc(css, depuis) {
  const ouverture = css.indexOf("{", depuis);
  if (ouverture === -1) return null;
  let profondeur = 0;
  for (let i = ouverture; i < css.length; i += 1) {
    if (css[i] === "{") profondeur += 1;
    else if (css[i] === "}") {
      profondeur -= 1;
      if (profondeur === 0) return { debut: depuis, fin: i + 1, dedans: css.slice(ouverture + 1, i) };
    }
  }
  return null;
}

/**
 * Le thème sombre du document, rendu **choisissable**.
 *
 * ⚠️ Seule transformation que ce script fait subir au document, et elle ne touche pas au texte :
 * le document déclare ses couleurs sombres sous `@media (prefers-color-scheme: dark)`, donc au
 * goût du système. Sur un site, un lecteur veut pouvoir choisir. Le bloc est recopié tel quel sous
 * `:root[data-theme="dark"]`, sans en changer une valeur : deux palettes qui divergeraient seraient
 * pires que pas de bascule du tout.
 */
function themeSombreExplicite(css) {
  const debut = css.indexOf("@media (prefers-color-scheme: dark)");
  if (debut === -1) return "";
  const trouve = bloc(css, debut);
  if (trouve === null) return "";
  const variables = trouve.dedans.replace(
    ':root:not([data-theme="light"])',
    ':root[data-theme="dark"]',
  );
  return `\n\n/* Engendré par outils/importer-le-document.mjs : le même thème, choisi plutôt que subi. */\n${variables}\n`;
}

/** Les seules déclarations de couleurs, pour les pages écrites en React. */
function variablesDeTheme(css) {
  const clair = bloc(css, css.indexOf(":root"));
  const sombreSysteme = bloc(css, css.indexOf("@media (prefers-color-scheme: dark)"));
  const morceaux = [
    "/* Engendré par outils/importer-le-document.mjs. Ne pas modifier ici :",
    "   la source est le document de conception, et lui seul. */",
    clair ? `:root {${clair.dedans}}` : "",
    sombreSysteme ? css.slice(sombreSysteme.debut, sombreSysteme.fin) : "",
    themeSombreExplicite(css),
  ];
  return morceaux.filter(Boolean).join("\n") + "\n";
}

/** La ligne de version du document. */
function version(html) {
  const eyebrow = html.match(/<p class="eyebrow">([\s\S]*?)<\/p>/);
  const ligne = eyebrow ? eyebrow[1].replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim() : "";
  const numero = ligne.match(/version\s+(\d+)/);
  return { ligne, numero: numero ? Number(numero[1]) : null };
}

/**
 * La navigation du site, engendrée depuis `donnees/site.json`.
 *
 * ⚠️ **Le même fichier sert les pages React.** Une barre recopiée dans deux langages diverge au
 * premier onglet ajouté : l'un des deux l'oublie, et le lecteur découvre une page en la devinant.
 */
function navigation(courant) {
  return SITE.navigation
    .map((entree) => {
      const actif = entree.href === courant;
      return `<a class="site-nav__lien${actif ? " est-actif" : ""}" href="${entree.href}"${
        actif ? ' aria-current="page"' : ""
      }>${entree.libelle}</a>`;
    })
    .join("\n        ");
}

/**
 * La page complète du document, engendrée à la construction (`public/document.html`).
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * ⚠️ POURQUOI UNE PAGE STATIQUE, ET NON UN COMPOSANT REACT
 *
 * Le premier montage rendait le document dans un composant serveur. React sérialise
 * alors **une seconde copie** du contenu dans la charge utile de navigation : mesuré
 * sur ce document, 2,17 Mo servis pour 966 Ko de texte, soit 340 Ko compressés au
 * lieu de 237. Sur les connexions que ce cabinet vise, et sur les téléphones
 * d'entrée de gamme qui devraient ensuite hydrater cent trente sections, c'est un
 * coût qu'aucune fonctionnalité ne justifie : la page ne contient aucun état.
 *
 * Elle est donc assemblée ici, une fois, et servie comme fichier. Les autres pages
 * du site, elles, sont légères et restent des pages React.
 * ─────────────────────────────────────────────────────────────────────────────
 */
function pageComplete({ titre, chapo, corps, css, version, sections, figures }) {
  const description = chapo.slice(0, 300).replace(/"/g, "&quot;");
  return `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${titre}</title>
<meta name="description" content="${description}">
<meta name="robots" content="noindex, nofollow">
<meta name="author" content="${SITE.concepteur.nom}">
<meta property="og:title" content="${titre}">
<meta property="og:description" content="${description}">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#f7f8fa">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0b1117">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<!-- ⚠️ Le thème choisi est posé avant le premier rendu : appliqué après, la page
     s'afficherait claire une fraction de seconde avant de virer au sombre. -->
<script>try{var t=localStorage.getItem('cga-theme');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
<style>
${css}
</style>
<style>
/* La coquille du site, autour du document. Aucune règle ne vise le document lui-même,
   dont les styles sont complets : les corriger ici ferait diverger le site du fichier
   que le cabinet relit et republie.

   ⚠️ La seule exception est la marge du corps. Le document est un fragment : il ne
   porte ni <html> ni <body>, donc pas de remise à zéro de la marge que le navigateur
   applique par défaut. Publié comme artefact, il hérite d'une page qui la remet à
   zéro ; servi ici, il gardait huit pixels de chaque côté, ce qui décollait la barre
   des bords et faisait déborder la page de neuf pixels sous 340 px de large. */
body{margin:0}
.site-entete{position:sticky;top:0;z-index:50;background:var(--surface);border-bottom:1px solid var(--trait)}
.site-entete__trait{display:block;height:2px;width:0;background:var(--accent);transition:width 120ms linear}
.site-entete__barre{max-width:var(--large);margin:0 auto;padding:10px 20px;display:flex;align-items:center;gap:12px 20px;flex-wrap:wrap}
.site-marque{display:flex;flex-direction:column;min-width:0;margin-right:auto}
.site-marque__nom{font:600 13.5px/1.35 var(--ui);color:var(--encre);text-decoration:none}
.site-marque__detail{font:400 11.5px/1.5 var(--ui);color:var(--encre-tres-doux)}
.site-nav{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.site-nav::-webkit-scrollbar{display:none}
.site-nav__lien{white-space:nowrap;padding:7px 12px;border-radius:999px;font:500 12.5px/1 var(--ui);color:var(--encre-doux);text-decoration:none;border:1px solid transparent}
.site-nav__lien:hover{color:var(--encre);background:var(--surface-2)}
.site-nav__lien.est-actif{color:var(--accent-vif);background:var(--accent-doux);border-color:var(--accent)}
.site-gestes{display:flex;gap:8px;flex-wrap:wrap}
.site-bouton{min-height:32px;padding:0 12px;display:inline-flex;align-items:center;border:1px solid var(--trait);border-radius:8px;background:var(--surface-2);color:var(--encre-doux);font:500 12px/1 var(--ui);text-decoration:none;cursor:pointer}
.site-bouton:hover{border-color:var(--trait-fort);color:var(--encre)}
@media (max-width:719px){
  .site-marque{width:100%;margin-right:0}
  .site-nav{width:100%;order:3}
  .site-gestes{order:2}
}
@media print{.site-entete{display:none}}
</style>
</head>
<body>
<header class="site-entete">
  <span class="site-entete__trait" id="progression" aria-hidden="true"></span>
  <div class="site-entete__barre">
    <span class="site-marque">
      <a class="site-marque__nom" href="/">${SITE.nom}</a>
      <span class="site-marque__detail">${
        version !== null ? `document version ${version} · ` : ""
      }${sections} sections · ${figures} figures</span>
    </span>
    <nav class="site-nav" aria-label="Sections du site">
        ${navigation("/document")}
    </nav>
    <span class="site-gestes">
      <a class="site-bouton" href="#sommaire">Sommaire</a>
      <button type="button" class="site-bouton" id="imprimer">Imprimer</button>
      <button type="button" class="site-bouton" id="theme" aria-pressed="false">Sombre</button>
    </span>
  </div>
</header>
${corps}
<script>
(function(){
  var racine=document.documentElement, bouton=document.getElementById('theme'), trait=document.getElementById('progression');
  function sombre(){return racine.dataset.theme? racine.dataset.theme==='dark' : matchMedia('(prefers-color-scheme: dark)').matches;}
  function nommer(){bouton.textContent=sombre()?'Clair':'Sombre';bouton.setAttribute('aria-pressed',String(sombre()));}
  nommer();
  bouton.addEventListener('click',function(){
    var prochain=sombre()?'light':'dark';
    racine.dataset.theme=prochain;
    try{localStorage.setItem('cga-theme',prochain);}catch(e){/* navigation privée : le thème vaut pour cette page */}
    nommer();
  });
  document.getElementById('imprimer').addEventListener('click',function(){window.print();});
  function progresser(){
    var hauteur=document.documentElement.scrollHeight-innerHeight;
    trait.style.width=(hauteur>0?Math.min(100,scrollY/hauteur*100):0)+'%';
  }
  progresser();
  addEventListener('scroll',progresser,{passive:true});
})();
</script>
</body>
</html>
`;
}

function importer() {
  const brut = readFileSync(SOURCE, "utf8");

  const styles = [...brut.matchAll(/<style>([\s\S]*?)<\/style>/g)].map((m) => m[1]).join("\n");
  const avecThemeExplicite = styles + themeSombreExplicite(styles);
  // Le corps : tout ce qui suit le dernier bloc de styles. Le document est un
  // fragment (il n'a ni <html> ni <body>), c'est ce qui rend ce découpage sûr.
  const finDesStyles = brut.lastIndexOf("</style>") + "</style>".length;
  // ⚠️ Une ancre, et rien d'autre : le document nomme son sommaire (`aria-label="Sommaire"`)
  // sans lui donner d'identifiant, et le bouton « Sommaire » de la barre a besoin d'une cible.
  // Ajouter un attribut ne change pas le texte ; réécrire le sommaire en changerait le sens.
  const corps = brut
    .slice(finDesStyles)
    .trim()
    .replace('<nav class="sommaire"', '<nav id="sommaire" class="sommaire"');

  const titre = (brut.match(/<title>([\s\S]*?)<\/title>/) ?? [, "Document de conception"])[1].trim();
  const chapo = (brut.match(/<p class="chapo">([\s\S]*?)<\/p>/) ?? [, ""])[1]
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
  const sections = sommaire(brut);
  const figures = (corps.match(/<figure/g) ?? []).length;
  const { ligne, numero } = version(brut);

  mkdirSync(DOSSIER, { recursive: true });
  writeFileSync(join(DOSSIER, "document.css"), avecThemeExplicite, "utf8");
  writeFileSync(join(DOSSIER, "theme.css"), variablesDeTheme(styles), "utf8");
  writeFileSync(join(DOSSIER, "document.html"), corps, "utf8");
  writeFileSync(
    join(DOSSIER, "document.json"),
    JSON.stringify(
      {
        titre,
        chapo,
        ligneDeVersion: ligne,
        version: numero,
        sections: sections.length,
        figures,
        importeLe: new Date().toISOString(),
        sommaire: sections,
      },
      null,
      2,
    ) + "\n",
    "utf8",
  );

  mkdirSync(join(PROJET, "public"), { recursive: true });
  const page = pageComplete({
    titre,
    chapo,
    corps,
    css: avecThemeExplicite,
    version: numero,
    sections: sections.length,
    figures,
  });
  writeFileSync(join(PROJET, "public", "document.html"), page, "utf8");

  console.log(
    `document importé : version ${numero ?? "?"}, ${sections.length} sections, ` +
      `${figures} figures, ` +
      // ⚠️ `page.length` compte des **caractères**, pas des octets : sur ce document, accents
      // compris, l'écart est de vingt kilo-octets. Ce qui voyage sur le réseau, c'est l'UTF-8.
      `page servie ${Math.round(Buffer.byteLength(page, "utf8") / 1024)} Ko`,
  );
}

if (existsSync(SOURCE)) {
  importer();
} else if (existsSync(join(DOSSIER, "document.html"))) {
  console.error(
    `⚠️  document source introuvable (${SOURCE}).\n` +
      "   Le site sera construit avec le dernier contenu importé, qui peut être en retard.",
  );
} else {
  console.error(`document source introuvable (${SOURCE}), et aucun contenu déjà importé.`);
  process.exit(1);
}
