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


class LeboncoinScraper(BaseScraper):
    """Scraper pour leboncoin.fr - Playwright + fallback API/HTML"""

    @property
    def site_name(self) -> str:
        return "leboncoin.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []

        # Méthode 1: Playwright (meilleure méthode)
        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(ville, rayon, max_pages)

        # Méthode 2: API directe (fallback)
        if not listings:
            listings = self._scrape_api(ville, rayon, max_pages)

        # Méthode 3: HTML simple (dernier recours)
        if not listings:
            listings = self._scrape_html(ville, rayon, max_pages)

        self._print_stats(listings)
        return listings

    def _scrape_playwright(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec Playwright (JavaScript rendu)"""
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

                # Bloquer les ressources inutiles pour accélérer
                page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())

                ville_encoded = ville.replace(' ', '%20')

                for page_num in range(1, max_pages + 1):
                    try:
                        url = f"https://www.leboncoin.fr/recherche?category=9&text={ville_encoded}&page={page_num}"
                        print(f"  📄 Page {page_num}: {url[:60]}...")

                        page.goto(url, wait_until='networkidle', timeout=30000)

                        # Attendre les annonces
                        try:
                            page.wait_for_selector('[data-qa-id="aditem_container"], article, [class*="styles_adCard"]', timeout=10000)
                        except:
                            print(f"    ⚠️ Timeout sélecteur page {page_num}")

                        # Extraire le HTML
                        html = page.content()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Chercher les annonces
                        ads = soup.select('[data-qa-id="aditem_container"]')
                        if not ads:
                            ads = soup.find_all('article')
                        if not ads:
                            ads = soup.find_all('a', href=re.compile(r'/ad/'))

                        if not ads:
                            print(f"    ⚠️ Aucune annonce trouvée page {page_num}")
                            break

                        print(f"    📋 {len(ads)} annonces trouvées")

                        for ad in ads[:15]:
                            listing = self._extract_listing_html(ad, ville)
                            if listing:
                                listings.append(listing)

                        self._wait()

                    except PlaywrightTimeout:
                        print(f"    ⏱️ Timeout page {page_num}")
                        break
                    except Exception as e:
                        print(f"    ⚠️ Erreur page {page_num}: {str(e)[:50]}")
                        break

                browser.close()

        except Exception as e:
            print(f"  ⚠️ Erreur Playwright: {e}")

        return listings

    def _scrape_api(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape via l'API LeBonCoin"""
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Origin': 'https://www.leboncoin.fr',
            'Referer': 'https://www.leboncoin.fr/',
            'api_key': 'ba0c2dad52b3ec',
        })

        try:
            print("  🔌 Mode API...")
            api_url = "https://api.leboncoin.fr/finder/search"

            for page_num in range(1, max_pages + 1):
                payload = {
                    "limit": 35,
                    "offset": (page_num - 1) * 35,
                    "filters": {
                        "category": {"id": "9"},
                        "enums": {"ad_type": ["offer"]},
                        "keywords": {"text": ville},
                    },
                    "sort_by": "time",
                    "sort_order": "desc"
                }

                try:
                    response = session.post(api_url, json=payload, timeout=15)

                    if response.status_code == 200:
                        data = response.json()
                        ads = data.get('ads', [])

                        if not ads:
                            break

                        print(f"    📋 Page {page_num}: {len(ads)} annonces (API)")

                        for ad in ads:
                            listing = self._parse_api_ad(ad, ville)
                            if listing:
                                listings.append(listing)

                        self._wait()
                    else:
                        print(f"    ⚠️ API Status {response.status_code}")
                        break

                except Exception as e:
                    print(f"    ⚠️ Erreur API: {e}")
                    break

        except Exception as e:
            print(f"  ⚠️ Erreur API générale: {e}")

        return listings

    def _scrape_html(self, ville: str, rayon: int, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape HTML simple (fallback)"""
        listings = []

        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        try:
            print("  📄 Mode HTML...")

            for page_num in range(1, max_pages + 1):
                url = f"https://www.leboncoin.fr/recherche?category=9&text={ville}&page={page_num}"

                try:
                    response = session.get(url, timeout=15)

                    if response.status_code != 200:
                        print(f"    ⚠️ Status {response.status_code}")
                        break

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Chercher le JSON __NEXT_DATA__
                    script = soup.find('script', id='__NEXT_DATA__')
                    if script and script.string:
                        try:
                            data = json.loads(script.string)
                            ads = self._find_ads_in_json(data)

                            if ads:
                                print(f"    📋 Page {page_num}: {len(ads)} annonces (JSON)")
                                for ad in ads:
                                    listing = self._parse_json_ad(ad, ville)
                                    if listing:
                                        listings.append(listing)
                        except:
                            pass

                    self._wait()

                except Exception as e:
                    print(f"    ⚠️ Erreur HTML: {e}")
                    break

        except Exception as e:
            print(f"  ⚠️ Erreur HTML générale: {e}")

        return listings

    def _extract_listing_html(self, ad, ville: str) -> Dict[str, Any]:
        """Extrait une annonce du HTML Playwright"""
        try:
            # Lien
            lien = ''
            if ad.name == 'a':
                lien = ad.get('href', '')
            else:
                link = ad.find('a', href=True)
                if link:
                    lien = link.get('href', '')

            if not lien:
                return None

            if not lien.startswith('http'):
                lien = f"https://www.leboncoin.fr{lien}"

            # Ignorer les liens non-annonces
            if '/ad/' not in lien and '/ventes_immobilieres/' not in lien:
                return None

            # Titre
            titre = ''
            titre_elem = ad.find(['h2', 'h3']) or ad.select_one('[data-qa-id="aditem_title"]')
            if titre_elem:
                titre = titre_elem.get_text(strip=True)
            if not titre:
                titre = ad.get_text(strip=True)[:80]

            # Prix
            prix = 0
            prix_elem = ad.select_one('[data-qa-id="aditem_price"]') or ad.find(string=re.compile(r'[\d\s]+€'))
            if prix_elem:
                text = prix_elem.get_text() if hasattr(prix_elem, 'get_text') else str(prix_elem)
                prix = self._parse_price(text)

            # Localisation
            loc_elem = ad.select_one('[data-qa-id="aditem_location"]')
            localisation = loc_elem.get_text(strip=True) if loc_elem else ville

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and src.startswith('http'):
                    photos.append(src)

            # Pro ou particulier
            is_pro = bool(ad.select_one('[data-qa-id="aditem_pro"]'))

            return {
                'titre': titre or "Annonce LeBonCoin",
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': prix,
                'localisation': localisation,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,
                'surface': None,
                'pieces': None,
                'description': 'PRO' if is_pro else ''
            }
        except:
            return None

    def _parse_api_ad(self, ad: dict, ville: str) -> Dict[str, Any]:
        """Parse une annonce de l'API"""
        try:
            owner = ad.get('owner', {})
            is_pro = owner.get('type') == 'pro'

            attributes = {attr.get('key'): attr.get('value') for attr in ad.get('attributes', [])}

            photos = []
            for img in ad.get('images', {}).get('urls_large', [])[:5]:
                photos.append(img)

            price = ad.get('price', [0])
            if isinstance(price, list):
                price = price[0] if price else 0

            return {
                'titre': ad.get('subject', 'Annonce LeBonCoin'),
                'date_publication': ad.get('first_publication_date', '')[:10] or datetime.now().strftime('%Y-%m-%d'),
                'prix': int(price) if price else 0,
                'localisation': ad.get('location', {}).get('city', ville),
                'lien': f"https://www.leboncoin.fr/ad/ventes_immobilieres/{ad.get('list_id')}",
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,
                'surface': self._safe_int(attributes.get('square')),
                'pieces': self._safe_int(attributes.get('rooms')),
                'description': 'PRO' if is_pro else ''
            }
        except:
            return None

    def _parse_json_ad(self, ad: dict, ville: str) -> Dict[str, Any]:
        """Parse une annonce JSON"""
        try:
            return {
                'titre': ad.get('subject', ad.get('title', 'Annonce LeBonCoin')),
                'date_publication': datetime.now().strftime('%Y-%m-%d'),
                'prix': self._safe_int(ad.get('price')),
                'localisation': ad.get('location', {}).get('city', ville) if isinstance(ad.get('location'), dict) else ville,
                'lien': f"https://www.leboncoin.fr{ad.get('url', '')}",
                'site_source': self.site_name,
                'photos': ad.get('images', [])[:3] if isinstance(ad.get('images'), list) else [],
                'telephone': None,
                'surface': None,
                'pieces': None,
                'description': ''
            }
        except:
            return None

    def _find_ads_in_json(self, data: dict, depth=0) -> list:
        """Cherche les annonces dans le JSON"""
        if depth > 6:
            return []

        if isinstance(data, dict):
            if 'ads' in data and isinstance(data['ads'], list):
                return data['ads']
            for value in data.values():
                result = self._find_ads_in_json(value, depth + 1)
                if result:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_ads_in_json(item, depth + 1)
                if result:
                    return result

        return []

    def _parse_price(self, text: str) -> int:
        try:
            return int(re.sub(r'[^\d]', '', str(text)))
        except:
            return 0

    def _safe_int(self, value) -> int:
        try:
            if isinstance(value, list):
                value = value[0] if value else 0
            return int(value) if value else None
        except:
            return None
