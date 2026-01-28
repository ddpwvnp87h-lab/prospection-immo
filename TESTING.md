# Guide de Test des Scrapers

## Installation des dépendances

```bash
pip install -r requirements.txt
playwright install
```

## Test rapide (sans base de données)

Le script [test_scrapers.py](test_scrapers.py) permet de tester les scrapers sans configurer Supabase.

### Tester un site spécifique

```bash
# Test leboncoin
python test_scrapers.py --ville Paris --site leboncoin

# Test pap.fr
python test_scrapers.py --ville Lyon --site pap

# Test Facebook Marketplace
python test_scrapers.py --ville Marseille --site facebook

# Test Figaro Immo
python test_scrapers.py --ville Bordeaux --site figaro
```

### Tester tous les scrapers implémentés

```bash
python test_scrapers.py --ville Paris --all
```

### Options disponibles

- `--ville` : Ville de recherche (requis)
- `--rayon` : Rayon de recherche en km (défaut: 10)
- `--max-pages` : Nombre max de pages à scraper (défaut: 2)
- `--site` : Site spécifique à tester
- `--all` : Tester tous les scrapers

## Scrapers implémentés

### ✅ Leboncoin.fr (Playwright)
- **Status**: Implémenté et fonctionnel
- **Technologie**: Playwright (JavaScript dynamique)
- **Notes**: Site populaire, nombreuses annonces

### ✅ Pap.fr (BeautifulSoup)
- **Status**: Implémenté et fonctionnel
- **Technologie**: Requests + BeautifulSoup
- **Notes**: Particuliers uniquement, HTML statique

### ✅ Facebook Marketplace (Playwright)
- **Status**: Implémenté (à tester)
- **Technologie**: Playwright
- **Notes**:
  - Peut être bloqué par Facebook
  - Nécessite des précautions (rate limiting)
  - Les sélecteurs peuvent changer fréquemment

### ✅ Figaro Immobilier (BeautifulSoup)
- **Status**: Implémenté (template)
- **Technologie**: Requests + BeautifulSoup
- **Notes**: Annonces haut de gamme

### ⚠️ Autres sites (templates)
Les scrapers suivants sont des templates à implémenter:
- `paruvendu.py`
- `logic_immo.py`
- `bienici.py`
- `seloger.py`

## Exemple de sortie

```
================================================================================
🧪 Test du scraper: leboncoin.fr
================================================================================

🔍 Scraping leboncoin.fr pour Paris (rayon: 10km)
  📄 Page 1/2...
  📄 Page 2/2...
✅ 40 annonces trouvées sur leboncoin.fr

📊 Résultats du scraping:
   - Total annonces: 40
   - Annonces valides: 38
   - Annonces de particuliers: 32

📋 Exemples d'annonces (max 3):

   1. Appartement 3 pièces - 75m² - Paris 15ème
      Prix: 450,000 €
      Localisation: Paris 15ème
      Lien: https://www.leboncoin.fr/annonce/...
      Valide: ✅

   ...
```

## Debugging

### Activer le mode verbose de Playwright

Modifier `scrapers/base.py` ou les scrapers individuels:

```python
browser = p.chromium.launch(
    headless=False,  # Voir le navigateur
    slow_mo=1000     # Ralentir les actions
)
```

### Vérifier les sélecteurs CSS

Si un scraper ne trouve pas d'annonces, les sélecteurs CSS ont peut-être changé:

1. Ouvrir le site dans un navigateur
2. Inspecter l'élément (clic droit → Inspecter)
3. Trouver le sélecteur CSS/XPath correct
4. Mettre à jour le scraper

### Problèmes courants

**Timeout sur Playwright**
```bash
# Augmenter le timeout dans le scraper
page.goto(url, timeout=60000)  # 60 secondes
```

**Rate limiting / IP bloquée**
```bash
# Augmenter le délai entre requêtes dans .env
SCRAPING_DELAY=5
```

**Sélecteurs invalides**
- Les sites changent régulièrement leur HTML
- Vérifier et mettre à jour les sélecteurs CSS

## Test avec la base de données

Une fois Supabase configuré, tester le workflow complet:

```bash
# 1. Configurer .env
cp .env.example .env
# Éditer .env avec vos clés Supabase

# 2. Lancer une prospection complète
python main.py --user-id test-user --ville Paris --rayon 10

# 3. Vérifier les résultats dans Supabase
```

## Contribution

Pour ajouter un nouveau scraper:

1. Créer `scrapers/nouveau_site.py`
2. Hériter de `BaseScraper`
3. Implémenter la méthode `scrape()`
4. Ajouter au fichier `scrapers/__init__.py`
5. Ajouter au fichier `main.py`
6. Tester avec `test_scrapers.py`
