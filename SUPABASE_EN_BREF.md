# 🗄️ Supabase en 5 Minutes

## 🎯 Les 5 Étapes Essentielles

### 1️⃣ Créer un Compte (30 secondes)

**Va sur:** https://supabase.com

**Clique:** "Start your project" → Connecte-toi avec GitHub ou Google

---

### 2️⃣ Créer un Projet (1 minute)

**Clique:** "+ New Project"

**Remplis:**
- Name: `prospection-immo`
- Database Password: (note-le quelque part!)
- Region: `West EU (Paris)`
- Plan: `Free`

**Attends:** 1-2 minutes que ça se crée ☕

---

### 3️⃣ Créer les Tables (1 minute)

**Dans Supabase:**
1. Menu gauche → "SQL Editor"
2. "New query"
3. Copie le contenu de `database_schema.sql`
4. Clique "Run"

✅ Tables créées!

---

### 4️⃣ Récupérer les Clés (30 secondes)

**Dans Supabase:**
1. Menu gauche → "Settings" → "API"
2. Copie **Project URL**
3. Copie **anon public**

---

### 5️⃣ Configurer le Projet (1 minute)

**Dans le terminal:**

```bash
cd "/Users/user/Desktop/dossier sans titre"
cp .env.example .env
nano .env
```

**Colle tes clés dans .env:**

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJ...
```

**Sauvegarde:** Ctrl+O, Enter, Ctrl+X

---

## ✅ Tester

```bash
# Installer supabase
pip3 install supabase python-dotenv

# Tester la connexion
python3 test_supabase.py
```

**Résultat attendu:**
```
✅ Connexion OK
✅ Tables trouvées
✅ Insertion OK
🎉 TOUS LES TESTS PASSÉS!
```

---

## 🆘 Besoin d'aide?

**Guide complet:** [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

**Problème?**
- Certificat SSL → `pip3 install --upgrade certifi`
- Module manquant → `pip3 install supabase`
- Tables manquantes → Étape 3 du guide complet

---

## 📊 C'est Fait!

Une fois que `test_supabase.py` fonctionne:

```bash
# Scraping avec sauvegarde en DB
python3 main.py --user-id maureen --ville Paris --rayon 10
```

**🎉 Tout fonctionne!**
