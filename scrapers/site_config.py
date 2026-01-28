"""
Configuration des profils de scraping par site.
Basé sur strat-scraping-anti-blocage-v3-sites.md
"""

from dataclasses import dataclass
from typing import List, Tuple
import time
import random


@dataclass
class SiteProfile:
    """Profil de configuration pour un site de scraping."""

    # Identification
    name: str
    enabled: bool = True
    disabled_reason: str = ""

    # Mode: 'http', 'hybrid', 'browser'
    mode: str = 'http'

    # Rate limiting
    rps: float = 1.0  # Requests per second
    burst: int = 1  # Max burst
    jitter_range: Tuple[int, int] = (200, 800)  # ms min/max

    # Pagination
    max_pages: int = 5
    stop_early_if_unchanged: bool = True

    # Refresh intervals (en minutes)
    list_refresh_min: int = 15
    detail_refresh_hours: int = 72

    # Retry/Backoff (en secondes)
    backoff_sequence: List[int] = None  # [10, 30, 60, 120]

    # Circuit breaker
    circuit_breaker_fails: int = 10  # Nombre d'échecs avant pause
    circuit_breaker_pause: int = 20  # Pause en minutes

    # Validation localisation
    strict_location: bool = False  # Si True, rejette les annonces sans CP

    def __post_init__(self):
        if self.backoff_sequence is None:
            self.backoff_sequence = [10, 30, 60, 120]


# ============================================================================
# PROFILS PAR SITE (selon la stratégie V3)
# ============================================================================

SITE_PROFILES = {
    # PAP - Site classique HTML stable
    'pap': SiteProfile(
        name='pap.fr',
        enabled=True,
        mode='http',
        rps=1.5,
        burst=2,
        jitter_range=(200, 800),
        max_pages=10,
        list_refresh_min=15,
        detail_refresh_hours=72,
        backoff_sequence=[10, 30, 60, 120],
        circuit_breaker_fails=10,
        circuit_breaker_pause=20,
        strict_location=False
    ),

    # ParuVendu - Site classique
    'paruvendu': SiteProfile(
        name='paruvendu.fr',
        enabled=True,
        mode='http',
        rps=1.5,
        burst=2,
        jitter_range=(250, 900),
        max_pages=8,
        list_refresh_min=20,
        detail_refresh_hours=72,
        backoff_sequence=[10, 30, 60, 120],
        circuit_breaker_fails=10,
        circuit_breaker_pause=20,
        strict_location=False
    ),

    # EntreParticuliers - Site classique
    'entreparticuliers': SiteProfile(
        name='entreparticuliers.com',
        enabled=True,
        mode='http',
        rps=1.5,
        burst=2,
        jitter_range=(200, 800),
        max_pages=8,
        list_refresh_min=20,
        detail_refresh_hours=72,
        backoff_sequence=[10, 30, 60, 120],
        circuit_breaker_fails=10,
        circuit_breaker_pause=20,
        strict_location=False
    ),

    # Leboncoin - Site mi-JS, hybrid
    'leboncoin': SiteProfile(
        name='leboncoin.fr',
        enabled=True,
        mode='hybrid',
        rps=1.0,
        burst=1,
        jitter_range=(400, 1200),
        max_pages=4,
        list_refresh_min=20,
        detail_refresh_hours=72,
        backoff_sequence=[20, 60, 120, 240, 300],
        circuit_breaker_fails=8,
        circuit_breaker_pause=30,
        strict_location=False
    ),

    # Figaro Immo - Agrégateur strict
    'figaro': SiteProfile(
        name='figaro-immo',
        enabled=True,
        mode='http',
        rps=1.0,
        burst=1,
        jitter_range=(300, 1100),
        max_pages=4,
        list_refresh_min=30,
        detail_refresh_hours=96,
        backoff_sequence=[20, 60, 120, 240],
        circuit_breaker_fails=8,
        circuit_breaker_pause=30,
        strict_location=True  # Validation localisation stricte
    ),

    # MoteurImmo - Agrégateur strict (même profil que Figaro)
    'moteurimmo': SiteProfile(
        name='moteurimmo.fr',
        enabled=True,
        mode='http',
        rps=1.0,
        burst=1,
        jitter_range=(300, 1100),
        max_pages=4,
        list_refresh_min=30,
        detail_refresh_hours=96,
        backoff_sequence=[20, 60, 120, 240],
        circuit_breaker_fails=8,
        circuit_breaker_pause=30,
        strict_location=True  # Validation localisation stricte
    ),

    # Facebook Marketplace - DÉSACTIVÉ par défaut
    'facebook': SiteProfile(
        name='facebook-marketplace',
        enabled=False,  # Désactivé par défaut
        disabled_reason='Site hostile, captcha fréquent',
        mode='browser',
        rps=0.3,
        burst=1,
        jitter_range=(800, 2500),
        max_pages=1,
        list_refresh_min=60,
        detail_refresh_hours=96,
        backoff_sequence=[30, 60, 120, 300, 600],
        circuit_breaker_fails=5,
        circuit_breaker_pause=60,
        strict_location=True
    ),
}


