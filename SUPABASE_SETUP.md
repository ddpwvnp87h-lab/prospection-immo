# 🗄️ Configuration Supabase - Guide Complet

## 📋 C'est Quoi Supabase?

**Supabase = Base de données PostgreSQL gratuite dans le cloud**

✅ Gratuit jusqu'à 500 MB
✅ Pas de carte bancaire requise
✅ Interface web simple
✅ API automatique

---

## 🚀 Étape 1: Créer un Compte (2 minutes)

### 1.1 Aller sur Supabase

Ouvre ton navigateur et va sur:
```
https://supabase.com
```

### 1.2 S'inscrire

Clique sur **"Start your project"** ou **"Sign Up"**

**Options de connexion:**
- GitHub (recommandé - le plus rapide)
- Google
- Email

→ Choisis GitHub ou Google, c'est instantané!

---

## 🏗️ Étape 2: Créer un Projet (1 minute)

### 2.1 Nouveau Projet

Une fois connecté, tu verras un bouton:
```
+ New Project
```

Clique dessus!

### 2.2 Configurer le Projet

**Remplis les champs:**

| Champ | Valeur |
|-------|--------|
| **Name** | `prospection-immo` |
| **Database Password** | (Génère un mot de passe fort) |
| **Region** | `West EU (Paris)` ← Choisis le plus proche |
| **Pricing Plan** | `Free` ← Gratuit! |

**⚠️ IMPORTANT:**
- Note le **Database Password** quelque part (tu en auras besoin!)
- Ou copie-le dans un fichier texte

### 2.3 Créer

Clique sur **"Create new project"**

→ Attends 1-2 minutes que le projet se crée ☕

---

## 📊 Étape 3: Créer les Tables (2 minutes)

### 3.1 Ouvrir l'Éditeur SQL

Une fois ton projet créé:

1. Dans le menu de gauche, clique sur **"SQL Editor"**
2. Clique sur **"New query"**

### 3.2 Copier le Schéma

Ouvre le fichier `database_schema.sql` dans le projet:

```bash
cat database_schema.sql
```

**Ou copie ce code:**

```sql
-- Table des utilisateurs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table des annonces
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    hash TEXT NOT NULL,
    title TEXT NOT NULL,
    price INTEGER NOT NULL,
    location TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    photos TEXT[],
    phone TEXT,
    surface INTEGER,
    rooms INTEGER,
    description TEXT,
    status TEXT DEFAULT 'Nouveau',
    published_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW()
);

-- Index pour les performances
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_url ON listings(url);
```

### 3.3 Exécuter le SQL

1. Colle le code dans l'éditeur SQL
2. Clique sur **"Run"** (ou Ctrl/Cmd + Enter)
3. Tu devrais voir: `Success. No rows returned`

✅ **Tes tables sont créées!**

---

## 🔑 Étape 4: Récupérer les Clés (1 minute)

### 4.1 Aller dans Settings

