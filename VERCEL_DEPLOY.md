# 🚀 Déployer sur Vercel - Guide Complet

## 🎯 Pourquoi Vercel?

✅ **Gratuit** (pour les projets personnels)
✅ **Accessible 24/7** de partout
✅ **HTTPS automatique**
✅ **Déploiement en 2 minutes**
✅ **Git automatique** (push = déploiement)

---

## ⚠️ Important à Savoir

### Ce qui Fonctionne sur Vercel

✅ Application web complète
✅ Dashboard, login, filtres
✅ Gestion des annonces et statuts
✅ Vue détaillée
✅ API JSON
✅ PWA installable

### Ce qui ne Fonctionne PAS sur Vercel

❌ **Scraping directement depuis Vercel**
- Vercel = serverless functions (timeout 10 secondes)
- Le scraping prend plusieurs minutes
- **Solution**: Lance le scraping en local sur ton Mac

**Workflow:**
1. Scraping en local: `python3 main.py --user-id ton-email@example.com --ville Paris`
2. Les données vont dans Supabase
3. L'app Vercel les affiche automatiquement!

---

## 📋 Prérequis

### 1. Compte Vercel

Va sur https://vercel.com et crée un compte (gratuit).

**Options:**
- GitHub (recommandé)
- GitLab
- Bitbucket
- Email

### 2. Supabase Configuré

Tu as déjà fait ça! Si non, suis [SUPABASE_EN_BREF.md](SUPABASE_EN_BREF.md)

### 3. Git

Ton projet doit être sur GitHub/GitLab.

---

## 🚀 Méthode 1: Déploiement via GitHub (Recommandé)

### Étape 1: Push sur GitHub

```bash
cd "/Users/user/Desktop/dossier sans titre"

# Initialiser Git (si pas fait)
git init

# Ajouter .gitignore
cat > .gitignore << 'EOF'
.env
.env.local
__pycache__/
*.pyc
venv/
node_modules/
.DS_Store
EOF

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "Initial commit - Prospection Immo"

# Créer un repo sur GitHub
# Va sur https://github.com/new
# Nom: prospection-immo
# Public ou Private (au choix)

# Push vers GitHub
git remote add origin https://github.com/ton-username/prospection-immo.git
git branch -M main
git push -u origin main
```

### Étape 2: Connecter Vercel

1. **Va sur https://vercel.com/new**

2. **Import Git Repository**
   - Choisis ton repo GitHub `prospection-immo`
   - Clique "Import"

3. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (laisse vide)
   - **Output Directory**: (laisse vide)

4. **Environment Variables** (Important!)

   Ajoute ces 3 variables:

   | Name | Value |
   |------|-------|
   | `SUPABASE_URL` | Ta URL Supabase (depuis .env) |
   | `SUPABASE_KEY` | Ta clé Supabase (depuis .env) |
   | `FLASK_SECRET_KEY` | Une clé secrète aléatoire |

   **Générer une FLASK_SECRET_KEY:**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copie le résultat et colle-le dans Vercel.

5. **Deploy**
   - Clique "Deploy"
   - Attends 1-2 minutes ☕
   - Ton app est en ligne! 🎉

### Étape 3: Teste ton App

Vercel te donne une URL comme:
```
https://prospection-immo.vercel.app
```