def get_profile(site_key: str) -> SiteProfile:
    """Récupère le profil d'un site."""
    return SITE_PROFILES.get(site_key, SiteProfile(name=site_key))


def is_site_enabled(site_key: str) -> bool:
    """Vérifie si un site est activé."""
    profile = SITE_PROFILES.get(site_key)
    return profile.enabled if profile else True


def get_all_enabled_sites() -> List[str]:
    """Retourne la liste des sites activés."""
    return [key for key, profile in SITE_PROFILES.items() if profile.enabled]


class RateLimiter:
    """Rate limiter avec jitter pour un site."""

    def __init__(self, profile: SiteProfile):
        self.profile = profile
        self.last_request_time = 0
        self.request_count = 0
        self.fail_count = 0
        self.circuit_open = False
        self.circuit_open_until = 0
        self.current_backoff_index = 0

    def wait(self):
        """Attend le temps nécessaire avant la prochaine requête."""
        # Vérifier circuit breaker
        if self.circuit_open:
            if time.time() < self.circuit_open_until:
                remaining = int(self.circuit_open_until - time.time())
                print(f"  ⚡ Circuit ouvert, pause {remaining}s restantes")
                time.sleep(min(remaining, 60))  # Attendre max 60s à la fois
                return
            else:
                print(f"  ✅ Circuit fermé, reprise du scraping")
                self.circuit_open = False
                self.fail_count = 0

        # Calculer le délai avec jitter
        min_delay = 1.0 / self.profile.rps
        jitter_ms = random.randint(*self.profile.jitter_range)
        jitter_s = jitter_ms / 1000.0
        total_delay = min_delay + jitter_s

        # Attendre depuis la dernière requête
        elapsed = time.time() - self.last_request_time
        if elapsed < total_delay:
            sleep_time = total_delay - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def record_success(self):
        """Enregistre une requête réussie."""
        self.fail_count = 0
        self.current_backoff_index = 0

    def record_failure(self, status_code: int = None):
        """Enregistre un échec et applique le backoff si nécessaire."""
        self.fail_count += 1

        # Vérifier circuit breaker
        if self.fail_count >= self.profile.circuit_breaker_fails:
            self.circuit_open = True
            pause_seconds = self.profile.circuit_breaker_pause * 60
            self.circuit_open_until = time.time() + pause_seconds
            print(f"  🔴 Circuit ouvert! Pause de {self.profile.circuit_breaker_pause} minutes")
            return

        # Appliquer backoff
        if status_code in [429, 500, 502, 503, 504]:
            backoff_time = self.profile.backoff_sequence[
                min(self.current_backoff_index, len(self.profile.backoff_sequence) - 1)
            ]
            self.current_backoff_index += 1
            print(f"  ⏳ Backoff {backoff_time}s (erreur {status_code})")
            time.sleep(backoff_time)

    def should_stop(self) -> bool:
        """Vérifie si on doit arrêter (circuit ouvert trop longtemps)."""
        return self.circuit_open and (time.time() < self.circuit_open_until)


class SiteManager:
    """Gestionnaire des sites avec kill switch."""

    _disabled_sites = {}  # site_key -> (reason, timestamp)

    @classmethod
    def disable_site(cls, site_key: str, reason: str):
        """Désactive un site (kill switch)."""
        cls._disabled_sites[site_key] = (reason, time.time())
        print(f"  🚫 Site {site_key} désactivé: {reason}")

    @classmethod
    def enable_site(cls, site_key: str):
        """Réactive un site."""
        if site_key in cls._disabled_sites:
            del cls._disabled_sites[site_key]
            print(f"  ✅ Site {site_key} réactivé")

    @classmethod
    def is_site_available(cls, site_key: str) -> bool:
        """Vérifie si un site est disponible."""
        # Vérifier kill switch runtime
        if site_key in cls._disabled_sites:
            return False

        # Vérifier config statique
        profile = SITE_PROFILES.get(site_key)
        if profile and not profile.enabled:
            return False

        return True

    @classmethod
    def get_disabled_reason(cls, site_key: str) -> str:
        """Retourne la raison de désactivation."""
        if site_key in cls._disabled_sites:
            reason, _ = cls._disabled_sites[site_key]
            return reason

        profile = SITE_PROFILES.get(site_key)
        if profile and not profile.enabled:
            return profile.disabled_reason

        return ""
