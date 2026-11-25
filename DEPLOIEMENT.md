# Mettre la plateforme en ligne sur Render

Résultat : une adresse publique (ex. `https://exetat-plateforme.onrender.com`) ; les élèves ouvrent le lien, installent
l'application et travaillent hors ligne ; les enseignants accèdent à l'atelier avec un mot de passe. Base PostgreSQL
hébergée par Render : les données survivent aux redémarrages. Coût : offre gratuite de Render (le service s'endort
après 15 minutes sans visite et met ~30 s à se réveiller ; la base gratuite a une durée limitée — vérifier les
conditions actuelles de Render et passer à l'offre payante pour un usage réel).

## 1. Mettre le dossier sur GitHub (une fois)
1. Créer un compte sur https://github.com et un dépôt vide (privé possible), par exemple `exetat-plateforme`.
2. Y envoyer le contenu du dossier `exetat-platform` : avec GitHub Desktop (glisser le dossier), ou en ligne de
   commande :
   ```
   cd exetat-platform
   git init && git add . && git commit -m "Plateforme EXETAT"
   git branch -M main && git remote add origin https://github.com/VOTRE-COMPTE/exetat-plateforme.git
   git push -u origin main
   ```
   Le fichier `.gitignore` exclut `.env`, la base locale et les exports : rien de secret ne part.

## 2. Créer le service sur Render
1. Compte sur https://render.com (connexion avec GitHub).
2. **New → Blueprint**, choisir le dépôt. Render lit `render.yaml` et propose un service web + une base PostgreSQL.
3. Renseigner les deux variables demandées :
   - `ANTHROPIC_API_KEY` : votre clé API (génération automatique dans l'atelier).
   - `ATELIER_MOT_DE_PASSE` : le mot de passe de l'atelier (identifiant : `atelier`, modifiable via `ATELIER_UTILISATEUR`).
4. **Apply**. Le premier déploiement prend 2 à 4 minutes. Au démarrage, la plateforme crée les tables, charge le E.32 et,
   si la banque est vide, les items de démonstration (`EXETAT_DEMO=1` ; mettre `0` pour une base vierge).

## 3. Utiliser
- Accueil : `https://<votre-service>.onrender.com/`
- Élèves : `/eleve/` — bouton « Installer » (Chrome/Edge) ou « Ajouter à l'écran d'accueil » (téléphone).
- Enseignants : `/validateur/` — page de connexion ; premier compte : `atelier` + `ATELIER_MOT_DE_PASSE`, puis créez les comptes dans l'onglet Comptes.
- API : `/docs` (protégée par le même mot de passe).

## 4. Mettre à jour
Chaque `git push` sur `main` redéploie automatiquement. Les données (items, situations, résultats) restent dans la base.

## 5. Reprendre une base locale
Pour transférer des items validés localement vers Render : dans l'atelier en ligne, « Importer un JSON » accepte le
format `{"items":[...]}` ; ou exécutez localement `python -m app.cli banque` et importez `exports/banque.json`
(champ `items`). Une commande de migration directe SQLite → PostgreSQL peut être ajoutée si le besoin se confirme.

## Variables d'environnement
| Variable | Rôle |
| --- | --- |
| `DATABASE_URL` | renseignée par Render (PostgreSQL) ; vide = SQLite local |
| `ANTHROPIC_API_KEY` | génération IA |
| `ATELIER_MOT_DE_PASSE`, `ATELIER_UTILISATEUR` | compte administrateur initial |
| `CLE_SECRETE` | signature des sessions (générée automatiquement par le Blueprint) |
| `MODELE_IA` | identifiant du modèle IA utilisé pour la génération |
| `EXETAT_DEMO` | `1` charge la démo si la banque est vide |
| `ACTUALITE_DEBUT`, `ACTUALITE_FIN` | fenêtre temporelle de la matière Actualité (AAAA-MM-JJ), fixée par le jury à chaque session ; par défaut du 1er janvier de l'année précédente à aujourd'hui. La génération d'Actualité utilise la recherche web de l'API (facturée en plus des jetons) |
| `RELECTURES_REQUISES` | nombre d'enseignants distincts devant avoir donné, à l'aveugle, la même réponse que la clé avant qu'une question validée soit publiée aux élèves (`1` par défaut ; `2` = double relecture) |
