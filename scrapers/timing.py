"""
Timing humain pour scraping furtif.
Simule des délais réalistes d'utilisateur humain.
"""

import random
import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class TimingProfile:
    """Profil de timing humain."""

    # Délais de base (secondes)
    min_delay: float = 2.0
    max_delay: float = 5.0

    # Probabilités de comportement
    prob_quick_scan: float = 0.10   # 10% : scroll rapide
    prob_reading: float = 0.20      # 20% : lecture attentive
    prob_distraction: float = 0.05  # 5% : pause longue (distraction)

    # Délais par comportement (secondes)
    quick_scan_range: tuple = (0.8, 1.5)
    reading_range: tuple = (5.0, 12.0)
    distraction_range: tuple = (15.0, 45.0)

    # Backoff après erreurs
    backoff_429: List[int] = field(default_factory=lambda: [30, 60, 120, 240, 300])
    backoff_403: tuple = (60, 180)
    backoff_5xx: tuple = (5, 15)


# Profils par site
TIMING_PROFILES = {
    'pap': TimingProfile(
        min_delay=2.0,
        max_delay=4.0,
        prob_reading=0.15,
        prob_distraction=0.03,
    ),

    'paruvendu': TimingProfile(
        min_delay=2.0,
        max_delay=4.0,
        prob_reading=0.15,
    ),

    'entreparticuliers': TimingProfile(
        min_delay=2.0,
        max_delay=4.0,
        prob_reading=0.15,
    ),

    'leboncoin': TimingProfile(
        min_delay=3.0,       # Plus lent - site très surveillé
        max_delay=7.0,
        prob_reading=0.25,   # Plus de "lecture"
        prob_distraction=0.10,  # Plus de pauses
        backoff_429=[60, 120, 240, 300, 600],  # Backoff plus agressif
    ),

    'figaro': TimingProfile(
        min_delay=2.5,
        max_delay=5.0,
        prob_reading=0.20,
    ),

    'moteurimmo': TimingProfile(
        min_delay=2.5,
        max_delay=5.0,
        prob_reading=0.20,
    ),

    'default': TimingProfile(),
}


class HumanTimer:
    """
    Simule des délais humains réalistes.

    Usage:
        timer = HumanTimer('leboncoin')
        timer.wait_before_request()  # Avant chaque requête
        timer.wait_after_error(429, attempt=1)  # Après erreur
    """

    def __init__(self, site_key: str = 'default'):
        """
        Args:
            site_key: Clé du site pour profil adapté
        """
        self.profile = TIMING_PROFILES.get(site_key, TIMING_PROFILES['default'])
        self._page_count = 0
        self._session_start = time.time()
        self._last_request_time = 0
        self._consecutive_errors = 0

    def wait_before_request(self) -> float:
        """
        Attend avant une requête avec pattern humain.

        Returns:
            Durée d'attente effectuée (en secondes)
        """
        p = self.profile
        roll = random.random()

        if roll < p.prob_quick_scan:
            # Scroll rapide (utilisateur pressé)
            delay = random.uniform(*p.quick_scan_range)
            behavior = "quick"

        elif roll < p.prob_quick_scan + p.prob_reading:
            # Lecture attentive
            delay = random.uniform(*p.reading_range)
            behavior = "reading"

        elif roll < p.prob_quick_scan + p.prob_reading + p.prob_distraction:
            # Distraction (téléphone, café, etc.)
            delay = random.uniform(*p.distraction_range)
            behavior = "pause"

        else:
            # Comportement normal avec jitter gaussien
            base = random.uniform(p.min_delay, p.max_delay)
            jitter = random.gauss(0, 0.5)  # Variation naturelle
            delay = max(1.0, base + jitter)
            behavior = "normal"

        # Fatigue : après 10 pages, délais augmentent progressivement
        if self._page_count > 10:
            fatigue_factor = 1 + (self._page_count - 10) * 0.05
            delay *= min(fatigue_factor, 2.0)  # Max 2x

        # Si beaucoup d'erreurs récentes, être plus prudent
        if self._consecutive_errors > 0:
            delay *= (1 + self._consecutive_errors * 0.5)

        self._page_count += 1
        self._last_request_time = time.time()

        time.sleep(delay)
        return delay

    def wait_after_error(self, error_code: int, attempt: int = 1) -> float:
        """
        Backoff intelligent après erreur.

        Args:
            error_code: Code HTTP d'erreur
            attempt: Numéro de tentative (1 = première)

        Returns:
            Durée d'attente effectuée
        """
        self._consecutive_errors += 1
        p = self.profile

        if error_code == 429:
            # Too Many Requests : backoff exponentiel
            idx = min(attempt - 1, len(p.backoff_429) - 1)
            base_delay = p.backoff_429[idx]
            jitter = random.uniform(0, base_delay * 0.3)
            delay = base_delay + jitter

        elif error_code == 403:
            # Forbidden : possiblement bloqué
            delay = random.uniform(*p.backoff_403)

        elif error_code >= 500:
            # Erreur serveur : retry plus rapide
            delay = random.uniform(*p.backoff_5xx)

        else:
            delay = random.uniform(10, 30)

        # Max 10 minutes
        delay = min(delay, 600)

        print(f"    ⏳ Backoff {delay:.0f}s (erreur {error_code}, tentative {attempt})")
        time.sleep(delay)
        return delay

    def record_success(self):
        """Enregistre un succès (reset erreurs consécutives)."""
        self._consecutive_errors = 0

    def reset_session(self):
        """Reset pour nouvelle session de scraping."""
        self._page_count = 0
        self._session_start = time.time()
        self._consecutive_errors = 0

    def get_session_duration(self) -> float:
        """Retourne la durée de la session en secondes."""
        return time.time() - self._session_start

    def should_take_break(self) -> bool:
        """
        Indique si on devrait faire une pause (session longue).

        Returns:
            True si pause recommandée
        """
        # Pause après 30 minutes ou 50 pages
        duration = self.get_session_duration()
        return duration > 1800 or self._page_count > 50


def get_timer(site_key: str) -> HumanTimer:
    """
    Helper pour obtenir un timer adapté au site.

    Args:
        site_key: Clé du site

    Returns:
        HumanTimer configuré
    """
    return HumanTimer(site_key)
