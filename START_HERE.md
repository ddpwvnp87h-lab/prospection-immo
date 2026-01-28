# 🚀 START HERE - Prospection Immo Team Maureen

## Projet complet et prêt à l'emploi!

### 🎯 Ce qui a été fait

✅ **Architecture simple sans IA**
- Scrapers classiques avec Playwright et BeautifulSoup
- Pas de CrewAI, pas d'OpenAI, pas de complexité inutile
- Code Python direct et facile à maintenir

✅ **4 Scrapers implémentés**
1. **leboncoin.fr** (Playwright) - Le plus populaire
2. **pap.fr** (BeautifulSoup) - Particuliers uniquement
3. **Facebook Marketplace** (Playwright) - Marketplace social
4. **Figaro Immobilier** (BeautifulSoup) - Haut de gamme

✅ **6 Templates disponibles**
- paruvendu.fr
- logic-immo.com
- bienici.com
- seloger.com
- (prêts à être implémentés)

✅ **Base de données Supabase**
- Schéma SQL complet
- Déduplication automatique
- Nettoyage automatique (90 jours)
- Isolation par utilisateur

✅ **Validation et filtrage**
- Vérification des champs obligatoires
- Déduplication par URL et signature
- Filtrage des agences immobilières
- Normalisation des données

✅ **Documentation complète**
- README.md - Vue d'ensemble
- QUICKSTART.md - Installation rapide
- TESTING.md - Guide de test
- COMMANDS.md - Toutes les commandes
- START_HERE.md - Ce fichier!

---

## 🏃 Quick Start (3 minutes)

### 1. Installation

```bash
# Installer les dépendances
make install

# Ou manuellement
pip install -r requirements.txt
playwright install
```

### 2. Test sans base de données

```bash
# Tester leboncoin Paris
make test-leboncoin

# Ou manuellement
python test_scrapers.py --ville Paris --site leboncoin
```

**✅ Ça devrait fonctionner immédiatement!**

### 3. Configuration Supabase (optionnel)

Pour utiliser la base de données:

```bash
# 1. Créer un compte sur https://supabase.com
# 2. Créer un nouveau projet
# 3. Copier database_schema.sql dans l'éditeur SQL
# 4. Configurer .env
cp .env.example .env
# Éditer .env avec vos clés
```

### 4. Prospection complète

```bash
# Avec Supabase configuré
python main.py --user-id maureen --ville Paris --rayon 10
```

---

## 📁 Structure du projet

```
prospection-immo/
│
├── 📄 START_HERE.md          ← Vous êtes ici!
├── 📄 README.md              ← Vue d'ensemble
├── 📄 QUICKSTART.md          ← Installation
├── 📄 TESTING.md             ← Tests
├── 📄 COMMANDS.md            ← Commandes
├── 📄 Makefile               ← Raccourcis
│
├── 🐍 main.py                ← Point d'entrée production
├── 🧪 test_scrapers.py       ← Tests sans DB
├── ⚙️  config.py              ← Configuration
├── 📋 requirements.txt       ← Dépendances
│
├── 📂 scrapers/              ← Scrapers par site
│   ├── base.py              ← Classe de base
│   ├── leboncoin.py         ← ✅ Implémenté
│   ├── pap.py               ← ✅ Implémenté
│   ├── facebook_marketplace.py ← ✅ Implémenté
│   ├── figaro_immo.py       ← ✅ Implémenté
│   └── ...                  ← Templates
│
├── 📂 database/              ← Gestion Supabase
│   └── manager.py
│
└── 📂 utils/                 ← Validation
    └── validator.py
```

---

## 🎮 Commandes principales

### Tests (pas de DB requise)

```bash
# Leboncoin Paris
make test-leboncoin

# Tous les scrapers
make test-all

# Personnalisé
python test_scrapers.py --ville Lyon --site pap --max-pages 3
```

### Prospection (DB requise)

```bash
# Toutes annonces Paris
make scrape VILLE=Paris USER_ID=maureen

# Sites spécifiques
python main.py --user-id maureen --ville Lyon --sites leboncoin pap facebook

# Plus de pages
python main.py --user-id maureen --ville Marseille --max-pages 10
```

### Nettoyage

```bash
# Nettoyer la DB (90 jours + "Pas intéressé")
make cleanup USER_ID=maureen

# Nettoyer les fichiers Python
make clean
```

---

## 🔧 Configuration

### Fichier .env

```bash
# Créer le fichier
cp .env.example .env

# Éditer avec vos clés
nano .env
```

Variables importantes:
- `SUPABASE_URL` - URL de votre projet Supabase
- `SUPABASE_KEY` - Clé anon de Supabase
- `SCRAPING_DELAY` - Délai entre requêtes (2 sec par défaut)
- `MAX_PAGES_PER_SITE` - Pages max par site (5 par défaut)

---

## 📊 Workflow de scraping

```
1. SCRAPING
   ├─ leboncoin.fr (Playwright)
   ├─ pap.fr (BeautifulSoup)
   ├─ Facebook (Playwright)
   └─ Figaro (BeautifulSoup)
        ↓
2. VALIDATION
   ├─ Champs obligatoires
   └─ Format des données
        ↓
3. FILTRAGE
   ├─ Supprimer agences
   ├─ Dédupliquer par URL
   └─ Dédupliquer par signature
        ↓
4. STOCKAGE
   ├─ Insertion Supabase
   ├─ Skip doublons
   └─ Nettoyage auto
```

---

## 🆘 Aide

### Problèmes courants

**"Aucune annonce trouvée"**
- Les sélecteurs CSS ont peut-être changé
- Vérifier et mettre à jour le scraper
- Voir TESTING.md

**"Rate limiting / IP bloquée"**
```bash
# Augmenter le délai dans .env
SCRAPING_DELAY=5
```

**"Timeout Playwright"**
- Augmenter timeout dans le scraper
- Vérifier votre connexion internet

### Obtenir de l'aide

```bash
# Aide générale
make help

# Aide commandes
python main.py --help
python test_scrapers.py --help

# Documentation
cat README.md
cat TESTING.md
cat COMMANDS.md
```

---

## 🚀 Prochaines étapes

1. **Tester les scrapers**
   ```bash
   make test-all
   ```

2. **Configurer Supabase**
   - Créer un compte
   - Exécuter database_schema.sql
   - Configurer .env

3. **Première prospection**
   ```bash
   python main.py --user-id test --ville Paris --rayon 10
   ```

4. **Implémenter d'autres sites**
   - Copier un scraper existant
   - Adapter les sélecteurs CSS
   - Tester avec test_scrapers.py

---

## 💡 Notes importantes

- ✅ **Pas d'IA** - Code simple et direct
- ✅ **Scraping éthique** - Délais entre requêtes
- ✅ **Particuliers uniquement** - Filtrage des agences
- ✅ **Déduplication** - Pas de doublons
- ✅ **Nettoyage auto** - Base propre

---

## 📝 Licence

Projet privé pour Team Maureen.

---

**👉 Commencez par:** `make test-leboncoin`

**📖 Lire ensuite:** [TESTING.md](TESTING.md)

Bon scraping! 🏠
