# 📋 INDEX - Prospection Immo Team Maureen

## 🎯 UTILISATION IMMÉDIATE

### ⚡ Sans Installation (Python standard)

```bash
# Scraper LITE - FONCTIONNE MAINTENANT!
python3 scraper_lite.py Paris              # Mode démo
python3 scraper_lite.py Lyon --json        # Format JSON
python3 scraper_lite.py Nice --save        # Sauvegarde fichier

# Démos et tests
python3 demo_http.py                       # Démo interactive
python3 test_simple_https.py               # Test HTTPS
```

**Documentation:**
- **[LANCE_MOI.md](LANCE_MOI.md)** ← **COMMENCE ICI!**
- [PRET_A_UTILISER.md](PRET_A_UTILISER.md) - Guide scraper_lite.py

---

## 🔧 Avec Installation (Scrapers Complets)

### Installation Minimale

```bash
pip3 install requests beautifulsoup4 python-dotenv
```

### Tests Disponibles

```bash
# Scraper PAP.fr (HTTP simple)
python3 test_scrapers.py --ville Paris --site pap

# Tous les scrapers (démo)
python3 test_scrapers.py --ville Lyon --all
```

**Documentation:**
- [TESTING.md](TESTING.md) - Guide de test
- [GUIDE_HTTPS.md](GUIDE_HTTPS.md) - Comment ça marche

---

## 🚀 Installation Complète

### Toutes les Dépendances

```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

### Utilisation Production

```bash
# Configuration
cp .env.example .env
# Éditer .env avec clés Supabase

# Prospection complète
python3 main.py --user-id maureen --ville Paris --rayon 10

# Nettoyage
python3 main.py --cleanup --user-id maureen
```

**Documentation:**
- [START_HERE.md](START_HERE.md) - Guide complet
- [QUICKSTART.md](QUICKSTART.md) - Installation
- [COMMANDS.md](COMMANDS.md) - Toutes les commandes
- [PRD.md](PRD.md) - Spécifications

---

## 📁 Structure du Projet

```
✅ PRÊT MAINTENANT
├── scraper_lite.py          ← Scraper sans dépendances
├── demo_http.py             ← Démo interactive
├── test_simple_https.py     ← Test HTTPS
└── LANCE_MOI.md             ← Guide ultra-rapide

🔧 NÉCESSITE INSTALLATION
├── test_scrapers.py         ← Tests (requests + beautifulsoup4)
├── main.py                  ← Production (toutes dépendances)
├── scrapers/                ← Scrapers par site
│   ├── leboncoin.py        ← ✅ Implémenté (Playwright)
│   ├── pap.py              ← ✅ Implémenté (BeautifulSoup)
│   ├── facebook_marketplace.py ← ✅ Implémenté
│   └── figaro_immo.py      ← ✅ Implémenté
├── database/               ← Gestion Supabase
└── utils/                  ← Validation

📚 DOCUMENTATION
├── LANCE_MOI.md            ← 1 commande pour démarrer
├── PRET_A_UTILISER.md      ← Guide scraper_lite.py
├── START_HERE.md           ← Vue d'ensemble
├── GUIDE_HTTPS.md          ← Explications techniques
├── TESTING.md              ← Guide de test
├── COMMANDS.md             ← Référence commandes
├── QUICKSTART.md           ← Installation complète
└── README.md               ← Introduction
```

---

## 🎬 Workflow Recommandé

### 1️⃣ Test Immédiat (0 installation)

```bash
python3 scraper_lite.py Paris
```

→ Ça marche! Tu as 5 annonces en mode démo.

---

### 2️⃣ Installation Minimale

```bash
pip3 install requests beautifulsoup4
```

→ Permet de tester les scrapers réels.

---

### 3️⃣ Test Scrapers Réels

```bash
python3 test_scrapers.py --ville Paris --site pap
```

→ Scraping HTTP réel de pap.fr (BeautifulSoup).

---

### 4️⃣ Installation Complète (optionnel)

```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

→ Active tous les scrapers (leboncoin, Facebook, etc.).

---

### 5️⃣ Production avec Base de Données

```bash
# Configurer Supabase
cp .env.example .env
# Éditer .env

# Lancer prospection
python3 main.py --user-id maureen --ville Paris
```

→ Workflow complet avec stockage en base.

---

## 🆘 Aide Rapide

### Quel fichier utiliser?

| Besoin | Fichier | Installation |
|--------|---------|--------------|
| Tester maintenant | scraper_lite.py | ❌ Aucune |
| Démo HTTP | demo_http.py | ❌ Aucune |
| Scraper PAP réel | test_scrapers.py | ✅ Minimale |
| Scraper leboncoin | test_scrapers.py | ✅ Complète |
| Production complète | main.py | ✅ Complète + Supabase |

### Problème d'installation?

**Solution 1:** Utilise scraper_lite.py (aucune installation)
```bash
python3 scraper_lite.py Paris
```

**Solution 2:** Installation minimale seulement
```bash
pip3 install requests beautifulsoup4
python3 test_scrapers.py --ville Paris --site pap
```

**Solution 3:** Ignore lxml (utilise html.parser à la place)
```bash
# Modifier scrapers/pap.py ligne 47:
# soup = BeautifulSoup(response.content, 'html.parser')  # au lieu de 'lxml'
```

---

## 📊 Récapitulatif

### ✅ Ce qui fonctionne MAINTENANT

- scraper_lite.py (mode démo) ✅
- demo_http.py ✅
- test_simple_https.py ✅

### 🔧 Ce qui nécessite installation

- Scrapers complets (requests + beautifulsoup4)
- Playwright (leboncoin, Facebook)
- Supabase (base de données)

### 📝 Scrapers Implémentés

1. **leboncoin.fr** - Playwright ✅
2. **pap.fr** - BeautifulSoup ✅
3. **facebook.com/marketplace** - Playwright ✅
4. **figaro-immo.fr** - BeautifulSoup ✅

### 📋 Templates Disponibles

5. paruvendu.fr - Template prêt
6. logic-immo.com - Template prêt
7. bienici.com - Template prêt
8. seloger.com - Template prêt

---

## 🎯 Commande Magique

```bash
python3 scraper_lite.py Paris
```

**Ça marche sans rien installer! 🚀**

---

Besoin d'aide? Consulte [LANCE_MOI.md](LANCE_MOI.md) pour démarrer!
