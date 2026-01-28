# 🏠 Application Web - Prospection Immo Team Maureen

## 🎉 Ton Application est Prête!

Tu as maintenant une **application web complète** pour gérer tes annonces immobilières!

---

## ✨ Ce que tu as

### 🖥 Application Web Flask

- **Authentification**: Login/Register avec hashage des mots de passe
- **Dashboard**: Vue d'ensemble de toutes tes annonces
- **Filtres & Recherche**: Trouve rapidement ce que tu cherches
- **Gestion des statuts**: Organise tes annonces par priorité
- **Vue détaillée**: Toutes les infos d'une annonce
- **Responsive**: Fonctionne sur ordinateur et iPad
- **PWA**: Installable sur iPad comme une vraie app

### 🗄 Base de Données Supabase

- **Multi-utilisateurs**: Chaque utilisateur voit ses propres annonces
- **Stockage cloud**: Accessible de partout
- **Gratuit**: Jusqu'à 500 MB
- **Sécurisé**: Données isolées par utilisateur

### 🔍 Scrapers Implémentés

- **leboncoin.fr** (Playwright)
- **pap.fr** (BeautifulSoup)
- **facebook.com/marketplace** (Playwright)
- **figaro-immo.fr** (BeautifulSoup)
- **+ 4 templates prêts** (paruvendu, logic-immo, bienici, seloger)

---

## 📁 Structure de l'Application

```
ton-projet/
│
├── app.py                      ← Application Flask principale
│
├── templates/                  ← Pages HTML
│   ├── base.html              ← Template de base
│   ├── login.html             ← Page de connexion
│   ├── register.html          ← Page d'inscription
│   ├── dashboard.html         ← Dashboard principal
│   ├── listing_detail.html    ← Détails d'une annonce
│   └── scrape.html            ← Page de scraping
│
├── static/                     ← CSS, JS, images
│   ├── css/
│   │   └── style.css          ← Styles de l'app
│   ├── js/
│   │   └── app.js             ← JavaScript + PWA
│   └── service-worker.js      ← Service Worker PWA
│
├── database/                   ← Gestion Supabase
│   └── manager.py
│
├── scrapers/                   ← Scrapers par site
│   ├── leboncoin.py
│   ├── pap.py
│   ├── facebook_marketplace.py
│   └── figaro_immo.py
│
└── start_app.sh               ← Script de lancement
```

---

## 🚀 Comment Lancer

### Option 1: Script Automatique

```bash
./start_app.sh
```

### Option 2: Manuel

```bash
# Installer Flask (première fois)
pip3 install flask

# Lancer
python3 app.py
```

### Accès

**Sur ton Mac:**
```
http://localhost:5000
```

