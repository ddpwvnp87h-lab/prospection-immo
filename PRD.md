# PRD — Prospection Immo Team Maureen

## 1. Vision produit

Créer une **web app ultra simple** de prospection immobilière pour une équipe, permettant de :
- Scraper des annonces immobilières **de particuliers**
- Centraliser les annonces utiles
- Suivre l’état de contact
- Garder la base propre (anti-doublons + suppression auto)

⚠️ Pas de V2, pas de monétisation, pas de features bonus.

---

## 2. Plateforme & contraintes

- **Type** : Web app (PWA light / web app iPad-friendly)
- **Cible** : Tablette iPad (Safari)
- **Installation** : Aucune (mais ajout possible sur écran d’accueil)
- **Hébergement** : Vercel (low cost / gratuit)
- **Multi-utilisateurs** : Oui (comptes séparés)
- **Données isolées par utilisateur**
- **Nettoyage automatique** (90 jours)

---

## 3. Authentification (OBLIGATOIRE)

### 3.1 Connexion / inscription
- Page **Connexion**
- Page **Inscription**
- Auth par :
  - Email
  - Mot de passe

### 3.2 Règles
- Chaque utilisateur possède :
  - ses paramètres de recherche
  - ses annonces
  - ses statuts
- Mot de passe stocké hashé (jamais en clair)

---

## 4. iPad — bouton “mettre sur l’écran d’accueil” (OBLIGATOIRE)

### 4.1 Objectif
Permettre à l’utilisateur de transformer la web app en “icône d’app” sur l’iPad (Home Screen).
=> usage quotidien comme une vraie app.

### 4.2 Comportement attendu
- Afficher un **bouton stylé iOS** : `+ Ajouter à l’écran d’accueil`
- Au clic :
  - Ouvrir une **modale** simple avec instructions iOS :
    1) Appuie sur le bouton **Partager** (icône carré + flèche)
    2) Choisis **Sur l’écran d’accueil**
    3) Valide

### 4.3 Conditions d’affichage
- Le bouton s’affiche si :
  - device iOS/iPadOS détecté (User-Agent)
  - et idéalement si l’app n’est pas déjà “installée” (mode standalone)
- Si déjà installée : remplacer par badge `✅ Déjà sur l’écran d’accueil`

### 4.4 Assets requis
- Icône app (PNG) : 180x180 minimum
- Nom affiché : **Prospection Immo Team Maureen**

*(Option simple : juste instructions. Option un poil mieux : PWA minimal pour icône + mode plein écran.)*

---

## 5. Scraping d’annonces

### 5.1 Déclenchement
- Bouton unique : **« Scraper maintenant »**
- Scraping manuel uniquement

### 5.2 Sites à scraper (liste extensible)
- leboncoin.fr
- pap.fr
- paruvendu.fr
- logic-immo.com
- bienici.com
- seloger.com *(si faisable techniquement)*
- portails locaux (si besoin)

⚠️ Focus : **particuliers** (exclusion agences si identifiable)

---

## 6. Paramètres de recherche (par utilisateur)

- Ville principale
- Rayon (km) autour de la ville
- Région / pays (DOM, métropole, Suisse, etc.)

---

## 7. Données affichées par annonce

Obligatoires :
- Titre
- **Date de publication**
- Prix
- Localisation
- Lien annonce
- Site source
- 1 à 2 photos (si accessibles)
- Téléphone si visible publiquement

Optionnel :
- Surface, pièces (si dispo)

---

## 8. Statuts & règles de nettoyage

Statuts :
- `Nouveau`
- `Contacté`
- `Réponse reçue`
- `Pas de réponse`
- `Pas intéressé`

Règles :
- `Pas intéressé` => supprimé au prochain scraping
- Suppression automatique après **90 jours**
- Anti-doublon :
  - URL
  - sinon signature (titre + prix + localisation)

---

## 9. Interface (UI / UX)

Style :
- iOS/macOS-like
- Fluide, clean, animations légères
- Liste d’annonces lisible et rapide

Écrans :
1. Connexion
2. Inscription
3. Paramètres de recherche
4. Liste annonces
5. Fiche annonce (light)

---

## 10. Technique (simple)

- Scraping sans IA (Python Playwright/BS4 ou Node Puppeteer)
- API légère
- DB simple (Supabase/Postgres ou SQLite selon choix)
- Front Next.js/React
- Déploiement Vercel

---

## 11. Hors scope (volontaire)

- Monétisation
- V2
- CRM avancé
- Notifications push
- Messagerie intégrée
- Scoring IA
- Automatisation d’appels

---

## 12. Nom du projet

**Prospection Immo Team Maureen**
