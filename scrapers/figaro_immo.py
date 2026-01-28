from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from .base import BaseScraper

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class FigaroImmoScraper(BaseScraper):
    """Scraper pour proprietes.lefigaro.fr / explorimmo"""

    @property
    def site_key(self) -> str:
        return "figaro"

    @property
    def site_name(self) -> str:
        return "figaro-immo"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        location = self.get_location_info(ville)
        ville_name = location['ville']
        code_postal = location['code_postal']

        print(f"🔍 Scraping {self.site_name} pour {ville_name}", end="")
        if code_postal:
            print(f" ({code_postal})", end="")
        print(f" - rayon: {rayon}km")

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

        # Session avec headers Chrome complets
        session = self._create_session_with_headers()

        # Warm-up
        self._warm_session(session)

        urls = self._build_urls(location)

        for base_url in urls:
            # WAIT AVANT requête
            self._wait()

            print(f"  📄 {base_url[:50]}...")

            try:
                response = session.get(base_url, timeout=20)

                if response.status_code == 403:
                    print(f"    🚫 Bloqué (403)")
                    self._record_failure(403)
                    continue
                elif response.status_code == 200:
                    self._record_success()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    ads = self._find_ads(soup)

                    if ads:
                        print(f"    📋 {len(ads)} annonces")
                        for ad in ads[:20]:
                            listing = self._extract_listing(ad, location)
                            if listing:
                                listing = self._enrich_listing(listing, location)
                                should_reject, reason = self._should_reject_listing(listing)
                                if not should_reject:
                                    listings.append(listing)
                        break
                else:
                    print(f"    ⚠️ Status {response.status_code}")

            except Exception as e:
                print(f"    ⚠️ Erreur: {e}")
                continue

        return listings

    def _build_urls(self, location: dict) -> List[str]:
        urls = []
        slug = location['slug']
        code_postal = location['code_postal']

        urls.append(f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{slug}.html")

        if code_postal:
            urls.append(f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{code_postal}.html")

        urls.append(f"https://www.explorimmo.com/resultat/vente/{slug}")

        return urls

    def _find_ads(self, soup) -> list:
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

    def _extract_listing(self, ad, location: dict) -> Dict[str, Any]:
        try:
            link_elem = ad.find('a', href=True)
            if not link_elem:
                return None

            lien = link_elem.get('href', '')
            if lien and not lien.startswith('http'):
                lien = f"https://immobilier.lefigaro.fr{lien}"

            titre = None
            for tag in ['h2', 'h3', 'h4']:
                titre_elem = ad.find(tag)
                if titre_elem:
                    titre = titre_elem.get_text(strip=True)
                    break

            if not titre:
                titre = link_elem.get_text(strip=True)[:100] or "Annonce Figaro"

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

            # Localisation - extraire du texte de l'annonce
            text = ad.get_text()
            localisation = None

            # Pattern 1: "Ville (12345)" ou "Paris 17E (75017)"
            loc_match = re.search(r'([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9\s-]+)\s*\((\d{5})\)', text)
            if loc_match:
                localisation = f"{loc_match.group(1).strip()} ({loc_match.group(2)})"

            # Pattern 2: "12345 Ville"
            if not localisation:
                cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s-]+)', text)
                if cp_match:
                    localisation = f"{cp_match.group(2).strip()} ({cp_match.group(1)})"

            # Fallback: utiliser la localisation de recherche avec code postal
            if not localisation:
                if location['code_postal']:
                    localisation = f"{location['ville']} ({location['code_postal']})"
                else:
                    localisation = location['ville']

            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    photos.append(src)

            surface, pieces = self._extract_surface_pieces(titre + " " + text)

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
