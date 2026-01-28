#!/usr/bin/env python3
"""
SCRAPER LITE - Prêt à l'emploi!
Fonctionne avec Python standard - AUCUNE installation requise!

Usage:
    python3 scraper_lite.py Paris
    python3 scraper_lite.py Lyon --json
"""

import urllib.request
import urllib.parse
import json
import re
import sys
from html.parser import HTMLParser
from datetime import datetime


class AnnonceLiteParser(HTMLParser):
    """Parser HTML léger pour extraire les annonces."""

    def __init__(self):
        super().__init__()
        self.annonces = []
        self.current_annonce = None
        self.in_title = False
        self.in_price = False
        self.in_location = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Détecter le début d'une annonce
        if tag in ['article', 'div']:
            if 'class' in attrs_dict:
                class_name = attrs_dict.get('class', '').lower()
                if any(keyword in class_name for keyword in ['annonce', 'listing', 'card', 'item']):
                    self.current_annonce = {
                        'titre': '',
                        'prix': '',
                        'localisation': '',
                        'lien': '',
                        'photos': []
                    }

        # Liens
        if tag == 'a' and 'href' in attrs_dict and self.current_annonce is not None:
            href = attrs_dict['href']
            if self.current_annonce['lien'] == '':
                self.current_annonce['lien'] = href

        # Images
        if tag == 'img' and self.current_annonce is not None:
            src = attrs_dict.get('src', '') or attrs_dict.get('data-src', '')
            if src and 'http' in src:
                self.current_annonce['photos'].append(src)

        # Détecter les zones de texte
        if 'class' in attrs_dict:
            class_name = attrs_dict.get('class', '').lower()
            if any(keyword in class_name for keyword in ['title', 'titre', 'heading']):
                self.in_title = True
            if any(keyword in class_name for keyword in ['price', 'prix', 'amount']):
                self.in_price = True
            if any(keyword in class_name for keyword in ['location', 'ville', 'city', 'place']):
                self.in_location = True

    def handle_data(self, data):
        data = data.strip()
        if not data or self.current_annonce is None:
            return

        if self.in_title and len(data) > 5:
            self.current_annonce['titre'] = data
        if self.in_price and ('€' in data or 'EUR' in data or data.replace(' ', '').isdigit()):
            self.current_annonce['prix'] = data
        if self.in_location and len(data) > 2:
            self.current_annonce['localisation'] = data

    def handle_endtag(self, tag):
        self.in_title = False
        self.in_price = False
        self.in_location = False

        # Fin d'une annonce
        if tag in ['article', 'div'] and self.current_annonce is not None:
            # Si l'annonce a au moins un titre ou un prix, on la garde
            if self.current_annonce['titre'] or self.current_annonce['prix']:
                self.annonces.append(self.current_annonce.copy())
            self.current_annonce = None


def scraper_lite(ville, source='example'):
    """
    Scraper ultra-léger - fonctionne sans dépendances!

    Args:
        ville: Ville à rechercher
        source: Source (example, httpbin, custom)

    Returns:
        Liste d'annonces simulées ou réelles
    """
    print(f"🔍 Scraping pour: {ville}")
    print(f"📍 Source: {source}")
    print("-" * 60)

    if source == 'example':
        # Mode démo - données simulées
        return generer_annonces_demo(ville)

    elif source == 'real':
        # Mode réel - scraping HTTP (nécessite connexion)
        return scraper_http_real(ville)

    else:
        return []


def generer_annonces_demo(ville):
    """Génère des annonces de démo pour tester."""

    print("📊 Mode DÉMO - Génération d'annonces simulées\n")

    annonces = [
        {
            'titre': f'Appartement 3 pièces - {ville} Centre',
            'prix': '450 000 €',
            'localisation': f'{ville} 1er',
            'lien': 'https://www.pap.fr/annonce/demo-001',
            'surface': 75,
            'pieces': 3,
            'photos': ['https://example.com/photo1.jpg'],
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'site_source': 'demo'
        },
        {
            'titre': f'Maison 5 pièces avec jardin - {ville}',
            'prix': '680 000 €',
            'localisation': f'{ville} Ouest',
            'lien': 'https://www.pap.fr/annonce/demo-002',
            'surface': 120,
            'pieces': 5,
            'photos': ['https://example.com/photo2.jpg'],
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'site_source': 'demo'
        },
        {
            'titre': f'Studio - {ville} Quartier Latin',
            'prix': '220 000 €',
            'localisation': f'{ville} 5ème',
            'lien': 'https://www.leboncoin.fr/annonce/demo-003',
            'surface': 25,
            'pieces': 1,
            'photos': ['https://example.com/photo3.jpg'],
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'site_source': 'demo'
        },
        {
            'titre': f'Appartement 2 pièces rénové - {ville}',
            'prix': '380 000 €',
            'localisation': f'{ville} Nord',
            'lien': 'https://www.pap.fr/annonce/demo-004',
            'surface': 55,
            'pieces': 2,
            'photos': ['https://example.com/photo4.jpg'],
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'site_source': 'demo'
        },
        {
            'titre': f'Loft industriel - {ville} Gare',
            'prix': '520 000 €',
            'localisation': f'{ville} Centre',
            'lien': 'https://www.leboncoin.fr/annonce/demo-005',
            'surface': 95,
            'pieces': 3,
            'photos': ['https://example.com/photo5.jpg'],
            'date_publication': datetime.now().strftime('%Y-%m-%d'),
            'site_source': 'demo'
        }
    ]

    return annonces


