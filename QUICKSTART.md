# Quick Start Guide

## 1. Installation

### Prérequis
- Python 3.9+
- Compte Supabase (base de données)

### Étapes d'installation

```bash
# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Installer les navigateurs Playwright
playwright install

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter vos clés Supabase
```

## 2. Configuration de Supabase

1. Créer un nouveau projet sur [Supabase](https://supabase.com)
2. Exécuter le script SQL:
   - Copier le contenu de `database_schema.sql`
   - Le coller dans l'éditeur SQL de Supabase
3. Récupérer l'URL et la clé anon du projet
4. Les ajouter dans le fichier `.env`

## 3. Utilisation

### Lancer une prospection

```bash
python main.py \
  --user-id "user-123" \
  --ville "Paris" \
  --rayon 15
```

### Lancer le nettoyage automatique

```bash
python main.py --cleanup --user-id "user-123"
```

## 4. Architecture du projet

```
.
├── scrapers/            # Scrapers pour chaque site
│   ├── base.py
│   ├── leboncoin.py
│   ├── pap.py
│   └── ...
├── database/            # Gestion Supabase
│   └── manager.py
├── utils/               # Validation et déduplication
│   └── validator.py
├── main.py              # Point d'entrée
└── config.py            # Configuration globale
```

## 5. Prochaines étapes

### À implémenter:

1. **Scrapers spécifiques** (dans scrapers/)
   - Implémenter les fonctions de scraping pour chaque site
   - Utiliser Playwright pour les sites dynamiques
   - Gérer les sélecteurs CSS/XPath

2. **Tests**
   - Tester chaque scraper individuellement
   - Valider la déduplication
   - Vérifier l'intégration Supabase

## 6. Sites supportés

- leboncoin.fr
- pap.fr (De Particulier À Particulier)
- paruvendu.fr
- logic-immo.com
- bienici.com
- seloger.com

## 7. Support

Consulter le [PRD.md](PRD.md) pour les spécifications complètes.
