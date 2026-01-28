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


class PapScraper(BaseScraper):
    """Scraper pour pap.fr (De Particulier À Particulier) - 100% particuliers"""

    @property
    def site_key(self) -> str:
        return "pap"

    @property
    def site_name(self) -> str:
        return "pap.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        # Obtenir les infos de géolocalisation
        location = self.get_location_info(ville)
        ville_name = location['ville']
        code_postal = location['code_postal']

        print(f"🔍 Scraping {self.site_name} pour {ville_name}", end="")
        if code_postal:
            print(f" ({code_postal})", end="")
        print(f" - rayon: {rayon}km")

        listings = []

        # Méthode 1: Playwright
        if PLAYWRIGHT_AVAILABLE:
            listings = self._scrape_playwright(location, max_pages)

        # Méthode 2: Requests/BeautifulSoup
        if not listings:
            listings = self._scrape_html(location, max_pages)

        self._print_stats(listings)
        return listings

    def _scrape_playwright(self, location: dict, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec Playwright et fingerprint furtif"""
        listings = []
        import random

        try:
            print("  🎭 Mode Playwright (furtif)")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                # Context avec fingerprint randomisé
                viewports = [
                    {'width': 1920, 'height': 1080},
                    {'width': 1366, 'height': 768},
                    {'width': 1536, 'height': 864},
                ]
                user_agents = [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                ]

                context = browser.new_context(
                    user_agent=random.choice(user_agents),
                    viewport=random.choice(viewports),
                    locale='fr-FR',
                    timezone_id='Europe/Paris',
                )

                # Script anti-détection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = {runtime: {}};
                """)

                page = context.new_page()

                # Bloquer ressources inutiles
                page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())

                urls = self._build_urls(location)

                for url in urls:
                    try:
                        # WAIT AVANT navigation (timing humain)
                        self._wait()

                        print(f"  🔗 {url[:60]}...")
                        page.goto(url, wait_until='networkidle', timeout=25000)

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
                                    # Enrichir et filtrer
                                    listing = self._enrich_listing(listing, location)
                                    should_reject, reason = self._should_reject_listing(listing)
                                    if not should_reject:
                                        listings.append(listing)

                            # Page suivante
                            if page_num < max_pages:
                                next_btn = page.query_selector('a.next, a[rel="next"], .pagination a:last-child')
                                if next_btn:
                                    try:
                                        # WAIT AVANT click (crucial!)
                                        self._wait()
                                        next_btn.click()
                                        page.wait_for_load_state('networkidle', timeout=15000)
                                    except:
                                        break
                                else:
                                    break

                        if listings:
                            break

                    except PlaywrightTimeout:
                        print(f"    ⏱️ Timeout, essai suivant...")
                        continue
                    except Exception as e:
                        print(f"    ⚠️ Erreur: {str(e)[:40]}")
                        continue

                browser.close()

        except Exception as e:
            print(f"  ⚠️ Erreur Playwright: {e}")

        return listings

    def _scrape_html(self, location: dict, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape avec requests/BeautifulSoup et headers furtifs"""
        listings = []

        # Utiliser session avec headers Chrome complets
        session = self._create_session_with_headers()

        # Warm-up: visiter la page d'accueil d'abord
        self._warm_session(session)

        urls = self._build_urls(location)

        for base_url in urls:
            print(f"  📄 {base_url[:60]}...")

            for page_num in range(1, max_pages + 1):
                try:
                    # WAIT AVANT requête
                    self._wait()

                    url = f"{base_url}-page-{page_num}" if page_num > 1 else base_url

                    # Mettre à jour le Referer pour navigation interne
                    if page_num > 1:
                        session.headers['Referer'] = base_url
                        session.headers['Sec-Fetch-Site'] = 'same-origin'

                    response = session.get(url, timeout=20)

                    if response.status_code == 403:
                        print(f"    🚫 Bloqué (403), pause longue...")
                        self._record_failure(403)
                        break
                    elif response.status_code != 200:
                        print(f"    ⚠️ Status {response.status_code}")
                        break

                    self._record_success()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    ads = self._find_ads(soup)

                    if not ads:
                        if page_num == 1:
                            break  # Essayer URL suivante
                        else:
                            break

                    print(f"    📄 Page {page_num}: {len(ads)} annonces")

                    for ad in ads[:15]:
                        listing = self._extract_listing(ad, location)
                        if listing:
                            # Enrichir et filtrer
                            listing = self._enrich_listing(listing, location)
                            should_reject, reason = self._should_reject_listing(listing)
                            if not should_reject:
                                listings.append(listing)

                except Exception as e:
                    print(f"    ⚠️ Erreur page {page_num}: {e}")
                    break

            if listings:
                break

        return listings

    def _build_urls(self, location: dict) -> List[str]:
        """Construit les URLs de recherche PAP"""
        urls = []
        slug = location['slug']
        code_postal = location['code_postal']
        departement = location['departement']

        # URL avec slug de ville
        urls.append(f"https://www.pap.fr/annonce/vente-immobilier-{slug}")

        # URL avec code postal si disponible
        if code_postal:
            urls.append(f"https://www.pap.fr/annonce/vente-immobilier-{code_postal}")

        # URL avec département
        if departement:
            urls.append(f"https://www.pap.fr/annonce/vente-immobilier-departement-{departement}")

        # Autres formats
        urls.append(f"https://www.pap.fr/annonces/vente-{slug}")
        urls.append(f"https://www.pap.fr/annonce/vente-appartement-maison-{slug}")

        return urls

    def _find_ads(self, soup) -> list:
        """Trouve les annonces"""
        selectors = [
            ('div', {'class': re.compile(r'search-list-item|item-listing|annonce-row', re.I)}),
            ('article', {'class': re.compile(r'annonce', re.I)}),
            ('div', {'class': 'annonce'}),
            ('li', {'class': re.compile(r'annonce|listing', re.I)}),
        ]

        for tag, attrs in selectors:
            ads = soup.find_all(tag, attrs)
            if ads:
                return ads

        # Fallback
        links = soup.find_all('a', href=re.compile(r'/annonces/[a-z]+-[0-9]+'))
        return links if links else []

    def _extract_listing(self, ad, location: dict) -> Dict[str, Any]:
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

            # Localisation - extraire du texte de l'annonce
            localisation = None
            text = ad.get_text()

            # Pattern 1: "Paris 17E (75017)" ou "Ville (12345)"
            loc_match = re.search(r'([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9\s-]+)\s*\((\d{5})\)', text)
            if loc_match:
                ville_name = loc_match.group(1).strip()
                cp = loc_match.group(2)
                localisation = f"{ville_name} ({cp})"

            # Pattern 2: "12345 Ville"
            if not localisation:
                cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s-]+)', text)
                if cp_match:
                    localisation = f"{cp_match.group(2).strip()} ({cp_match.group(1)})"

            # Pattern 3: Chercher dans les éléments HTML
            if not localisation:
                for selector in ['.item-location', '.location', '.ville', '.lieu']:
                    elem = ad.select_one(selector)
                    if elem:
                        loc_text = elem.get_text(strip=True)
                        if loc_text and len(loc_text) > 2:
                            localisation = loc_text
                            break

            # Fallback: utiliser la localisation de recherche avec code postal
            if not localisation:
                if location.get('code_postal'):
                    localisation = f"{location['ville']} ({location['code_postal']})"
                else:
                    localisation = location['ville']

            # Photo
            photos = []
            img = ad.find('img')
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:') and 'http' in src:
                    photos.append(src)

            # Surface et pièces
            surface, pieces = self._extract_surface_pieces(text)

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
