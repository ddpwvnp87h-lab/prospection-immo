# 🚀 LANCE-MOI MAINTENANT!

## ⚡ En 1 Commande (sans DB)

```bash
python3 scraper_lite.py Paris
```

**C'est tout!** Ça fonctionne sans rien installer! 🎉

---

## 🗄️ Avec Base de Données Supabase

**Jamais utilisé Supabase?** Pas de problème!

**Guide complet:** [SUPABASE_SETUP.md](SUPABASE_SETUP.md) (10 minutes)

**Test rapide:**
```bash
python3 test_supabase.py
```

---

## 📋 Autres Exemples

```bash
# Lyon
python3 scraper_lite.py Lyon

# Marseille en JSON
python3 scraper_lite.py Marseille --json

# Nice + sauvegarde fichier
python3 scraper_lite.py Nice --save
```

---

## 📂 Fichiers Disponibles

### ✅ PRÊT MAINTENANT (0 installation)

| Fichier | Commande | Description |
|---------|----------|-------------|
| **scraper_lite.py** | `python3 scraper_lite.py Paris` | **← UTILISE CELUI-CI!** |
| demo_http.py | `python3 demo_http.py` | Démo interactive |
| test_simple_https.py | `python3 test_simple_https.py` | Test HTTPS |

### 🔧 Nécessite Installation

| Fichier | Commande | Installation requise |
|---------|----------|---------------------|
| test_scrapers.py | `python3 test_scrapers.py --ville Paris --site pap` | `pip3 install requests beautifulsoup4` |
| main.py | `python3 main.py --user-id test --ville Paris` | Installation complète |

---

## 🎯 Recommandation

**COMMENCE PAR:**
```bash
python3 scraper_lite.py Paris
```

**PUIS SI TU VEUX PLUS:**
```bash
pip3 install requests beautifulsoup4
python3 test_scrapers.py --ville Paris --site pap
```

---

## 📖 Documentation

- **[PRET_A_UTILISER.md](PRET_A_UTILISER.md)** - Guide complet scraper_lite.py
- **[START_HERE.md](START_HERE.md)** - Guide projet complet
- **[GUIDE_HTTPS.md](GUIDE_HTTPS.md)** - Comment fonctionne le scraping
- **[TESTING.md](TESTING.md)** - Guide de test

---

## ✨ C'EST SIMPLE!

```bash
python3 scraper_lite.py Paris
```

Pas d'installation. Pas de galère. Ça marche! 🚀
