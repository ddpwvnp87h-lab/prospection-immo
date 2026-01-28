from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from .base import BaseScraper

# Import Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class FacebookMarketplaceScraper(BaseScraper):
    """Scraper pour Facebook Marketplace - Playwright + fallback HTML"""

    @property
    def site_name(self) -> str:
        return "facebook-marketplace"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")
        print("  ⚠️ Facebook peut demander une connexion - résultats limités")

        listings = []

        # Méthode 1: Playwright (meilleure méthode)
        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(ville, rayon, max_pages)

        # Méthode 2: HTML simple (fallback)
        if not listings:
            listings = self._scrape_html(ville, max_pages)

        self._print_stats(listings)
        return listings

    def _scrape_playwright(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec Playwright"""
        listings = []

        try:
            print("  🎭 Mode Playwright activé")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    locale='fr-FR'
                )
                page = context.new_page()

                # Bloquer les ressources inutiles
                page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,mp4,webm}", lambda route: route.abort())

                ville_slug = ville.lower().replace(' ', '-').replace("'", "")

                # URLs à essayer
                urls = [
                    f"https://www.facebook.com/marketplace/{ville_slug}/propertyforsale",
                    f"https://www.facebook.com/marketplace/category/propertyforsale?query={ville}",
                    f"https://www.facebook.com/marketplace/search?query=appartement%20maison%20{ville}",
                ]

                for url in urls:
                    try:
                        print(f"  🔗 Tentative: {url[:50]}...")
                        page.goto(url, wait_until='domcontentloaded', timeout=20000)

                        # Attendre le chargement
                        page.wait_for_timeout(3000)

                        # Vérifier si login requis
                        if 'login' in page.url.lower():
                            print(f"    ⚠️ Connexion requise")
                            continue

                        # Scroll pour charger plus
                        for _ in range(min(max_pages, 3)):
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            page.wait_for_timeout(2000)

                        # Extraire HTML
                        html = page.content()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Chercher les annonces
                        ads = self._find_ads(soup)

                        if ads:
                            print(f"    📋 {len(ads)} annonces trouvées")
                            for ad in ads[:20]:
                                listing = self._extract_listing(ad, ville)
                                if listing:
                                    listings.append(listing)
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
        """Scrape HTML simple (fallback)"""
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        try:
            print("  📄 Mode HTML (limité)...")

            # Version mobile (moins de restrictions)
            mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            session.headers['User-Agent'] = mobile_ua

            url = f"https://m.facebook.com/marketplace/search/?query=immobilier%20{ville}"

            response = session.get(url, timeout=15, allow_redirects=True)

            if response.status_code == 200 and 'login' not in response.url.lower():
                soup = BeautifulSoup(response.content, 'html.parser')
                ads = self._find_ads(soup)

                if ads:
                    print(f"    📋 {len(ads)} annonces (mobile)")
                    for ad in ads[:15]:
                        listing = self._extract_listing(ad, ville)
                        if listing:
                            listings.append(listing)
            else:
                print(f"    ⚠️ Accès limité (connexion requise)")

        except Exception as e:
            print(f"  ⚠️ Erreur HTML: {e}")

        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces dans le HTML"""
        ads = []

        # Sélecteurs multiples
        selectors = [
            ('div', {'data-testid': 'marketplace-search-results'}),
            ('div', {'role': 'article'}),
            ('a', {'href': re.compile(r'/marketplace/item/')}),
            ('div', {'class': re.compile(r'x9f619.*x1lliihq', re.I)}),
        ]

        for tag, attrs in selectors:
            found = soup.find_all(tag, attrs)
            if found and len(found) > 2:
                ads = found
                break

        # Si pas trouvé, chercher tous les liens marketplace
        if not ads:
            ads = soup.find_all('a', href=re.compile(r'/marketplace/item/'))

        return ads[:30]

    def _extract_listing(self, ad, ville: str) -> Dict[str, Any]:
        """Extrait une annonce"""
        try:
            # Lien
            lien = ''
            if ad.name == 'a':
                lien = ad.get('href', '')
            else:
                link = ad.find('a', href=re.compile(r'/marketplace/item/'))
                if link:
                    lien = link.get('href', '')

            if not lien:
                return None

            if not lien.startswith('http'):
                lien = f"https://www.facebook.com{lien}"

            # Nettoyer l'URL
            if '?' in lien:
                lien = lien.split('?')[0]

            # Titre
            titre = ''
            # Chercher dans les spans
            spans = ad.find_all('span')
            for span in spans:
                text = span.get_text(strip=True)
                if len(text) > 10 and len(text) < 150 and '€' not in text:
                    titre = text
                    break

            if not titre:
                titre = ad.get_text(strip=True)[:80] or "Annonce Facebook"

            # Prix
            prix = 0
            text = ad.get_text()
            prix_match = re.search(r'(\d[\d\s.,]*)\s*€', text)
            if prix_match:
                prix_str = re.sub(r'[^\d]', '', prix_match.group(1))
                prix = int(prix_str) if prix_str else 0

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and 'http' in src and 'emoji' not in src:
                    photos.append(src)

            # Localisation
            localisation = ville
            loc_patterns = [
                r'(\d{5})\s+([A-Za-zÀ-ÿ\s-]+)',  # Code postal + ville
                r'([A-Za-zÀ-ÿ\s-]+)\s+\(\d+\)',   # Ville (département)
            ]
            for pattern in loc_patterns:
                match = re.search(pattern, text)
                if match:
                    localisation = match.group(0).strip()
                    break

            return {
                'titre': titre,
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': prix,
                'localisation': localisation,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,
                'surface': None,
                'pieces': None,
                'description': ''
            }
        except:
            return None
