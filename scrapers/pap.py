from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from .base import BaseScraper

# Import Playwright optionnel
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class PapScraper(BaseScraper):
    """Scraper pour pap.fr (De Particulier À Particulier) - 100% particuliers"""

    @property
    def site_name(self) -> str:
        return "pap.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []

        # Méthode 1: Playwright (si disponible)
        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(ville, max_pages)

        # Méthode 2: Requests/BeautifulSoup
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

                # URLs PAP
                urls = [
                    f"https://www.pap.fr/annonce/vente-immobilier-{ville_slug}",
                    f"https://www.pap.fr/annonces/vente-{ville_slug}",
                    f"https://www.pap.fr/annonce/vente-appartement-maison-{ville_slug}",
                ]

                for url in urls:
                    try:
                        print(f"  🔗 {url[:50]}...")
                        page.goto(url, wait_until='networkidle', timeout=20000)

                        # Scraper plusieurs pages
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
                                next_btn = page.query_selector('a.next, a[rel="next"], .pagination a:last-child')
                                if next_btn:
                                    try:
                                        next_btn.click()
                                        page.wait_for_load_state('networkidle', timeout=10000)
                                        self._wait()
                                    except:
                                        break
                                else:
                                    break

                        if listings:
                            break

                    except PlaywrightTimeout:
                        print(f"    ⏱️ Timeout")
                        continue
                    except Exception as e:
                        print(f"    ⚠️ Erreur: {str(e)[:40]}")
                        continue

                browser.close()

        except Exception as e:
            print(f"  ⚠️ Erreur Playwright: {e}")

        return listings

    def _scrape_html(self, ville: str, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec requests/BeautifulSoup"""
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })

        ville_slug = self._slugify(ville)

        # URLs à essayer
        base_urls = [
            f"https://www.pap.fr/annonce/vente-immobilier-{ville_slug}",
            f"https://www.pap.fr/annonces/vente-{ville_slug}",
            f"https://www.pap.fr/annonce/vente-appartement-maison-{ville_slug}",
        ]

        for base_url in base_urls:
            print(f"  📄 Mode HTML: {base_url[:50]}...")

            for page_num in range(1, max_pages + 1):
                try:
                    url = f"{base_url}-page-{page_num}" if page_num > 1 else base_url

                    response = session.get(url, timeout=15)

                    if response.status_code != 200:
                        print(f"    ⚠️ Status {response.status_code}")
                        break

                    soup = BeautifulSoup(response.content, 'html.parser')
                    ads = self._find_ads(soup)

                    if not ads:
                        if page_num == 1:
                            break  # Essayer URL suivante
                        else:
                            break  # Plus de pages

                    print(f"    📄 Page {page_num}: {len(ads)} annonces")

                    for ad in ads[:15]:
                        listing = self._extract_listing(ad, ville)
                        if listing:
                            listings.append(listing)

                    self._wait()

                except Exception as e:
                    print(f"    ⚠️ Erreur page {page_num}: {e}")
                    break

            if listings:
                break

        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces"""
        # Sélecteurs PAP
        selectors = [
            ('div', {'class': re.compile(r'search-list-item|item-listing|annonce-row', re.I)}),
            ('article', {'class': re.compile(r'annonce', re.I)}),
            ('div', {'class': 'annonce'}),
            ('div', {'class': 'box-annonce'}),
            ('li', {'class': re.compile(r'annonce|listing', re.I)}),
        ]

        for tag, attrs in selectors:
            ads = soup.find_all(tag, attrs)
            if ads and len(ads) > 0:
                return ads

        # Fallback: liens d'annonces
        links = soup.find_all('a', href=re.compile(r'/annonces/[a-z]+-[0-9]+'))
        if links:
            return links

        return []

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
                lien = f"https://www.pap.fr{lien}"

            # Titre
            titre = ''
            for selector in ['h2', 'h3', '.item-title', '.title', '.annonce-titre']:
                elem = ad.find(selector.replace('.', ''), class_=selector.lstrip('.')) if '.' in selector else ad.find(selector)
                if elem:
                    titre = elem.get_text(strip=True)
                    break

            if not titre:
                titre = ad.get_text(strip=True)[:80] or "Annonce PAP"

            # Prix
            prix = 0
            for selector in ['.item-price', '.price', '.prix', '.montant']:
                elem = ad.select_one(selector)
                if elem:
                    prix = self._parse_price(elem.get_text())
                    break

            if not prix:
                prix_match = re.search(r'(\d[\d\s]*)\s*€', ad.get_text())
                if prix_match:
                    prix = self._parse_price(prix_match.group(1))

            # Localisation
            localisation = ville
            for selector in ['.item-location', '.location', '.ville', '.lieu']:
                elem = ad.select_one(selector)
                if elem:
                    localisation = elem.get_text(strip=True)
                    break

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:') and 'http' in src:
                    photos.append(src)

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

    def _slugify(self, text: str) -> str:
        """Convertit en slug URL"""
        return text.lower().replace(' ', '-').replace("'", "-").replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('à', 'a').replace('ù', 'u').replace('ô', 'o').replace('î', 'i')

    def _parse_price(self, text: str) -> int:
        try:
            return int(re.sub(r'[^\d]', '', str(text)))
        except:
            return 0
