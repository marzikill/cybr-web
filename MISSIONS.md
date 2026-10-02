# Ajouter ou modifier une mission

1. Copie `missions/_modele.md` et renomme la copie, par exemple `missions/robotique.md`.
   Le nom du fichier donne l'adresse de la page : `mission-robotique/`.
2. Remplis le fichier (syntaxe Markdown de base).
3. Depuis le dossier `cybr/`, lance :

       python3 construire_missions.py

4. Mets en ligne `index.html`, `missions.css` et les dossiers `mission-…/`.

## Règles du fichier

- Première ligne : le titre, précédé de `# `. Ce qui est entre `*astérisques*` est mis en couleur et souligné en doré.
- Juste en dessous, sans ligne vide entre elles, les lignes d'en-tête `Clé : valeur`.
  - `Pôle`, `Résumé` et `Ordre` sont facultatifs. `Résumé` est le texte de la carte sur l'accueil. `Ordre` est un nombre qui fixe la position dans la liste.
  - Toutes les autres clés (`Livrable`, `Inscription`…) s'affichent comme infos sous le titre.
- Après une ligne vide : le texte d'introduction, puis les sections `## …`.
- Les sections `Objectif`, `À rendre`, `Réussie si`, `À savoir`, `Pour démarrer`, `Ressources` et `Outils` ont une mise en page dédiée. Toute autre section s'affiche sous l'objectif.
- Dans `Ressources` : `- [Titre](lien) : description`, regroupés sous des titres `### …`.
- Dans `Outils` : `- **Nom** : description`.

## À savoir

- Les fichiers dont le nom commence par `_` sont ignorés : c'est le cas du modèle.
- Pour retirer une mission, supprime son `.md` **et** son dossier `mission-…/`, puis relance le script.
- La liste des missions de l'accueil est réécrite entre `<!-- MISSIONS:DEBUT -->` et `<!-- MISSIONS:FIN -->` dans `index.html`. Ne modifie rien entre ces deux repères à la main.
- Les pages missions reprennent le style, l'en-tête et le pied de page de `index.html`. Après une modification du thème, relance le script.
