#!/usr/bin/env python3
"""Convertit un fichier FICHIER.org (arborescence org-mode) en données JS pour le
graphe cytoscape, écrites dans FICHIER.js sous la forme `const FICHIER = {...}`.

Usage :
    python3 parse_org.py FICHIER.org

Règles générales de conversion (voir la conversation où elles ont été définies
pour le pôle Operating Systems) :
- Le titre de plus haut niveau (ex: "*** Operating Systems") est le nom du pôle,
  pas un nœud du graphe.
- Chaque autre titre (**** ... ****** ...) devient un nœud du graphe.
- S'il n'a pas de propriété "needs", il reçoit une arête depuis son titre parent direct.
- S'il a une propriété "needs", il reçoit une arête depuis chacun de ses prérequis
  (le lien vers le parent structurel est alors redondant et n'est pas tracé).
- Type par défaut : "etape" pour toute étape/activité du parcours (voir FORCE_TYPE
  ci-dessous pour les exceptions spécifiques au pôle Operating Systems).
- Niveau : debutant=1, intermediaire=2, avancé/avance=3, expert=4.
- Les ressources "- [[url][label]] : note" produisent {label, url, note}.
  Les liens org imbriqués dans une note sont réduits à du texte brut (leur libellé).

NODE_ID_OVERRIDES et FORCE_TYPE ci-dessous sont indexés par TITRE de nœud : ce
sont des réglages éditoriaux propres au contenu du pôle Operating Systems (pour
avoir des identifiants courts et des types cohérents avec le graphe PG). Pour un
autre pôle (IA, Hacking, 3D...), ces titres ne correspondront à rien : les nœuds
recevront simplement un identifiant auto-généré et le type par défaut "etape".
Si besoin, complète ces deux dictionnaires au fur et à mesure des pôles.
"""
import re
import sys
import os
import json
import unicodedata

# Type explicite par nœud (choix éditorial, comme dans le graphe PG) : "etape" par défaut
# pour toute étape/activité du parcours ; "notion" pour un concept précis ; "outil" pour
# un logiciel ; "objectif" pour le nœud qui rassemble plusieurs projets à réaliser.
LEVEL_MAP = {"debutant": 1, "intermediaire": 2, "avance": 3, "expert": 4}

NODE_ID_OVERRIDES = {
    "Installer un environnement Linux": "linux-install",
    "Apprendre à utiliser la ligne de commande": "ligne-commande",
    "Écrire des scripts système": "scripts-systeme",
    "Utiliser Linux": "utiliser-linux",
    "Apprendre un éditeur de code": "editeur-code",
    "VScode": "vscode",
    "ViM": "vim",
    "Emacs": "emacs",
    "Programmer son éditeur": "prog-editeur",
    "Programmation système": "prog-systeme",
    "Construire un ordinateur": "construire-ordi",
    "Programmation bas niveau": "bas-niveau",
    "Langage assembleur": "assembleur",
    "Langage C": "langage-c",
    "Serveur web": "serveur-web",
    "Créer une page web locale": "page-locale",
    "Explorer le réseau du lycée": "reseau-lycee",
    "Réaliser des projets": "projets-web",
    "Un système de chat": "chat",
    "Un serveur de fichiers": "serveur-fichiers",
    "Un serveur mail": "serveur-mail",
    "Raspberry pi comme serveur web": "raspberry",
}


def slugify(title):
    if title in NODE_ID_OVERRIDES:
        return NODE_ID_OVERRIDES[title]
    n = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    n = re.sub(r"[^a-zA-Z0-9]+", "-", n).strip("-").lower()
    return n


LINK_RE = re.compile(r"\[\[([^\]]+)\](?:\[([^\]]+)\])?\]")


def strip_links_to_text(text):
    """Remplace tout lien org [[url][label]] ou [[label]] par du texte brut (son libellé)."""
    def _r(m):
        return m.group(2) if m.group(2) else m.group(1)
    return LINK_RE.sub(_r, text)


