# 🏠 Prospection Immo Team Maureen

Outil de prospection immobilière complet avec scraping automatisé et application web de gestion.

## 🚀 Démarrage Rapide

### Application Web

```bash
./start_app.sh
```

Puis ouvre **http://localhost:5000**

**Guide complet:** [LANCE_APPLICATION.md](LANCE_APPLICATION.md)

### Scraping Simple

```bash
python3 scraper_lite.py Paris
```

Fonctionne sans installation! **Guide:** [LANCE_MOI.md](LANCE_MOI.md)

---

## ✨ Fonctionnalités

### 🖥 Application Web
- **Authentification**: Login/Register sécurisé
- **Dashboard**: Vue d'ensemble avec statistiques
- **Filtres & Recherche**: Trouve rapidement les annonces
- **Gestion des statuts**: Nouveau, Intéressé, Visité, etc.
- **Vue détaillée**: Photos, description, infos complètes
- **📱 PWA**: Installable sur iPad comme une vraie app!

### 🔍 Scraping
- **4 sites implémentés**: leboncoin, pap.fr, Facebook, Figaro
- **Filtrage intelligent**: Particuliers uniquement
- **Déduplication**: Par URL et signature
- **Validation**: Vérification des données

### 🗄 Base de Données
- **Supabase** (PostgreSQL cloud gratuit)
- **Multi-utilisateurs**: Données isolées
- **Auto-cleanup**: Suppression après 90 jours

---

## 📋 Sites Supportés

### ✅ Implémentés (4)
- **leboncoin.fr** - Playwright (JavaScript dynamique)
- **pap.fr** - BeautifulSoup (Particulier À Particulier)
- **Facebook Marketplace** - Playwright
- **Figaro Immobilier** - BeautifulSoup

### 📋 Templates Disponibles (4)
- paruvendu.fr
- logic-immo.com
- bienici.com
- seloger.com

---

## 🛠 Installation

### Installation Minimale (Scraper Lite)

**Aucune installation nécessaire!**
```bash
python3 scraper_lite.py Paris
```

### Installation Application Web

```bash
# Installer Flask
pip3 install flask python-dotenv supabase

# Configurer Supabase (5 minutes)
# Voir: SUPABASE_EN_BREF.md

# Lancer l'app
./start_app.sh
```

### Installation Complète (Scrapers + App)

```bash
# 1. Dépendances
pip3 install -r requirements.txt

# 2. Playwright
python3 -m playwright install chromium

# 3. Configurer Supabase
cp .env.example .env
nano .env  # Ajouter les clés Supabase

# 4. Tester
python3 test_supabase.py
```

---

## 🎯 Utilisation

### Application Web

```bash
# Lancer l'application
./start_app.sh

# Ouvre ton navigateur
http://localhost:5000

# Sur iPad (même WiFi)
http://[ton-ip]:5000
```

**Guide complet:** [GUIDE_APPLICATION.md](GUIDE_APPLICATION.md)

### Scraping

```bash
# Scraper lite (démo, sans DB)
python3 scraper_lite.py Paris

# Scraper complet (avec DB)
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10

# Tester un site spécifique
python3 test_scrapers.py --ville Lyon --site pap

# Nettoyage (90 jours)
python3 main.py --cleanup --user-id ton-email@example.com
```

---

## 📁 Structure du Projet

```
.
├── app.py                       ← Application Flask
├── start_app.sh                 ← Script de lancement
│
├── templates/                   ← Pages HTML
│   ├── login.html
│   ├── dashboard.html
│   └── listing_detail.html
│
├── static/                      ← CSS, JS
│   ├── css/style.css
│   ├── js/app.js
│   └── service-worker.js
│
├── scrapers/                    ← Scrapers par site
│   ├── base.py
│   ├── leboncoin.py            ✅
│   ├── pap.py                  ✅
│   ├── facebook_marketplace.py ✅
│   ├── figaro_immo.py          ✅
│   └── [4 templates]           📋
│
├── database/                    ← Gestion Supabase
│   └── manager.py
│
├── utils/                       ← Validation
│   └── validator.py
│
├── main.py                      ← Scraping production
├── scraper_lite.py              ← Scraper standalone
├── test_scrapers.py             ← Tests
└── database_schema.sql          ← Schéma DB
```

---

## 📚 Documentation

### Démarrage

