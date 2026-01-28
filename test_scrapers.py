#!/usr/bin/env python3
"""
Script de test pour les scrapers - sans base de données

Usage:
    python test_scrapers.py --ville Paris --site leboncoin
    python test_scrapers.py --ville Lyon --all
"""

import argparse
from scrapers import (
    LeboncoinScraper,
    PapScraper,
    FacebookMarketplaceScraper,
    FigaroImmoScraper
)
from utils import validate_listing, filter_agencies


def test_scraper(scraper, ville: str, rayon: int = 10, max_pages: int = 2):
    """Teste un scraper et affiche les résultats."""
    print(f"\n{'='*80}")
    print(f"🧪 Test du scraper: {scraper.site_name}")
    print(f"{'='*80}\n")

    try:
        # Scraper les annonces
        listings = scraper.scrape(ville, rayon, max_pages)

        print(f"\n📊 Résultats du scraping:")
        print(f"   - Total annonces: {len(listings)}")

        if listings:
            # Valider les annonces
            valid_count = sum(1 for l in listings if validate_listing(l))
            print(f"   - Annonces valides: {valid_count}")

            # Filtrer les agences
            particuliers = filter_agencies(listings)
            print(f"   - Annonces de particuliers: {len(particuliers)}")

            # Afficher quelques exemples
            print(f"\n📋 Exemples d'annonces (max 3):\n")
            for i, listing in enumerate(listings[:3], 1):
                print(f"   {i}. {listing.get('titre', 'N/A')[:60]}")
                print(f"      Prix: {listing.get('prix', 0):,} €")
                print(f"      Localisation: {listing.get('localisation', 'N/A')}")
                print(f"      Lien: {listing.get('lien', 'N/A')[:80]}")
                print(f"      Valide: {'✅' if validate_listing(listing) else '❌'}")
                print()

        else:
            print("   ⚠️  Aucune annonce trouvée")

        return len(listings)

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Test des scrapers immobiliers")
    parser.add_argument('--ville', type=str, required=True, help="Ville de recherche")
    parser.add_argument('--rayon', type=int, default=10, help="Rayon en km (défaut: 10)")
    parser.add_argument('--max-pages', type=int, default=2, help="Nombre max de pages (défaut: 2)")
    parser.add_argument('--site', type=str, choices=['leboncoin', 'pap', 'facebook', 'figaro'],
                        help="Site à tester (si non spécifié, teste tous)")
    parser.add_argument('--all', action='store_true', help="Tester tous les scrapers implémentés")

    args = parser.parse_args()

    print(f"\n{'='*80}")
    print(f"🧪 TEST DES SCRAPERS IMMOBILIERS")
    print(f"{'='*80}")
    print(f"📍 Ville: {args.ville}")
    print(f"📏 Rayon: {args.rayon} km")
    print(f"📄 Pages max par site: {args.max_pages}")
    print(f"{'='*80}")

    # Définir les scrapers à tester
    all_scrapers = {
        'leboncoin': LeboncoinScraper(),
        'pap': PapScraper(),
        'facebook': FacebookMarketplaceScraper(),
        'figaro': FigaroImmoScraper()
    }

    if args.site:
        # Tester un seul scraper
        scrapers_to_test = {args.site: all_scrapers[args.site]}
    elif args.all:
        # Tester tous les scrapers
        scrapers_to_test = all_scrapers
    else:
        # Par défaut, tester leboncoin et pap (les plus fiables)
        scrapers_to_test = {
            'leboncoin': all_scrapers['leboncoin'],
            'pap': all_scrapers['pap']
        }

    # Tester chaque scraper
    results = {}
    for name, scraper in scrapers_to_test.items():
        count = test_scraper(scraper, args.ville, args.rayon, args.max_pages)
        results[name] = count

    # Résumé final
    print(f"\n{'='*80}")
    print(f"📊 RÉSUMÉ DES TESTS")
    print(f"{'='*80}")
    for name, count in results.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {name}: {count} annonces")
    print(f"{'='*80}\n")

    total = sum(results.values())
    print(f"🎯 Total: {total} annonces trouvées")
    print()


if __name__ == '__main__':
    main()
