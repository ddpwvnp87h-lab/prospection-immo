from .base import BaseScraper
from .leboncoin import LeboncoinScraper
from .pap import PapScraper
from .paruvendu import ParuvenduScraper
from .logic_immo import LogicImmoScraper
from .bienici import BieniciScraper
from .seloger import SelogerScraper
from .facebook_marketplace import FacebookMarketplaceScraper
from .figaro_immo import FigaroImmoScraper

__all__ = [
    'BaseScraper',
    'LeboncoinScraper',
    'PapScraper',
    'ParuvenduScraper',
    'LogicImmoScraper',
    'BieniciScraper',
    'SelogerScraper',
    'FacebookMarketplaceScraper',
    'FigaroImmoScraper'
]
