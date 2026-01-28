#!/usr/bin/env python3
"""
Script de test du scraping anti-blocage V3.
Lance un test rapide sur chaque scraper pour vérifier le bon fonctionnement.
"""

import sys
import time

def test_imports():
    """Teste que tous les imports fonctionnent."""
    print("=" * 60)
    print("TEST DES IMPORTS")
    print("=" * 60)

    try:
        from scrapers.base import BaseScraper
        print("✅ BaseScraper")
    except Exception as e:
        print(f"❌ BaseScraper: {e}")
        return False

    try:
        from scrapers.headers.factory import HeaderFactory
        print("✅ HeaderFactory")
    except Exception as e:
        print(f"❌ HeaderFactory: {e}")
        return False

    try:
        from scrapers.timing import HumanTimer, get_timer
        print("✅ HumanTimer")
    except Exception as e:
        print(f"❌ HumanTimer: {e}")
        return False

    try:
        from scrapers.http_client import StealthSession, is_stealth_available
        print(f"✅ StealthSession (curl_cffi: {is_stealth_available()})")
    except Exception as e:
        print(f"❌ StealthSession: {e}")
        return False

    try:
        from utils.geo_validator import haversine, validate_listing_location
        # Test haversine Paris -> Marseille
        distance = haversine(48.8566, 2.3522, 43.2965, 5.3698)
        print(f"✅ GeoValidator (Paris->Marseille: {distance:.0f}km)")
    except Exception as e:
        print(f"❌ GeoValidator: {e}")
        return False

    try:
        from scrapers.site_config import SITE_PROFILES, get_profile
        print(f"✅ SiteConfig ({len(SITE_PROFILES)} sites)")
        for key, profile in SITE_PROFILES.items():
            status = "✅" if profile.enabled else "❌"
            print(f"   {status} {key}: RPS={profile.rps}, max_pages={profile.max_pages}")
    except Exception as e:
        print(f"❌ SiteConfig: {e}")
        return False

    return True


def test_headers():
    """Teste la génération de headers."""
    print("\n" + "=" * 60)
    print("TEST DES HEADERS")
    print("=" * 60)

    from scrapers.headers.factory import HeaderFactory

    factory = HeaderFactory(rotate=True)
    headers = factory.get_initial_headers('https://www.pap.fr/')

    # Headers obligatoires pour tous les navigateurs
    required_headers = [
        'User-Agent',
        'Accept',
        'Accept-Language',
        'Referer',
    ]

    # Headers spécifiques Chrome (optionnels pour Safari/Firefox)
    chrome_headers = [
        'sec-ch-ua',
        'Sec-Fetch-Dest',
        'Sec-Fetch-Mode',
    ]

    profile_name = factory.get_current_profile_name()
    is_chrome = 'Chrome' in profile_name
    print(f"Profil: {profile_name}")
    print(f"Headers générés: {len(headers)}")

    all_ok = True
    for h in required_headers:
        if h in headers:
            print(f"  ✅ {h}: {headers[h][:50]}...")
        else:
            print(f"  ❌ {h}: MANQUANT")
            all_ok = False

    for h in chrome_headers:
        if h in headers:
            print(f"  ✅ {h}: {headers[h][:50]}...")
        else:
            if is_chrome:
                print(f"  ❌ {h}: MANQUANT (requis pour Chrome)")
                all_ok = False
            else:
                print(f"  ⚠️ {h}: absent (normal pour {profile_name})")

    return all_ok


def test_timing():
    """Teste le timing humain."""
    print("\n" + "=" * 60)
    print("TEST DU TIMING")
    print("=" * 60)

    from scrapers.timing import HumanTimer

    timer = HumanTimer('leboncoin')
    print(f"Profil: leboncoin")
    print(f"Min delay: {timer.profile.min_delay}s")
    print(f"Max delay: {timer.profile.max_delay}s")

    # Test 3 délais
    print("Test de 3 délais (peut prendre ~10s)...")
    delays = []
    for i in range(3):
        start = time.time()
        timer.wait_before_request()
        delay = time.time() - start
        delays.append(delay)
        print(f"  Délai {i+1}: {delay:.2f}s")

    avg = sum(delays) / len(delays)
    print(f"Moyenne: {avg:.2f}s")

    return avg >= 1.0  # Au moins 1 seconde de moyenne


def test_scraper_init():
    """Teste l'initialisation des scrapers."""
    print("\n" + "=" * 60)
    print("TEST INITIALISATION SCRAPERS")
    print("=" * 60)

    scrapers = [
        ('pap', 'scrapers.pap', 'PapScraper'),
        ('leboncoin', 'scrapers.leboncoin', 'LeboncoinScraper'),
        ('paruvendu', 'scrapers.paruvendu', 'ParuvenduScraper'),
        ('entreparticuliers', 'scrapers.entreparticuliers', 'EntreParticuliersScraper'),
        ('figaro', 'scrapers.figaro_immo', 'FigaroImmoScraper'),
    ]

    all_ok = True
    for key, module, classname in scrapers:
        try:
            mod = __import__(module, fromlist=[classname])
            cls = getattr(mod, classname)
            instance = cls()

            print(f"✅ {key}:")
            print(f"   - site_name: {instance.site_name}")
            print(f"   - max_pages: {instance.get_max_pages()}")
            print(f"   - strict_location: {instance.should_use_strict_location()}")
            print(f"   - available: {instance.is_available()}")

        except Exception as e:
            print(f"❌ {key}: {e}")
            all_ok = False

    return all_ok


def main():
    """Lance tous les tests."""
    print("\n" + "=" * 60)
    print("TESTS ANTI-BLOCAGE V3")
    print("=" * 60)
    print()

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Headers", test_headers()))
    results.append(("Timing", test_timing()))
    results.append(("Scrapers", test_scraper_init()))

    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 Tous les tests passent!")
        print("\nPour installer curl_cffi (TLS spoofing):")
        print("  pip install curl_cffi")
        return 0
    else:
        print("\n⚠️ Certains tests ont échoué")
        return 1


if __name__ == '__main__':
    sys.exit(main())
