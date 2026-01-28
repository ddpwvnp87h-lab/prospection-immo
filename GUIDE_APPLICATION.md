# 🏠 Guide d'Utilisation - Application Web

## 🚀 Lancer l'Application

### Méthode 1: Script automatique (recommandé)

```bash
./start_app.sh
```

### Méthode 2: Manuel

```bash
# Installer les dépendances (première fois)
pip3 install flask python-dotenv supabase

# Lancer l'application
python3 app.py
```

L'application sera disponible sur **http://localhost:5000**

---

## 📱 Accès depuis iPad

### Sur le même réseau WiFi

1. **Trouve ton IP** (affichée au démarrage de l'application)
   - Exemple: `http://192.168.1.50:5000`

2. **Ouvre Safari sur iPad** et va sur cette adresse

3. **Installe comme app** (PWA):
   - Clique sur le bouton "Partager" (carré avec flèche)
   - Sélectionne "Sur l'écran d'accueil"
   - Donne un nom: "Prospection Immo"
   - Clique "Ajouter"

4. **Lance depuis l'écran d'accueil**
   - L'app s'ouvre en plein écran comme une vraie app native!

---

## 🔐 Première Utilisation

### 1. Créer un Compte

1. Ouvre **http://localhost:5000**
2. Clique sur "S'inscrire"
3. Entre ton email et un mot de passe
4. Clique "Créer le compte"

Tu es automatiquement connecté!

### 2. Configuration Supabase (si pas fait)

Si tu n'as pas encore configuré Supabase:

1. Suis le guide [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md)
2. Configure ton fichier `.env`
3. Relance l'application

---

## 📊 Utiliser le Dashboard

### Vue d'ensemble

Le dashboard te montre:
- **Statistiques**: Total, Nouveau, Intéressé, Visité
- **Filtres**: Recherche, statut, tri
- **Liste des annonces** en cartes

### Filtrer les Annonces

```
🔍 Rechercher par:
- Titre de l'annonce
- Localisation

📋 Filtrer par statut:
- Tous les statuts
- Nouveau
- Intéressé
- Pas intéressé
- Visité
- Contact pris
- Offre faite

📊 Trier par:
- Date d'ajout
- Prix
- Date de publication

↕️ Ordre:
- Décroissant (du plus récent au plus ancien)
- Croissant (du plus ancien au plus récent)
```

### Changer le Statut d'une Annonce

**Option 1: Depuis la liste**
- Utilise le menu déroulant directement sur la carte
- Le changement est instantané

**Option 2: Depuis les détails**
- Clique sur l'annonce pour voir les détails
- Clique sur un des boutons de statut
- Le statut est mis à jour

### Statuts Disponibles

| Statut | Signification | Usage |
|--------|---------------|-------|
| **Nouveau** | Jamais vue | Par défaut pour les nouvelles annonces |
| **Intéressé** | À creuser | Tu veux en savoir plus |
| **Pas intéressé** | À ignorer | Ne correspond pas |
| **Visité** | Visite faite | Tu as visité le bien |
| **Contact pris** | En discussion | Contact avec le vendeur |
| **Offre faite** | Offre envoyée | Tu as fait une offre |

---

## 🔍 Voir une Annonce

### Depuis le Dashboard

Clique sur le titre de l'annonce → Page de détails

### Page de Détails

Tu verras:
- **Photos** (galerie cliquable)
- **Prix** en gros
- **Localisation, surface, pièces**
- **Description complète**
- **Source** (leboncoin, pap, etc.)
- **Dates** (publication, ajout, dernière vue)
- **Téléphone** (si disponible)
- **Boutons de statut**

### Actions Disponibles

- **Voir l'annonce complète**: Ouvre le site source dans un nouvel onglet
- **Changer le statut**: Clique sur les boutons
- **Supprimer**: Supprime définitivement l'annonce

---

## 🔄 Lancer un Scraping

### Via l'Interface Web (bientôt)

Pour l'instant, l'interface de scraping affiche les instructions.

### Via Ligne de Commande (recommandé)

```bash
# Scraping complet
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10

# Test d'un site spécifique
python3 test_scrapers.py --ville Lyon --site pap

# Scraper lite (sans DB)
python3 scraper_lite.py Marseille
```

### Fréquence Recommandée

- **1 fois par jour** pour avoir les nouvelles annonces
- **Le matin tôt** (6h-7h) pour être le premier

---

## 🧹 Nettoyage Automatique

Le système nettoie automatiquement:
- Annonces de plus de **90 jours**
- Annonces marquées **"Pas intéressé"**

Pour forcer un nettoyage:
```bash
python3 main.py --cleanup --user-id ton-email@example.com
```

---

## 📱 Utilisation sur iPad

### Mode Standalone

Une fois installée sur l'écran d'accueil:
- L'app s'ouvre en plein écran
- Pas de barre d'adresse Safari
- Comme une vraie app native!

### Gestes

- **Swipe vers le bas** (en haut de page): Rafraîchir
- **Tap sur une annonce**: Voir les détails
- **Tap sur une photo**: Agrandir

### Raccourcis Clavier (iPad avec clavier)

- **Cmd + K**: Focus sur la recherche
- **Escape**: Effacer la recherche

---

## 🔒 Sécurité

### Mots de Passe

Les mots de passe sont hashés (SHA-256) avant stockage.

**⚠️ Note de sécurité:**
- Pour une app en production, utilise un hash plus robuste (bcrypt)
- Active HTTPS pour l'accès distant
- Ne partage jamais tes clés Supabase

### Multi-Utilisateurs

Chaque utilisateur voit uniquement **ses propres annonces**.

Les données sont isolées par `user_id`.

---

## 🆘 Problèmes Courants

### "Module 'flask' not found"

```bash
pip3 install flask
```

### "Connection refused" depuis iPad

1. Vérifie que ton Mac et iPad sont sur le **même WiFi**
2. Vérifie le firewall Mac (Préférences Système → Sécurité → Pare-feu)
3. Utilise l'IP affichée au démarrage de l'app

### "Invalid API key" - Supabase

1. Vérifie que `.env` existe
2. Vérifie que les clés sont correctes
3. Consulte [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

### Les annonces ne s'affichent pas

1. Vérifie que Supabase est configuré
2. Lance un scraping:
   ```bash
   python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
   ```
3. Rafraîchis la page web

---

## 🎯 Workflow Complet

### Jour 1 - Installation

1. Configure Supabase ([SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md))
2. Lance l'app: `./start_app.sh`
3. Crée ton compte
4. Lance un scraping:
   ```bash
   python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
   ```

### Jour 2+ - Utilisation Quotidienne

**Matin:**
1. Lance un nouveau scraping (nouvelles annonces)
2. Ouvre le dashboard
3. Filtre par "Nouveau"
4. Parcours les nouvelles annonces

**Pour chaque annonce:**
1. Regarde les photos et détails
2. Marque le statut:
   - Intéressé → À creuser
   - Pas intéressé → Masquer
3. Pour les intéressantes:
   - Clique "Voir l'annonce complète"
   - Prends contact si ça vaut le coup
   - Marque "Contact pris"

**Après visite:**
- Marque "Visité"
- Si tu fais une offre → "Offre faite"

---

## 📈 Prochaines Fonctionnalités

**V1.1 (bientôt):**
- Scraping depuis l'interface web
- Notifications push (nouvelles annonces)
- Historique des modifications de statut
- Export des annonces en CSV/PDF

**V1.2 (plus tard):**
- Notes personnalisées sur les annonces
- Système de favoris
- Comparateur de biens
- Calcul de rentabilité locative

---

## 💡 Astuces

### Recherche Rapide

Utilise la recherche pour trouver:
- Par arrondissement: "15ème"
- Par quartier: "Montmartre"
- Par type: "studio", "T3", "duplex"
- Par prix: "400000"

### Filtres Multiples

Combine les filtres:
1. Filtre par statut "Intéressé"
2. Trie par prix (croissant)
3. Recherche "balcon"

→ Tu obtiens les annonces intéressantes avec balcon, du moins cher au plus cher!

### Organisation

**Stratégie recommandée:**
1. **Nouveau** → À traiter
2. **Intéressé** → À suivre de près
3. **Pas intéressé** → Sera nettoyé automatiquement
4. **Visité** → Historique des visites
5. **Contact pris** → En cours de discussion
6. **Offre faite** → Attente de réponse

---

## 🎉 C'est Parti!

Ton application est prête à l'emploi!

**Commande magique:**
```bash
./start_app.sh
```

Puis ouvre **http://localhost:5000** dans ton navigateur.

**Questions?** Consulte:
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Config base de données
- [START_HERE.md](START_HERE.md) - Guide complet du projet
- [TESTING.md](TESTING.md) - Tester les scrapers
