# Prospection Immo

Application web de prospection immobilière - scraping d'annonces de particuliers.

## Fonctionnalités

- Scraping automatique de pap.fr et Figaro Immo
- Filtrage automatique des agences (particuliers uniquement)
- Dashboard pour gérer les annonces
- Suivi par statut (Nouveau, Intéressé, Visité, etc.)
- PWA installable sur iPad

## Déploiement sur Railway

### 1. Prérequis

- Compte [Railway](https://railway.app)
- Compte [Supabase](https://supabase.com)

### 2. Configuration Supabase

Dans Supabase SQL Editor, exécutez le contenu de `database_schema.sql`.

### 3. Variables d'environnement Railway

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
FLASK_SECRET_KEY=une-clé-secrète-aléatoire
```

### 4. Déploiement

1. Push le code sur GitHub
2. Connectez le repo à Railway
3. Railway détecte automatiquement Python et déploie

## Structure

```
├── app.py              # Application Flask principale
├── database/
│   └── manager.py      # Connexion Supabase REST API
├── scrapers/
│   ├── pap.py          # Scraper pap.fr
│   └── figaro_immo.py  # Scraper Figaro Immo
├── templates/          # Templates HTML
├── static/             # CSS, JS
└── utils/
    └── validator.py    # Validation des annonces
```

## Utilisation

1. Créez un compte sur l'application
2. Allez dans "Scraper"
3. Choisissez une ville et lancez le scraping
4. Les annonces apparaissent dans le dashboard

## Technologies

- Flask (Python)
- Supabase (PostgreSQL)
- BeautifulSoup (scraping)
- Railway (hébergement)
