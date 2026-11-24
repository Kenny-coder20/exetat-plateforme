-- Plateforme EXETAT — schéma SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS options (
  code TEXT PRIMARY KEY,          -- 1.02
  nom  TEXT NOT NULL,             -- Sciences
  famille TEXT,                   -- Humanités littéraires et scientifiques
  session INTEGER NOT NULL        -- 2026 (année du E.32)
);

-- Une épreuve (M.xx) est partagée par toutes les options qui la portent : la banque est organisée par épreuve.
CREATE TABLE IF NOT EXISTS epreuves (
  code TEXT PRIMARY KEY,          -- M.46
  libelle TEXT NOT NULL,
  nb_items INTEGER NOT NULL,
  nb_series INTEGER NOT NULL,     -- 0 = série unique
  duree_h REAL NOT NULL,
  actif INTEGER NOT NULL DEFAULT 0    -- 1 = banque ouverte dans la plateforme
);

CREATE TABLE IF NOT EXISTS quotas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  epreuve_code TEXT NOT NULL REFERENCES epreuves(code),
  ordre INTEGER NOT NULL,
  discipline TEXT NOT NULL,
  sous_discipline TEXT,
  nb_items INTEGER NOT NULL
);

-- Calendrier de chaque option : jour → épreuve
CREATE TABLE IF NOT EXISTS option_epreuves (
  option_code TEXT NOT NULL REFERENCES options(code),
  jour INTEGER NOT NULL,
  epreuve_code TEXT NOT NULL REFERENCES epreuves(code),
  PRIMARY KEY (option_code, jour)
);

CREATE TABLE IF NOT EXISTS programme (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  discipline TEXT NOT NULL,
  sous_discipline TEXT,
  chapitre TEXT NOT NULL,
  poids REAL NOT NULL DEFAULT 1,  -- part indicative dans l'épreuve
  source TEXT,                    -- 'officiel 2021', 'reconstitue'…
  epreuve_code TEXT               -- NULL = tous les épreuves de la discipline
);

