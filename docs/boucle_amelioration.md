# Boucle d'amélioration : comment les corrections et avis des validateurs améliorent la production

*Plateforme EXETAT — dispositif en service depuis le 24 novembre 2026*

## Principe

Le modèle n'est pas réentraîné. À chaque nouvelle commande de génération, il reçoit, en plus de la charte et du cahier des charges, un bloc **« Retours des validateurs »** construit automatiquement à partir des décisions des enseignants dans la même matière sur les 30 derniers jours. Les retours entrent dans la commande comme *données* (statistiques et exemples), jamais comme instructions brutes : une remarque mal formulée ne peut pas dérégler la production.

## Étage 1 — Mémoire des corrections

Chaque décision d'un validateur (valider, enregistrer des corrections, rejeter) est enregistrée dans une table `corrections` :

| Champ | Contenu |
|---|---|
| item_id, type | question ou situation étendue |
| discipline, sous-discipline, épreuve, chapitre | pour filtrer par matière |
| validateur, date, décision | traçabilité |
| motif | l'un des 8 motifs normalisés de rejet |
| observations | remarque libre de l'enseignant |
| champ, avant, après | **une ligne par champ corrigé** (énoncé, proposition 1 à 5, bonne réponse, correction…) avec le texte d'origine et le texte corrigé |

L'interface des validateurs ne change pas : ils continuent à corriger dans la fiche et à cliquer Valider / Enregistrer / Rejeter.

## Étage 2 — Réinjection dans la commande

Le bloc joint à chaque commande contient, pour la matière concernée :

1. **Les motifs de rejet les plus fréquents** traduits en consignes correctives :
   - Réponse marquée fausse → recalculer la bonne réponse deux fois avant d'écrire les propositions
   - Plusieurs réponses possibles → aucune autre proposition défendable, même à l'arrondi près
   - Hors programme → strictement le chapitre et le niveau de 4e des humanités
   - Énoncé confus → 35 à 75 mots, une seule question, grandeur nommée
   - Données inexactes → données vérifiables, simples et sûres
   - Contexte artificiel → le contexte fournit une donnée utilisée, rien de décoratif
   - Doublon → varier savoir essentiel, données et angle
2. **Jusqu'à 4 exemples avant/après** de corrections faites par des enseignants (à imiter, sans recopier), avec la remarque associée.
3. **Les remarques libres** sur les questions rejetées.
4. **2 questions validées telles quelles** comme référence du niveau et de la forme attendus.

S'il n'y a aucun retour dans la matière, la commande part avec la charte seule.

Les situations étendues reçoivent le même bloc.

## Étage 3 — Tableau de bord Qualité

Onglet **Qualité** de l'atelier (administrateurs et rédacteurs), sur 90 jours :

- taux de questions validées telles quelles / validées après correction / rejetées, global et par matière ;
- motifs de rejet, avec détail par matière ;
- chapitres les plus retouchés ou rejetés (à partir de 3 relectures) ;
- champs les plus corrigés par les enseignants (énoncé, propositions, correction…) ;
- tableau des relecteurs (voir étage 4) et questions contestées ;
- **aperçu des consignes** qui seront transmises à l'assistant pour une matière donnée ;
- journal des dernières décisions avec le texte avant / après.

API : `GET /api/qualite?jours=90`, `GET /api/qualite/consignes?discipline=…` (réservées aux comptes connectés).

## Étage 4 — Relecture à l'aveugle (ajouté le 24 novembre 2026)

**Principe.** Dans la fiche de relecture, l'enseignant voit d'abord la question **exactement comme l'élève**, sans clé ni correction (elles sont retenues côté serveur, pas seulement masquées à l'écran). Il choisit la proposition qui lui paraît juste (clic ou touches 1 à 5, puis Entrée). La clé et la correction s'affichent ensuite, avec le résultat :

- **concordance** : « Vous avez répondu 2, comme la clé » → relecture normale (le premier point de contrôle est pré-coché) ;
- **désaccord** : « Vous avez répondu 3 ; la clé prévue est 2 » → l'enseignant qualifie le désaccord après lecture de la correction : *je m'étais trompé(e)* / *la clé est fausse* (il corrige alors la clé d'un clic) / *deux réponses défendables* (rejet « Plusieurs réponses possibles » ou correction des propositions).

Une question ne peut pas être validée sans que l'enseignant ait d'abord donné sa réponse (contrôle serveur). Le rejet reste possible sans répondre.

**Ce qui est enregistré** (table `relectures`) : réponse donnée, clé au moment de la relecture, concordance, temps de réflexion, verdict après révélation, date, enseignant.

**Ce qui est mesuré, et pourquoi.** La performance d'un enseignant n'est pas « être d'accord avec l'assistant » : l'assistant se trompe parfois et l'enseignant qui le contredit à raison est le meilleur relecteur. Les indicateurs sont donc :

| Indicateur | Définition |
|---|---|
| D'accord avec la clé **finale** | part des relectures où la réponse donnée est la clé telle qu'elle est *après* corrections |
| Détections | désaccords suivis d'un changement de clé ou d'un rejet de la question : à son crédit |
| Erreurs reconnues | désaccords où l'enseignant a conclu « je m'étais trompé(e) » |
| Ambiguïtés signalées | désaccords conclus « deux réponses défendables » |
| Temps médian, trop rapides | relectures de moins de 8 secondes comptées à part |

Chaque enseignant voit ses propres chiffres (encadré « Mes relectures ») ; la coordination voit le tableau complet dans l'onglet Qualité ; il n'y a pas de classement public.

**Questions contestées.** L'onglet Qualité liste les questions où au moins un enseignant a choisi une autre réponse que la clé finale : à faire relire en priorité par un second enseignant.

**Double relecture.** La variable `RELECTURES_REQUISES` fixe le nombre d'enseignants distincts devant avoir donné, à l'aveugle, la même réponse que la clé avant qu'une question validée soit embarquée dans l'application élève et dans les épreuves assemblées (`1` par défaut ; `2` pour la double relecture indépendante). Les questions validées avant le dispositif, sans aucune relecture à l'aveugle, restent publiées. Avec `2`, la fiche affiche « 1/2 relectures concordantes » et un second enseignant doit ouvrir la question dans la liste « Validées » et répondre.

API : `POST /api/items/{id}/relecture` (réponse, durée), `POST /api/relectures/{id}/verdict`, `GET /api/moi/relectures`, et dans `GET /api/qualite` : `relecteurs`, `items_suspects`, `relectures_requises`.

## Usage recommandé par la coordination

- Si un chapitre concentre les rejets, revoir le libellé du chapitre dans le programme ou ajouter une précision dans la charte : l'automatique corrige la tendance, la coordination corrige la cause.
- Encourager les enseignants à **corriger dans la fiche plutôt que rejeter** quand la question est récupérable : chaque correction devient un exemple d'apprentissage ; un rejet n'apporte qu'un motif.
- Encourager une **remarque courte et précise** lors d'un rejet (« les propositions 2 et 4 sont équivalentes à l'arrondi près ») : elle est transmise telle quelle au modèle.
- Présenter la relecture à l'aveugle aux enseignants comme ce qu'elle est : le meilleur test de la question, pas un examen des enseignants. Leurs désaccords justifiés sont valorisés (détections).
- Passer `RELECTURES_REQUISES` à `2` dès que l'équipe compte au moins deux enseignants par matière.
