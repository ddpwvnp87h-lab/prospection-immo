from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import time
import os
import re
import random
import requests
from config import SCRAPING_DELAY, USER_AGENT
from .site_config import get_profile, RateLimiter, SiteManager, SiteProfile
from .headers.factory import HeaderFactory
from .timing import HumanTimer, get_timer
from .http_client import StealthSession, create_session, is_stealth_available


class BaseScraper(ABC):
    """
    Classe de base pour tous les scrapers de sites immobiliers.

    Intègre:
    - Headers de navigateur réalistes (Chrome/Firefox)
    - Timing humain (délais variables)
    - TLS fingerprint spoofing (via curl_cffi si disponible)
    - Gestion 403/429 avec backoff intelligent
    - Validation de localisation avec confidence scoring
    """

    def __init__(self):
        """Initialise le scraper avec tous les modules anti-blocage."""
        self.delay = int(os.getenv('SCRAPING_DELAY', SCRAPING_DELAY))
        self.user_agent = os.getenv('USER_AGENT', USER_AGENT)
        self._geo_cache = {}

        # Charger le profil du site
        self._profile: SiteProfile = get_profile(self.site_key)
        self._rate_limiter = RateLimiter(self._profile)

        # Nouveaux modules anti-blocage
        self._headers_factory = HeaderFactory(rotate=True)
        self._timer = get_timer(self.site_key)
        self._stealth_session: Optional[StealthSession] = None
        self._current_url: Optional[str] = None

        # Stats de session
        self._session_requests = 0
        self._session_errors = 0

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

    def _create_stealth_session(self) -> StealthSession:
        """
        Crée une session HTTP furtive avec:
        - Headers Chrome/Firefox complets
        - TLS fingerprint spoofing
        - Cookie persistence
        """
        if self._stealth_session is None:
            self._stealth_session = create_session(self.site_key)
        return self._stealth_session

    def _create_session_with_headers(self) -> requests.Session:
        """
        Crée une session requests standard avec headers complets.
        Fallback si StealthSession non utilisée.
        """
        session = requests.Session()

        # Obtenir les headers complets du factory
        base_url = self._get_base_url()
        headers = self._headers_factory.get_initial_headers(base_url)

        session.headers.update(headers)
        return session

    def _get_base_url(self) -> str:
        """Retourne l'URL de base du site."""
        base_urls = {
            'pap': 'https://www.pap.fr/',
            'leboncoin': 'https://www.leboncoin.fr/',
            'paruvendu': 'https://www.paruvendu.fr/',
            'entreparticuliers': 'https://www.entreparticuliers.com/',
            'figaro': 'https://immobilier.lefigaro.fr/',
            'moteurimmo': 'https://www.moteurimmo.fr/',
        }
        return base_urls.get(self.site_key, 'https://www.google.fr/')

    def _warm_session(self, session: requests.Session) -> bool:
        """
        Réchauffe la session en visitant la page d'accueil.
        Récupère les cookies et établit un historique naturel.
        """
        try:
            base_url = self._get_base_url()
            print(f"  🔥 Warm-up: {base_url}")

            # Attente humaine avant la première requête
            time.sleep(random.uniform(1, 3))

            response = session.get(base_url, timeout=20)

            if response.status_code == 200:
                self._current_url = base_url
                print(f"  ✅ Session prête ({len(session.cookies)} cookies)")
                # Pause naturelle après chargement
                time.sleep(random.uniform(2, 5))
                return True
            else:
                print(f"  ⚠️ Warm-up status: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ Warm-up failed: {e}")
            return False

    def _human_wait(self):
        """Attend avec un pattern humain (remplace _wait pour plus de réalisme)."""
        self._timer.wait_before_request()

    def _wait(self):
        """Attend entre les requêtes avec rate limiting et jitter."""
        # Utiliser le timing humain plutôt que le rate limiter basique
        self._timer.wait_before_request()

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
            elif response.status_code == 403:
                # 403 Forbidden = probablement bloqué, backoff agressif
                print(f"    🚫 Bloqué (403) sur {url[:50]}...")
                self._record_failure(403)
                # Pause longue pour 403 (60-180s)
                import random
                pause = random.uniform(60, 180)
                print(f"    ⏳ Pause anti-blocage {pause:.0f}s...")
                import time
                time.sleep(pause)

                if self._should_stop():
                    print(f"    🛑 Circuit breaker activé, arrêt du scraping")
                    return None
                return None
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
                self._record_failure(response.status_code)
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

    def _extract_location_with_confidence(
        self,
        text: str,
        fallback_location: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Extrait la localisation avec score de confiance.

        Args:
            text: Texte contenant potentiellement la localisation
            fallback_location: Localisation de recherche (fallback)

        Returns:
            Tuple (localisation, confidence, source)
            - confidence: 'high', 'medium', 'low', 'inferred'
            - source: description de la méthode d'extraction
        """
        # Pattern 1: "Ville (12345)" ou "Paris 17E (75017)" → HIGH confidence
        loc_match = re.search(r'([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9\s\-\']+)\s*\((\d{5})\)', text)
        if loc_match:
            ville = loc_match.group(1).strip()
            cp = loc_match.group(2)
            return f"{ville} ({cp})", 'high', 'pattern_ville_cp'

        # Pattern 2: "12345 Ville" → HIGH confidence
        cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-\']+)', text)
        if cp_match:
            return f"{cp_match.group(2).strip()} ({cp_match.group(1)})", 'high', 'pattern_cp_ville'

        # Pattern 3: Code postal seul → MEDIUM confidence
        cp_only = re.search(r'\b(\d{5})\b', text)
        if cp_only:
            cp = cp_only.group(1)
            # Essayer de géocoder pour avoir le nom de ville
            try:
                from utils.geolocation import geo
                geo_info = geo.search(cp)
                if geo_info and geo_info.get('nom'):
                    return f"{geo_info['nom']} ({cp})", 'medium', 'geocoded_cp'
            except Exception:
                pass
            return f"Code postal {cp}", 'medium', 'cp_only'

        # Pattern 4: Nom de ville connu dans le texte → MEDIUM confidence
        fallback_ville = fallback_location.get('ville', '')
        if fallback_ville and len(fallback_ville) > 2:
            # Chercher le nom de ville (insensible à la casse)
            ville_pattern = re.escape(fallback_ville)
            if re.search(ville_pattern, text, re.I):
                cp = fallback_location.get('code_postal')
                if cp:
                    return f"{fallback_ville} ({cp})", 'medium', 'ville_in_text'
                else:
                    return fallback_ville, 'low', 'ville_in_text_no_cp'

        # FALLBACK: utiliser la localisation de recherche → INFERRED (pas fiable)
        # Ceci indique que l'extraction a échoué
        fallback_cp = fallback_location.get('code_postal')
        if fallback_cp:
            return f"{fallback_location.get('ville', 'Inconnu')} ({fallback_cp})", 'inferred', 'fallback'
        else:
            return fallback_location.get('ville', 'Localisation inconnue'), 'inferred', 'fallback_no_cp'

    def _should_reject_listing(self, listing: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Vérifie si une annonce doit être rejetée selon les critères de qualité.

        Args:
            listing: Données de l'annonce

        Returns:
            Tuple (should_reject, reason)
        """
        # Vérifier confidence de localisation si strict_location activé
        if self._profile.strict_location:
            confidence = listing.get('_geo_confidence', 'unknown')
            if confidence == 'inferred':
                return True, 'inferred_location'

        # Vérifier correspondance département (crucial pour DOM-TOM)
        expected_dept = listing.get('_expected_dept')
        extracted_cp = listing.get('_geo_cp')
        if expected_dept and extracted_cp:
            # Extraire le département du code postal
            # DOM-TOM: 97X (971=Guadeloupe, 972=Martinique, 973=Guyane, 974=Réunion, 976=Mayotte)
            # Métropole: 2 premiers chiffres (sauf Corse: 2A/2B → 20)
            if extracted_cp.startswith('97'):
                extracted_dept = extracted_cp[:3]  # 971, 972, 973, 974, 976
            else:
                extracted_dept = extracted_cp[:2]  # 75, 13, 69, etc.

            if extracted_dept != expected_dept:
                return True, f'wrong_department:{extracted_dept}!={expected_dept}'

        # Vérifier prix (doit être > 0)
        prix = listing.get('prix', 0)
        if not prix or prix <= 0:
            return True, 'no_price'

        # Vérifier lien
        lien = listing.get('lien', '')
        if not lien or len(lien) < 10:
            return True, 'no_link'

        return False, ''

    def _enrich_listing(
        self,
        listing: Dict[str, Any],
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrichit une annonce avec des métadonnées de qualité.

        Args:
            listing: Données brutes de l'annonce
            location: Informations de localisation de recherche

        Returns:
            Annonce enrichie
        """
        # Ajouter métadonnées de scraping
        listing['_scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        listing['_scraper'] = self.site_key

        # Stocker le département attendu (depuis la recherche)
        search_cp = location.get('code_postal', '')
        if search_cp:
            # DOM-TOM: 97X (971=Guadeloupe, 972=Martinique, 973=Guyane, 974=Réunion, 976=Mayotte)
            if search_cp.startswith('97'):
                listing['_expected_dept'] = search_cp[:3]
            else:
                listing['_expected_dept'] = search_cp[:2]

        # Si localisation présente, analyser la confidence
        if 'localisation' in listing and listing['localisation']:
            loc_text = listing['localisation']

            # Extraire CP si présent
            cp_match = re.search(r'\b(\d{5})\b', loc_text)
            if cp_match:
                listing['_geo_confidence'] = 'high'
                listing['_geo_cp'] = cp_match.group(1)
            else:
                # Vérifier si c'est un fallback
                fallback_ville = location.get('ville', '')
                if fallback_ville.lower() in loc_text.lower():
                    listing['_geo_confidence'] = 'medium'
                else:
                    listing['_geo_confidence'] = 'inferred'

        return listing
