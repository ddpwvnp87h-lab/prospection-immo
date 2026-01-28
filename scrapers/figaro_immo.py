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


class FigaroImmoScraper(BaseScraper):
    """Scraper pour proprietes.lefigaro.fr / explorimmo"""

    @property
    def site_name(self) -> str:
        return "figaro-immo"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

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

                urls = [
                    f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{ville_slug}.html",
                    f"https://www.explorimmo.com/resultat/vente/{ville_slug}",
                ]

                for url in urls:
                    try:
                        print(f"  🔗 {url[:50]}...")
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

                        if listings:
                            break

                    except PlaywrightTimeout:
                        continue
                    except Exception as e:
                        print(f"    ⚠️ Erreur: {str(e)[:40]}")
                        continue

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

        urls = [
            f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{ville_slug}.html",
            f"https://www.explorimmo.com/resultat/vente/{ville_slug}",
            f"https://immobilier.lefigaro.fr/annonces/annonce-vente-{ville_slug}.html",
        ]

        for base_url in urls:
            print(f"  📄 {base_url[:50]}...")

            try:
                response = session.get(base_url, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Debug
                    title = soup.find('title')
                    if title:
                        print(f"    📄 Page: {title.get_text()[:50]}")

                    ads = self._find_ads(soup)

                    if ads:
                        print(f"    📋 {len(ads)} annonces")
                        for ad in ads[:20]:
                            listing = self._extract_listing(ad, ville)
                            if listing:
                                listings.append(listing)
                        break
                else:
                    print(f"    ⚠️ Status {response.status_code}")

            except Exception as e:
                print(f"    ⚠️ Erreur: {e}")
                continue

        # Essayer JSON-LD
        if not listings:
            listings = self._try_json_data(session, ville)

        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces"""
        selectors = [
            ('article', {}),
            ('div', {'class': re.compile(r'classified-card|annonce-item|listing-item|card', re.I)}),
            ('li', {'class': re.compile(r'annonce', re.I)}),
        ]

        for tag, attrs in selectors:
            if attrs:
                ads = soup.find_all(tag, attrs)
            else:
                ads = soup.find_all(tag)
                ads = [a for a in ads if a.find('a', href=True)]

            if ads and len(ads) > 2:
                return ads[:30]

        return []

    def _try_json_data(self, session, ville: str) -> List[Dict[str, Any]]:
        """Essaie JSON-LD"""
        listings = []

        try:
            print("  🔄 Recherche JSON-LD...")
            url = f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{ville.lower()}.html"
            response = session.get(url, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                scripts = soup.find_all('script', type='application/ld+json')

                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'Product' or 'offer' in str(item).lower():
                                    listing = self._parse_json_ld(item, ville)
                                    if listing:
                                        listings.append(listing)
                    except:
                        pass

        except Exception as e:
            print(f"    ⚠️ JSON-LD: {e}")

        return listings

    def _parse_json_ld(self, data: dict, ville: str) -> Dict[str, Any]:
        """Parse JSON-LD"""
        try:
            return {
                'titre': data.get('name', 'Annonce Figaro'),
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': int(data.get('offers', {}).get('price', 0)),
                'localisation': ville,
                'lien': data.get('url', ''),
                'site_source': self.site_name,
                'photos': [data.get('image', '')] if data.get('image') else [],
                'telephone': None,
                'surface': None,
                'pieces': None,
                'description': ''
            }
        except:
            return None

    def _extract_listing(self, ad, ville: str) -> Dict[str, Any]:
        """Extrait une annonce"""
        try:
            link_elem = ad.find('a', href=True)
            if not link_elem:
                return None

            lien = link_elem.get('href', '')
            if lien and not lien.startswith('http'):
                lien = f"https://immobilier.lefigaro.fr{lien}"

            # Titre
            titre = None
            for tag in ['h2', 'h3', 'h4']:
                titre_elem = ad.find(tag)
                if titre_elem:
                    titre = titre_elem.get_text(strip=True)
                    break

            if not titre:
                titre = link_elem.get_text(strip=True)[:100] or "Annonce Figaro"

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

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    photos.append(src)

            # Surface et pièces
            text = titre + " " + ad.get_text()
            surface, pieces = self._extract_surface_pieces(text)

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

    def _extract_surface_pieces(self, text: str):
        surface = None
        pieces = None

        surface_match = re.search(r'(\d+)\s*m[²2]', text, re.I)
        if surface_match:
            surface = int(surface_match.group(1))

        pieces_match = re.search(r'(\d+)\s*pièces?|[TF](\d+)', text, re.I)
        if pieces_match:
            pieces = int(pieces_match.group(1) or pieces_match.group(2))

        return surface, pieces