1. Menu de gauche → **"Settings"** (icône d'engrenage)
2. Clique sur **"API"**

### 4.2 Copier les Clés

Tu vas voir 2 informations importantes:

**1. Project URL**
```
https://xxxxxxxxxxxxx.supabase.co
```
→ Copie-la!

**2. anon public (API Key)**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx
```
→ Copie-la!

**⚠️ GARDE CES CLÉS!** Tu en auras besoin dans 30 secondes.

---

## ⚙️ Étape 5: Configurer le Projet (30 secondes)

### 5.1 Créer le fichier .env

Dans le terminal:

```bash
cd "/Users/user/Desktop/dossier sans titre"
cp .env.example .env
```

### 5.2 Éditer .env

Ouvre le fichier `.env` avec un éditeur de texte:

```bash
nano .env
```

Ou ouvre-le dans VSCode.

### 5.3 Coller tes Clés

Remplace les valeurs:

```bash
# Remplace avec TES vraies clés
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx

# Garde les autres valeurs par défaut
SCRAPING_DELAY=2
MAX_PAGES_PER_SITE=5
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
```

**Sauvegarde le fichier:**
- Nano: Ctrl+O, Enter, Ctrl+X
- VSCode: Cmd+S

---

## ✅ Étape 6: Tester la Connexion (1 minute)

### 6.1 Script de Test

Créons un script de test rapide:

```bash
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print('✅ Fichier .env chargé!')
print(f'URL: {url[:30]}...')
print(f'Key: {key[:50]}...')

if url and 'supabase.co' in url and key and len(key) > 100:
    print('\\n🎉 Configuration OK!')
else:
    print('\\n❌ Erreur de configuration')
"
```

**Résultat attendu:**
```
✅ Fichier .env chargé!
URL: https://xxxxxxxxxxxxx.supabase...
Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...

🎉 Configuration OK!
```

---

## 🧪 Étape 7: Test Complet avec Insertion (2 minutes)

### 7.1 Installer Supabase Python

```bash
pip3 install supabase python-dotenv
```

### 7.2 Test d'Insertion

Crée un fichier de test:

```bash
cat > test_supabase.py << 'EOF'
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

# Charger .env
load_dotenv()

# Connexion
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("🔌 Connexion à Supabase...")

# Test 1: Insérer un utilisateur de test
print("\n1️⃣ Insertion utilisateur test...")
user_data = {
    'email': 'test@example.com',
    'password_hash': 'hashed_password_here'
}

try:
    result = supabase.table('users').insert(user_data).execute()
    user_id = result.data[0]['id']
    print(f"✅ Utilisateur créé: {user_id}")
except Exception as e:
    if 'duplicate key' in str(e):
        print("⚠️  Utilisateur existe déjà (normal si 2e test)")
        # Récupérer l'utilisateur existant
        result = supabase.table('users').select('id').eq('email', 'test@example.com').execute()
        user_id = result.data[0]['id']
    else:
        print(f"❌ Erreur: {e}")
        exit(1)

# Test 2: Insérer une annonce de test
print("\n2️⃣ Insertion annonce test...")
listing_data = {
    'user_id': user_id,
    'hash': 'test_hash_123',
    'title': 'Appartement 3 pièces - Paris',
    'price': 450000,
    'location': 'Paris 15ème',
    'url': 'https://example.com/test-123',
    'source': 'test',
    'status': 'Nouveau'
}

try:
    result = supabase.table('listings').insert(listing_data).execute()
    listing_id = result.data[0]['id']
    print(f"✅ Annonce créée: {listing_id}")
except Exception as e:
    print(f"⚠️  {e}")

# Test 3: Récupérer les annonces
print("\n3️⃣ Récupération annonces...")
result = supabase.table('listings').select('*').eq('user_id', user_id).execute()
print(f"✅ {len(result.data)} annonce(s) trouvée(s)")

for listing in result.data:
    print(f"  • {listing['title']} - {listing['price']:,}€")

print("\n🎉 Tous les tests passés! Supabase fonctionne!")
EOF

chmod +x test_supabase.py
python3 test_supabase.py
```

**Résultat attendu:**
```
🔌 Connexion à Supabase...

1️⃣ Insertion utilisateur test...
✅ Utilisateur créé: abc123...

2️⃣ Insertion annonce test...
✅ Annonce créée: def456...

3️⃣ Récupération annonces...
✅ 1 annonce(s) trouvée(s)
  • Appartement 3 pièces - Paris - 450,000€

🎉 Tous les tests passés! Supabase fonctionne!
```

---

## 🎯 Étape 8: Utiliser le Projet Complet

### 8.1 Installer les Dépendances

```bash
pip3 install requests beautifulsoup4 python-dotenv supabase
```

### 8.2 Première Prospection

```bash
python3 main.py --user-id maureen --ville Paris --rayon 10
```

**Note:** Les scrapers retourneront `[]` pour l'instant (templates), mais la DB fonctionne!

---

## 🔍 Visualiser les Données

### Dans Supabase

1. Va sur Supabase → ton projet
2. Menu de gauche → **"Table Editor"**
3. Sélectionne la table **"listings"**
4. Tu verras toutes tes annonces!

**Tu peux:**
- ✅ Voir les données
- ✅ Modifier manuellement
- ✅ Supprimer
- ✅ Exporter en CSV

---

## 📊 Résumé

### Ce qui a été fait:

✅ **Compte Supabase créé**
✅ **Projet créé**
✅ **Tables créées (users, listings)**
✅ **Clés récupérées**
✅ **Fichier .env configuré**
✅ **Connexion testée**

### Fichiers importants:

```
.env                    ← Tes clés Supabase (ne JAMAIS commit!)
database_schema.sql     ← Schéma des tables
test_supabase.py        ← Script de test
```

### Prochaines étapes:

1. ✅ Supabase configuré
2. → Installer les scrapers: `pip3 install requests beautifulsoup4`
3. → Tester: `python3 test_scrapers.py --ville Paris --site pap`
4. → Production: `python3 main.py --user-id maureen --ville Paris`

---

## 🆘 Problèmes Courants

### "SSL: CERTIFICATE_VERIFY_FAILED"

```bash
pip3 install --upgrade certifi
```

### "ModuleNotFoundError: No module named 'supabase'"

```bash
pip3 install supabase
```

### "Invalid API key"

→ Revérifie que tu as copié la bonne clé dans `.env`
→ La clé doit commencer par `eyJ...`

### "relation 'users' does not exist"

→ Tu as oublié d'exécuter le SQL de l'étape 3
→ Retourne dans SQL Editor et exécute `database_schema.sql`

---

## 🎉 C'est Tout!

Supabase est maintenant **configuré et prêt**!

**Test rapide:**
```bash
python3 test_supabase.py
```

Si ça marche → **Tu es prêt pour la prospection!** 🚀
