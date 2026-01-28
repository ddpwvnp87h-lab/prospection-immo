#!/usr/bin/env python3
"""
Point d'entrée principal pour la prospection immobilière.

Usage:
    python main.py --user-id USER_ID --ville VILLE [--rayon RAYON]
    python main.py --cleanup --user-id USER_ID
"""

import argparse
import os
from dotenv import load_dotenv
from database import DatabaseManager
from scrapers import (
    LeboncoinScraper,
    PapScraper,
    ParuvenduScraper,
    LogicImmoScraper,
    BieniciScraper,
    SelogerScraper,
    FacebookMarketplaceScraper,
    FigaroImmoScraper
)
from utils import (
    validate_listing,
    deduplicate_by_url,
    deduplicate_by_signature,
    filter_agencies
)
from config import MAX_PAGES_PER_SITE


def main():
    """Point d'entrée principal."""
    load_dotenv()

    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ Erreur: SUPABASE_URL et SUPABASE_KEY doivent être définis dans .env")
        return

    parser = argparse.ArgumentParser(description="Prospection Immo Team Maureen")
    parser.add_argument('--user-id', type=str, required=True, help="ID de l'utilisateur")
    parser.add_argument('--ville', type=str, help="Ville de recherche")
    parser.add_argument('--rayon', type=int, default=10, help="Rayon en km (défaut: 10)")
    parser.add_argument('--max-pages', type=int, default=MAX_PAGES_PER_SITE)
    parser.add_argument('--cleanup', action='store_true', help="Nettoyage uniquement")
    parser.add_argument('--sites', type=str, nargs='+',
                        choices=['leboncoin', 'pap', 'paruvendu', 'logic-immo', 'bienici', 'seloger', 'facebook', 'figaro'])

    args = parser.parse_args()

    try:
        db_manager = DatabaseManager()
    except ValueError as e:
        print(f"❌ Erreur: {e}")
        return

    if args.cleanup:
        run_cleanup(db_manager, args.user_id)
    else:
        if not args.ville:
            print("❌ Erreur: --ville requis")
            return
        run_prospection(db_manager, args.user_id, args.ville, args.rayon, args.max_pages, args.sites)


def run_prospection(db_manager, user_id, ville, rayon, max_pages, selected_sites=None):
    print(f"\n{'='*60}")
    print(f"🚀 Prospection Immo Team Maureen")
    print(f"👤 Utilisateur: {user_id} | 📍 Ville: {ville} | 📏 Rayon: {rayon} km")
    print(f"{'='*60}\n")

    all_scrapers = {
        'leboncoin': LeboncoinScraper(),
        'pap': PapScraper(),
        'paruvendu': ParuvenduScraper(),
        'logic-immo': LogicImmoScraper(),
        'bienici': BieniciScraper(),
        'seloger': SelogerScraper(),
        'facebook': FacebookMarketplaceScraper(),
        'figaro': FigaroImmoScraper()
    }

    scrapers = {n: s for n, s in all_scrapers.items() if not selected_sites or n in selected_sites}

    print("📡 Étape 1/4: Scraping...\n")
    all_listings = []
    for name, scraper in scrapers.items():
        try:
            listings = scraper.scrape(ville, rayon, max_pages)
            all_listings.extend(listings)
        except Exception as e:
            print(f"⚠️  Erreur {name}: {e}")

    print(f"\n📊 Total: {len(all_listings)} annonces\n")
    if not all_listings:
        print("❌ Aucune annonce trouvée")
        return

    print("✅ Étape 2/4: Validation...\n")
    valid_listings = [l for l in all_listings if validate_listing(l)]
    print(f"✅ {len(valid_listings)} valides\n")

    print("🔍 Étape 3/4: Filtrage et déduplication...\n")
    particulier_listings = filter_agencies(valid_listings)
    dedup_url = deduplicate_by_url(particulier_listings)
    final_listings = deduplicate_by_signature(dedup_url)
    print(f"✅ {len(final_listings)} uniques\n")

    print("💾 Étape 4/4: Stockage...\n")
    result = db_manager.insert_listings(user_id, final_listings)

    print("\n🧹 Nettoyage...\n")
    deleted = db_manager.cleanup(user_id)

    print(f"\n{'='*60}")
    print("✅ Prospection terminée!")
    print(f"📊 Stats: {result['added']} ajoutées | {result['duplicates']} doublons | {deleted} nettoyées")
    print(f"{'='*60}\n")


def run_cleanup(db_manager, user_id):
    print(f"\n{'='*60}")
    print(f"🧹 Nettoyage - Utilisateur: {user_id}")
    print(f"{'='*60}\n")
    deleted = db_manager.cleanup(user_id)
    print(f"\n✅ {deleted} annonces supprimées\n")


if __name__ == '__main__':
    main()