def parse_resource_line(line):
    line = line.strip()
    if not line.startswith("- "):
        return None
    body = line[2:].strip()
    m = re.match(r"^\[\[([^\]]+)\]\[([^\]]+)\]\](.*)$", body)
    if not m:
        return None
    url, label, rest = m.group(1), m.group(2), m.group(3).strip()
    note = None
    if rest.startswith(":"):
        note = strip_links_to_text(rest[1:].strip())
    res = {"label": label, "url": url}
    if note:
        res["note"] = note
    return res


VALID_TYPES = {"etape", "notion", "outil", "objectif", "concours"}


def parse(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    nodes = []          # dans l'ordre du fichier
    stack = []           # (level, node_id ou None)
    root_level = None    # niveau du titre du pôle (ex: "*** Operating Systems"), qui n'est pas un nœud
    root_start_title = None  # valeur de la propriété :start: du titre du pôle, s'il y en a une
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^(\*+)\s+(.*)$", line)
        if not m:
            i += 1
            continue
        level = len(m.group(1))
        title = m.group(2).strip()
        i += 1
        if root_level is None:
            root_level = level

        # pop la pile jusqu'au parent direct
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_id = stack[-1][1] if stack else None

        # propriétés éventuelles (:PROPERTIES: ... :END:), communes au titre du pôle et aux nœuds
        niveau = None
        needs_titles = []
        type_override = None
        start_title = None
        if i < n and lines[i].strip() == ":PROPERTIES:":
            i += 1
            while i < n and lines[i].strip() != ":END:":
                pm = re.match(r"^:(\w+):\s*(.*)$", lines[i].strip())
                if pm:
                    key, val = pm.group(1), pm.group(2).strip()
                    if key == "niveau":
                        niveau = unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode().lower()
                    elif key == "needs":
                        needs_titles = [g for g in re.findall(r"\[\[([^\]]+)\]\]", val)]
                    elif key == "type":
                        type_override = unicodedata.normalize("NFKD", val).encode("ascii", "ignore").decode().strip().lower()
                        if type_override not in VALID_TYPES:
                            print(f"# avertissement : type {val!r} inconnu pour « {title} » "
                                  f"(valeurs possibles : {', '.join(sorted(VALID_TYPES))})", file=sys.stderr)
                            type_override = None
                    elif key == "start":
                        refs = re.findall(r"\[\[([^\]]+)\]\]", val)
                        start_title = refs[0] if refs else val.strip()
                i += 1
            i += 1  # saute :END:

        if level == root_level:
            # Le titre du pôle lui-même : pas un nœud du graphe, ses enfants directs seront des
            # racines. On retient seulement sa propriété :start:, si elle est présente.
            root_start_title = start_title
            stack.append((level, None))
            # on ignore un éventuel texte sous ce titre : il n'appartient à aucun nœud
            while i < n and not re.match(r"^\*+\s+", lines[i]):
                i += 1
            continue

        node_id = slugify(title)

        # corps du texte : paragraphes puis "Ressources." + liste
        desc_lines = []
        resources = []
        while i < n and not re.match(r"^\*+\s+", lines[i]):
            raw = lines[i]
            stripped = raw.strip()
            if stripped == "Ressources." or stripped == "Ressources. ":
                i += 1
                while i < n and lines[i].strip().startswith("- "):
                    r = parse_resource_line(lines[i])
                    if r:
                        resources.append(r)
                    i += 1
                continue
            if stripped:
                desc_lines.append(strip_links_to_text(stripped))
            i += 1

        description = " ".join(desc_lines).strip()

        needs_ids = [slugify(t) for t in needs_titles]

        nodes.append({
            "id": node_id,
            "title": title,
            "level": level,
            "niveau": niveau,
            "needs": needs_ids,
            "parent": parent_id,
            "description": description,
            "resources": resources,
            "type_override": type_override,
        })
        stack.append((level, node_id))

    return nodes, root_start_title


def build_graph(nodes, start_title=None):
    by_id = {n["id"]: n for n in nodes}
    children = {}
    for n in nodes:
        if n["parent"]:
            children.setdefault(n["parent"], []).append(n["id"])

    edges = []
    for n in nodes:
        if n["needs"]:
            for pre in n["needs"]:
                edges.append((pre, n["id"]))
        elif n["parent"]:
            edges.append((n["parent"], n["id"]))

    out_nodes = []
    for n in nodes:
        # priorité : :type: explicite dans le fichier org, sinon réglage éditorial
        # par titre (FORCE_TYPE), sinon "etape" par défaut.
        ntype = n["type_override"] or "etape"
        entry = {"id": n["id"], "title": n["title"], "type": ntype}
        if n["niveau"] and n["niveau"] in LEVEL_MAP:
            entry["level"] = LEVEL_MAP[n["niveau"]]
        if n["description"]:
            entry["description"] = n["description"]
        if n["resources"]:
            entry["resources"] = n["resources"]
        out_nodes.append(entry)

    out_edges = [{"from": f, "to": t} for f, t in edges]

    # nœud sélectionné par défaut : la propriété :start: du titre du pôle si elle est
    # présente et valide, sinon la première racine du graphe (sans parent ni prérequis).
    start = None
    if start_title:
        start_id = slugify(start_title)
        if start_id in by_id:
            start = start_id
        else:
            print(f"# avertissement : le nœud de départ {start_title!r} (propriété :start:) "
                  f"est introuvable, utilisation de la racine par défaut.", file=sys.stderr)
    if start is None:
        roots = [n["id"] for n in nodes if not n["parent"] and not n["needs"]]
        start = roots[0] if roots else nodes[0]["id"]
    return start, out_nodes, out_edges


def js_string(s):
    return json.dumps(s, ensure_ascii=False)


def to_js(const_name, start, nodes, edges):
    lines = []
    lines.append(f"const {const_name} = {{")
    lines.append(f"  start: {js_string(start)},")
    lines.append("  nodes: [")
    for n in nodes:
        parts = [f"id: {js_string(n['id'])}", f"title: {js_string(n['title'])}", f"type: {js_string(n['type'])}"]
        if "level" in n:
            parts.append(f"level: {n['level']}")
        line = "    { " + ", ".join(parts)
        if n.get("description"):
            line += ",\n      description: " + js_string(n["description"])
        if n.get("resources"):
            res_items = []
            for r in n["resources"]:
                rp = [f"label: {js_string(r['label'])}", f"url: {js_string(r['url'])}"]
                if r.get("note"):
                    rp.append(f"note: {js_string(r['note'])}")
                res_items.append("{ " + ", ".join(rp) + " }")
            line += ",\n      resources: [" + ", ".join(res_items) + "]"
        line += " },"
        lines.append(line)
    lines.append("  ],")
    lines.append("  edges: [")
    edge_strs = [f'{{ from: {js_string(e["from"])}, to: {js_string(e["to"])} }}' for e in edges]
    for chunk_start in range(0, len(edge_strs), 3):
        lines.append("    " + ", ".join(edge_strs[chunk_start:chunk_start + 3]) + ",")
    lines.append("  ]")
    lines.append("};")
    return "\n".join(lines)


def js_identifier(name):
    """Transforme un nom de fichier (sans extension) en identifiant JS valide et
    en MAJUSCULES, ex. 'os' -> 'OS', 'intelligence-artificielle' -> 'INTELLIGENCE_ARTIFICIELLE'."""
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    n = re.sub(r"[^a-zA-Z0-9_]+", "_", n).strip("_").upper()
    if not n or n[0].isdigit():
        n = "_" + n
    return n


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".org"):
        print("Usage : python3 parse_org.py FICHIER.org", file=sys.stderr)
        sys.exit(1)

    org_path = sys.argv[1]
    base = os.path.splitext(os.path.basename(org_path))[0]
    const_name = js_identifier(base)
    js_path = os.path.join(os.path.dirname(org_path), base + ".js")

    nodes, root_start_title = parse(org_path)
    start, out_nodes, out_edges = build_graph(nodes, root_start_title)
    print(f"# {len(out_nodes)} nœuds, {len(out_edges)} arêtes, racine de départ retenue : {start}")
    js = to_js(const_name, start, out_nodes, out_edges)
    open(js_path, "w", encoding="utf-8").write(js)
    print(f"-> {js_path} (const {const_name})")
