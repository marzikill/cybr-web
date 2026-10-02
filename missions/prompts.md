# Prompts système *pour réviser.*

Pôle : IA
Ordre : 1
Résumé : Écrire les instructions qui transforment un chatbot en tuteur qui fait réfléchir, au lieu de donner les réponses.
Livrable : bibliothèque de prompts

Écrire les instructions qui transforment un assistant IA en **tuteur de révision** : il pose des questions, corrige, explique… mais ne fait pas le travail à ta place.

## Objectif

Un **prompt système** est le texte d'instructions donné à l'IA *avant* la conversation : il fixe son rôle, son ton, ce qu'elle a le droit de faire ou pas. Bien écrit, il transforme ChatGPT, Claude ou Gemini en coach de révision adapté à une matière et à un niveau.

Ta mission : construire une petite bibliothèque de prompts **testés**, que n'importe quel élève du lycée peut copier-coller pour réviser intelligemment.

## À rendre

- 4 à 6 prompts système, chacun pour un usage précis (ex. tuteur socratique de maths, générateur de quiz, entraîneur au Grand oral, correcteur de méthode de dissertation, créateur de fiches)
- Pour chaque prompt : une fiche « matière · niveau · mode d'emploi · limites connues »
- Un exemple de conversation réelle (capture ou copie) montrant le prompt en action
- Une page de présentation de la bibliothèque (à intégrer au site CYBR)

## Réussie si

- L'IA ne donne pas directement la réponse finale : elle guide par étapes
- Le prompt a été testé par au moins 2 élèves qui ne l'ont pas écrit
- Il prévoit le cas où l'élève se trompe et le cas où l'IA se trompe
- Il rappelle de vérifier dans le cours (les IA inventent parfois)

## Squelette de départ

À copier puis adapter. Les parties entre crochets sont à remplir.

```
# Rôle
Tu es un tuteur de [matière] pour un élève de [niveau].

# Objectif
Aider l'élève à comprendre et à retenir, pas à finir un devoir.

# Règles
- Ne donne jamais la réponse finale directement : pose une question
  qui fait avancer d'une étape.
- Si l'élève se trompe, montre où, sans corriger à sa place.
- Au bout de 3 essais ratés, donne un indice plus précis.
- Fais des réponses courtes (5 lignes max) et un seul exercice à la fois.
- Si tu n'es pas sûr d'une information, dis-le, et invite l'élève
  à vérifier dans son cours.

# Déroulé
1. Demande à l'élève le chapitre qu'il révise.
2. Pose une question de difficulté moyenne.
3. Adapte la difficulté selon ses réponses.
4. Termine par un récapitulatif en 3 points.
```

## À savoir

**À savoir :** chaque service d'IA a ses conditions d'âge (certains exigent 18 ans). Utilise les outils et comptes autorisés par le lycée, et ne colle jamais d'informations personnelles dans un chatbot.

## Pour démarrer

1. Lire un guide de prompt engineering (voir ressources) et noter 5 règles
2. Choisir les matières et interroger des élèves/profs sur leurs besoins
3. Écrire une v1, la tester, noter ce qui rate, réécrire (au moins 3 itérations)

## Ressources

### Apprendre à écrire un prompt

- [Prompt engineering — vue d'ensemble](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) : Le guide officiel d'Anthropic : rôle, exemples, structure (en anglais).
- [Tutoriel interactif de prompt engineering](https://github.com/anthropics/prompt-eng-interactive-tutorial) : Exercices pas à pas, du prompt basique au prompt avancé.
- [Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) : Les conseils d'OpenAI, bonnes pratiques et exemples.
- [Learn Prompting](https://learnprompting.org/) : Cours gratuit et progressif, idéal pour débuter.

### Contenu des révisions

- [Programmes du lycée](https://eduscol.education.fr/) : Pour caler chaque prompt sur ce qui est vraiment au programme.
- [Lumni — révisions lycée](https://www.lumni.fr/lycee) : Vidéos et fiches de l'audiovisuel public pour vérifier ce que dit l'IA.

## Outils

- **Claude** : Projets + instructions personnalisées
- **ChatGPT** : GPTs / instructions personnalisées
- **Gemini** : Gems = assistants sur mesure
- **Le Chat (Mistral)** : Alternative française, agents
- **Doc partagé** : Rédiger et versionner les prompts (v1, v2…)
- **Grille de test** : Tableau : prompt × élève × ce qui a raté
