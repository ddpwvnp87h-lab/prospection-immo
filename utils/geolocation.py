"""
Utilitaire de géolocalisation pour la recherche immobilière.
Utilise l'API gouvernementale geo.api.gouv.fr (gratuite, fiable).
"""
import requests
from typing import Optional, Dict, List, Tuple
import re


class GeoLocation:
    """Gère la géolocalisation des villes françaises."""

    API_BASE = "https://geo.api.gouv.fr"

    def __init__(self):
        self.cache = {}  # Cache des recherches

    def search(self, query: str) -> Optional[Dict]:
        """
        Recherche une localisation (ville ou code postal).

        Args:
            query: Nom de ville ou code postal (ex: "Paris", "75001", "Lyon 3")

        Returns:
            Dict avec: nom, code_postal, code_insee, departement, lat, lon
        """
        query = query.strip()

        # Vérifier le cache
        if query in self.cache:
            return self.cache[query]

        result = None

        # Détecter si c'est un code postal
        if re.match(r'^\d{5}$', query):
            result = self._search_by_postal_code(query)
        else:
            result = self._search_by_name(query)

        if result:
            self.cache[query] = result

        return result

    def _search_by_postal_code(self, code_postal: str) -> Optional[Dict]:
        """Recherche par code postal."""
        try:
            url = f"{self.API_BASE}/communes"
            params = {
                'codePostal': code_postal,
                'fields': 'nom,code,codesPostaux,centre,codeDepartement,population',
                'limit': 1
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    commune = data[0]
                    return self._format_result(commune, code_postal)

        except Exception as e:
            print(f"⚠️ Erreur géocodage CP {code_postal}: {e}")

        return None

    def _search_by_name(self, nom: str) -> Optional[Dict]:
        """Recherche par nom de ville."""
        try:
            # Nettoyer le nom
            nom_clean = re.sub(r'\s*\d+e?r?\s*$', '', nom)  # Enlever arrondissement
            nom_clean = nom_clean.strip()

            url = f"{self.API_BASE}/communes"
            params = {
                'nom': nom_clean,
                'fields': 'nom,code,codesPostaux,centre,codeDepartement,population',
                'boost': 'population',  # Favoriser les grandes villes
                'limit': 5
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    # Trouver la meilleure correspondance
                    for commune in data:
                        if commune['nom'].lower() == nom_clean.lower():
                            return self._format_result(commune)

                    # Sinon prendre la plus peuplée
                    return self._format_result(data[0])

        except Exception as e:
            print(f"⚠️ Erreur géocodage {nom}: {e}")

        return None

    def _format_result(self, commune: dict, code_postal: str = None) -> Dict:
        """Formate le résultat."""
        codes_postaux = commune.get('codesPostaux', [])
        cp = code_postal or (codes_postaux[0] if codes_postaux else None)

        centre = commune.get('centre', {}).get('coordinates', [None, None])

        return {
            'nom': commune.get('nom'),
            'code_postal': cp,
            'code_insee': commune.get('code'),
            'departement': commune.get('codeDepartement'),
            'lat': centre[1] if len(centre) > 1 else None,
            'lon': centre[0] if len(centre) > 0 else None,
            'tous_codes_postaux': codes_postaux
        }

    def get_nearby_cities(self, lat: float, lon: float, rayon_km: int = 10) -> List[Dict]:
        """
        Trouve les villes dans un rayon donné.

        Args:
            lat: Latitude
            lon: Longitude
            rayon_km: Rayon en kilomètres

        Returns:
            Liste de communes proches
        """
        try:
            # Convertir km en mètres
            rayon_m = rayon_km * 1000

            url = f"{self.API_BASE}/communes"
            params = {
                'lat': lat,
                'lon': lon,
                'fields': 'nom,code,codesPostaux,centre,codeDepartement',
                'limit': 50
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            print(f"⚠️ Erreur recherche proximité: {e}")

        return []

    def get_departement_cities(self, departement: str) -> List[str]:
        """Récupère toutes les villes d'un département."""
        try:
            url = f"{self.API_BASE}/departements/{departement}/communes"
            params = {'fields': 'nom,codesPostaux'}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return [c['nom'] for c in data]

        except Exception as e:
            print(f"⚠️ Erreur département {departement}: {e}")

        return []


# Instance globale
geo = GeoLocation()


def get_location_info(query: str) -> Optional[Dict]:
    """Fonction helper pour obtenir les infos de localisation."""
    return geo.search(query)


def format_location_for_scraper(query: str) -> Dict:
    """
    Prépare les données de localisation pour les scrapers.

    Returns:
        Dict avec: ville, code_postal, lat, lon, slug, search_terms
    """
    info = geo.search(query)

    if info:
        ville = info['nom']
        cp = info['code_postal']

        # Créer différents formats pour les recherches
        slug = ville.lower().replace(' ', '-').replace("'", "-")

        return {
            'ville': ville,
            'code_postal': cp,
            'departement': info['departement'],
            'lat': info['lat'],
            'lon': info['lon'],
            'slug': slug,
            'search_terms': [
                ville,
                cp,
                f"{ville} {cp}",
                f"{cp} {ville}"
            ]
        }

    # Fallback si pas trouvé
    slug = query.lower().replace(' ', '-').replace("'", "-")
    return {
        'ville': query,
        'code_postal': None,
        'departement': None,
        'lat': None,
        'lon': None,
        'slug': slug,
        'search_terms': [query]
    }
