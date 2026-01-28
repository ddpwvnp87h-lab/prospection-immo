from typing import List, Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
import re
from .base import BaseScraper


class FacebookMarketplaceScraper(BaseScraper):
    """Scraper pour Facebook Marketplace - Immobilier"""

    @property
    def site_name(self) -> str:
        return "facebook.com/marketplace"

    def scrape(self, ville: str, rayon: int, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape les annonces immobilières de Facebook Marketplace

        NOTE: Facebook peut bloquer le scraping ou demander une connexion.
        Ce scraper est à utiliser avec prudence.

        Args:
            ville: Ville de recherche
            rayon: Rayon en km
            max_pages: Nombre max de pages

        Returns:
            Liste d'annonces normalisées
        """
        print(f"🔍 Scraping {self.site_name} pour {ville} (rayon: {rayon}km)")
        print(f"    ⚠️  Facebook peut bloquer le scraping - utiliser avec prudence")

        listings = []

        try:
            with sync_playwright() as p:
                # Lancer le navigateur
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.user_agent,
                    viewport={'width': 1920, 'height': 1080},
                    locale='fr-FR'
                )
                page = context.new_page()

                # Construire l'URL de recherche
                # Format: /marketplace/{ville}/propertyrentals ou /propertyforsale
                # Simplifié: recherche générale immobilier
                base_url = f"https://www.facebook.com/marketplace/{ville.lower()}/search"
                params = "?query=appartement%20maison&exact=false"

                try:
                    print(f"  📄 Chargement de la page...")
                    page.goto(base_url + params, timeout=30000, wait_until='domcontentloaded')

                    # Attendre un peu pour le chargement dynamique
                    page.wait_for_timeout(3000)

                    # Scroll pour charger plus d'annonces
                    for scroll in range(max_pages):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2000)

                    # Extraire les annonces
                    # NOTE: Les sélecteurs Facebook changent fréquemment
                    # Ceci est un exemple qui peut nécessiter des ajustements
                    ads = page.query_selector_all('[data-testid="marketplace-card"]') or \
                          page.query_selector_all('div[role="article"]')

                    print(f"  📊 {len(ads)} annonces potentielles trouvées")

                    for ad in ads:
                        try:
                            listing = self._extract_listing(ad, ville)
                            if listing:
                                listings.append(listing)
                        except Exception as e:
                            print(f"    ⚠️  Erreur extraction annonce: {e}")
                            continue

                except PlaywrightTimeout:
                    print(f"    ⏱️  Timeout - Facebook peut bloquer le scraping")
                except Exception as e:
                    print(f"    ⚠️  Erreur: {e}")

                browser.close()

        except Exception as e:
            print(f"⚠️  Erreur générale Facebook Marketplace: {e}")

        self._print_stats(listings)
        return listings

    def _extract_listing(self, ad_element, ville: str) -> Dict[str, Any]:
        """Extrait les données d'une annonce."""
        try:
            # Lien de l'annonce
            link_elem = ad_element.query_selector('a[href*="/marketplace/item/"]')
            if not link_elem:
                return None

            href = link_elem.get_attribute('href')
            lien = f"https://www.facebook.com{href}" if href.startswith('/') else href

            # Titre (span avec attribut dir="auto")
            titre_elem = ad_element.query_selector('span[dir="auto"]')
            titre = titre_elem.inner_text().strip() if titre_elem else "Titre inconnu"

            # Prix
            prix_elems = ad_element.query_selector_all('span')
            prix = 0
            for elem in prix_elems:
                text = elem.inner_text().strip()
                if '€' in text or 'EUR' in text:
                    prix = self._parse_price(text)
                    break

            # Localisation (souvent dans un span après le prix)
            localisation = ville
            location_elems = ad_element.query_selector_all('span')
            for elem in location_elems:
                text = elem.inner_text().strip()
                # Chercher un texte qui ressemble à une ville
                if len(text) > 3 and len(text) < 50 and not '€' in text and not text.isdigit():
                    localisation = text
                    break

            # Date de publication
            date_publication = datetime.now().strftime('%Y-%m-%d')

            # Photos
            photos = []
            img_elem = ad_element.query_selector('img')
            if img_elem:
                img_src = img_elem.get_attribute('src')
                if img_src and 'http' in img_src:
                    photos.append(img_src)

            return {
                'titre': titre,
                'date_publication': date_publication,
                'prix': prix,
                'localisation': localisation,
                'lien': lien,
                'site_source': self.site_name,
                'photos': photos,
                'telephone': None,
                'surface': None,
                'pieces': None,
                'description': ""
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
