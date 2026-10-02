#!/usr/bin/env python3
"""
Club CYBR — construction des pages missions
============================================

Utilisation (depuis le dossier cybr/) :

    python3 construire_missions.py

Ce que fait le script :
  1. Lit chaque fichier .md du dossier missions/ (ceux qui commencent par _ sont ignorés).
  2. Crée une page indépendante par mission : missions/prompts.md -> mission-prompts/index.html
  3. Met à jour la liste des missions dans index.html, entre les deux repères
         <!-- MISSIONS:DEBUT -->  et  <!-- MISSIONS:FIN -->
     (s'ils n'existent pas, ils sont ajoutés juste après la section des pôles).

Les pages missions reprennent automatiquement le style, l'en-tête et le pied de page
de index.html : si tu modifies le thème du site, relance simplement le script.

Aucune installation nécessaire : Python 3 suffit. Le format des fichiers .md est
expliqué dans missions/_modele.md.
"""

import html
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
DOSSIER_MD = ICI / "missions"
INDEX = ICI / "index.html"
CSS_MISSIONS = "missions.css"
DEBUT, FIN = "<!-- MISSIONS:DEBUT -->", "<!-- MISSIONS:FIN -->"

# Clés de l'en-tête qui ne sont pas affichées comme « infos » sous le titre
# (Code et Statut sont acceptés pour compatibilité mais ne sont plus affichés)
CLES_SPECIALES = {"code", "pole", "statut", "resume", "ordre"}
MOTS_ETAPES = {1: ["Pour commencer"], 2: ["D'abord", "Ensuite"], 3: ["D'abord", "Ensuite", "Enfin"],
               4: ["D'abord", "Ensuite", "Puis", "Enfin"]}


