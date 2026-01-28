from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import os
from supabase import create_client, Client


class DatabaseManager:
    """Gestionnaire de base de données Supabase pour les annonces immobilières."""

    def __init__(self):
        """Initialise la connexion Supabase."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            print("⚠️ SUPABASE_URL et SUPABASE_KEY non définis - mode démo")
            self.client = None
        else:
            try:
                self.client: Client = create_client(supabase_url, supabase_key)
                print("✅ Connexion Supabase établie")
            except Exception as e:
                print(f"⚠️ Erreur connexion Supabase: {e} - mode démo")
                self.client = None

    def insert_listings(self, user_id: str, listings: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Insère de nouvelles annonces en base avec déduplication.

        Args:
            user_id: ID de l'utilisateur
            listings: Liste des annonces à insérer

        Returns:
            Dict avec le nombre d'annonces ajoutées et dupliquées
        """
        if not listings:
            return {"added": 0, "duplicates": 0}

        if not self.client:
            print("⚠️ Mode démo: pas de connexion Supabase")
            return {"added": 0, "duplicates": 0, "demo": True}

        added = 0
        duplicates = 0

        for listing in listings:
            try:
                # Générer hash pour déduplication
                listing_hash = self._generate_hash(listing)

                # Vérifier si l'annonce existe déjà (par URL)
                existing = self.client.table('listings')\
                    .select('id')\
                    .eq('user_id', user_id)\
                    .eq('url', listing['lien'])\
                    .execute()

                if existing.data:
                    # Annonce existe déjà, mettre à jour last_seen_at
                    self.client.table('listings')\
                        .update({'last_seen_at': datetime.now().isoformat()})\
                        .eq('id', existing.data[0]['id'])\
                        .execute()
                    duplicates += 1
                else:
                    # Nouvelle annonce, insérer
                    self.client.table('listings').insert({
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
                    }).execute()
                    added += 1

            except Exception as e:
                print(f"⚠️  Erreur insertion annonce {listing.get('lien', 'N/A')}: {e}")
                continue

        print(f"✅ {added} annonces ajoutées, {duplicates} doublons ignorés")
        return {"added": added, "duplicates": duplicates}

    def update_listing_status(self, listing_id: str, user_id: str, status: str) -> bool:
        """
        Met à jour le statut d'une annonce.

        Args:
            listing_id: ID de l'annonce
            user_id: ID de l'utilisateur (sécurité)
            status: Nouveau statut

        Returns:
            True si mis à jour, False sinon
        """
        if not self.client:
            print("⚠️ Mode démo: pas de connexion Supabase")
            return False

        try:
            self.client.table('listings').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', listing_id).eq('user_id', user_id).execute()

            print(f"✅ Annonce {listing_id} mise à jour: {status}")
            return True
        except Exception as e:
            print(f"⚠️  Erreur mise à jour annonce {listing_id}: {e}")
            return False

    def delete_listing(self, listing_id: str, user_id: str) -> bool:
        """
        Supprime une annonce.

        Args:
            listing_id: ID de l'annonce
            user_id: ID de l'utilisateur (sécurité)

        Returns:
            True si supprimée, False sinon
        """
        if not self.client:
            print("⚠️ Mode démo: pas de connexion Supabase")
            return False

        try:
            self.client.table('listings')\
                .delete()\
                .eq('id', listing_id)\
                .eq('user_id', user_id)\
                .execute()

            print(f"✅ Annonce {listing_id} supprimée")
            return True
        except Exception as e:
            print(f"⚠️  Erreur suppression annonce {listing_id}: {e}")
            return False

    def cleanup(self, user_id: str) -> int:
        """
        Nettoyage automatique:
        1. Supprime les annonces avec statut "Pas intéressé"
        2. Supprime les annonces de plus de 90 jours

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Nombre total d'annonces supprimées
        """
        if not self.client:
            print("⚠️ Mode démo: pas de connexion Supabase")
            return 0

        deleted_count = 0

        try:
            # 1. Supprimer les "Pas intéressé"
            result1 = self.client.table('listings')\
                .delete()\
                .eq('user_id', user_id)\
                .eq('status', 'Pas intéressé')\
                .execute()
            deleted_count += len(result1.data) if result1.data else 0

            # 2. Supprimer les annonces de plus de 90 jours
            cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
            result2 = self.client.table('listings')\
                .delete()\
                .eq('user_id', user_id)\
                .lt('created_at', cutoff_date)\
                .execute()
            deleted_count += len(result2.data) if result2.data else 0

            print(f"🧹 {deleted_count} annonces supprimées lors du nettoyage")
            return deleted_count

        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage: {e}")
            return deleted_count

    def get_listings(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les annonces d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            status: Filtrer par statut (optionnel)

        Returns:
            Liste des annonces
        """
        if not self.client:
            print("⚠️ Mode démo: pas de connexion Supabase")
            return []

        try:
            query = self.client.table('listings').select('*').eq('user_id', user_id)

            if status:
                query = query.eq('status', status)

            result = query.order('created_at', desc=True).execute()
            return result.data if result.data else []

        except Exception as e:
            print(f"⚠️  Erreur récupération annonces: {e}")
            return []

    def _generate_hash(self, listing: Dict[str, Any]) -> str:
        """
        Génère un hash unique basé sur titre + prix + localisation.

        Args:
            listing: Données de l'annonce

        Returns:
            Hash MD5
        """
        signature = f"{listing['titre']}_{listing['prix']}_{listing['localisation']}"
        return hashlib.md5(signature.encode()).hexdigest()
