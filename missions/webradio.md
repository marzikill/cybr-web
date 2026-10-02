# Le site de *la web radio.*

Pôle : Programmation
Ordre : 7
Résumé : Donner une maison en ligne à la web radio du lycée : émissions à réécouter, grille, équipe.
Livrable : site en ligne

Construire le **site de la web radio du lycée** : on y réécoute les émissions, on découvre la grille et l'équipe. Pensé pour le téléphone, parce que c'est là qu'on écoute.

## Objectif

La web radio produit des émissions, mais une fois enregistrées elles disparaissent dans un dossier. Le site doit les rendre faciles à trouver et à écouter, et donner envie de rejoindre l'équipe.

Comme pour le journal, la radio est le « client » : on part de ses besoins (combien d'émissions, qui publie, à quel rythme) avant de coder. La partie technique la plus intéressante est le lecteur audio : écouter un épisode sans quitter la page, voir sa durée, passer au suivant.

## À rendre

- Une page d'accueil avec la dernière émission en avant et un lecteur intégré
- Une page « émissions » qui liste les épisodes par rubrique, avec date et durée
- Une page « l'équipe » et un moyen de proposer un sujet ou de rejoindre la radio
- Une marche à suivre pour que la radio ajoute un épisode sans l'aide du club

## Réussie si

- Un épisode se lance en deux clics depuis un téléphone
- Les fichiers audio sont compressés pour rester légers (MP3 autour de 96 à 128 kbit/s)
- Chaque musique diffusée est libre de droits ou autorisée, et créditée
- Les élèves qui parlent à l'antenne ont donné leur accord, avec celui des parents pour les mineurs

## À savoir

**Droits :** une musique du commerce ne peut pas être diffusée librement sur un site, même pour un lycée. Utilise des morceaux sous licence libre et crédite leurs auteurs. Pour les voix des élèves, même règle que pour les photos : autorisation écrite avant publication.

## Pour démarrer

1. Rencontrer l'équipe de la radio : rubriques, nombre d'émissions, qui publie
2. Coder d'abord un lecteur avec la balise audio sur un épisode test
3. Construire la liste des épisodes à partir d'un simple fichier de données, puis habiller le tout

## Ressources

### Faire une web radio scolaire

- [CLEMI](https://www.clemi.fr/) : Ressources officielles sur les médias scolaires, dont la web radio : droits, organisation, exemples.
- [Free Music Archive](https://freemusicarchive.org/) : Musiques sous licence libre pour les jingles et les fonds sonores.

### Coder le site

- [La balise audio — MDN](https://developer.mozilla.org/fr/docs/Web/HTML/Element/audio) : Tout sur le lecteur audio intégré au navigateur.
- [Apprendre le développement web](https://developer.mozilla.org/fr/docs/Learn) : HTML, CSS et JavaScript depuis le début.

## Outils

- **Audacity** : Monter, nettoyer et exporter les épisodes en MP3
- **VS Code** : Écrire le code du site
- **DevTools du navigateur** : Tester l'affichage sur téléphone
- **Git + GitHub** : Travailler à plusieurs
- **Fichier JSON** : Liste des épisodes, facile à mettre à jour
