"""
Factory pour générer des headers de navigateur réalistes.
"""

import random
from typing import Dict, Optional
from urllib.parse import urlparse
from .profiles import BROWSER_PROFILES, CHROME_120_MACOS, REFERERS


class HeaderFactory:
    """
    Génère des headers de navigateur réalistes.

    Usage:
        factory = HeaderFactory(rotate=True)
        headers = factory.get_initial_headers('https://www.pap.fr/')
        # ... première requête
        headers = factory.get_navigation_headers(current_url, next_url)
        # ... requêtes suivantes
    """

    def __init__(self, rotate: bool = True, profile: dict = None):
        """
        Args:
            rotate: Si True, change de profil aléatoirement
            profile: Profil spécifique à utiliser (sinon aléatoire)
        """
        self.rotate = rotate
        self._current_profile = profile or random.choice(BROWSER_PROFILES)
        self._current_url = None
        self._request_count = 0

    def get_initial_headers(self, target_url: str, referer: str = None) -> Dict[str, str]:
        """
        Headers pour la première requête (arrivée depuis Google).

        Args:
            target_url: URL cible
            referer: Referer personnalisé (sinon Google)

        Returns:
            Dict de headers complets
        """
        if self.rotate:
            self._current_profile = random.choice(BROWSER_PROFILES)

        headers = dict(self._current_profile['base'])

        # Referer depuis Google
        if referer:
            headers['Referer'] = referer
        else:
            domain = urlparse(target_url).netloc
            site_referers = REFERERS.get(domain, REFERERS['default'])
            headers['Referer'] = random.choice(site_referers)

        # Sec-Fetch-Site = cross-site (vient de Google)
        if 'cross_site' in self._current_profile:
            headers.update(self._current_profile['cross_site'])
        else:
            headers['Sec-Fetch-Site'] = 'cross-site'

        self._current_url = target_url
        self._request_count = 1

        return headers

    def get_navigation_headers(self, current_url: str, target_url: str) -> Dict[str, str]:
        """
        Headers pour navigation interne (page 2, 3, etc.)

        Args:
            current_url: URL actuelle (devient le Referer)
            target_url: URL cible

        Returns:
            Dict de headers
        """
        headers = dict(self._current_profile['base'])

        # Referer = page précédente
        headers['Referer'] = current_url

        # Mettre à jour Sec-Fetch-Site pour same-origin
        current_domain = urlparse(current_url).netloc
        target_domain = urlparse(target_url).netloc

        if current_domain == target_domain:
            if 'same_origin' in self._current_profile:
                headers.update(self._current_profile['same_origin'])
            else:
                headers['Sec-Fetch-Site'] = 'same-origin'
        else:
            headers['Sec-Fetch-Site'] = 'cross-site'

        self._current_url = target_url
        self._request_count += 1

        return headers

    def get_api_headers(self, target_url: str, origin: str = None) -> Dict[str, str]:
        """
        Headers pour appels API (XHR/fetch).

        Args:
            target_url: URL de l'API
            origin: Origin header (auto-détecté si None)

        Returns:
            Dict de headers pour API
        """
        headers = dict(self._current_profile['base'])

        # Modifier pour ressembler à un appel fetch()
        headers['Accept'] = 'application/json, text/plain, */*'
        headers['Sec-Fetch-Dest'] = 'empty'
        headers['Sec-Fetch-Mode'] = 'cors'
        headers['Sec-Fetch-Site'] = 'same-origin'

        # Origin header pour CORS
        if origin:
            headers['Origin'] = origin
        else:
            parsed = urlparse(target_url)
            headers['Origin'] = f"{parsed.scheme}://{parsed.netloc}"

        # Referer
        if self._current_url:
            headers['Referer'] = self._current_url
        else:
            headers['Referer'] = headers['Origin'] + '/'

        # Retirer les headers de navigation pure
        headers.pop('Upgrade-Insecure-Requests', None)
        headers.pop('Sec-Fetch-User', None)
        headers.pop('Cache-Control', None)

        return headers

    def get_current_profile_name(self) -> str:
        """Retourne le nom du profil actuel."""
        return self._current_profile.get('name', 'Unknown')

    def rotate_profile(self):
        """Force une rotation de profil."""
        self._current_profile = random.choice(BROWSER_PROFILES)
        self._request_count = 0


def get_headers_for_site(site_key: str) -> Dict[str, str]:
    """
    Helper pour obtenir des headers adaptés à un site.

    Args:
        site_key: Clé du site (pap, leboncoin, etc.)

    Returns:
        Dict de headers
    """
    factory = HeaderFactory(rotate=True)

    site_urls = {
        'pap': 'https://www.pap.fr/',
        'leboncoin': 'https://www.leboncoin.fr/',
        'paruvendu': 'https://www.paruvendu.fr/',
        'entreparticuliers': 'https://www.entreparticuliers.com/',
        'figaro': 'https://immobilier.lefigaro.fr/',
        'moteurimmo': 'https://www.moteurimmo.fr/',
    }

    url = site_urls.get(site_key, 'https://www.google.fr/')
    return factory.get_initial_headers(url)
