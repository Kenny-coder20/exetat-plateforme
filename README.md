# Plateforme de génération d'items EXETAT — version 1

Atelier de production (génération IA + validation par des enseignants + export) et application élève hors ligne,
selon la *Charte de rédaction des items IA*, le *Cahier des charges* et le programme **E.32 session 2026**.

**Organisation par épreuve.** Le E.32 (48 options, 9 familles) est chargé intégralement (`app/e32.py`). Une épreuve
(code M.xx) est partagée par toutes les options qui la portent : la banque de **M.01** (culture générale) sert aux
options 1.01, 1.02, 1.03, 1.04, 5.01 et 5.02. Dans l'atelier comme dans l'application élève, on choisit d'abord
l'**option**, puis le **jour**, ce qui désigne l'épreuve et sa banque. Épreuves ouvertes : M.01, M.46, M.07
(`EPREUVES_ACTIVES` dans `app/e32.py`).

```
exetat-platform/
├── app/            backend : base SQLite, génération (assistant IA), assemblage, export, API FastAPI, CLI
├── docs/           charte, cahier des charges, prompt système de l'agent
├── static/
│   ├── validateur/ atelier : file d'attente, checklist, génération, import
│   └── eleve/      application élève (PWA hors ligne)
├── data/           base exetat.sqlite (créée au premier lancement)
└── exports/        séries exportées (.json, .tex, .pdf) et banque.json
```

## Démarrage en un double-clic

1. Installer **Python 3.10 ou plus** une seule fois (python.org ; sur Windows cocher « Add Python to PATH »).
2. Double-cliquer sur **`Lancer EXETAT.bat`** (Windows) ou **`Lancer EXETAT.command`** (Mac/Linux).
   Au premier lancement, les composants s'installent et la base se crée avec les items de démonstration ;
   ensuite la plateforme s'ouvre dans le navigateur. Laissez la petite fenêtre noire ouverte ; la fermer arrête la plateforme.
3. Pour la génération automatique : ouvrir le fichier `.env` (créé au premier lancement) et coller la clé API.

**Application élève comme une vraie appli** : sur la page `/eleve/`, cliquer « Installer l'application »
(Chrome/Edge) ou, sur téléphone, « Ajouter à l'écran d'accueil ». L'icône EXETAT s'ouvre alors sans barre
d'adresse et fonctionne hors ligne. Sur un téléphone, remplacer `127.0.0.1` par l'adresse de l'ordinateur sur le
réseau local (ex. `http://192.168.1.20:8000/eleve/`) lors de la première ouverture.

## Installation manuelle (alternative)

1. Installer **Python 3.10 ou plus** (python.org ; sur Windows cocher « Add Python to PATH »).
2. Ouvrir un terminal dans le dossier `exetat-platform` et lancer :
   ```
   pip install -r requirements.txt
   python -m app.cli init
   python -m app.cli demo
   ```
   `init` crée la base et charge le E.32 ; `demo` insère 23 items de démonstration déjà validés.
3. Copier `.env.example` en `.env` et y coller votre clé API Anthropic (`ANTHROPIC_API_KEY=sk-ant-...`).
4. Démarrer :
   ```
   uvicorn app.main:app --port 8000
   ```
   puis ouvrir <http://127.0.0.1:8000> — atelier validateur sur `/validateur/`, application élève sur `/eleve/`.

Facultatif : une distribution LaTeX (MiKTeX, TeX Live) pour produire les PDF ; sans elle, les fichiers `.tex` sont produits et se compilent ailleurs (Overleaf, par exemple).

## Flux de travail

```
commande ──► génération IA ──► items « en_attente » ──► validateur (checklist) ──► « valide »
                                                                                      │
                 application élève ◄── banque.json (hors ligne) ◄── assemblage ◄──────┘
                 export LaTeX / PDF ◄───────────────────────────────┘
```

### 1. Générer (atelier, réseau requis)
Depuis l'interface validateur (bloc « Générer ») ou en ligne de commande :
```
python -m app.cli generer --epreuve M.01                 # culture générale : Civisme 2, Géo 6, Histoire 6, Philo 6
python -m app.cli generer --epreuve M.07 --serie A       # SPTIC : Chimie 6, Physique 6, TIC 3
python -m app.cli generer --epreuve M.46 --discipline Mathématiques -n 6 --chapitre "Probabilités (MM6.14)"
```
Chaque quota du E.32 donne lieu à un appel API ; les items arrivent **en attente**, avec les anomalies
mécaniques détectées (nombre de mots, 5 propositions, réponse dans 1..5, répartition des réponses…).

Sans clé API : bouton « Copier le prompt », collez-le dans votre assistant IA, puis « Importer un JSON ».

### 2. Valider (atelier) — pensé pour des enseignants
L'enseignant choisit son option et le jour, puis relit les questions une par une, **telles que l'élève les verra** :
bonne réponse en vert, correction en dessous. Il peut corriger directement dans le texte (cliquer, modifier),
changer la bonne réponse (cliquer sur son numéro), puis **Valider** (touche V), **Enregistrer ses corrections** (E)
ou **Rejeter** avec un motif (R). Six points de contrôle à cocher avant de valider. Aucun outil technique n'est
requis ; les figures ou tableaux éventuels sont réservés à la version imprimée.
Seules les questions **validées** atteignent les élèves.