def normaliser(texte):
    """« À rendre » -> « a rendre » : sert à reconnaître les titres de section et les clés."""
    texte = unicodedata.normalize("NFD", texte.strip().lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def sans_balises(texte):
    return re.sub(r"<[^>]+>", "", texte)


# ---------------------------------------------------------------------------
# Mini convertisseur Markdown (syntaxe de base uniquement)
# ---------------------------------------------------------------------------

def en_ligne(texte):
    """Gras, italique, code, liens."""
    t = html.escape(texte, quote=False)
    codes = []
    t = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", t)


def blocs(lignes):
    """Découpe des lignes Markdown en blocs : ('titre', niveau, texte), ('p', texte),
    ('ul', [items]), ('ol', [items]), ('code', texte)."""
    res, i = [], 0
    while i < len(lignes):
        ligne = lignes[i]
        if not ligne.strip():
            i += 1
        elif ligne.startswith("```"):
            j = i + 1
            while j < len(lignes) and not lignes[j].startswith("```"):
                j += 1
            res.append(("code", "\n".join(lignes[i + 1:j])))
            i = j + 1
        elif re.match(r"#{1,6} ", ligne):
            niveau = len(ligne) - len(ligne.lstrip("#"))
            res.append(("titre", niveau, ligne[niveau:].strip()))
            i += 1
        elif re.match(r"\s*([-*+]|\d+[.)])\s+", ligne):
            ordonnee = bool(re.match(r"\s*\d+[.)]\s+", ligne))
            items = []
            while i < len(lignes) and lignes[i].strip():
                m = re.match(r"\s*([-*+]|\d+[.)])\s+(.*)", lignes[i])
                if m:
                    items.append(m.group(2))
                elif items:                      # suite d'un élément sur plusieurs lignes
                    items[-1] += " " + lignes[i].strip()
                i += 1
            res.append(("ol" if ordonnee else "ul", items))
        else:
            para = []
            while (i < len(lignes) and lignes[i].strip() and not lignes[i].startswith(("```", "#"))
                   and not re.match(r"\s*([-*+]|\d+[.)])\s+", lignes[i])):
                para.append(lignes[i].strip())
                i += 1
            res.append(("p", " ".join(para)))
    return res


def blocs_en_html(liste, classe_liste="m-list"):
    sortie = []
    for b in liste:
        if b[0] == "p":
            sortie.append(f"<p>{en_ligne(b[1])}</p>")
        elif b[0] in ("ul", "ol"):
            balise = b[0]
            sortie.append(f'<{balise} class="{classe_liste}">' +
                          "".join(f"<li>{en_ligne(x)}</li>" for x in b[1]) + f"</{balise}>")
        elif b[0] == "code":
            sortie.append(f'<pre class="m-pre"><code>{html.escape(b[1])}</code></pre>')
        elif b[0] == "titre":
            sortie.append(f"<h4>{en_ligne(b[2])}</h4>")
    return "\n".join(sortie)


# ---------------------------------------------------------------------------
# Lecture d'un fichier mission
# ---------------------------------------------------------------------------

def lire_mission(chemin):
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    while lignes and not lignes[0].strip():
        lignes.pop(0)
    if not lignes or not lignes[0].startswith("# "):
        raise ValueError("la première ligne doit être le titre, par exemple : # Mon *titre.*")
    titre = lignes[0][2:].strip()

    # En-tête : lignes « Clé : valeur » juste après le titre, jusqu'à la première ligne vide
    i = 1
    while i < len(lignes) and not lignes[i].strip():
        i += 1
    infos, meta = [], {}
    while i < len(lignes) and lignes[i].strip():
        cle, sep, valeur = lignes[i].partition(":")
        if not sep:
            raise ValueError(f"ligne d'en-tête sans « : » → {lignes[i]!r}")
        cle_n = normaliser(cle)
        meta[cle_n] = valeur.strip()
        if cle_n not in CLES_SPECIALES:
            infos.append((cle.strip(), valeur.strip()))
        i += 1

    # Corps : texte d'introduction puis sections « ## »
    intro, sections, courant = [], [], None
    for ligne in lignes[i:]:
        if ligne.startswith("## "):
            courant = (ligne[3:].strip(), [])
            sections.append(courant)
        elif courant:
            courant[1].append(ligne)
        else:
            intro.append(ligne)

    return {
        "slug": chemin.stem,
        "titre": titre,
        "titre_court": sans_balises(en_ligne(titre)).rstrip(". "),
        "pole": meta.get("pole", ""),
        "resume": meta.get("resume", ""),
        "ordre": float(meta["ordre"]) if meta.get("ordre", "").replace(".", "", 1).isdigit() else 999,
        "infos": infos,
        "intro": blocs(intro),
        "sections": [(nom, blocs(contenu)) for nom, contenu in sections],
    }


# ---------------------------------------------------------------------------
# Rendu
# ---------------------------------------------------------------------------

def rendu_ressources(blocs_section):
    sortie = []
    for b in blocs_section:
        if b[0] == "titre":
            sortie.append(f'<div class="res-group">{html.escape(b[2]).upper()}</div>')
        elif b[0] in ("ul", "ol"):
            items = []
            for item in b[1]:
                m = re.match(r"\[([^\]]+)\]\(([^)\s]+)\)\s*[:—–-]?\s*(.*)", item)
                if m:
                    domaine = re.sub(r"^https?://(www\.)?", "", m.group(2)).split("/")[0]
                    note = f"{domaine} · {en_ligne(m.group(3))}" if m.group(3) else domaine
                    items.append(f'<li><a href="{m.group(2)}" target="_blank" rel="noopener">'
                                 f'{en_ligne(m.group(1))} ↗</a><p class="res-note">{note}</p></li>')
                else:
                    items.append(f"<li>{en_ligne(item)}</li>")
            sortie.append('<ul class="res">' + "".join(items) + "</ul>")
        else:
            sortie.append(f'<div class="m-frame-txt">{blocs_en_html([b])}</div>')
    return "\n".join(sortie)


def rendu_outils(blocs_section):
    sortie = []
    for b in blocs_section:
        if b[0] in ("ul", "ol"):
            items = []
            for item in b[1]:
                m = re.match(r"\*\*(.+?)\*\*\s*[:—–-]?\s*(.*)", item)
                if m:
                    items.append(f"<li><strong>{en_ligne(m.group(1))}</strong><span>{en_ligne(m.group(2))}</span></li>")
                else:
                    items.append(f"<li><span>{en_ligne(item)}</span></li>")
            sortie.append('<ul class="res m-tools">' + "".join(items) + "</ul>")
        else:
            sortie.append(f'<div class="m-frame-txt">{blocs_en_html([b])}</div>')
    return "\n".join(sortie)


def cadre(titre, contenu):
    return f'''<div class="graph-frame m-frame">
        <div class="graph-header"><div><span class="terminal-dot red"></span><span class="terminal-dot yellow"></span><span class="terminal-dot green"></span><strong>{titre}</strong></div></div>
        {contenu}
      </div>'''


def page_mission(m, precedente, suivante, modele):
    gauche, droite, etapes, ressources, outils = [], [], None, None, None
    for nom, contenu in m["sections"]:
        n = normaliser(nom)
        if n == "objectif":
            gauche.insert(0, f'<div class="m-prose">{blocs_en_html(contenu)}</div>')
        elif n in ("a rendre", "livrables"):
            droite.append(f'<span class="section-label">{html.escape(nom)}</span>{blocs_en_html(contenu)}')
        elif n in ("reussie si", "mission reussie si", "criteres"):
            droite.append(f'<div class="m-ok"><span class="section-label">{html.escape(nom)}</span>{blocs_en_html(contenu)}</div>')
        elif n == "pour demarrer":
            etapes = [x for b in contenu if b[0] in ("ol", "ul") for x in b[1]]
        elif n == "ressources":
            ressources = rendu_ressources(contenu)
        elif n == "outils":
            outils = rendu_outils(contenu)
        elif n in ("a savoir", "attention", "important"):
            gauche.append(f'<div class="m-note">{blocs_en_html(contenu)}</div>')
        else:
            gauche.append(f'<div class="m-extra"><h3>{en_ligne(nom)}</h3>{blocs_en_html(contenu)}</div>')

    infos = "".join(f"<div><i></i>{html.escape(k.upper())}<b>{en_ligne(v)}</b></div>" for k, v in m["infos"])
    kicker = " - ".join(x for x in ["MISSION", (m["pole"].upper() if normaliser(m["pole"]).startswith("tous") else "PÔLE " + m["pole"].upper()) if m["pole"] else ""] if x)

    bloc_etapes = ""
    if etapes:
        mots = MOTS_ETAPES.get(len(etapes), [f"Étape {k}" for k in range(1, len(etapes) + 1)])
        bloc_etapes = f'''
  <section class="principle page-width">
    <div class="principle-card">
      <div class="principle-title"><span class="section-label">POUR DÉMARRER</span><h2>Par où<br><em>commencer.</em></h2></div>
      <div class="steps m-steps" style="--n:{len(etapes)}">{"".join(f'<div class="step"><strong>{mot}</strong><p>{en_ligne(e)}</p></div>' for mot, e in zip(mots, etapes))}</div>
    </div>
  </section>'''

    cadres = [cadre("RESSOURCES", ressources) if ressources else "", cadre("OUTILS", outils) if outils else ""]
    bloc_boite = ""
    if ressources or outils:
        bloc_boite = f'''
  <section class="m-sec page-width">
    <div class="section-topline curriculum-intro"><div><span class="section-label">RESSOURCES ET OUTILS</span><h2>Ta boîte <em>à outils.</em></h2></div></div>
    <div class="m-two">{"".join(cadres)}</div>
  </section>'''

    contenu = f'''
  <main class="m-page" id="haut">
  <section class="m-hero page-width">
    <a class="back-link" href="../index.html#missions">← TOUTES LES MISSIONS</a>
    <div class="kicker"><span class="kicker-line"></span> {html.escape(kicker)}</div>
    <h1>{en_ligne(m["titre"])}</h1>
    <div class="hero-lead">{blocs_en_html(m["intro"])}</div>
    {f'<div class="m-facts">{infos}</div>' if infos else ""}
  </section>

  <section class="m-sec page-width">
    <div class="section-topline curriculum-intro"><div><span class="section-label">OBJECTIF</span><h2>Ce qu'on attend <em>de toi.</em></h2></div></div>
    <div class="m-body">
      <div>{"".join(gauche)}</div>
      <div class="m-side">{"".join(droite)}</div>
    </div>
  </section>
  {bloc_etapes}
  {bloc_boite}
  <nav class="m-pager page-width" aria-label="Autres missions">
    <a href="../mission-{precedente["slug"]}/index.html"><small>← MISSION PRÉCÉDENTE</small><b>{html.escape(precedente["titre_court"])}</b></a>
    <a href="../mission-{suivante["slug"]}/index.html"><small>MISSION SUIVANTE →</small><b>{html.escape(suivante["titre_court"])}</b></a>
  </nav>
  </main>'''

    return (modele.replace("{{TITRE}}", html.escape(f"{m['titre_court']} — Club CYBR"))
                  .replace("{{DESCRIPTION}}", html.escape(sans_balises(blocs_en_html(m["intro"]))[:200]))
                  .replace("{{CONTENU}}", contenu))


def liste_missions(missions):
    cartes = "".join(f'''
    <a class="mission" href="mission-{m["slug"]}/index.html">
      <strong>{html.escape(m["titre_court"])}</strong>
      <p>{en_ligne(m["resume"])}</p>
      <span class="pole-arrow">↗</span>
    </a>''' for m in missions)
    return f'''{DEBUT}
    <section id="missions" class="missions page-width">
      <div class="section-topline curriculum-intro">
        <div><span class="section-label">MISSIONS EN COURS</span><h2>Des projets <em>pour de vrai.</em></h2></div>
        <p>Chaque mission répond à un besoin réel du lycée. Ouvre le brief : <strong>objectif, ressources, outils.</strong></p>
      </div>
      <div class="mission-grid">{cartes}
      </div>
    </section>
    {FIN}'''


# ---------------------------------------------------------------------------
# Modèle de page tiré de index.html
# ---------------------------------------------------------------------------

def vers_parent(fragment):
    """Adapte les liens de index.html pour une page située un dossier plus bas."""
    fragment = re.sub(r'(href|src)="(?!https?:|mailto:|data:|/|\.\./)#', r'\1="../index.html#', fragment)
    fragment = re.sub(r'(href|src)="(?!https?:|mailto:|data:|/|#|\.\./)', r'\1="../', fragment)
    return fragment


def construire_modele(index_html):
    styles = "\n".join(re.findall(r"<style[^>]*>.*?</style>", index_html, re.S))
    liens_css = "\n".join(l for l in re.findall(r"<link[^>]+>", index_html)
                          if "stylesheet" in l and CSS_MISSIONS not in l)
    entete = re.search(r"<header.*?</header>", index_html, re.S)
    pied = re.search(r"<footer.*?</footer>", index_html, re.S)
    fonds = re.findall(r'<div class="bg-grid"[^>]*></div>', index_html)
    if not entete or not pied:
        raise ValueError("index.html doit contenir un <header> et un <footer>")
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#063d70">
  <meta name="description" content="{{{{DESCRIPTION}}}}">
  <title>{{{{TITRE}}}}</title>
  {vers_parent(liens_css)}
  {styles}
  <link rel="stylesheet" href="../{CSS_MISSIONS}">
</head>
<body>
  {"".join(fonds)}
  {vers_parent(entete.group(0))}
{{{{CONTENU}}}}
  {vers_parent(pied.group(0)).replace('"../index.html#accueil"', '"#haut"')}
</body>
</html>
'''


def mettre_a_jour_index(index_html, missions):
    bloc = liste_missions(missions)
    if DEBUT in index_html and FIN in index_html:
        index_html = re.sub(re.escape(DEBUT) + ".*?" + re.escape(FIN), lambda _: bloc, index_html, flags=re.S)
    else:
        poles = re.search(r'<section[^>]*id="poles".*?</section>', index_html, re.S)
        if not poles:
            raise ValueError(f"ajoute {DEBUT} et {FIN} dans index.html, là où la liste doit apparaître")
        index_html = index_html[:poles.end()] + "\n\n    " + bloc + index_html[poles.end():]
        print("  Repères MISSIONS ajoutés dans index.html, juste après la section des pôles.")
    if CSS_MISSIONS not in index_html:
        index_html = index_html.replace("</head>", f'  <link rel="stylesheet" href="{CSS_MISSIONS}">\n</head>', 1)
        print(f"  Lien vers {CSS_MISSIONS} ajouté dans index.html.")
    nav = re.search(r'<nav class="header-nav".*?</nav>', index_html, re.S)
    if nav and 'href="#missions"' not in nav.group(0):
        nouveau = nav.group(0).replace("</nav>", '  <a class="nav-ms" href="#missions">MISSIONS</a>\n      </nav>')
        index_html = index_html.replace(nav.group(0), nouveau)
        print("  Bouton MISSIONS ajouté dans le menu.")
    return index_html


def main():
    if not INDEX.exists():
        sys.exit(f"Introuvable : {INDEX}. Lance le script depuis le dossier cybr/.")
    fichiers = sorted(p for p in DOSSIER_MD.glob("*.md") if not p.name.startswith("_"))
    if not fichiers:
        sys.exit("Aucun fichier .md dans missions/.")

    missions, erreurs = [], 0
    for f in fichiers:
        try:
            missions.append(lire_mission(f))
        except ValueError as e:
            print(f"  ✗ {f.name} : {e}")
            erreurs += 1
    missions.sort(key=lambda m: (m["ordre"], m["slug"]))

    index_html = INDEX.read_text(encoding="utf-8")
    index_html = mettre_a_jour_index(index_html, missions)
    modele = construire_modele(index_html)

    for k, m in enumerate(missions):
        dossier = ICI / f"mission-{m['slug']}"
        dossier.mkdir(exist_ok=True)
        page = page_mission(m, missions[k - 1], missions[(k + 1) % len(missions)], modele)
        (dossier / "index.html").write_text(page, encoding="utf-8")
        print(f"  ✓ missions/{m['slug']}.md → mission-{m['slug']}/index.html")

    INDEX.write_text(index_html, encoding="utf-8")
    print(f"\n{len(missions)} mission(s) publiée(s), liste mise à jour dans index.html."
          + (f" {erreurs} fichier(s) ignoré(s) à cause d'une erreur." if erreurs else ""))


if __name__ == "__main__":
    main()
