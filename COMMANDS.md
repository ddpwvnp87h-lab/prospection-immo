# Guide des Commandes

## Installation

```bash
# Installation complète
make install

# Ou manuellement
pip install -r requirements.txt
playwright install
```

## Tests (sans base de données)

```bash
# Test leboncoin (le plus fiable)
make test-leboncoin

# Test pap.fr
make test-pap

# Test Facebook Marketplace
make test-facebook

# Test tous les scrapers implémentés
make test-all

# Test personnalisé
python test_scrapers.py --ville Lyon --site leboncoin --max-pages 3
```

## Prospection complète (avec Supabase)

```bash
# Prospection Paris
make scrape VILLE=Paris USER_ID=maureen-team

# Prospection Lyon avec sites spécifiques
python main.py --user-id maureen-team --ville Lyon --sites leboncoin pap

# Prospection avec plus de pages
python main.py --user-id maureen-team --ville Marseille --max-pages 10
```

## Nettoyage

```bash
# Nettoyage base de données (90 jours + "Pas intéressé")
make cleanup USER_ID=maureen-team

# Nettoyage fichiers temporaires Python
make clean
```

## Exemples réels

### Scraper toutes les annonces à Paris

```bash
python main.py \
  --user-id maureen-team \
  --ville "Paris" \
  --rayon 15 \
  --max-pages 5
```

### Scraper uniquement leboncoin et pap à Lyon

```bash
python main.py \
  --user-id maureen-team \
  --ville "Lyon" \
  --rayon 10 \
  --sites leboncoin pap
```

### Test rapide sans base de données

```bash
# Test leboncoin Paris (2 pages)
python test_scrapers.py --ville Paris --site leboncoin

# Test tous les sites Lyon (1 page par défaut)
python test_scrapers.py --ville Lyon --all --max-pages 1
```

## Variables d'environnement

Créer un fichier `.env`:

```bash
# Supabase (obligatoire pour main.py)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx

# Configuration scraping (optionnel)
SCRAPING_DELAY=2
MAX_PAGES_PER_SITE=5
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

## Debugging

### Voir le navigateur Playwright (mode non-headless)

Modifier `scrapers/leboncoin.py` ou `scrapers/facebook_marketplace.py`:

```python
browser = p.chromium.launch(
    headless=False,  # Voir le navigateur
    slow_mo=500      # Ralentir (ms)
)
```

### Augmenter les timeouts

```python
page.goto(url, timeout=60000)  # 60 secondes au lieu de 30
```

### Logs détaillés

Ajouter des `print()` dans les scrapers pour suivre l'exécution.

## Commandes utiles

```bash
# Lister les scrapers disponibles
ls -la scrapers/*.py

# Vérifier la structure de la base
cat database_schema.sql

# Voir les stats d'un scraping
python test_scrapers.py --ville Paris --site leboncoin | grep "📊"

# Nettoyer tous les fichiers Python compilés
make clean
```

## Aide

```bash
# Aide générale
make help

# Aide main.py
python main.py --help

# Aide test_scrapers.py
python test_scrapers.py --help
```
