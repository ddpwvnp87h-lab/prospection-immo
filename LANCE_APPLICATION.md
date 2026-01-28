# 🚀 LANCE L'APPLICATION MAINTENANT!

## ⚡ En 1 Commande

```bash
./start_app.sh
```

**C'est tout!** L'application web se lance! 🎉

---

## 📱 Ouvre ton Navigateur

```
http://localhost:5000
```

---

## 🔐 Première Utilisation

### 1. Crée ton Compte

1. Clique "S'inscrire"
2. Entre ton email et mot de passe
3. C'est fait!

### 2. Configure Supabase (si pas fait)

**Première fois?** Suis ce guide en 5 minutes:

[SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md)

**Puis teste:**
```bash
python3 test_supabase.py
```

---

## 📊 Utilise le Dashboard

### Voir tes Annonces

Le dashboard affiche:
- 📊 Statistiques (Total, Nouveau, Intéressé, Visité)
- 🔍 Filtres de recherche
- 📋 Liste des annonces en cartes

### Changer le Statut

**Directement sur la carte:**
- Utilise le menu déroulant
- Changement instantané!

**Ou dans les détails:**
- Clique sur l'annonce
- Clique sur un bouton de statut

### Statuts Disponibles

- **Nouveau** - Par défaut
- **✓ Intéressé** - À suivre
- **✗ Pas intéressé** - À ignorer
- **👁 Visité** - Visite faite
- **📞 Contact pris** - En discussion
- **💰 Offre faite** - Offre envoyée

---

## 🔄 Ajouter des Annonces

### Via Scraping

```bash
# Scraper complet
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10

# Scraper lite (test)
python3 scraper_lite.py Paris
```

Les annonces apparaissent automatiquement dans le dashboard!

---

## 📱 Installer sur iPad

### Méthode PWA (Progressive Web App)

1. **Trouve ton IP** (affichée au démarrage)
   - Exemple: `192.168.1.50`

2. **Sur iPad, ouvre Safari:**
   ```
   http://192.168.1.50:5000
   ```

3. **Installe sur l'écran d'accueil:**
   - Tap sur le bouton "Partager" (carré avec flèche)
   - Sélectionne "Sur l'écran d'accueil"
   - Nomme l'app: "Prospection Immo"
   - Tap "Ajouter"

4. **Lance depuis l'écran d'accueil**
   - L'app s'ouvre en plein écran! 🎉

---

## 🎯 Workflow Quotidien

### Matin

1. Lance un scraping:
   ```bash
   python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
   ```

2. Ouvre le dashboard

3. Filtre par "Nouveau"

4. Parcours les nouvelles annonces

### Pour Chaque Annonce

1. Regarde photos et détails
2. Marque le statut:
   - Intéressant? → "Intéressé"
   - Pas top? → "Pas intéressé"
3. Clique "Voir l'annonce complète" pour le site source
4. Prends contact si c'est bien
5. Marque "Contact pris"

### Après Visite

- Marque "Visité"
- Si tu fais une offre → "Offre faite"

---

## 🆘 Problèmes?

### Flask manquant

```bash
pip3 install flask
```

### Supabase pas configuré

Suis [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md) (5 minutes)

### iPad ne se connecte pas

- Vérifie que Mac et iPad sont sur le même WiFi
- Utilise l'IP affichée au démarrage

---

## 📚 Documentation Complète

- [GUIDE_APPLICATION.md](GUIDE_APPLICATION.md) - Guide complet de l'app
- [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md) - Config Supabase 5 min
- [START_HERE.md](START_HERE.md) - Vue d'ensemble du projet

---

## ✨ Fonctionnalités

### ✅ Disponible Maintenant

- 🔐 Authentification (login/register)
- 📊 Dashboard avec stats
- 🔍 Recherche et filtres
- 📋 Gestion des statuts
- 📱 PWA installable sur iPad
- 👁 Vue détaillée des annonces
- 🗑 Suppression d'annonces
- 🔄 Nettoyage automatique (90 jours)

### 🚧 Prochainement

- Scraping depuis l'interface web
- Notifications push
- Historique des modifications
- Export CSV/PDF

---

## 🎉 C'est Parti!

```bash
./start_app.sh
```

Ouvre **http://localhost:5000** et profite! 🚀
