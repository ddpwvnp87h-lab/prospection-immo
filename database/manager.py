"""
Gestionnaire de base de données Supabase via API REST.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import os
import requests


class DatabaseManager:
    """Gestionnaire Supabase via API REST directe."""

    def __init__(self):
        self.base_url = os.getenv('SUPABASE_URL')
        self.api_key = os.getenv('SUPABASE_KEY')
        self.connected = False
        self.connection_error = None

        print(f"[DB] Initialisation...", flush=True)
        print(f"[DB] SUPABASE_URL: {'OK' if self.base_url else 'MANQUANT'}", flush=True)
        print(f"[DB] SUPABASE_KEY: {'OK' if self.api_key else 'MANQUANT'}", flush=True)

        if self.base_url and self.api_key:
            try:
                # Test de connexion
                self._api_request('GET', 'users', {'select': 'id', 'limit': '1'})
                self.connected = True
                print("✅ Connexion Supabase OK", flush=True)
            except Exception as e:
                self.connection_error = str(e)
                print(f"❌ Erreur Supabase: {e}", flush=True)
        else:
            self.connection_error = "Variables SUPABASE_URL/KEY manquantes"
            print(f"❌ {self.connection_error}", flush=True)

    @property
    def client(self):
        """Retourne self si connecté, None sinon (compatibilité)."""
        return self if self.connected else None

    @property
    def supabase_url_found(self):
        return bool(self.base_url)

    @property
    def supabase_key_found(self):
        return bool(self.api_key)

    def _api_request(self, method: str, table: str, params: dict = None, data: dict = None):
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
            params=params,
            json=data,
            timeout=30
        )

        if response.status_code >= 400:
            raise Exception(f"Supabase {response.status_code}: {response.text[:200]}")

        if response.text:
            return response.json()
        return []

    def table(self, name: str):
        """Crée une requête pour une table."""
        return Query(self, name)

    # ============ Méthodes directes pour les listings ============

    def insert_listings(self, user_id: str, listings: List[Dict]) -> Dict:
        """Insère des annonces avec déduplication."""
        if not self.connected or not listings:
            return {"added": 0, "duplicates": 0}

        added = 0
        duplicates = 0

        for listing in listings:
            try:
                # Vérifier si existe déjà
                existing = self._api_request('GET', 'listings', {
                    'select': 'id',
                    'user_id': f'eq.{user_id}',
                    'url': f"eq.{listing['lien']}"
                })

                if existing:
                    duplicates += 1
                else:
                    self._api_request('POST', 'listings', data={
                        'user_id': user_id,
                        'hash': hashlib.md5(f"{listing['titre']}_{listing['prix']}".encode()).hexdigest(),
                        'title': listing['titre'],
                        'price': listing['prix'],
                        'location': listing['localisation'],
                        'url': listing['lien'],
                        'source': listing['site_source'],
                        'photos': listing.get('photos', []),
                        'phone': listing.get('telephone'),
                        'surface': listing.get('surface'),
                        'rooms': listing.get('pieces'),
                        'description': listing.get('description', ''),
                        'status': 'Nouveau',
                        'published_date': listing.get('date_publication'),
                        'created_at': datetime.now().isoformat(),
                        'last_seen_at': datetime.now().isoformat()
                    })
                    added += 1
            except Exception as e:
                print(f"⚠️ Erreur insertion: {e}", flush=True)

        print(f"✅ {added} ajoutées, {duplicates} doublons", flush=True)
        return {"added": added, "duplicates": duplicates}

    def update_listing_status(self, listing_id: str, user_id: str, status: str) -> bool:
        """Met à jour le statut d'une annonce."""
        if not self.connected:
            return False
        try:
            self._api_request('PATCH', 'listings',
                params={'id': f'eq.{listing_id}', 'user_id': f'eq.{user_id}'},
                data={'status': status, 'updated_at': datetime.now().isoformat()})
            return True
        except Exception as e:
            print(f"⚠️ Erreur update: {e}", flush=True)
            return False

    def delete_listing(self, listing_id: str, user_id: str) -> bool:
        """Supprime une annonce."""
        if not self.connected:
            return False
        try:
            self._api_request('DELETE', 'listings',
                params={'id': f'eq.{listing_id}', 'user_id': f'eq.{user_id}'})
            return True
        except Exception as e:
            print(f"⚠️ Erreur delete: {e}", flush=True)
            return False


class Query:
    """Constructeur de requêtes chainable."""

    def __init__(self, db: DatabaseManager, table: str):
        self.db = db
        self._table = table
        self._params = {}
        self._data = None
        self._method = 'GET'

    def select(self, columns: str = '*', count: str = None):
        self._params['select'] = columns
        self._method = 'GET'
        return self

    def eq(self, column: str, value):
        self._params[column] = f'eq.{value}'
        return self

    def order(self, column: str, desc: bool = False):
        direction = 'desc' if desc else 'asc'
        self._params['order'] = f'{column}.{direction}'
        return self

    def insert(self, data: dict):
        self._data = data
        self._method = 'POST'
        return self

    def update(self, data: dict):
        self._data = data
        self._method = 'PATCH'
        return self

    def delete(self):
        self._method = 'DELETE'
        return self

    def execute(self):
        """Exécute la requête."""
        result = self.db._api_request(
            self._method,
            self._table,
            params=self._params if self._params else None,
            data=self._data
        )

        # Normaliser le résultat
        if isinstance(result, list):
            return Result(result)
        elif isinstance(result, dict):
            return Result([result])
        else:
            return Result([])


class Result:
    """Résultat d'une requête."""

    def __init__(self, data: list):
        self.data = data if data else []
