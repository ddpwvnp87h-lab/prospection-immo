from abc import ABC, abstractmethod
from typing import List, Dict, Any
import time
import os
from config import SCRAPING_DELAY, USER_AGENT


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers de sites immobiliers."""

    def __init__(self):
        """Initialise le scraper."""
        self.delay = int(os.getenv('SCRAPING_DELAY', SCRAPING_DELAY))
        self.user_agent = os.getenv('USER_AGENT', USER_AGENT)

    @abstractmethod
    def scrape(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """
        Scrape les annonces immobilières.

        Args:
            ville: Ville de recherche
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

        Args:
            raw_data: Données brutes du site

        Returns:
            Données normalisées
        """
        # À implémenter dans chaque scraper spécifique
        return raw_data

    def _print_stats(self, listings: List[Dict[str, Any]]):
        """Affiche les statistiques de scraping."""
        print(f"✅ {len(listings)} annonces trouvées sur {self.site_name}")
