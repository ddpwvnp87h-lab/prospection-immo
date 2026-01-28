from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from .base import BaseScraper


class PapScraper(BaseScraper):
    """Scraper pour pap.fr (De Particulier À Particulier)"""

    @property
    def site_name(self) -> str:
        return "pap.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape les annonces immobilières de pap.fr avec requests + BeautifulSoup

        Args:
            ville: Ville de recherche
            rayon: Rayon en km
            max_pages: Nombre max de pages

        Returns:
            Liste d'annonces normalisées
        """
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []
        session = requests.Session()
        session.headers.update({'User-Agent': self.user_agent})

        # Construire l'URL de recherche
        # pap.fr utilise des codes de villes, pour simplifier on fait une recherche texte
        base_url = f"https://www.pap.fr/annonce/vente-immobilier-{ville.lower().replace(' ', '-')}"

        try:
            for page_num in range(max_pages):
                url = f"{base_url}?p={page_num + 1}" if page_num > 0 else base_url

                try:
                    print(f"  📄 Page {page_num + 1}/{max_pages}...")
                    response = session.get(url, timeout=15)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Trouver les annonces (les sélecteurs peuvent varier)
                    # PAP utilise généralement des classes comme 'search-list-item'
                    ads = soup.find_all('div', class_='search-list-item')

                    if not ads:
                        # Essayer un autre sélecteur
                        ads = soup.find_all('article', class_='annonce')

                    if not ads:
                        print(f"    ⚠️  Aucune annonce trouvée sur la page {page_num + 1}")
                        break

                    for ad in ads:
                        try:
                            listing = self._extract_listing(ad, ville)
                            if listing:
                                listings.append(listing)
                        except Exception as e:
                            print(f"    ⚠️  Erreur extraction annonce: {e}")
                            continue

                    # Attendre entre les pages
                    self._wait()

                except requests.RequestException as e:
                    print(f"    ⚠️  Erreur requête page {page_num + 1}: {e}")
                    break
                except Exception as e:
                    print(f"    ⚠️  Erreur page {page_num + 1}: {e}")
                    break

        except Exception as e:
            print(f"⚠️  Erreur générale pap.fr: {e}")

        self._print_stats(listings)
        return listings

    def _extract_listing(self, ad_element, ville: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce."""
        try:
            # Lien de l'annonce
            link_elem = ad_element.find('a', class_='item-title')
            if not link_elem:
                link_elem = ad_element.find('a', href=True)

            if not link_elem:
                return None

            lien = link_elem.get('href', '')
            if lien and not lien.startswith('http'):
                lien = f"https://www.pap.fr{lien}"

            # Titre
            titre_elem = ad_element.find('span', class_='item-title') or ad_element.find('h2')
            titre = titre_elem.get_text(strip=True) if titre_elem else "Titre inconnu"

            # Prix
            prix_elem = ad_element.find('span', class_='item-price') or ad_element.find('span', class_='price')
            prix_text = prix_elem.get_text(strip=True) if prix_elem else "0"
            prix = self._parse_price(prix_text)

            # Localisation
            location_elem = ad_element.find('span', class_='item-location') or ad_element.find('span', class_='ville')
            localisation = location_elem.get_text(strip=True) if location_elem else ville

            # Date de publication (pas toujours disponible sur la page de liste)
            date_publication = datetime.now().strftime('%Y-%m-%d')

            # Photos
            photos = []
            img_elem = ad_element.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    photos.append(img_src)

            # Surface et pièces (souvent dans le titre ou description)
            surface, pieces = self._extract_surface_pieces(titre)

            # Description courte
            desc_elem = ad_element.find('span', class_='item-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            return {
                'titre': titre,
                'date_publication': date_publication,
                'prix': prix,
                'localisation': localisation,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,  # Pas accessible sans ouvrir l'annonce
                'surface': surface,
                'pieces': pieces,
                'description': description
            }

        except Exception as e:
            print(f"      ⚠️  Erreur extraction détails: {e}")
            return None

    def _parse_price(self, price_text: str) -> int:
        """Parse le prix depuis le texte."""
        try:
            # Enlever tout sauf les chiffres
            price_clean = re.sub(r'[^\d]', '', price_text)
            return int(price_clean) if price_clean else 0
        except:
            return 0

    def _extract_surface_pieces(self, text: str):
        """Extrait la surface et le nombre de pièces depuis le texte."""
        surface = None
        pieces = None

        # Chercher surface (ex: "75 m²", "75m2")
        surface_match = re.search(r'(\d+)\s*m[²2]', text, re.IGNORECASE)
        if surface_match:
            surface = int(surface_match.group(1))

        # Chercher pièces (ex: "3 pièces", "T3", "F3")
        pieces_match = re.search(r'(\d+)\s*pièces?|[TF](\d+)', text, re.IGNORECASE)
        if pieces_match:
            pieces = int(pieces_match.group(1) or pieces_match.group(2))

        return surface, pieces
