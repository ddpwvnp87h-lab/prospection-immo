from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base import BaseScraper

# Import Playwright optionnel
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class EntreParticuliersScraper(BaseScraper):
    """Scraper pour entreparticuliers.com - 100% particuliers"""

    @property
    def site_name(self) -> str:
        return "entreparticuliers.com"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        print(f"🔍 Scraping {self.site_name} pour {ville}")

        listings = []

        # Méthode 1: Playwright
        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(ville, max_pages)

        # Méthode 2: HTML
        if not listings:
            listings = self._scrape_html(ville, max_pages)

        self._print_stats(listings)
        return listings

    def _scrape_playwright(self, ville: str, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec Playwright"""
        listings = []

        try:
            print("  🎭 Mode Playwright")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    locale='fr-FR'
                )
                page = context.new_page()

                ville_slug = self._slugify(ville)
                url = f"https://www.entreparticuliers.com/achat-immobilier/{ville_slug}"

                print(f"  🔗 {url}")
                page.goto(url, wait_until='networkidle', timeout=20000)

                for page_num in range(1, max_pages + 1):
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')

                    ads = self._find_ads(soup)
                    if not ads:
                        break

                    print(f"    📄 Page {page_num}: {len(ads)} annonces")

                    for ad in ads[:15]:
                        listing = self._extract_listing(ad, ville)
                        if listing:
                            listings.append(listing)

                    # Page suivante
                    if page_num < max_pages:
                        try:
                            next_btn = page.query_selector('a.next, a[rel="next"], .pagination-next')
                            if next_btn:
                                next_btn.click()
                                page.wait_for_load_state('networkidle', timeout=10000)
                                self._wait()
                            else:
                                break
                        except:
                            break

                browser.close()

        except Exception as e:
            print(f"  ⚠️ Erreur Playwright: {e}")

        return listings

    def _scrape_html(self, ville: str, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec requests"""
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        ville_slug = self._slugify(ville)

        for page_num in range(1, max_pages + 1):
            try:
                url = f"https://www.entreparticuliers.com/achat-immobilier/{ville_slug}?page={page_num}"
                print(f"  📄 Page {page_num}: {url[:60]}...")

                response = session.get(url, timeout=15)
                if response.status_code != 200:
                    print(f"    ⚠️ Status {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                ads = self._find_ads(soup)

                if not ads:
                    print(f"    ⚠️ Aucune annonce")
                    break

                print(f"    📋 {len(ads)} annonces")

                for ad in ads[:15]:
                    listing = self._extract_listing(ad, ville)
                    if listing:
                        listings.append(listing)

                self._wait()

            except Exception as e:
                print(f"    ⚠️ Erreur: {e}")
                break

        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces"""
        selectors = [
            ('article', {'class': re.compile(r'annonce', re.I)}),
            ('div', {'class': re.compile(r'listing-item|annonce|property-card', re.I)}),
            ('li', {'class': re.compile(r'annonce', re.I)}),
        ]

        for tag, attrs in selectors:
            ads = soup.find_all(tag, attrs)
            if ads:
                return ads

        # Fallback: liens d'annonces
        links = soup.find_all('a', href=re.compile(r'/annonce/'))
        return links if links else []

    def _extract_listing(self, ad, ville: str) -> Dict[str, Any]:
        """Extrait une annonce"""
        try:
            # Lien
            if ad.name == 'a':
                lien = ad.get('href', '')
            else:
                link = ad.find('a', href=True)
                lien = link.get('href', '') if link else ''

            if not lien:
                return None

            if not lien.startswith('http'):
                lien = f"https://www.entreparticuliers.com{lien}"

            # Titre
            titre = None
            for tag in ['h2', 'h3', '.titre', '.title']:
                elem = ad.find(tag.replace('.', ''), class_=tag.lstrip('.')) if '.' in tag else ad.find(tag)
                if elem:
                    titre = elem.get_text(strip=True)
                    break

            if not titre:
                titre = ad.get_text(strip=True)[:80] or "Annonce EntreParticuliers"

            # Prix
            prix = 0
            prix_elem = ad.find(string=re.compile(r'[\d\s]+€'))
            if prix_elem:
                prix = self._parse_price(prix_elem)
            else:
                for elem in ad.find_all(['span', 'div', 'p']):
                    text = elem.get_text()
                    if '€' in text:
                        prix = self._parse_price(text)
                        if prix > 10000:
                            break

            # Surface et pièces
            text = ad.get_text()
            surface = None
            pieces = None

            surface_match = re.search(r'(\d+)\s*m[²2]', text, re.I)
            if surface_match:
                surface = int(surface_match.group(1))

            pieces_match = re.search(r'(\d+)\s*pièces?|[TF](\d+)', text, re.I)
            if pieces_match:
                pieces = int(pieces_match.group(1) or pieces_match.group(2))

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    if not src.startswith('http'):
                        src = f"https://www.entreparticuliers.com{src}"
                    photos.append(src)

            return {
                'titre': titre,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': prix,
                'localisation': ville,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,
                'surface': surface,
                'pieces': pieces,
                'description': ''
            }
        except:
            return None

    def _slugify(self, text: str) -> str:
        return text.lower().replace(' ', '-').replace("'", "-")

    def _parse_price(self, text: str) -> int:
        try:
            return int(re.sub(r'[^\d]', '', str(text)))
        except:
            return 0
