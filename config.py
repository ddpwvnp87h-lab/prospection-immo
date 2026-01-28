"""
Configuration globale du projet.
"""

import os
from typing import List

# Sites de scraping
SCRAPING_SITES: List[str] = [
    'leboncoin.fr',
    'pap.fr',
    'paruvendu.fr',
    'logic-immo.com',
    'bienici.com',
    'seloger.com',
    'facebook.com/marketplace',
    'proprietes.lefigaro.fr'
]

# Statuts possibles des annonces
LISTING_STATUSES: List[str] = [
    'Nouveau',
    'Contacté',
    'Réponse reçue',
    'Pas de réponse',
    'Pas intéressé'
]

# Délai entre requêtes de scraping (secondes)
SCRAPING_DELAY: int = int(os.getenv('SCRAPING_DELAY', 2))

# Nombre maximum de pages à scraper par site
MAX_PAGES_PER_SITE: int = int(os.getenv('MAX_PAGES_PER_SITE', 5))

# Délai de conservation des annonces (jours)
CLEANUP_DAYS: int = 90

# Mots-clés pour détecter les agences
AGENCY_KEYWORDS: List[str] = [
    'agence',
    'immobilier',
    'immo',
    'real estate',
    'sarl',
    'sas',
    'eurl',
    'siret',
    'siren',
    'professional',
    'professionnel'
]

# Configuration Supabase
SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')

# Configuration User Agent
USER_AGENT: str = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
