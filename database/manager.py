from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import os
import requests


class DatabaseManager:
    """Gestionnaire de base de données Supabase via API REST directe."""

    def __init__(self):
        """Initialise la connexion Supabase."""
        self.connection_error = None
        self.supabase_url_found = False
        self.supabase_key_found = False
        self.client = None  # Pour compatibilité avec le code existant

        self.base_url = os.getenv('SUPABASE_URL')
        self.api_key = os.getenv('SUPABASE_KEY')

        self.supabase_url_found = bool(self.base_url)
        self.supabase_key_found = bool(self.api_key)

        print(f"[DB] SUPABASE_URL exists: {self.supabase_url_found}", flush=True)
        print(f"[DB] SUPABASE_KEY exists: {self.supabase_key_found}", flush=True)

        if self.base_url and self.api_key:
            # Test de connexion
            try:
                self._request('GET', 'users', params={'select': 'id', 'limit': '1'})
                self.client = True  # Marque comme connecté
                print("✅ Connexion Supabase établie", flush=True)
            except Exception as e:
                self.connection_error = str(e)
                print(f"⚠️ Erreur connexion Supabase: {e}", flush=True)
        else:
            self.connection_error = "SUPABASE_URL et/ou SUPABASE_KEY non définis"
            print(f"⚠️ {self.connection_error} - mode démo", flush=True)

    def _request(self, method: str, table: str, data: dict = None, params: dict = None) -> dict:
        """Effectue une requête à l'API REST Supabase."""
        url = f"{self.base_url}/rest/v1/{table}"

        headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=30
        )

        if response.status_code >= 400:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        if response.text:
            return response.json()
        return {}

    def table(self, name: str):
        """Retourne un objet pour construire des requêtes (compatibilité)."""
        return TableQuery(self, name)

    def insert_listings(self, user_id: str, listings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insère de nouvelles annonces en base avec déduplication."""
        if not listings:
            return {"added": 0, "duplicates": 0}

        if not self.client:
            return {"added": 0, "duplicates": 0, "demo": True}

        added = 0
        duplicates = 0

        for listing in listings:
            try:
                listing_hash = self._generate_hash(listing)

                # Vérifier si existe
                existing = self._request('GET', 'listings', params={
                    'select': 'id',
                    'user_id': f'eq.{user_id}',
                    'url': f"eq.{listing['lien']}"
                })

                if existing:
                    # Update last_seen_at
                    self._request('PATCH', 'listings',
                        data={'last_seen_at': datetime.now().isoformat()},
                        params={'id': f"eq.{existing[0]['id']}"})
                    duplicates += 1
                else:
                    # Insert
                    self._request('POST', 'listings', data={
                        'user_id': user_id,
                        'hash': listing_hash,
                        'title': listing['titre'],
                        'price': listing['prix'],
                        'location': listing['localisation'],
                        'url': listing['lien'],
                        'source': listing['site_source'],
                        'photos': listing.get('photos', []),
                        'phone': listing.get('telephone'),
                        'surface': listing.get('surface'),
                        'rooms': listing.get('pieces'),
                        'description': listing.get('description'),
                        'status': 'Nouveau',
                        'published_date': listing.get('date_publication'),
                        'created_at': datetime.now().isoformat(),
                        'last_seen_at': datetime.now().isoformat()
                    })
                    added += 1

            except Exception as e:
                print(f"⚠️ Erreur insertion: {e}")
                continue

        print(f"✅ {added} annonces ajoutées, {duplicates} doublons")
        return {"added": added, "duplicates": duplicates}

    def update_listing_status(self, listing_id: str, user_id: str, status: str) -> bool:
        """Met à jour le statut d'une annonce."""
        if not self.client:
            return False

        try:
            self._request('PATCH', 'listings',
                data={'status': status, 'updated_at': datetime.now().isoformat()},
                params={'id': f'eq.{listing_id}', 'user_id': f'eq.{user_id}'})
            return True
        except Exception as e:
            print(f"⚠️ Erreur update: {e}")
            return False

    def delete_listing(self, listing_id: str, user_id: str) -> bool:
        """Supprime une annonce."""
        if not self.client:
            return False

        try:
            self._request('DELETE', 'listings',
                params={'id': f'eq.{listing_id}', 'user_id': f'eq.{user_id}'})
            return True
        except Exception as e:
            print(f"⚠️ Erreur delete: {e}")
            return False

    def _generate_hash(self, listing: Dict[str, Any]) -> str:
        """Génère un hash unique."""
        signature = f"{listing['titre']}_{listing['prix']}_{listing['localisation']}"
        return hashlib.md5(signature.encode()).hexdigest()


class TableQuery:
    """Helper pour construire des requêtes compatibles avec l'ancien code."""

    def __init__(self, db: DatabaseManager, table: str):
        self.db = db
        self.table = table
        self.params = {'select': '*'}

    def select(self, columns: str = '*', count: str = None):
        self.params['select'] = columns
        if count:
            self.params['count'] = count
        return self

    def eq(self, column: str, value: Any):
        self.params[column] = f'eq.{value}'
        return self

    def lt(self, column: str, value: Any):
        self.params[column] = f'lt.{value}'
        return self

    def order(self, column: str, desc: bool = False):
        direction = 'desc' if desc else 'asc'
        self.params['order'] = f'{column}.{direction}'
        return self

    def execute(self):
        result = self.db._request('GET', self.table, params=self.params)
        return QueryResult(result)

    def insert(self, data: dict):
        result = self.db._request('POST', self.table, data=data)
        return QueryResult(result if isinstance(result, list) else [result])

    def update(self, data: dict):
        self._update_data = data
        return self

    def delete(self):
        self._delete = True
        return self


class QueryResult:
    """Résultat d'une requête."""
    def __init__(self, data):
        self.data = data if isinstance(data, list) else [data] if data else []
