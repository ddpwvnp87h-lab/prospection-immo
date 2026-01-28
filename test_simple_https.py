#!/usr/bin/env python3
"""
Test simple HTTPS scraping - Sans dépendances externes!
Utilise uniquement la bibliothèque standard Python
"""

import urllib.request
import json
from html.parser import HTMLParser
from datetime import datetime


class SimpleHTMLParser(HTMLParser):
    """Parser HTML simple pour extraire les données."""

    def __init__(self):
        super().__init__()
        self.in_price = False
        self.in_title = False
        self.prices = []
        self.titles = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Détecter les prix (contiennent souvent 'price' dans la classe)
        if 'class' in attrs_dict:
            class_name = attrs_dict['class'].lower()
            if 'price' in class_name or 'prix' in class_name:
                self.in_price = True
            if 'title' in class_name or 'titre' in class_name:
                self.in_title = True

        # Collecter les liens
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])

    def handle_data(self, data):
        data = data.strip()
        if self.in_price and data:
            self.prices.append(data)
        if self.in_title and data:
            self.titles.append(data)

    def handle_endtag(self, tag):
        self.in_price = False
        self.in_title = False


def test_https_request():
    """Teste une requête HTTPS réelle."""

    print("="*80)
    print("🌐 TEST HTTPS - Scraping avec bibliothèque standard Python")
    print("="*80)
    print()

    # URL de test - un site simple d'exemple
    test_urls = [
        "https://httpbin.org/html",  # Site de test HTTP
        "https://example.com",  # Site basique
    ]

    for url in test_urls:
        print(f"📡 Test #{test_urls.index(url) + 1}: {url}")
        print("-" * 80)

        try:
            # 1. Créer la requête avec headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)

            # 2. Envoyer la requête HTTPS
            print("  🔐 Connexion HTTPS...")
            with urllib.request.urlopen(req, timeout=10) as response:
                # 3. Lire la réponse
                print(f"  ✅ Status Code: {response.status}")
                print(f"  ✅ Content-Type: {response.headers.get('Content-Type', 'N/A')}")

                html_content = response.read().decode('utf-8')
                print(f"  ✅ Taille: {len(html_content):,} bytes")

                # 4. Parser le HTML
                parser = SimpleHTMLParser()
                parser.feed(html_content)

                # 5. Afficher les résultats
                print(f"\n  📊 Données extraites:")
                print(f"    • Liens trouvés: {len(parser.links)}")
                if parser.links[:3]:
                    for i, link in enumerate(parser.links[:3], 1):
                        print(f"      {i}. {link[:70]}")

                print(f"    • Titres trouvés: {len(parser.titles)}")
                if parser.titles[:3]:
                    for i, title in enumerate(parser.titles[:3], 1):
                        print(f"      {i}. {title[:70]}")

                print(f"    • Prix trouvés: {len(parser.prices)}")
                if parser.prices[:3]:
                    for i, price in enumerate(parser.prices[:3], 1):
                        print(f"      {i}. {price[:70]}")

        except Exception as e:
            print(f"  ❌ Erreur: {e}")

        print()


def demo_site_immobilier():
    """Montre comment ça marche pour un site immobilier."""

    print("="*80)
    print("🏠 DÉMO: Structure d'un scraper immobilier")
    print("="*80)
    print()

    print("📝 Workflow typique:")
    print("-" * 80)

    workflow = [
        ("1. URL de recherche", "https://www.pap.fr/annonce/vente-appartement-paris-75"),
        ("2. Requête HTTPS GET", "urllib.request.urlopen(url)"),
        ("3. Récupération HTML", "html = response.read().decode('utf-8')"),
        ("4. Parsing", "parser.feed(html)"),
        ("5. Extraction", "Trouve les divs avec class='annonce'"),
        ("6. Normalisation", "Crée un dict avec titre, prix, lien, etc."),
    ]

    for step, detail in workflow:
        print(f"  {step}")
        print(f"    → {detail}")

    print()
    print("📦 Exemple de données extraites:")
    print("-" * 80)

    example_listing = {
        "titre": "Appartement 3 pièces - 75m² - Paris 15ème",
        "date_publication": datetime.now().strftime('%Y-%m-%d'),
        "prix": 450000,
        "localisation": "Paris 15ème",
        "lien": "https://www.pap.fr/annonce/exemple-123456",
        "site_source": "pap.fr",
        "photos": [
            "https://www.pap.fr/photos/exemple1.jpg"
        ],
        "telephone": "Non visible",
        "surface": 75,
        "pieces": 3,
        "description": "Bel appartement lumineux..."
    }

    print(json.dumps(example_listing, indent=2, ensure_ascii=False))
    print()


def show_real_code():
    """Montre le code réel utilisé dans les scrapers."""

    print("="*80)
    print("💻 CODE RÉEL: Extrait de scrapers/pap.py")
    print("="*80)
    print()

    code = '''
# Dans scrapers/pap.py (lignes 35-60)

session = requests.Session()
session.headers.update({'User-Agent': self.user_agent})

# URL de recherche
url = f"https://www.pap.fr/annonce/vente-immobilier-{ville}"

# Requête HTTPS
response = session.get(url, timeout=15)
response.raise_for_status()

# Parsing HTML
soup = BeautifulSoup(response.content, 'lxml')

# Trouver les annonces
ads = soup.find_all('div', class_='search-list-item')

for ad in ads:
    # Extraire le titre
    titre_elem = ad.find('span', class_='item-title')
    titre = titre_elem.get_text(strip=True)

    # Extraire le prix
    prix_elem = ad.find('span', class_='item-price')
    prix = self._parse_price(prix_elem.get_text())

    # Extraire le lien
    link_elem = ad.find('a', href=True)
    lien = f"https://www.pap.fr{link_elem['href']}"

    # Créer l'objet annonce
    listing = {
        'titre': titre,
        'prix': prix,
        'lien': lien,
        ...
    }
'''

    print(code)
    print()


def main():
    """Point d'entrée."""

    print("\n" + "🎬 " * 20)
    print("DÉMONSTRATION: HTTPS Scraping en Python")
    print("🎬 " * 20 + "\n")

    # Test 1: Requête HTTPS basique
    test_https_request()

    # Test 2: Workflow immobilier
    demo_site_immobilier()

    # Test 3: Code réel
    show_real_code()

    print("="*80)
    print("🎯 CONCLUSION")
    print("="*80)
    print()
    print("✅ HTTPS fonctionne avec urllib (bibliothèque standard)")
    print("✅ Pour de vrais sites, utiliser requests + BeautifulSoup")
    print("✅ Les scrapers dans le projet utilisent:")
    print("   • requests pour HTTPS")
    print("   • BeautifulSoup pour parser HTML")
    print("   • Playwright pour JavaScript dynamique")
    print()
    print("💡 Pour installer et tester:")
    print("   pip3 install requests beautifulsoup4")
    print("   python3 test_scrapers.py --ville Paris --site pap")
    print()


if __name__ == '__main__':
    main()