**Sur iPad (même WiFi):**
```
http://[ton-ip]:5000
```
(L'IP est affichée au démarrage)

---

## 🎯 Fonctionnalités Principales

### 1. Authentification

**Route:** `/login` et `/register`

- Inscription avec email + mot de passe
- Hashage SHA-256 des mots de passe
- Sessions Flask sécurisées
- Redirection automatique si non connecté

### 2. Dashboard

**Route:** `/`

**Affichage:**
- Statistiques en haut (Total, Nouveau, Intéressé, Visité)
- Filtres de recherche
- Grille d'annonces avec photos
- Menu déroulant de statut sur chaque carte

**Filtres disponibles:**
- Recherche textuelle (titre, localisation)
- Filtre par statut
- Tri (date, prix, publication)
- Ordre (croissant/décroissant)

### 3. Vue Détaillée

**Route:** `/listing/<id>`

**Affichage:**
- Galerie de photos (cliquable)
- Prix, localisation, surface, pièces
- Description complète
- Boutons de statut (6 options)
- Lien vers l'annonce source
- Bouton supprimer

### 4. Gestion des Statuts

**6 statuts disponibles:**

| Statut | Badge | Usage |
|--------|-------|-------|
| Nouveau | 🔵 Bleu | Par défaut |
| Intéressé | 🟢 Vert | À suivre |
| Pas intéressé | ⚪ Gris | À ignorer |
| Visité | 🟡 Jaune | Visite faite |
| Contact pris | 🔵 Bleu | En discussion |
| Offre faite | 💰 Or | Offre envoyée |

**Changement de statut:**
- Depuis le dashboard (menu déroulant)
- Depuis la page détaillée (boutons)
- Mise à jour instantanée en base

### 5. Scraping

**Route:** `/scrape`

Pour l'instant, affiche les instructions pour lancer le scraping en ligne de commande.

**À venir:** Scraping directement depuis l'interface web.

### 6. PWA (Progressive Web App)

**Installation sur iPad:**

1. Ouvre Safari sur iPad
2. Va sur l'URL de l'app
3. Tap "Partager" → "Sur l'écran d'accueil"
4. Lance depuis l'icône

**Fonctionnalités PWA:**
- Mode plein écran (pas de barre Safari)
- Icône sur l'écran d'accueil
- Cache pour fonctionnement offline
- Service Worker pour les performances

---

## 🔌 API Endpoints

### Publiques

- `GET /` - Dashboard (login requis)
- `GET /login` - Page de connexion
- `POST /login` - Authentification
- `GET /register` - Page d'inscription
- `POST /register` - Création de compte
- `GET /logout` - Déconnexion

### Annonces

- `GET /listing/<id>` - Détails d'une annonce
- `POST /listing/<id>/status` - Mettre à jour le statut
- `POST /listing/<id>/delete` - Supprimer une annonce

### Scraping

- `GET /scrape` - Page de scraping
- `POST /scrape/run` - Lancer un scraping (à implémenter)

### API JSON

- `GET /api/listings` - Liste des annonces (JSON)
- `GET /api/stats` - Statistiques (JSON)

### PWA

- `GET /manifest.json` - Manifeste PWA
- `GET /service-worker.js` - Service Worker

---

## 🎨 Interface Utilisateur

### Design

- **Moderne**: Interface épurée type "Tailwind"
- **Responsive**: S'adapte à tous les écrans
- **Accessible**: Contrastes et tailles de texte optimaux
- **Intuitive**: Navigation simple et claire

### Couleurs

```css
Primary (Indigo):   #4F46E5
Secondary (Green):  #10B981
Danger (Red):       #EF4444
Warning (Yellow):   #F59E0B
Info (Blue):        #3B82F6
```

### Composants

- **Cards**: Annonces en grilles
- **Badges**: Statuts colorés
- **Buttons**: Primaire, Secondaire, Outline, Danger
- **Forms**: Inputs, Selects, Checkboxes
- **Alerts**: Success, Error, Warning, Info
- **Stats**: Cartes de statistiques

---

## 💾 Base de Données

### Tables Utilisées

**users**
- `id` (UUID)
- `email` (unique)
- `password_hash`
- `created_at`
- `updated_at`

**listings**
- `id` (UUID)
- `user_id` (FK vers users)
- `hash` (pour déduplication)
- `title`, `price`, `location`, `url`
- `source`, `photos`, `phone`
- `surface`, `rooms`, `description`
- `status` (Nouveau, Intéressé, etc.)
- `published_date`
- `created_at`, `updated_at`, `last_seen_at`

### Isolation des Données

Chaque requête filtre par `user_id`:
```python
.eq('user_id', session['user_id'])
```

→ Les utilisateurs ne voient que leurs propres annonces.

---

## 🔒 Sécurité

### Mots de Passe

```python
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

**Note:** Pour la production, utilise `bcrypt` au lieu de SHA-256.

### Sessions

```python
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
```

**Important:** Change la `FLASK_SECRET_KEY` dans `.env` en production!

### Protection des Routes

```python
@login_required
def dashboard():
    ...
```

→ Redirige vers `/login` si non authentifié.

### CSRF

**À ajouter en production:** Flask-WTF pour la protection CSRF.

---

## 📱 PWA - Details Techniques

### manifest.json

```json
{
  "name": "Prospection Immo",
  "short_name": "Prospection",
  "display": "standalone",
  "start_url": "/",
  "theme_color": "#4F46E5"
}
```

### Service Worker

**Fonctionnalités:**
- Cache des ressources statiques (CSS, JS)
- Stratégie "Cache first, network fallback"
- Mise à jour automatique du cache
- Préparation pour notifications push

### Installation

**iOS/iPad:**
- Safari uniquement (Chrome ne supporte pas PWA sur iOS)
- Bouton "Ajouter à l'écran d'accueil"
- Mode standalone automatique

---

## 🔄 Workflow Complet

### 1. Setup Initial

```bash
# Configurer Supabase
cp .env.example .env
nano .env  # Ajouter les clés Supabase

# Tester la connexion
python3 test_supabase.py

# Lancer l'app
./start_app.sh
```

### 2. Utilisation Quotidienne

**Matin:**
```bash
# Lancer un scraping
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
```

**Sur le web:**
1. Ouvre http://localhost:5000
2. Connecte-toi
3. Dashboard → Filtre "Nouveau"
4. Parcours les annonces
5. Change les statuts

**Sur iPad:**
1. Lance l'app depuis l'écran d'accueil
2. Même workflow qu'au-dessus
3. Pull-to-refresh pour actualiser

### 3. Suivi

**Organisation par statut:**
- **Nouveau** → Annonces à traiter
- **Intéressé** → Follow-up quotidien
- **Contact pris** → En attente de réponse
- **Visité** → Décision à prendre
- **Offre faite** → Attente vendeur
- **Pas intéressé** → Auto-suppression

---

## 🚀 Prochaines Étapes

### V1.1 (À venir)

- [ ] Scraping depuis l'interface web
- [ ] Worker asynchrone (Celery/RQ)
- [ ] Notifications push (nouvelles annonces)
- [ ] Historique des modifications de statut
- [ ] Export CSV/PDF des annonces

### V1.2 (Plus tard)

- [ ] Notes personnalisées sur les annonces
- [ ] Système de favoris/bookmarks
- [ ] Comparateur de biens (tableau)
- [ ] Calcul de rentabilité locative
- [ ] Intégration carte interactive
- [ ] Alertes email (nouvelles annonces)

### V2.0 (Futur)

- [ ] Application mobile native (React Native)
- [ ] OCR pour extraire infos des photos
- [ ] IA pour scoring des annonces
- [ ] Chatbot pour questions automatiques
- [ ] Intégration calendrier (visites)
- [ ] Système de partage (équipe)

---

## 🆘 Support et Dépannage

### Problèmes Courants

**1. "Module 'flask' not found"**
```bash
pip3 install flask
```

**2. "Connection refused" depuis iPad**
- Mac et iPad sur le même WiFi?
- Firewall Mac désactivé?
- Bonne IP utilisée?

**3. "Invalid API key" - Supabase**
- Fichier `.env` existe?
- Clés correctes?
- Voir [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

**4. Page blanche**
- Ouvre la console JavaScript (F12)
- Vérifie les erreurs
- Vérifie que les fichiers CSS/JS sont chargés

**5. Les statuts ne se sauvegardent pas**
- Supabase configuré?
- Connexion internet OK?
- Vérifie les logs dans le terminal

### Logs

Les logs Flask s'affichent dans le terminal:
```
127.0.0.1 - - [28/Jan/2026 15:30:45] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [28/Jan/2026 15:30:50] "POST /listing/abc123/status HTTP/1.1" 302 -
```

### Debug Mode

Pour plus de détails, active le mode debug:
```python
# Dans app.py, dernière ligne:
app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## 📚 Documentation Complète

| Document | Description |
|----------|-------------|
| [LANCE_APPLICATION.md](LANCE_APPLICATION.md) | Guide ultra-rapide |
| [GUIDE_APPLICATION.md](GUIDE_APPLICATION.md) | Guide complet d'utilisation |
| [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md) | Config Supabase (5 min) |
| [SUPABASE_SETUP.md](SUPABASE_SETUP.md) | Config Supabase (complète) |
| [START_HERE.md](START_HERE.md) | Vue d'ensemble du projet |
| [TESTING.md](TESTING.md) | Guide de test des scrapers |
| [INDEX.md](INDEX.md) | Index de navigation |

---

## 🎉 Récapitulatif

Tu as maintenant:

✅ **Application web Flask complète**
- Login/Register
- Dashboard avec stats
- Filtres et recherche
- Gestion des statuts
- Vue détaillée des annonces

✅ **PWA installable sur iPad**
- Mode standalone
- Service Worker
- Cache offline
- Pull-to-refresh

✅ **Base de données Supabase**
- Multi-utilisateurs
- Isolation des données
- Stockage cloud

✅ **Scrapers fonctionnels**
- 4 sites implémentés
- Templates pour 4 autres
- Validation et déduplication

✅ **Documentation complète**
- Guides d'utilisation
- Setup Supabase
- Tests

---

## 🚀 Commande Magique

```bash
./start_app.sh
```

Puis ouvre **http://localhost:5000**

**Profite bien! 🏠**