Ouvre-la et teste:
1. Créer un compte
2. Se connecter
3. Voir le dashboard (vide pour l'instant)

### Étape 4: Ajouter des Annonces

**Sur ton Mac:**
```bash
# Lance un scraping
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
```

Les annonces vont dans Supabase, et apparaissent automatiquement sur ton app Vercel! 🎉

---

## 🚀 Méthode 2: Déploiement Direct (CLI Vercel)

### Étape 1: Installer Vercel CLI

```bash
npm install -g vercel
```

### Étape 2: Login

```bash
vercel login
```

### Étape 3: Déployer

```bash
cd "/Users/user/Desktop/dossier sans titre"

# Premier déploiement
vercel
```

**Questions posées:**
- Setup and deploy? **Y**
- Which scope? Choisis ton compte
- Link to existing project? **N**
- Project name? **prospection-immo**
- Directory? **./** (Enter)
- Override settings? **N**

### Étape 4: Variables d'Environnement

```bash
# Ajouter les variables
vercel env add SUPABASE_URL
# Colle ta SUPABASE_URL

vercel env add SUPABASE_KEY
# Colle ta SUPABASE_KEY

vercel env add FLASK_SECRET_KEY
# Génère avec: python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Étape 5: Redéployer avec les Variables

```bash
vercel --prod
```

Ton app est en ligne! 🎉

---

## 📱 Domaine Personnalisé (Optionnel)

### Utiliser ton Propre Domaine

1. **Achète un domaine** (ex: OVH, Google Domains, Namecheap)

2. **Dans Vercel:**
   - Va dans ton projet
   - Settings → Domains
   - Ajoute ton domaine: `prospection-immo.com`

3. **Configure le DNS:**
   - Ajoute un enregistrement CNAME:
     - Name: `www` ou `@`
     - Value: `cname.vercel-dns.com`

4. **Attends** quelques minutes (propagation DNS)

5. **Accède à ton app:**
   ```
   https://prospection-immo.com
   ```

---

## 🔄 Mises à Jour

### Déploiement Automatique (GitHub)

**C'est automatique!**

Chaque fois que tu push sur GitHub:
```bash
git add .
git commit -m "Ajout de nouvelles fonctionnalités"
git push
```

→ Vercel détecte le push et redéploie automatiquement! 🎉

### Déploiement Manuel (CLI)

```bash
vercel --prod
```

---

## 🔧 Configuration Avancée

### Ajouter des Variables d'Environnement

**Via le Dashboard:**
1. Va sur https://vercel.com
2. Sélectionne ton projet
3. Settings → Environment Variables
4. Ajoute une variable

**Via la CLI:**
```bash
vercel env add NOM_VARIABLE
```

### Voir les Logs

**Dashboard:**
- Deployments → Sélectionne un déploiement → Logs

**CLI:**
```bash
vercel logs
```

---

## 🆘 Problèmes Courants

### "Build failed"

**Cause:** Erreur dans requirements.txt ou code

**Solution:**
```bash
# Vérifie les logs
vercel logs

# Test en local d'abord
python3 -m flask run
```

### "Internal Server Error"

**Cause:** Variables d'environnement manquantes

**Solution:**
1. Vérifie que SUPABASE_URL et SUPABASE_KEY sont définies
2. Settings → Environment Variables
3. Redéploie

### "502 Bad Gateway"

**Cause:** Timeout (fonction prend trop de temps)

**Solution:**
- Les fonctions Vercel ont un timeout de 10s (gratuit) ou 60s (pro)
- Le scraping doit rester en local

### "Module not found"

**Cause:** Dépendance manquante dans requirements.txt

**Solution:**
```bash
# Ajoute la dépendance
echo "nom-module==version" >> requirements-vercel.txt

# Redéploie
git add requirements-vercel.txt
git commit -m "Fix: ajout dépendance"
git push
```

---

## 📊 Workflow Complet

### Quotidien

**1. Scraping (Sur ton Mac):**
```bash
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10
```

**2. Voir les Annonces (Sur Vercel):**
```
https://prospection-immo.vercel.app
```

**3. Gérer les Annonces:**
- Filtre "Nouveau"
- Change les statuts
- Marque comme "Intéressé" ou "Pas intéressé"

### Hebdomadaire

**Nettoyage:**
```bash
python3 main.py --cleanup --user-id ton-email@example.com
```

---

## 💡 Astuces

### 1. Automatiser le Scraping

**GitHub Actions (gratuit):**

Crée `.github/workflows/scrape.yml`:
```yaml
name: Scraping Quotidien

on:
  schedule:
    - cron: '0 6 * * *'  # Tous les jours à 6h

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python3 main.py --user-id ${{ secrets.USER_EMAIL }} --ville Paris
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

### 2. Notifications

**Ajoute des alertes email** quand de nouvelles annonces arrivent:
- Utilise SendGrid (gratuit 100 emails/jour)
- Ajoute un webhook Vercel

### 3. Analytics

**Ajoute Google Analytics:**
- Crée un compte GA4
- Ajoute le script dans `templates/base.html`

---

## 🎉 Récapitulatif

**Tu as maintenant:**

✅ **App hébergée sur Vercel**
- Accessible 24/7 de partout
- HTTPS automatique
- URL type: `https://prospection-immo.vercel.app`

✅ **Base de données Supabase**
- Cloud gratuit
- Multi-utilisateurs
- Synchronisée automatiquement

✅ **Scraping en local**
- Lance sur ton Mac quand tu veux
- Les données vont directement dans Supabase
- L'app Vercel les affiche automatiquement

✅ **PWA installable**
- Sur iPad, iPhone, Android
- Comme une vraie app native

---

## 🚀 Commande Magique

```bash
# Sur ton Mac (scraping)
python3 main.py --user-id ton-email@example.com --ville Paris --rayon 10

# Sur le web (consultation)
https://prospection-immo.vercel.app
```

---

## 📚 Ressources

- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/

---

**Besoin d'aide?**
- Vercel Support: https://vercel.com/support
- Supabase Discord: https://discord.supabase.com

**Prêt à déployer?** Commence maintenant! 🚀
