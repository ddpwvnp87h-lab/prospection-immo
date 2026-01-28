from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from .base import BaseScraper


class PapScraper(BaseScraper):
    """Scraper pour pap.fr (De Particulier À Particulier)"""

    @property
    def site_name(self) -> str:
        return "pap.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape les annonces immobilières de pap.fr"""
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        # URLs à essayer pour PAP
        ville_slug = ville.lower().replace(' ', '-').replace("'", "-")
        urls_to_try = [
            f"https://www.pap.fr/annonce/vente-immobilier-{ville_slug}",
            f"https://www.pap.fr/annonces/vente-{ville_slug}",
            f"https://www.pap.fr/annonce/vente-appartement-maison-{ville_slug}",
        ]

        for base_url in urls_to_try:
            try:
                print(f"  🔗 Tentative: {base_url}")
                response = session.get(base_url, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Chercher les annonces avec différents sélecteurs
                    ads = self._find_ads(soup)

                    if ads:
                        print(f"  ✅ {len(ads)} annonces trouvées!")
                        for ad in ads[:20]:  # Limiter à 20
                            listing = self._extract_listing(ad, ville)
                            if listing:
                                listings.append(listing)
                        break
                    else:
                        print(f"  ⚠️ Aucune annonce avec cette URL")
                else:
                    print(f"  ⚠️ Status {response.status_code}")

            except Exception as e:
                print(f"  ⚠️ Erreur: {e}")
                continue

        # Si toujours rien, essayer l'API JSON de PAP
        if not listings:
            listings = self._try_api(session, ville)

        self._print_stats(listings)
        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces avec différents sélecteurs possibles."""
        selectors = [
            ('div', {'class': 'search-list-item'}),
            ('div', {'class': 'item-listing'}),
            ('article', {'class': 'annonce'}),
            ('div', {'class': 'annonce'}),
            ('div', {'class': 'box-annonce'}),
            ('li', {'class': 'annonce'}),
            ('div', {'data-testid': 'listing'}),
        ]

        for tag, attrs in selectors:
            ads = soup.find_all(tag, attrs)
            if ads:
                print(f"    📋 Sélecteur trouvé: {tag}.{attrs}")
                return ads

        # Dernière tentative: chercher tous les liens vers des annonces
        links = soup.find_all('a', href=re.compile(r'/annonces/'))
        if links:
            print(f"    📋 {len(links)} liens d'annonces trouvés")
            return links

        return []

    def _try_api(self, session, ville: str) -> List[Dict[str, Any]]:
        """Essaie d'utiliser l'API JSON de PAP."""
        print("  🔄 Tentative via API...")
        listings = []

        try:
            # PAP a parfois une API de recherche
            api_url = "https://www.pap.fr/json/ac-geo"
            params = {'q': ville}
            response = session.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"    API geo: {data}")
        except Exception as e:
            print(f"    ⚠️ API non disponible: {e}")

        return listings

    def _extract_listing(self, ad_element, ville: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce."""
        try:
            # Chercher le lien
            if ad_element.name == 'a':
                link_elem = ad_element
            else:
                link_elem = ad_element.find('a', href=True)

            if not link_elem:
                return None

            lien = link_elem.get('href', '')
            if lien and not lien.startswith('http'):
                lien = f"https://www.pap.fr{lien}"

            # Titre - essayer plusieurs sélecteurs
            titre = None
            for selector in ['h2', 'h3', '.item-title', '.title', 'span.title']:
                titre_elem = ad_element.select_one(selector) if '.' in selector else ad_element.find(selector)
                if titre_elem:
                    titre = titre_elem.get_text(strip=True)
                    break

            if not titre:
                titre = link_elem.get_text(strip=True)[:100] or "Annonce PAP"

            # Prix
            prix = 0
            for selector in ['.item-price', '.price', 'span.prix', '.amount']:
                prix_elem = ad_element.select_one(selector) if '.' in selector else ad_element.find('span', class_='price')
                if prix_elem:
                    prix = self._parse_price(prix_elem.get_text())
                    break

            # Localisation
            localisation = ville
            for selector in ['.item-location', '.location', '.ville', '.city']:
                loc_elem = ad_element.select_one(selector) if '.' in selector else None
                if loc_elem:
                    localisation = loc_elem.get_text(strip=True)
                    break

            # Photo
            photos = []
            img = ad_element.find('img')
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:'):
                    photos.append(src)

            # Surface et pièces
            surface, pieces = self._extract_surface_pieces(titre)

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
                'description': ""
            }

        except Exception as e:
            print(f"      ⚠️ Erreur extraction: {e}")
            return None

    def _parse_price(self, price_text: str) -> int:
        try:
            price_clean = re.sub(r'[^\d]', '', price_text)
            return int(price_clean) if price_clean else 0
        except:
            return 0

    def _extract_surface_pieces(self, text: str):
        surface = None
        pieces = None

        surface_match = re.search(r'(\d+)\s*m[²2]', text, re.IGNORECASE)
        if surface_match:
            surface = int(surface_match.group(1))

        pieces_match = re.search(r'(\d+)\s*pièces?|[TF](\d+)', text, re.IGNORECASE)
        if pieces_match:
            pieces = int(pieces_match.group(1) or pieces_match.group(2))

        return surface, pieces
