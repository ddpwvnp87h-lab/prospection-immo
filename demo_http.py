#!/usr/bin/env python3
"""
Démonstration du scraping HTTP avec requests + BeautifulSoup
Montre comment le scraping fonctionne étape par étape
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def demo_simple_http():
    """Exemple simple de requête HTTP et parsing HTML."""

    print("="*80)
    print("🌐 DÉMO: Scraping HTTP avec Requests + BeautifulSoup")
    print("="*80)
    print()

    # 1. Configuration
    print("📋 Étape 1: Configuration")
    print("-" * 80)

    url = "https://www.pap.fr/annonce/vente-appartement-paris-75"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    print(f"URL cible: {url}")
    print(f"User-Agent: {headers['User-Agent'][:50]}...")
    print()

    # 2. Requête HTTP
    print("📡 Étape 2: Envoi de la requête HTTP GET")
    print("-" * 80)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"✅ Taille de la réponse: {len(response.content):,} bytes")
        print()

        # 3. Parsing HTML
        print("🔍 Étape 3: Parsing du HTML avec BeautifulSoup")
        print("-" * 80)

        soup = BeautifulSoup(response.content, 'lxml')
        print(f"✅ Parser utilisé: lxml")
        print(f"✅ Title de la page: {soup.title.string if soup.title else 'N/A'}")
        print()

        # 4. Extraction des données (exemple générique)
        print("📊 Étape 4: Extraction des données")
        print("-" * 80)

        # Chercher des éléments typiques d'une page immobilière
        # (les sélecteurs varient selon le site)

        # Exemple: chercher tous les liens
        links = soup.find_all('a', href=True, limit=5)
        print(f"Liens trouvés (5 premiers):")
        for i, link in enumerate(links, 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"  {i}. {text} → {href[:60]}")
        print()

        # Exemple: chercher des prix (pattern commun)
        prices = soup.find_all(text=lambda text: text and '€' in str(text))
        print(f"Prix potentiels trouvés: {len(prices[:5])}")
        for i, price in enumerate(prices[:3], 1):
            print(f"  {i}. {str(price).strip()[:50]}")
        print()

        # 5. Structure de données normalisée
        print("📦 Étape 5: Structure de données normalisée")
        print("-" * 80)

        # Exemple de ce qu'on extrait vraiment
        example_listing = {
            "titre": "Appartement 3 pièces - 75m² - Paris 15ème",
            "date_publication": datetime.now().strftime('%Y-%m-%d'),
            "prix": 450000,
            "localisation": "Paris 15ème",
            "lien": "https://www.pap.fr/annonce/exemple-123456",
            "site_source": "pap.fr",
            "photos": [
                "https://www.pap.fr/photos/exemple1.jpg",
                "https://www.pap.fr/photos/exemple2.jpg"
            ],
            "telephone": None,
            "surface": 75,
            "pieces": 3,
            "description": "Bel appartement..."
        }

        print("Exemple de données extraites:")
        print(json.dumps(example_listing, indent=2, ensure_ascii=False))
        print()

    except requests.RequestException as e:
        print(f"❌ Erreur HTTP: {e}")
        print()
        return None

    print("="*80)
    print("✅ Démo terminée!")
    print("="*80)
    print()


def demo_with_selectors():
    """Exemple montrant les sélecteurs CSS."""

    print("="*80)
    print("🎯 DÉMO: Sélecteurs CSS pour l'extraction")
    print("="*80)
    print()

    # HTML d'exemple (simulé)
    example_html = """
    <html>
    <body>
        <div class="search-results">
            <article class="listing" data-id="12345">
                <h2 class="listing-title">Appartement 3 pièces - Paris</h2>
                <span class="price">450 000 €</span>
                <span class="location">Paris 15ème</span>
                <div class="details">
                    <span class="surface">75 m²</span>
                    <span class="rooms">3 pièces</span>
                </div>
                <a href="/annonce/12345" class="listing-link">Voir l'annonce</a>
                <img src="photo1.jpg" alt="Photo appartement">
            </article>

            <article class="listing" data-id="67890">
                <h2 class="listing-title">Maison 5 pièces - Lyon</h2>
                <span class="price">650 000 €</span>
                <span class="location">Lyon 6ème</span>
                <div class="details">
                    <span class="surface">120 m²</span>
                    <span class="rooms">5 pièces</span>
                </div>
                <a href="/annonce/67890" class="listing-link">Voir l'annonce</a>
                <img src="photo2.jpg" alt="Photo maison">
            </article>
        </div>
    </body>
    </html>
    """

    soup = BeautifulSoup(example_html, 'lxml')

    print("📝 HTML d'exemple chargé")
    print()

    # Démonstration des sélecteurs
    print("🔍 Sélecteurs CSS utilisés:")
    print("-" * 80)

    # 1. Trouver toutes les annonces
    listings = soup.find_all('article', class_='listing')
    print(f"1. soup.find_all('article', class_='listing')")
    print(f"   → {len(listings)} annonces trouvées")
    print()

    # 2. Pour chaque annonce, extraire les données
    for i, listing in enumerate(listings, 1):
        print(f"Annonce #{i}:")

        # Titre
        title = listing.find('h2', class_='listing-title')
        print(f"  • Titre: {title.get_text(strip=True) if title else 'N/A'}")

        # Prix
        price = listing.find('span', class_='price')
        print(f"  • Prix: {price.get_text(strip=True) if price else 'N/A'}")

        # Localisation
        location = listing.find('span', class_='location')
        print(f"  • Localisation: {location.get_text(strip=True) if location else 'N/A'}")

        # Surface
        surface = listing.find('span', class_='surface')
        print(f"  • Surface: {surface.get_text(strip=True) if surface else 'N/A'}")

        # Lien
        link = listing.find('a', class_='listing-link')
        print(f"  • Lien: {link.get('href') if link else 'N/A'}")

        # Photo
        img = listing.find('img')
        print(f"  • Photo: {img.get('src') if img else 'N/A'}")

        print()


def demo_comparison():
    """Comparaison Requests vs Playwright."""

    print("="*80)
    print("⚖️  COMPARAISON: Requests vs Playwright")
    print("="*80)
    print()

    comparison = {
        "Requests + BeautifulSoup": {
            "Avantages": [
                "✅ Rapide (pas de navigateur)",
                "✅ Léger en mémoire",
                "✅ Simple à utiliser",
                "✅ Parfait pour HTML statique"
            ],
            "Inconvénients": [
                "❌ Pas de JavaScript",
                "❌ Pas de contenu dynamique",
                "❌ Pas de rendu CSS"
            ],
            "Utilisé pour": [
                "pap.fr",
                "figaro-immo.fr"
            ]
        },
        "Playwright": {
            "Avantages": [
                "✅ Exécute JavaScript",
                "✅ Contenu dynamique",
                "✅ Scroll, clics, interactions",
                "✅ Screenshots possibles"
            ],
            "Inconvénients": [
                "❌ Plus lent",
                "❌ Plus de mémoire",
                "❌ Installation navigateur requise"
            ],
            "Utilisé pour": [
                "leboncoin.fr",
                "facebook.com/marketplace"
            ]
        }
    }

    for method, details in comparison.items():
        print(f"📌 {method}")
        print("-" * 80)

        print("\n🟢 Avantages:")
        for adv in details["Avantages"]:
            print(f"   {adv}")

        print("\n🔴 Inconvénients:")
        for dis in details["Inconvénients"]:
            print(f"   {dis}")

        print(f"\n🎯 Utilisé pour:")
        for site in details["Utilisé pour"]:
            print(f"   • {site}")

        print("\n")


def main():
    """Point d'entrée de la démo."""

    print("\n" + "🎬 " * 20)
    print("DÉMONSTRATION: Comment fonctionne le scraping HTTP")
    print("🎬 " * 20 + "\n")

    # Menu
    print("Choisissez une démo:")
    print("  1. Démo simple HTTP (requête réelle)")
    print("  2. Démo sélecteurs CSS (HTML d'exemple)")
    print("  3. Comparaison Requests vs Playwright")
    print("  4. Tout montrer")
    print()

    choice = input("Votre choix (1-4): ").strip()
    print()

    if choice == "1":
        demo_simple_http()
    elif choice == "2":
        demo_with_selectors()
    elif choice == "3":
        demo_comparison()
    elif choice == "4":
        demo_simple_http()
        demo_with_selectors()
        demo_comparison()
    else:
        print("❌ Choix invalide")

    print("\n💡 Pour scraper vraiment:")
    print("   python test_scrapers.py --ville Paris --site pap")
    print()


if __name__ == '__main__':
    main()