### 3. Servir (élève, hors ligne)
L'application `/eleve/` télécharge une fois la banque validée (`/api/banque.json`) et l'enregistre sur
l'appareil ; passation, corrigé détaillé et score fonctionnent ensuite **sans réseau**. Trois modes :
épreuve du jour (quotas et ordre du E.32, chronomètre), une discipline, un chapitre (n questions,
difficulté). Les résultats sont gardés localement et envoyés au serveur quand une connexion passe.
Après une nouvelle vague de validation : bouton « Mettre à jour la banque ».

Distribution sans réseau : `python -m app.cli banque` produit `exports/banque.json` à copier sur clé USB
(ou servir la plateforme sur le réseau local d'une salle informatique).

### Situations étendues (exercice de synthèse)
Second format : une situation longue (150–300 mots) avec un document (tableau, fiche, schéma), suivie de 4 à 6
questions de difficulté croissante qui en découlent, chacune répondable indépendamment, et une synthèse finale.
- Générer : onglet « Produire » de l'atelier, « Un exercice de synthèse », ou
  `python -m app.cli generer --situation --epreuve M.07 --discipline Physique -n 5`.
- Valider : file « Situations étendues » ; chaque question se valide comme un item, puis la situation elle-même.
- Élève : onglet « Synthèse », situation épinglée en haut, corrigé puis synthèse.
- Export imprimable : `/api/export/situation/<id>?pdf=true` (réservé aux coordinateurs).
Les questions de situation ne sont jamais tirées dans les épreuves du jour.

### 4. Exporter (papier)
```
python -m app.cli assembler --epreuve M.07 --serie A --pdf
python -m app.cli assembler --epreuve M.46 --discipline Mathématiques --serie B --pdf
python -m app.cli assembler --epreuve M.07 --discipline Chimie --chapitre "Électrochimie : potentiel redox, pile (MSPC6.7)" -n 10
```
Produit `exports/*.json`, `*.tex` (A4, 12 pt, marges 2,2 cm, encadrés consignes/compétences, propositions
1 à 5, feuille de réponses, corrigé en fin) et `*.pdf` si LaTeX est installé.

## Mettre en ligne (Render)

Voir `DEPLOIEMENT.md` : dépôt GitHub + Blueprint Render (`render.yaml`) avec base PostgreSQL, mot de passe sur l'atelier.

## Programmes officiels chargés

| Discipline | Source | Année |
| --- | --- | --- |
| Mathématiques, SVT, SPTTIC (Chimie, Physique, TIC) | Programmes éducatifs 4e HS (6e Sc), DIPROMAD/MEPST — edu-nc.gouv.cd/national-programmes | 2021 |
| Civisme (Éducation civique et morale) | Programme national ECM secondaire, 6e année — edu-nc.gouv.cd | 2007 |
| Histoire | Programme national d'histoire, 6e année — edu-nc.gouv.cd | 2005 |
| Géographie | Programme national de géographie, 6e année — edu-nc.gouv.cd | 2005 |
| Philosophie | **Reconstitué** (programme officiel introuvable en ligne) — à confirmer par un inspecteur | — |

Le jour 1 (M.01, culture générale : Civisme 2, Géographie 6, Histoire 6, Philosophie 6) est actif. Le jour 4 (langues) reste à venir.

## Programme officiel (remplacement par CSV)

Le programme chargé par `init` est **indicatif** (chapitres du cahier des charges et du programme usuel).
Pour le remplacer par le programme officiel, préparez un CSV :
```
discipline,sous_discipline,chapitre,poids
Mathématiques,,Nombres complexes,2
SVT,Biologie,Génétique et hérédité,2
```
puis `python -m app.cli programme programme.csv`. Le poids règle la part de chaque chapitre dans une série.

## Changer d'année (nouveau E.32)

Mettre à jour `app/e32.py` (épreuves, quotas, calendrier des options, `EPREUVES_ACTIVES`), puis redémarrer :
les tables de configuration sont reconstruites au démarrage, les items existants sont conservés.

## Configuration (.env)

| Variable | Rôle |
| --- | --- |
| `ANTHROPIC_API_KEY` | clé API pour la génération |
| `MODELE_IA` | identifiant du modèle IA utilisé pour la génération |
| `EXETAT_DB` | chemin de la base SQLite |

## Limites de cette V1 et suite prévue

- Une seule option (1.02 Sciences) ; Culture générale et Langues sont déclarées mais inactives.
- Pas de comptes utilisateurs : l'atelier est prévu pour un poste ou un réseau local de confiance.
- Les figures/tableaux générés sont en LaTeX ; l'application élève les affiche en texte brut (rendu graphique à venir).
- Suite : déploiement serveur (PostgreSQL, Docker), comptes validateurs, statistiques par chapitre, génération à la volée pour les chapitres pauvres (marquée non validée).
