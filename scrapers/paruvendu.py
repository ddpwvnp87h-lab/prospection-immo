from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base import BaseScraper

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ParuvenduScraper(BaseScraper):
    """Scraper pour paruvendu.fr - filtre particuliers"""

    @property
    def site_name(self) -> str:
        return "paruvendu.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        location = self.get_location_info(ville)
        ville_name = location['ville']
        code_postal = location['code_postal']

        print(f"🔍 Scraping {self.site_name} pour {ville_name}", end="")
        if code_postal:
            print(f" ({code_postal})", end="")
        print()

        listings = []

        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(location, max_pages)

        if not listings:
            listings = self._scrape_html(location, max_pages)

        self._print_stats(listings)
        return listings

    def _scrape_playwright(self, location: dict, max_pages: int) -> List[Dict[str, Any]]:
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

                urls = self._build_urls(location)

                for url in urls:
                    try:
                        print(f"  🔗 {url[:60]}...")
                        page.goto(url, wait_until='networkidle', timeout=20000)

                        for page_num in range(1, max_pages + 1):
                            html = page.content()
                            soup = BeautifulSoup(html, 'html.parser')

                            ads = self._find_ads(soup)
                            if not ads:
                                break

                            print(f"    📄 Page {page_num}: {len(ads)} annonces")

                            for ad in ads[:15]:
                                listing = self._extract_listing(ad, location)
                                if listing:
                                    listings.append(listing)

                            if page_num < max_pages:
                                try:
                                    next_btn = page.query_selector('a.next, a[rel="next"]')
                                    if next_btn:
                                        next_btn.click()
                                        page.wait_for_load_state('networkidle', timeout=10000)
                                        self._wait()
                                    else:
                                        break
                                except:
                                    break

                        if listings:
                            break

                    except:
                        continue

                browser.close()

        except Exception as e:
            print(f"  ⚠️ Erreur Playwright: {e}")

        return listings

    def _scrape_html(self, location: dict, max_pages: int) -> List[Dict[str, Any]]:
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        urls = self._build_urls(location)

        for base_url in urls:
            for page_num in range(1, max_pages + 1):
                try:
                    url = f"{base_url}&p={page_num}" if '?' in base_url else f"{base_url}?p={page_num}"
                    print(f"  📄 Page {page_num}: {url[:60]}...")

                    response = session.get(url, timeout=15)
                    if response.status_code != 200:
                        break

                    soup = BeautifulSoup(response.content, 'html.parser')
                    ads = self._find_ads(soup)

                    if not ads:
                        break

                    print(f"    📋 {len(ads)} annonces")

                    for ad in ads[:15]:
                        listing = self._extract_listing(ad, location)
                        if listing:
                            listings.append(listing)

                    self._wait()

                except Exception as e:
                    print(f"    ⚠️ Erreur: {e}")
                    break

            if listings:
                break

        return listings

    def _build_urls(self, location: dict) -> List[str]:
        urls = []
        slug = location['slug']
        code_postal = location['code_postal']

        # pa=1 = particulier uniquement
        if code_postal:
            urls.append(f"https://www.paruvendu.fr/immobilier/vente/{code_postal}/?pa=1")

        urls.append(f"https://www.paruvendu.fr/immobilier/vente/{slug}/?pa=1")

        return urls

    def _find_ads(self, soup) -> list:
        selectors = [
            ('div', {'class': re.compile(r'annonce|ergov3-annonce', re.I)}),
            ('article', {'class': re.compile(r'annonce', re.I)}),
            ('li', {'class': re.compile(r'annonce', re.I)}),
        ]

        for tag, attrs in selectors:
            ads = soup.find_all(tag, attrs)
            if ads:
                return ads

        links = soup.find_all('a', href=re.compile(r'/immobilier/vente/'))
        return [l for l in links if 'annonce' in str(l.get('class', []))] or links[:20]

    def _extract_listing(self, ad, location: dict) -> Dict[str, Any]:
        try:
            if ad.name == 'a':
                lien = ad.get('href', '')
            else:
                link = ad.find('a', href=True)
                lien = link.get('href', '') if link else ''

            if not lien:
                return None

            if not lien.startswith('http'):
                lien = f"https://www.paruvendu.fr{lien}"

            titre = None
            titre_elem = ad.find(['h2', 'h3']) or ad.find(class_=re.compile(r'titre', re.I))
            if titre_elem:
                titre = titre_elem.get_text(strip=True)
            if not titre:
                titre = ad.get_text(strip=True)[:80] or "Annonce ParuVendu"

            prix = 0
            prix_elem = ad.find(class_=re.compile(r'prix|price', re.I)) or ad.find(string=re.compile(r'[\d\s]+€'))
            if prix_elem:
                text = prix_elem.get_text() if hasattr(prix_elem, 'get_text') else str(prix_elem)
                prix = self._parse_price(text)

            # Localisation
            text = ad.get_text()
            localisation = location['ville']
            if location['code_postal']:
                localisation = f"{location['ville']} ({location['code_postal']})"

            cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ\s-]+)', text)
            if cp_match:
                localisation = f"{cp_match.group(2).strip()} ({cp_match.group(1)})"

            surface, pieces = self._extract_surface_pieces(text)

            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:'):
                    if not src.startswith('http'):
                        src = f"https://www.paruvendu.fr{src}"
                    photos.append(src)

            return {
                'titre': titre,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': prix,
                'localisation': localisation,
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
