from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import os
import re
from config import SCRAPING_DELAY, USER_AGENT


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers de sites immobiliers."""

    def __init__(self):
        """Initialise le scraper."""
        self.delay = int(os.getenv('SCRAPING_DELAY', SCRAPING_DELAY))
        self.user_agent = os.getenv('USER_AGENT', USER_AGENT)
        self._geo_cache = {}

    @abstractmethod
    def scrape(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """
        Scrape les annonces immobilières.

        Args:
            ville: Ville de recherche (nom ou code postal)
            rayon: Rayon de recherche en km
            max_pages: Nombre maximum de pages à scraper

        Returns:
            Liste d'annonces au format standardisé
        """
        pass

    @property
    @abstractmethod
    def site_name(self) -> str:
        """Nom du site scraped."""
        pass

    def get_location_info(self, query: str) -> Dict:
        """
        Obtient les informations de géolocalisation.

        Args:
            query: Nom de ville ou code postal

        Returns:
            Dict avec: ville, code_postal, departement, lat, lon, slug
        """
        if query in self._geo_cache:
            return self._geo_cache[query]

        try:
            from utils.geolocation import format_location_for_scraper
            result = format_location_for_scraper(query)
            self._geo_cache[query] = result
            return result
        except ImportError:
            # Fallback si le module n'est pas disponible
            return self._basic_location_info(query)

    def _basic_location_info(self, query: str) -> Dict:
        """Fallback basique pour la localisation."""
        query = query.strip()

        # Détecter code postal
        cp_match = re.match(r'^(\d{5})$', query)
        if cp_match:
            code_postal = cp_match.group(1)
            departement = code_postal[:2]
            return {
                'ville': query,
                'code_postal': code_postal,
                'departement': departement,
                'lat': None,
                'lon': None,
                'slug': query,
                'search_terms': [query]
            }

        # Nom de ville
        slug = self._slugify(query)
        return {
            'ville': query,
            'code_postal': None,
            'departement': None,
            'lat': None,
            'lon': None,
            'slug': slug,
            'search_terms': [query]
        }

    def _slugify(self, text: str) -> str:
        """Convertit un texte en slug URL."""
        text = text.lower()
        # Remplacer les accents
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ô': 'o', 'ö': 'o',
            'î': 'i', 'ï': 'i',
            'ç': 'c',
            "'": '-', ' ': '-'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Nettoyer les tirets multiples
        text = re.sub(r'-+', '-', text)
        text = text.strip('-')
        return text

    def _wait(self):
        """Attend entre les requêtes pour respecter les serveurs."""
        time.sleep(self.delay)

    def _normalize_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise les données d'une annonce au format standardisé.

        Format standardisé:
        {
            "titre": str,
            "date_publication": str,  # ISO format YYYY-MM-DD
            "prix": int,
            "localisation": str,
            "lien": str,
            "site_source": str,
            "photos": List[str],  # URLs
            "telephone": Optional[str],
            "surface": Optional[int],
            "pieces": Optional[int],
            "description": Optional[str]
        }
        """
        return raw_data

    def _print_stats(self, listings: List[Dict[str, Any]]):
        """Affiche les statistiques de scraping."""
        print(f"✅ {len(listings)} annonces trouvées sur {self.site_name}")

    def _parse_price(self, text: str) -> int:
        """Parse un prix depuis du texte."""
        try:
            return int(re.sub(r'[^\d]', '', str(text)))
        except:
            return 0

    def _extract_surface_pieces(self, text: str) -> tuple:
        """Extrait surface et nombre de pièces du texte."""
        surface = None
        pieces = None

        surface_match = re.search(r'(\d+)\s*m[²2]', text, re.I)
        if surface_match:
            surface = int(surface_match.group(1))

        pieces_match = re.search(r'(\d+)\s*pièces?|[TF](\d+)', text, re.I)
        if pieces_match:
            pieces = int(pieces_match.group(1) or pieces_match.group(2))

        return surface, pieces
