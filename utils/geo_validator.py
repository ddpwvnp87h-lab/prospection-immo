"""
Validation GPS des annonces.
Vérifie que les annonces sont dans le rayon demandé.
"""

import re
from math import radians, cos, sin, asin, sqrt
from typing import Optional, Tuple, List, Dict, Any
from .geolocation import geo


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en km entre deux points GPS (formule haversine).

    Args:
        lat1, lon1: Coordonnées du point 1
        lat2, lon2: Coordonnées du point 2

    Returns:
        Distance en kilomètres
    """
    R = 6371  # Rayon de la Terre en km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c


def extract_postal_code(text: str) -> Optional[str]:
    """
    Extrait un code postal français d'un texte.

    Args:
        text: Texte contenant potentiellement un code postal

    Returns:
        Code postal ou None
    """
    if not text:
        return None

    # Pattern: 5 chiffres
    match = re.search(r'\b(\d{5})\b', text)
    if match:
        return match.group(1)

    return None


def validate_listing_location(
    listing: dict,
    target_lat: float,
    target_lon: float,
    max_radius_km: int
) -> Tuple[bool, Optional[float], str]:
    """
    Valide qu'une annonce est dans le rayon demandé.

    Args:
        listing: Données de l'annonce
        target_lat: Latitude cible
        target_lon: Longitude cible
        max_radius_km: Rayon maximum en km

    Returns:
        Tuple (is_valid, distance_km, reason)
        - is_valid: True si dans le rayon ou impossible à valider
        - distance_km: Distance calculée (None si impossible)
        - reason: Explication du résultat
    """
    localisation = listing.get('localisation', '')
    confidence = listing.get('_geo_confidence', 'unknown')

    # Extraire le code postal
    cp = extract_postal_code(localisation)

    if not cp:
        # Pas de CP → impossible de valider
        if confidence == 'inferred':
            # Localisation inférée + pas de CP = probablement faux
            return False, None, 'rejected_inferred_no_cp'
        else:
            # Bénéfice du doute si la localisation a été extraite
            return True, None, 'kept_no_cp'

    # Géocoder le code postal
    try:
        geo_info = geo.search(cp)
    except Exception:
        geo_info = None

    if not geo_info or not geo_info.get('lat'):
        # Impossible de géocoder → bénéfice du doute
        return True, None, 'geocoding_failed'

    # Calculer la distance
    distance = haversine(
        target_lat, target_lon,
        geo_info['lat'], geo_info['lon']
    )

    # Ajouter une marge de 10% pour les imprécisions
    effective_radius = max_radius_km * 1.1

    if distance <= effective_radius:
        return True, round(distance, 1), 'within_radius'
    else:
        return False, round(distance, 1), f'outside_radius_{int(distance)}km'


def filter_listings_by_radius(
    listings: List[Dict[str, Any]],
    target_lat: float,
    target_lon: float,
    max_radius_km: int,
    strict: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Filtre les annonces par distance GPS.

    Args:
        listings: Liste des annonces
        target_lat: Latitude cible
        target_lon: Longitude cible
        max_radius_km: Rayon maximum en km
        strict: Si True, rejette aussi les annonces sans CP

    Returns:
        Tuple (filtered_listings, stats)
    """
    filtered = []
    stats = {
        'total': len(listings),
        'valid_with_distance': 0,
        'valid_no_validation': 0,
        'rejected_distance': 0,
        'rejected_no_cp': 0,
        'rejected_inferred': 0,
    }

    for listing in listings:
        is_valid, distance, reason = validate_listing_location(
            listing, target_lat, target_lon, max_radius_km
        )

        if is_valid:
            # Enrichir avec les infos de validation
            listing['_distance_km'] = distance
            listing['_geo_validation'] = reason
            filtered.append(listing)

            if distance is not None:
                stats['valid_with_distance'] += 1
            else:
                stats['valid_no_validation'] += 1

        else:
            # Rejeté
            if 'no_cp' in reason:
                stats['rejected_no_cp'] += 1
            elif 'inferred' in reason:
                stats['rejected_inferred'] += 1
            else:
                stats['rejected_distance'] += 1

            loc = listing.get('localisation', 'N/A')[:40]
            dist_str = f"{distance}km" if distance else "?"
            print(f"  ❌ Hors zone: {loc} ({dist_str})")

    # Résumé
    if stats['rejected_distance'] > 0 or stats['rejected_no_cp'] > 0:
        print(f"📍 Validation GPS: {len(filtered)}/{len(listings)} dans le rayon de {max_radius_km}km")
        if stats['rejected_distance'] > 0:
            print(f"   - {stats['rejected_distance']} hors distance")
        if stats['rejected_no_cp'] > 0:
            print(f"   - {stats['rejected_no_cp']} sans code postal (inféré)")

    return filtered, stats


def enrich_listing_with_geo(
    listing: Dict[str, Any],
    fallback_location: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enrichit une annonce avec des métadonnées de géolocalisation.

    Args:
        listing: Données de l'annonce
        fallback_location: Localisation de recherche (fallback)

    Returns:
        Annonce enrichie avec _geo_* fields
    """
    localisation = listing.get('localisation', '')

    # Extraire le CP
    cp = extract_postal_code(localisation)

    if cp:
        # CP trouvé dans la localisation
        listing['_geo_confidence'] = 'high'
        listing['_geo_source'] = 'extracted'
        listing['_geo_cp'] = cp

        # Essayer de géocoder pour enrichir
        try:
            geo_info = geo.search(cp)
            if geo_info:
                listing['_geo_lat'] = geo_info.get('lat')
                listing['_geo_lon'] = geo_info.get('lon')
                listing['_geo_dept'] = geo_info.get('departement')
        except Exception:
            pass

    else:
        # Pas de CP → vérifier si c'est un fallback
        fallback_cp = fallback_location.get('code_postal')
        fallback_ville = fallback_location.get('ville', '')

        if fallback_ville and fallback_ville.lower() in localisation.lower():
            # Le nom de ville correspond au fallback
            listing['_geo_confidence'] = 'medium'
            listing['_geo_source'] = 'partial_match'
        else:
            # Localisation probablement fausse (fallback silencieux)
            listing['_geo_confidence'] = 'inferred'
            listing['_geo_source'] = 'fallback'

    return listing


def get_department_from_cp(code_postal: str) -> Optional[str]:
    """
    Extrait le département d'un code postal.

    Args:
        code_postal: Code postal français

    Returns:
        Code département (2 ou 3 caractères)
    """
    if not code_postal or len(code_postal) != 5:
        return None

    # DOM-TOM: 97xxx, 98xxx
    if code_postal.startswith('97') or code_postal.startswith('98'):
        return code_postal[:3]

    # Corse: 20xxx -> 2A ou 2B
    if code_postal.startswith('20'):
        return '2A' if int(code_postal) < 20200 else '2B'

    # Métropole
    return code_postal[:2]
