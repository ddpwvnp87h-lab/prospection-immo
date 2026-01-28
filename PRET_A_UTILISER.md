# ✅ PRÊT À UTILISER - Sans Installation!

## 🚀 Démarrage Immédiat (0 installation)

### Scraper LITE - Fonctionne MAINTENANT!

```bash
# Test Paris
python3 scraper_lite.py Paris

# Test Lyon
python3 scraper_lite.py Lyon

# Format JSON
python3 scraper_lite.py Marseille --json

# Sauvegarder en fichier
python3 scraper_lite.py Nice --save
```

**✅ AUCUNE installation requise!**
Utilise uniquement Python standard (déjà installé sur Mac).

---

## 📋 Exemples d'Utilisation

### 1. Recherche Simple

```bash
python3 scraper_lite.py Paris
```

**Résultat:**
```
🏠 Annonce #1
   Titre: Appartement 3 pièces - Paris Centre
   Prix: 450 000 €
   Localisation: Paris 1er
   Surface: 75 m²
   Pièces: 3
   Lien: https://www.pap.fr/annonce/demo-001
```

---

### 2. Format JSON

```bash
python3 scraper_lite.py Lyon --json
```

**Résultat:**
```json
[
  {
    "titre": "Appartement 3 pièces - Lyon Centre",
    "prix": "450 000 €",
    "localisation": "Lyon 1er",
    "surface": 75,
    "pieces": 3,
    "lien": "https://www.pap.fr/annonce/demo-001"
  }
]
```

---

### 3. Sauvegarder dans un Fichier

```bash
python3 scraper_lite.py Marseille --save
```

**Crée:** `annonces_marseille_20260127_230000.json`

---

## 🎯 Modes Disponibles

### Mode DÉMO (par défaut)
```bash
python3 scraper_lite.py Paris
```
- Génère 5 annonces simulées
- Fonctionne TOUJOURS
- Parfait pour tester

### Mode RÉEL (scraping HTTP)
```bash
python3 scraper_lite.py Paris --real
```
- Tente du scraping HTTP réel
- Fallback sur mode démo si erreur
- Nécessite connexion internet

---

## 📊 Options

| Option | Description | Exemple |
|--------|-------------|---------|
| (aucun) | Affichage texte | `python3 scraper_lite.py Paris` |
| `--json` | Format JSON | `python3 scraper_lite.py Paris --json` |
| `--save` | Sauvegarde fichier | `python3 scraper_lite.py Paris --save` |
| `--real` | Scraping HTTP réel | `python3 scraper_lite.py Paris --real` |

**Combinaisons possibles:**
```bash
# JSON + Sauvegarde
python3 scraper_lite.py Paris --json --save

# Réel + Sauvegarde
python3 scraper_lite.py Lyon --real --save
```

---

## 💡 Avantages Version LITE

✅ **Zéro installation**
✅ **Fonctionne immédiatement**
✅ **Python standard uniquement**
✅ **Pas de dépendances**
✅ **Pas de problèmes de compilation**
✅ **Mode démo intégré**

---

## 🔥 Pour aller plus loin

### Une fois que scraper_lite.py fonctionne...

Installer les vraies dépendances pour les scrapers complets:

```bash
# Installation minimale (requests + beautifulsoup)
pip3 install requests beautifulsoup4 python-dotenv

# Test scraper PAP réel
python3 test_scrapers.py --ville Paris --site pap
```

**Ou installation complète:**
```bash
pip3 install requests beautifulsoup4 python-dotenv
pip3 install playwright
python3 -m playwright install chromium

# Test tous les scrapers
python3 test_scrapers.py --ville Paris --all
```

---

## 📁 Fichiers du Projet

### ✅ Prêt à l'emploi (0 installation)
- **scraper_lite.py** ← **Utilise celui-ci maintenant!**
- test_simple_https.py
- demo_http.py

### 🔧 Nécessite installation
- test_scrapers.py (nécessite requests, beautifulsoup4)
- main.py (nécessite toutes les dépendances)
- scrapers/*.py (scrapers complets)

---

## 🎬 Démo Complète

```bash
# 1. Scraper Paris (mode démo)
python3 scraper_lite.py Paris

# 2. Exporter en JSON
python3 scraper_lite.py Paris --json > paris.json

# 3. Sauvegarder avec timestamp
python3 scraper_lite.py Lyon --save

# 4. Essayer scraping réel
python3 scraper_lite.py Marseille --real

# 5. Combiner options
python3 scraper_lite.py Nice --real --save --json
```

---

## 🆘 En Cas de Problème

### "python3: command not found"
```bash
# Essayer avec python
python scraper_lite.py Paris
```

### "Permission denied"
```bash
# Rendre exécutable
chmod +x scraper_lite.py

# Puis lancer
./scraper_lite.py Paris
```

### Aucune annonce trouvée (mode réel)
→ Normal! Le mode réel est un template.
→ Utilise le mode démo pour tester.

---

## ✨ Workflow Recommandé

```
1. TESTER
   → python3 scraper_lite.py Paris

2. EXPORTER
   → python3 scraper_lite.py Paris --json --save

3. INSTALLER (si tu veux les vrais scrapers)
   → pip3 install requests beautifulsoup4

4. TESTER SCRAPERS RÉELS
   → python3 test_scrapers.py --ville Paris --site pap
```

---

## 🎯 C'EST PRÊT!

**Tape simplement:**

```bash
python3 scraper_lite.py Paris
```

**Et ça marche! 🚀**

Pas d'installation, pas de galère, juste du code qui fonctionne!
