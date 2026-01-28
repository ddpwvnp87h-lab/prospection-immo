from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
from .base import BaseScraper


class FigaroImmoScraper(BaseScraper):
    """Scraper pour proprietes.lefigaro.fr / explorimmo"""

    @property
    def site_name(self) -> str:
        return "figaro-immo"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape les annonces de Figaro Immobilier / Explorimmo"""
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })

        ville_slug = ville.lower().replace(' ', '-').replace("'", "-")

        # URLs à essayer
        urls_to_try = [
            f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{ville_slug}.html",
            f"https://www.explorimmo.com/resultat/vente/{ville_slug}",
            f"https://immobilier.lefigaro.fr/annonces/annonce-vente-{ville_slug}.html",
        ]

        for base_url in urls_to_try:
            try:
                print(f"  🔗 Tentative: {base_url}")
                response = session.get(base_url, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Debug: afficher le titre de la page
                    title = soup.find('title')
                    if title:
                        print(f"    📄 Page: {title.get_text()[:50]}")

                    ads = self._find_ads(soup)

                    if ads:
                        print(f"  ✅ {len(ads)} annonces trouvées!")
                        for ad in ads[:20]:
                            listing = self._extract_listing(ad, ville)
                            if listing:
                                listings.append(listing)
                        break
                    else:
                        print(f"  ⚠️ Aucune annonce")
                else:
                    print(f"  ⚠️ Status {response.status_code}")

            except Exception as e:
                print(f"  ⚠️ Erreur: {e}")
                continue

        # Essayer l'API si disponible
        if not listings:
            listings = self._try_json_data(session, ville)

        self._print_stats(listings)
        return listings

    def _find_ads(self, soup) -> list:
        """Trouve les annonces avec différents sélecteurs."""
        selectors = [
            ('article', {}),
            ('div', {'class': 'classified-card'}),
            ('div', {'class': 'annonce-item'}),
            ('div', {'class': 'listing-item'}),
            ('li', {'class': 'annonce'}),
            ('div', {'class': 'card'}),
        ]

        for tag, attrs in selectors:
            if attrs:
                ads = soup.find_all(tag, attrs)
            else:
                ads = soup.find_all(tag)
                # Filtrer pour garder seulement ceux avec des liens
                ads = [a for a in ads if a.find('a', href=True)]

            if ads and len(ads) > 2:  # Au moins 3 pour éviter les faux positifs
                print(f"    📋 Sélecteur: {tag} {attrs}")
                return ads[:30]  # Limiter

        return []

    def _try_json_data(self, session, ville: str) -> List[Dict[str, Any]]:
        """Essaie de trouver des données JSON dans la page."""
        print("  🔄 Recherche données JSON...")
        listings = []

        try:
            # Certains sites incluent des données JSON dans la page
            url = f"https://immobilier.lefigaro.fr/annonces/immobilier-vente-bien-{ville.lower()}.html"
            response = session.get(url, timeout=15)

            if response.status_code == 200:
                # Chercher des scripts JSON-LD
                soup = BeautifulSoup(response.content, 'html.parser')
                scripts = soup.find_all('script', type='application/ld+json')

                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        print(f"    JSON-LD trouvé: {type(data)}")
                    except:
                        pass

        except Exception as e:
            print(f"    ⚠️ Erreur JSON: {e}")

        return listings

    def _extract_listing(self, ad_element, ville: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce."""
        try:
            link_elem = ad_element.find('a', href=True)
            if not link_elem:
                return None

            lien = link_elem.get('href', '')
            if lien and not lien.startswith('http'):
                lien = f"https://immobilier.lefigaro.fr{lien}"

            # Titre
            titre = None
            for tag in ['h2', 'h3', 'h4']:
                titre_elem = ad_element.find(tag)
                if titre_elem:
                    titre = titre_elem.get_text(strip=True)
                    break

            if not titre:
                titre = link_elem.get_text(strip=True)[:100] or "Annonce Figaro"

            # Prix
            prix = 0
            prix_elem = ad_element.find(string=re.compile(r'[\d\s]+€'))
            if prix_elem:
                prix = self._parse_price(prix_elem)
            else:
                for elem in ad_element.find_all(['span', 'div', 'p']):
                    text = elem.get_text()
                    if '€' in text:
                        prix = self._parse_price(text)
                        if prix > 10000:  # Prix réaliste
                            break

            # Localisation
            localisation = ville

            # Photo
            photos = []
            img = ad_element.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    photos.append(src)

            # Surface et pièces
            surface, pieces = self._extract_surface_pieces(titre + " " + ad_element.get_text())

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
            return None

    def _parse_price(self, price_text: str) -> int:
        try:
            price_clean = re.sub(r'[^\d]', '', str(price_text))
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
