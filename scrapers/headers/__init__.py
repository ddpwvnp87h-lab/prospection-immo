"""
Headers factory pour scraping furtif.
Génère des headers de navigateur réalistes.
"""

from .factory import HeaderFactory, get_headers_for_site
from .profiles import BROWSER_PROFILES, CHROME_120_MACOS

__all__ = ['HeaderFactory', 'get_headers_for_site', 'BROWSER_PROFILES', 'CHROME_120_MACOS']
