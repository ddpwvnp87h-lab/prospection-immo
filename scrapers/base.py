from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import os
import re
import requests
from config import SCRAPING_DELAY, USER_AGENT
from .site_config import get_profile, RateLimiter, SiteManager, SiteProfile


class BaseScraper(ABC):
    """Classe de base pour tous les scrapers de sites immobiliers."""

    def __init__(self):
        """Initialise le scraper."""
        self.delay = int(os.getenv('SCRAPING_DELAY', SCRAPING_DELAY))
        self.user_agent = os.getenv('USER_AGENT', USER_AGENT)
        self._geo_cache = {}

        # Charger le profil du site
        self._profile: SiteProfile = get_profile(self.site_key)
        self._rate_limiter = RateLimiter(self._profile)

    @property
    @abstractmethod
    def site_key(self) -> str:
        """Clé unique du site (pour la config)."""
        pass

    def is_available(self) -> bool:
        """Vérifie si le site est disponible (pas désactivé)."""
        return SiteManager.is_site_available(self.site_key)

    def get_max_pages(self) -> int:
        """Retourne le nombre max de pages selon le profil."""
        return self._profile.max_pages

    def should_use_strict_location(self) -> bool:
        """Vérifie si la validation stricte de localisation est activée."""
        return self._profile.strict_location

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
        """Attend entre les requêtes avec rate limiting et jitter."""
        self._rate_limiter.wait()

    def _record_success(self):
        """Enregistre une requête réussie (reset backoff)."""
        self._rate_limiter.record_success()

    def _record_failure(self, status_code: int = None):
        """Enregistre un échec et applique le backoff."""
        self._rate_limiter.record_failure(status_code)

    def _should_stop(self) -> bool:
        """Vérifie si le circuit breaker est ouvert."""
        return self._rate_limiter.should_stop()

    def _make_request(self, session: requests.Session, url: str, timeout: int = 15) -> Optional[requests.Response]:
        """
        Effectue une requête HTTP avec gestion des erreurs et backoff.

        Returns:
            Response si succès, None si échec
        """
        try:
            self._wait()
            response = session.get(url, timeout=timeout)

            if response.status_code == 200:
                self._record_success()
                return response
            elif response.status_code in [429, 500, 502, 503, 504]:
                print(f"    ⚠️ Erreur {response.status_code} sur {url[:50]}...")
                self._record_failure(response.status_code)

                # Vérifier si on doit arrêter
                if self._should_stop():
                    print(f"    🛑 Circuit breaker activé, arrêt du scraping")
                    return None

                return None
            else:
                print(f"    ⚠️ Status {response.status_code}")
                return None

        except requests.Timeout:
            print(f"    ⏱️ Timeout sur {url[:50]}...")
            self._record_failure(504)
            return None
        except requests.RequestException as e:
            print(f"    ❌ Erreur requête: {str(e)[:50]}")
            self._record_failure(500)
            return None

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