def scraper_http_real(ville):
    """Scraper HTTP réel (version basique)."""

    print("🌐 Mode RÉEL - Scraping HTTP\n")

    # URL de test (remplacer par vrai site)
    ville_formatted = urllib.parse.quote(ville.lower())
    url = f"https://www.example.com/search?ville={ville_formatted}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        print(f"  📡 Requête: {url}")

        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8')
            print(f"  ✅ HTML reçu: {len(html_content):,} bytes")

            # Parser le HTML
            parser = AnnonceLiteParser()
            parser.feed(html_content)

            return parser.annonces

    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print(f"  💡 Utilisation du mode démo à la place")
        return generer_annonces_demo(ville)


def afficher_annonces(annonces, format='text'):
    """Affiche les annonces."""

    if format == 'json':
        print(json.dumps(annonces, indent=2, ensure_ascii=False))
        return

    # Format texte
    print(f"\n{'='*60}")
    print(f"📊 {len(annonces)} ANNONCES TROUVÉES")
    print(f"{'='*60}\n")

    for i, annonce in enumerate(annonces, 1):
        print(f"🏠 Annonce #{i}")
        print(f"   Titre: {annonce.get('titre', 'N/A')}")
        print(f"   Prix: {annonce.get('prix', 'N/A')}")
        print(f"   Localisation: {annonce.get('localisation', 'N/A')}")
        print(f"   Surface: {annonce.get('surface', 'N/A')} m²")
        print(f"   Pièces: {annonce.get('pieces', 'N/A')}")
        print(f"   Lien: {annonce.get('lien', 'N/A')[:60]}")
        print(f"   Source: {annonce.get('site_source', 'N/A')}")
        print()


def sauvegarder_json(annonces, ville):
    """Sauvegarde les annonces en JSON."""

    filename = f"annonces_{ville.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    data = {
        'ville': ville,
        'date': datetime.now().isoformat(),
        'total': len(annonces),
        'annonces': annonces
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Sauvegardé: {filename}")
    return filename


def main():
    """Point d'entrée."""

    print("\n" + "🏠 " * 20)
    print("SCRAPER LITE - Prospection Immobilière")
    print("Prêt à l'emploi - Aucune installation requise!")
    print("🏠 " * 20 + "\n")

    # Parser les arguments
    if len(sys.argv) < 2:
        print("❌ Usage: python3 scraper_lite.py VILLE [--json] [--save] [--real]")
        print("\nExemples:")
        print("  python3 scraper_lite.py Paris")
        print("  python3 scraper_lite.py Lyon --json")
        print("  python3 scraper_lite.py Marseille --save")
        print("  python3 scraper_lite.py Nice --real  # Scraping HTTP réel")
        sys.exit(1)

    ville = sys.argv[1]
    args = sys.argv[2:]

    # Options
    format_json = '--json' in args
    save = '--save' in args
    real = '--real' in args

    # Scraper
    source = 'real' if real else 'example'
    annonces = scraper_lite(ville, source=source)

    # Afficher
    afficher_annonces(annonces, format='json' if format_json else 'text')

    # Sauvegarder
    if save:
        sauvegarder_json(annonces, ville)

    # Statistiques
    print(f"{'='*60}")
    print(f"✅ Terminé!")
    print(f"   📍 Ville: {ville}")
    print(f"   📊 Total: {len(annonces)} annonces")
    print(f"   ⏱️  Mode: {'Réel (HTTP)' if real else 'Démo (simulé)'}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
