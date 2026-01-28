from typing import List, Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
import re
from .base import BaseScraper


class LeboncoinScraper(BaseScraper):
    """Scraper pour leboncoin.fr"""

    @property
    def site_name(self) -> str:
        return "leboncoin.fr"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape les annonces immobilières de leboncoin.fr

        Args:
            ville: Ville de recherche
            rayon: Rayon en km
            max_pages: Nombre max de pages

        Returns:
            Liste d'annonces normalisées
        """
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")

        listings = []

        try:
            with sync_playwright() as p:
                # Lancer le navigateur en mode headless
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                # Construire l'URL de recherche
                # Category 9 = Immobilier vente
                base_url = f"https://www.leboncoin.fr/recherche?category=9&text={ville}"

                for page_num in range(max_pages):
                    url = f"{base_url}&page={page_num + 1}" if page_num > 0 else base_url

                    try:
                        print(f"  📄 Page {page_num + 1}/{max_pages}...")
                        page.goto(url, timeout=30000, wait_until='networkidle')

                        # Attendre que les annonces soient chargées
                        page.wait_for_selector('[data-qa-id="aditem_container"]', timeout=10000)

                        # Extraire les annonces de la page
                        ads = page.query_selector_all('[data-qa-id="aditem_container"]')

                        for ad in ads:
                            try:
                                listing = self._extract_listing(ad, page)
                                if listing:
                                    listings.append(listing)
                            except Exception as e:
                                print(f"    ⚠️  Erreur extraction annonce: {e}")
                                continue

                        # Attendre entre les pages
                        self._wait()

                    except PlaywrightTimeout:
                        print(f"    ⏱️  Timeout sur la page {page_num + 1}")
                        break
                    except Exception as e:
                        print(f"    ⚠️  Erreur page {page_num + 1}: {e}")
                        break

                browser.close()

        except Exception as e:
            print(f"⚠️  Erreur générale leboncoin: {e}")

        self._print_stats(listings)
        return listings

    def _extract_listing(self, ad_element, page) -> Dict[str, Any]:
        """Extrait les données d'une annonce."""
        try:
            # Lien de l'annonce
            link_elem = ad_element.query_selector('a[data-qa-id="aditem_link"]')
            if not link_elem:
                return None

            lien = "https://www.leboncoin.fr" + link_elem.get_attribute('href')

            # Titre
            titre_elem = ad_element.query_selector('[data-qa-id="aditem_title"]')
            titre = titre_elem.inner_text().strip() if titre_elem else "Titre inconnu"

            # Prix
            prix_elem = ad_element.query_selector('[data-qa-id="aditem_price"]')
            prix_text = prix_elem.inner_text().strip() if prix_elem else "0"
            prix = self._parse_price(prix_text)

            # Localisation
            location_elem = ad_element.query_selector('[data-qa-id="aditem_location"]')
            localisation = location_elem.inner_text().strip() if location_elem else ville

            # Date de publication
            date_elem = ad_element.query_selector('[data-qa-id="aditem_date"]')
            date_text = date_elem.inner_text().strip() if date_elem else ""
            date_publication = self._parse_date(date_text)

            # Photos (prendre la première image)
            photos = []
            img_elem = ad_element.query_selector('img')
            if img_elem:
                img_src = img_elem.get_attribute('src')
                if img_src:
                    photos.append(img_src)

            # Vérifier si c'est un pro (agence)
            is_pro = ad_element.query_selector('[data-qa-id="aditem_pro"]') is not None

            # Si c'est un pro, on le marque mais on laisse le filtre global s'en occuper
            description = "PRO" if is_pro else ""

            return {
                'titre': titre,
                'date_publication': date_publication,
                'prix': prix,
                'localisation': localisation,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,  # Pas accessible sans ouvrir l'annonce
                'surface': None,    # Nécessiterait de parser le titre/description
                'pieces': None,     # Nécessiterait de parser le titre/description
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

    def _parse_date(self, date_text: str) -> str:
        """Parse la date de publication."""
        today = datetime.now()

        # Leboncoin affiche "Aujourd'hui", "Hier", ou une date
        if "aujourd'hui" in date_text.lower() or "aujourd hui" in date_text.lower():
            return today.strftime('%Y-%m-%d')
        elif "hier" in date_text.lower():
            yesterday = today.replace(day=today.day - 1)
            return yesterday.strftime('%Y-%m-%d')
        else:
            # Essayer de parser la date (format peut varier)
            # Pour l'instant, retourner la date du jour
            return today.strftime('%Y-%m-%d')
