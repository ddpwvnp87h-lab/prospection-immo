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
    resul    resul    resul    resul    resul    resul data).execute()
                           a[0]['i                           a[0][ée: {listing_id}")
except Exception as e:
    print(f"⚠️  {e}")

# Test 3: Récupérer les annonces
print("\n3️⃣ Récupération annonces...")
result = supabase.table('listings').select('*').eq('user_id', user_id).execute()
print(f"✅ {len(result.data)} annonce(s) trouvée(s)")

for listing in result.data:
    print(f"  • {listing['title']} - {listing['price']:,}€")

print("\n🎉 Tous les tests passés! Supabase fonctionne!")