-- Situations étendues (exercice de synthèse) : une situation longue + 4 à 6 questions liées
CREATE TABLE IF NOT EXISTS situations (
  id TEXT PRIMARY KEY,
  option_code TEXT REFERENCES options(code),
  epreuve_code TEXT,
  discipline TEXT NOT NULL,
  sous_discipline TEXT,
  chapitres TEXT,                  -- "Électricité ; Énergie"
  titre TEXT NOT NULL,
  texte TEXT NOT NULL,             -- 150 à 300 mots
  document_texte TEXT,             -- résumé lisible du document (tableau, fiche…)
  document_latex TEXT,             -- tabular / TikZ
  synthese TEXT,                   -- réponse finale au problème posé (3 à 5 lignes)
  duree_min INTEGER DEFAULT 25,
  nb_mots INTEGER,
  version TEXT NOT NULL DEFAULT 'initiale',
  modele TEXT,
  statut_validation TEXT NOT NULL DEFAULT 'en_attente'
      CHECK (statut_validation IN ('en_attente','valide','rejete')),
  validateur TEXT, date_validation TEXT, observations TEXT, motif_rejet TEXT,
  cree_le TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS items (
  id TEXT PRIMARY KEY,            -- J3-M07-A-08 ou GEN-<uuid>
  option_code TEXT REFERENCES options(code),
  jour INTEGER,
  epreuve_code TEXT,
  serie TEXT,                     -- A..D ou NULL (banque)
  numero INTEGER,
  discipline TEXT NOT NULL,
  sous_discipline TEXT,
  chapitre TEXT,
  savoir_essentiel TEXT NOT NULL,
  competence TEXT,                -- calculer, modéliser, raisonner, analyser, interpréter, transférer
  difficulte TEXT NOT NULL CHECK (difficulte IN ('facile','moyen','difficile')),
  famille_contexte TEXT,
  support TEXT DEFAULT 'aucun',   -- aucun | tableau | figure
  support_latex TEXT,             -- tabular / TikZ si support
  figure_svg TEXT,                -- figure vectorielle (SVG) affichée à l'écran
  figure_legende TEXT,            -- légende courte de la figure
  titre TEXT NOT NULL,
  tige TEXT NOT NULL,
  p1 TEXT NOT NULL, p2 TEXT NOT NULL, p3 TEXT NOT NULL, p4 TEXT NOT NULL, p5 TEXT NOT NULL,
  reponse INTEGER NOT NULL CHECK (reponse BETWEEN 1 AND 5),
  correction_detaillee TEXT NOT NULL,
  erreurs_distracteurs TEXT,
  nb_mots_tige INTEGER,
  version TEXT NOT NULL DEFAULT 'initiale',
  modele TEXT,                    -- modèle IA utilisé
  statut_validation TEXT NOT NULL DEFAULT 'en_attente'
      CHECK (statut_validation IN ('en_attente','valide','rejete')),
  validateur TEXT,
  date_validation TEXT,
  observations TEXT,
  motif_rejet TEXT,
  situation_id TEXT REFERENCES situations(id),
  ordre_situation INTEGER,
  cree_le TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_items_statut ON items(statut_validation, discipline, sous_discipline, difficulte);

CREATE TABLE IF NOT EXISTS lots_generation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  commande TEXT NOT NULL,         -- description de la commande
  modele TEXT,
  nb_demandes INTEGER,
  nb_recus INTEGER,
  cout_tokens_in INTEGER,
  cout_tokens_out INTEGER,
  erreur TEXT,
  cree_le TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS resultats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  eleve TEXT,                     -- identifiant local de l'appareil
  mode TEXT NOT NULL,             -- epreuve | discipline | chapitre
  option_code TEXT, jour INTEGER, epreuve_code TEXT, discipline TEXT, chapitre TEXT,
  nb_items INTEGER NOT NULL,
  score INTEGER NOT NULL,
  details TEXT,                   -- JSON : [{item_id, reponse_donnee, juste}]
  date_passation TEXT NOT NULL,
  synchronise_le TEXT NOT NULL DEFAULT (datetime('now'))
);


-- Comptes des enseignants (atelier)
CREATE TABLE IF NOT EXISTS utilisateurs (
  identifiant TEXT PRIMARY KEY,
  nom TEXT NOT NULL,
  mdp_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'validateur',   -- admin | redacteur | validateur
  disciplines TEXT,                          -- facultatif : "Physique ; Chimie"
  actif INTEGER NOT NULL DEFAULT 1,
  cree_le TEXT,
  derniere_connexion TEXT
);


-- Mémoire des corrections et avis des validateurs (boucle d'amélioration)
CREATE TABLE IF NOT EXISTS corrections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT,                   -- item ou situation concerné
  type TEXT NOT NULL DEFAULT 'item',   -- item | situation
  discipline TEXT,
  sous_discipline TEXT,
  epreuve_code TEXT,
  chapitre TEXT,
  validateur TEXT,
  date TEXT NOT NULL,
  decision TEXT NOT NULL,         -- valide | rejete | en_attente
  motif TEXT,                     -- motif de rejet normalisé
  observations TEXT,
  champ TEXT,                     -- champ corrigé (NULL si décision sans retouche)
  avant TEXT,
  apres TEXT
);
CREATE INDEX IF NOT EXISTS idx_corr_disc ON corrections(discipline, date);


-- Relecture à l'aveugle : l'enseignant répond avant de voir la clé
CREATE TABLE IF NOT EXISTS relectures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id TEXT NOT NULL,
  validateur TEXT NOT NULL,       -- identifiant du compte
  nom TEXT,
  discipline TEXT,
  epreuve_code TEXT,
  reponse_donnee INTEGER NOT NULL,
  cle_affichee INTEGER NOT NULL,  -- clé au moment de la relecture
  concordant INTEGER NOT NULL,    -- 1 si reponse_donnee = cle_affichee
  duree_s INTEGER,                -- temps de réflexion avant de répondre
  verdict TEXT,                   -- après révélation en cas de désaccord : erreur_relecteur | cle_fausse | ambigu
  date TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_relectures_item ON relectures(item_id);
CREATE INDEX IF NOT EXISTS idx_relectures_val ON relectures(validateur, date);
