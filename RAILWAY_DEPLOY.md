# 🚂 Déployer sur Railway - 5 Minutes

## Pourquoi Railway?

- ✅ **Gratuit** (500h/mois = ~20 jours)
- ✅ **Scraping possible** (pas de timeout)
- ✅ **Python complet** (pas serverless)
- ✅ **Déploiement simple** (GitHub)
- ✅ **HTTPS automatique**

---

## Étape 1: Crée un compte Railway (1 min)

1. Va sur **https://railway.app**
2. Clique "Login"
3. Connecte-toi avec **GitHub** (recommandé)

---

## Étape 2: Push ton projet sur GitHub (2 min)

```bash
cd "/Users/user/Desktop/dossier sans titre"

# Init Git
git init

# .gitignore
echo ".env
__pycache__/
*.pyc
.DS_Store" > .gitignore

# Commit
git add .
git commit -m "Prospection Immo"

# Crée un repo sur github.com/new
# Puis push:
git remote add origin https://github.com/TON-USERNAME/prospection-immo.git
git push -u origin main
```

---

## Étape 3: Déploie sur Railway (2 min)

1. Va sur **https://railway.app/new**

2. Clique **"Deploy from GitHub repo"**

3. Sélectionne ton repo **prospection-immo**

4. Railway détecte automatiquement Python et déploie!

5. Attends 1-2 minutes...

---

## Étape 4: Configure les Variables (1 min)

Dans Railway:

1. Clique sur ton projet
2. Va dans **Variables**
3. Ajoute:

| Variable | Valeur |
|----------|--------|
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | `eyJhbG...` |
| `FLASK_SECRET_KEY` | (génère une clé aléatoire) |

**Générer FLASK_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

4. Railway redéploie automatiquement

---

## Étape 5: Accède à ton App

1. Dans Railway, clique **Settings**
2. Section **Domains**
3. Clique **Generate Domain**

Tu obtiens une URL comme:
```
https://prospection-immo-production.up.railway.app
```

**C'est ton app en ligne! 🎉**

---

## Utilisation

### Sur ton App Railway

1. Ouvre l'URL Railway dans ton navigateur
2. Crée un compte
3. Va dans "Scraping"
4. Clique **"🚀 Lancer le Scraping"**
5. Les annonces apparaissent dans le Dashboard!

### Sur iPad

1. Ouvre Safari
2. Va sur ton URL Railway
3. Partager → "Sur l'écran d'accueil"
4. L'app est installée comme une vraie app!

---

## Résumé

```
1. Compte Railway (GitHub login)
2. Push sur GitHub
3. Deploy from GitHub sur Railway
4. Ajoute les variables SUPABASE_URL, SUPABASE_KEY, FLASK_SECRET_KEY
5. Generate Domain
6. C'est en ligne! 🎉
```

**Temps total: ~5 minutes**

---

## Coûts

**Plan Gratuit Railway:**
- 500 heures / mois
- ~20 jours d'utilisation continue
- Ou illimité si l'app dort (se réveille à la demande)

**Pour une utilisation plus intensive:**
- Plan Hobby: $5/mois (illimité)

---

## Problèmes?

### "Build failed"
- Vérifie que requirements.txt existe
- Vérifie les logs dans Railway

### "Application error"
- Vérifie les variables d'environnement
- Vérifie les logs: Railway → Deployments → Logs

### Le scraping ne marche pas
- Vérifie que Supabase est configuré
- Vérifie les logs pour voir l'erreur

---

## Alternative: Render.com

Si Railway ne convient pas:

1. Va sur **https://render.com**
2. Même principe que Railway
3. Plan gratuit aussi disponible

---

**Bon déploiement! 🚂**