| Document | Description |
|----------|-------------|
| [LANCE_APPLICATION.md](LANCE_APPLICATION.md) | Lancer l'app web (1 commande) |
| [LANCE_MOI.md](LANCE_MOI.md) | Lancer le scraper (sans installation) |
| [INDEX.md](INDEX.md) | Index de navigation |

### Application Web

| Document | Description |
|----------|-------------|
| [GUIDE_APPLICATION.md](GUIDE_APPLICATION.md) | Guide complet de l'app web |
| [APPLICATION_WEB_COMPLETE.md](APPLICATION_WEB_COMPLETE.md) | Documentation technique complète |

### Supabase

| Document | Description |
|----------|-------------|
| [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md) | Setup Supabase (5 minutes) |
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Setup Supabase (complet) |

### Développement

| Document | Description |
|----------|-------------|
| [START_HERE.md](START_HERE.md) | Vue d'ensemble du projet |
| [TESTING.md](TESTING.md) | Guide de test des scrapers |
| [GUIDE_HTTPS.md](GUIDE_HTTPS.md) | Explications techniques |
| [PRD.md](PRD.md) | Spécifications du projet |

---

## 🔄 Workflow Complet

### 1. Installation (une fois)

```bash
# Configurer Supabase
cp .env.example .env
nano .env  # Ajouter clés

# Tester
python3 test_supabase.py

# Installer Flask
pip3 install flask python-dotenv supabase
```

### 2. Utilisation Quotidienne

**Matin:**
```bash
# Lancer un scraping
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
```

**Sur le Web:**
```bash
# Lancer l'app
./start_app.sh

# Ouvrir
http://localhost:5000
```

**Workflow:**
1. Dashboard → Filtre "Nouveau"
2. Parcours les annonces
3. Change les statuts (Intéressé/Pas intéressé)
4. Clique sur une annonce pour voir les détails
5. "Voir l'annonce complète" pour aller sur le site source

---

## 📱 PWA - Application iPad

### Installation sur iPad

1. Ouvre **Safari** sur iPad
2. Va sur `http://[ton-ip]:5000` (IP affichée au démarrage)
3. Tap sur "Partager" (carré avec flèche)
4. Sélectionne "Sur l'écran d'accueil"
5. Nomme l'app: "Prospection Immo"
6. Tap "Ajouter"

### Avantages

- ✅ Icône sur l'écran d'accueil
- ✅ Ouverture en plein écran
- ✅ Pas de barre Safari
- ✅ Comme une vraie app native!

---

## 🛠 Technologies

- **Flask** - Application web Python
- **Python 3.9+** - Backend
- **Playwright** - Sites JavaScript (leboncoin, Facebook)
- **BeautifulSoup** - Sites statiques (pap, Figaro)
- **Supabase** - Base de données PostgreSQL cloud
- **PWA** - Progressive Web App pour iPad
- **Requests** - Requêtes HTTP

---

## 🎨 Captures d'Écran

### Dashboard
- Statistiques en haut
- Filtres de recherche
- Grille d'annonces avec photos

### Vue Détaillée
- Galerie de photos
- Prix, localisation, surface
- Description complète
- Boutons de statut

### Mobile/iPad
- Interface responsive
- PWA installable
- Mode plein écran

---

## 🔒 Sécurité

- ✅ Authentification par email/password
- ✅ Hashage des mots de passe (SHA-256)
- ✅ Sessions Flask sécurisées
- ✅ Isolation des données par utilisateur
- ✅ Protection des routes (@login_required)

**Note:** Pour la production, utilise bcrypt et active HTTPS.

---

## 🆘 Support

### Problèmes Courants

**"Flask not found"**
```bash
pip3 install flask
```

**"Connection refused" depuis iPad**
- Mac et iPad sur le même WiFi?
- Bonne IP utilisée?

**"Invalid API key" Supabase**
- Fichier `.env` configuré?
- Voir [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md)

**Pas d'annonces**
- Lancer un scraping d'abord:
  ```bash
  python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
  ```

---

## 🚀 Commandes Magiques

```bash
# LANCE L'APPLICATION WEB
./start_app.sh

# SCRAPING SANS INSTALLATION
python3 scraper_lite.py Paris

# SCRAPING COMPLET
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
```

---

## 🎉 Prêt à Utiliser!

**Tout est prêt:**
- ✅ Application web complète
- ✅ PWA installable sur iPad
- ✅ 4 scrapers fonctionnels
- ✅ Base de données Supabase
- ✅ Documentation complète

**Commence maintenant:**
```bash
./start_app.sh
```

**Profite bien! 🏠**
