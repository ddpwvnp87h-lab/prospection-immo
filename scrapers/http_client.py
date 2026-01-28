"""
Client HTTP furtif avec TLS fingerprint spoofing.
Utilise curl_cffi si disponible, sinon requests standard.
"""

import random
from typing import Dict, Optional, Any
from urllib.parse import urlparse

# Tenter d'importer curl_cffi pour TLS spoofing
try:
    from curl_cffi import requests as curl_requests
    from curl_cffi.requests import Session as CurlSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    import requests as curl_requests
    from requests import Session as CurlSession

# Import standard requests pour fallback
import requests
from requests import Session

from .headers.factory import HeaderFactory


# Fingerprints disponibles avec curl_cffi
IMPERSONATE_OPTIONS = [
    "chrome120",
    "chrome119",
    "chrome110",
    "firefox121",
    "firefox120",
    "safari17_2_ios",
]


class StealthSession:
    """
    Session HTTP furtive avec:
    - TLS fingerprint réaliste (via curl_cffi)
    - Headers de navigateur complets
    - Rotation de profil optionnelle

    Usage:
        session = StealthSession(site_key='leboncoin')
        response = session.get('https://www.leboncoin.fr/')
    """

    def __init__(
        self,
        site_key: str = 'default',
        rotate_fingerprint: bool = True,
        rotate_headers: bool = True
    ):
        """
        Args:
            site_key: Clé du site pour configuration
            rotate_fingerprint: Rotation de fingerprint TLS
            rotate_headers: Rotation de profil headers
        """
        self.site_key = site_key
        self.rotate_fingerprint = rotate_fingerprint
        self.rotate_headers = rotate_headers

        self._impersonate = random.choice(IMPERSONATE_OPTIONS) if rotate_fingerprint else "chrome120"
        self._headers_factory = HeaderFactory(rotate=rotate_headers)
        self._current_url = None
        self._cookies = {}

        # Créer la session sous-jacente
        if CURL_CFFI_AVAILABLE:
            self._session = CurlSession(impersonate=self._impersonate)
            self._mode = 'curl_cffi'
        else:
            self._session = Session()
            self._mode = 'requests'

        # Log du mode
        if CURL_CFFI_AVAILABLE:
            print(f"  🔒 Mode furtif: curl_cffi ({self._impersonate})")
        else:
            print(f"  ⚠️ Mode standard: requests (TLS détectable)")

    def get(
        self,
        url: str,
        headers: Dict[str, str] = None,
        timeout: int = 15,
        **kwargs
    ) -> requests.Response:
        """
        GET avec fingerprint furtif.

        Args:
            url: URL cible
            headers: Headers personnalisés (sinon auto-générés)
            timeout: Timeout en secondes
            **kwargs: Arguments supplémentaires

        Returns:
            Response object
        """
        # Générer headers si non fournis
        if headers is None:
            if self._current_url is None:
                headers = self._headers_factory.get_initial_headers(url)
            else:
                headers = self._headers_factory.get_navigation_headers(self._current_url, url)

        self._current_url = url

        # Rotation de fingerprint optionnelle
        if self.rotate_fingerprint and CURL_CFFI_AVAILABLE:
            if random.random() < 0.1:  # 10% de chance de rotation
                self._impersonate = random.choice(IMPERSONATE_OPTIONS)
                self._session = CurlSession(impersonate=self._impersonate)

        if CURL_CFFI_AVAILABLE:
            return self._session.get(
                url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
        else:
            return self._session.get(
                url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )

    def post(
        self,
        url: str,
        headers: Dict[str, str] = None,
        json: Any = None,
        data: Any = None,
        timeout: int = 15,
        **kwargs
    ) -> requests.Response:
        """
        POST avec fingerprint furtif.
        """
        # Headers pour API
        if headers is None:
            headers = self._headers_factory.get_api_headers(url)

        self._current_url = url

        if CURL_CFFI_AVAILABLE:
            return self._session.post(
                url,
                headers=headers,
                json=json,
                data=data,
                timeout=timeout,
                **kwargs
            )
        else:
            return self._session.post(
                url,
                headers=headers,
                json=json,
                data=data,
                timeout=timeout,
                **kwargs
            )

    def warm_up(self, base_url: str) -> bool:
        """
        Réchauffe la session en visitant la page d'accueil.
        Permet de récupérer cookies et paraître plus naturel.

        Args:
            base_url: URL de base du site

        Returns:
            True si succès
        """
        try:
            print(f"  🔥 Warm-up session: {base_url}")

            # Visite page d'accueil
            headers = self._headers_factory.get_initial_headers(base_url)
            response = self.get(base_url, headers=headers, timeout=20)

            if response.status_code == 200:
                self._current_url = base_url
                print(f"  ✅ Session prête")
                return True
            else:
                print(f"  ⚠️ Warm-up status: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ Warm-up failed: {e}")
            return False

    def get_mode(self) -> str:
        """Retourne le mode actuel (curl_cffi ou requests)."""
        return self._mode

    def get_fingerprint(self) -> str:
        """Retourne le fingerprint TLS actuel."""
        if CURL_CFFI_AVAILABLE:
            return self._impersonate
        else:
            return "python-requests (detectable)"

    def rotate(self):
        """Force une rotation de fingerprint et headers."""
        if CURL_CFFI_AVAILABLE:
            self._impersonate = random.choice(IMPERSONATE_OPTIONS)
            self._session = CurlSession(impersonate=self._impersonate)
        self._headers_factory.rotate_profile()
        self._current_url = None

    def close(self):
        """Ferme la session."""
        if hasattr(self._session, 'close'):
            self._session.close()


def create_session(site_key: str = 'default') -> StealthSession:
    """
    Helper pour créer une session furtive.

    Args:
        site_key: Clé du site

    Returns:
        StealthSession configurée
    """
    return StealthSession(site_key=site_key)


def is_stealth_available() -> bool:
    """Vérifie si le mode furtif (curl_cffi) est disponible."""
    return CURL_CFFI_AVAILABLE
