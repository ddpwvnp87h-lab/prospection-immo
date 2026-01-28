from typing import Dict, List, Any, Set
import hashlib
from config import AGENCY_KEYWORDS


def validate_listing(listing: Dict[str, Any]) -> bool:
    """
    Valide qu'une annonce contient tous les champs obligatoires.

    Champs obligatoires:
    - titre
    - date_publication
    - prix
    - localisation
    - lien
    - site_source

    Args:
        listing: Données de l'annonce

    Returns:
        True si valide, False sinon
    """
    required_fields = ['titre', 'date_publication', 'prix', 'localisation', 'lien', 'site_source']

    for field in required_fields:
        if field not in listing or not listing[field]:
            print(f"⚠️  Annonce invalide: champ '{field}' manquant")
            return False

    # Validation du prix (doit être un nombre positif)
    try:
        prix = int(listing['prix'])
        if prix <= 0:
            print(f"⚠️  Annonce invalide: prix doit être positif ({prix})")
            return False
    except (ValueError, TypeError):
        print(f"⚠️  Annonce invalide: prix invalide ({listing['prix']})")
        return False

    return True


def deduplicate_by_url(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Déduplique les annonces par URL exacte.

    Args:
        listings: Liste des annonces

    Returns:
        Liste des annonces uniques
    """
    seen_urls: Set[str] = set()
    unique_listings = []

    for listing in listings:
        url = listing.get('lien', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_listings.append(listing)

    duplicates_removed = len(listings) - len(unique_listings)
    if duplicates_removed > 0:
        print(f"🔍 {duplicates_removed} doublons supprimés (par URL)")

    return unique_listings


def deduplicate_by_signature(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Déduplique les annonces par signature (hash de titre + prix + localisation).

    Utilisé pour détecter les annonces similaires avec des URLs différentes.

    Args:
        listings: Liste des annonces

    Returns:
        Liste des annonces uniques
    """
    seen_signatures: Set[str] = set()
    unique_listings = []

    for listing in listings:
        signature = _generate_signature(listing)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_listings.append(listing)

    duplicates_removed = len(listings) - len(unique_listings)
    if duplicates_removed > 0:
        print(f"🔍 {duplicates_removed} doublons supprimés (par signature)")

    return unique_listings


def is_agency(listing: Dict[str, Any]) -> bool:
    """
    Détecte si une annonce provient d'une agence immobilière.

    Recherche les mots-clés d'agence dans:
    - Titre
    - Description (si présente)

    Args:
        listing: Données de l'annonce

    Returns:
        True si agence détectée, False si particulier
    """
    titre = listing.get('titre', '').lower()
    description = listing.get('description', '').lower()

    # Vérifier les mots-clés d'agence
    for keyword in AGENCY_KEYWORDS:
        if keyword in titre or keyword in description:
            return True

    return False


def filter_agencies(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtre les annonces d'agences, ne garde que les particuliers.

    Args:
        listings: Liste des annonces

    Returns:
        Liste des annonces de particuliers uniquement
    """
    particulier_listings = [listing for listing in listings if not is_agency(listing)]

    agencies_removed = len(listings) - len(particulier_listings)
    if agencies_removed > 0:
        print(f"🏢 {agencies_removed} annonces d'agences filtrées")

    return particulier_listings


def _generate_signature(listing: Dict[str, Any]) -> str:
    """
    Génère une signature unique basée sur titre + prix + localisation.

    Args:
        listing: Données de l'annonce

    Returns:
        Hash MD5 de la signature
    """
    titre = listing.get('titre', '')
    prix = str(listing.get('prix', ''))
    localisation = listing.get('localisation', '')

    signature = f"{titre}_{prix}_{localisation}"
    return hashlib.md5(signature.encode()).hexdigest()
