#!/usr/bin/env python3
"""
Application Web - Prospection Immo Team Maureen

Lance l'application web pour gérer les annonces immobilières.

Usage:
    python3 app.py

Puis ouvre: http://localhost:5000
"""

import os
import threading
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from dotenv import load_dotenv
from database.manager import DatabaseManager
from datetime import datetime, timedelta
import hashlib

# Charger .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Database manager
db = DatabaseManager()

def is_db_connected():
    """Vérifie si la connexion Supabase est active"""
    return db.client is not None

# ============================================================================
# SCRAPING STATUS TRACKER
# ============================================================================

# Stockage du statut des scrapings en cours (en mémoire)
scraping_status = {}

def get_scraping_status(user_id):
    """Récupère le statut du scraping pour un utilisateur"""
    return scraping_status.get(user_id, {
        'running': False,
        'progress': 0,
        'message': '',
        'results': None,
        'started_at': None,
        'finished_at': None
    })

def update_scraping_status(user_id, **kwargs):
    """Met à jour le statut du scraping"""
    if user_id not in scraping_status:
        scraping_status[user_id] = {
            'running': False,
            'progress': 0,
            'message': '',
            'results': None,
            'started_at': None,
            'finished_at': None
        }
    scraping_status[user_id].update(kwargs)

# ============================================================================
# AUTHENTICATION
# ============================================================================

def login_required(f):
    """Décorateur pour protéger les routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('login.html')

        # Mode démo si pas de Supabase
        if not is_db_connected():
            # Mode démo: accepte n'importe quel login
            session['user_id'] = 'demo-user'
            session['email'] = email
            flash('Mode démo (pas de base de données)', 'warning')
            return redirect(url_for('dashboard'))

        # Vérifier les credentials
        try:
            result = db.client.table('users').select('*').eq('email', email).execute()

            if result.data:
                user = result.data[0]
                # Hash le password pour comparer
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                if user['password_hash'] == password_hash:
                    session['user_id'] = user['id']
                    session['email'] = user['email']
                    flash('Connexion réussie!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Mot de passe incorrect', 'error')
            else:
                flash('Utilisateur introuvable', 'error')
        except Exception as e:
            flash(f'Erreur de connexion: {e}', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('register.html')

        # Mode démo si pas de Supabase
        if not is_db_connected():
            session['user_id'] = 'demo-user'
            session['email'] = email
            flash('Mode démo (pas de base de données)', 'warning')
            return redirect(url_for('dashboard'))

        # Créer le compte
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            user_data = {
                'email': email,
                'password_hash': password_hash
            }

            result = db.client.table('users').insert(user_data).execute()

            if result.data:
                user = result.data[0]
                session['user_id'] = user['id']
                session['email'] = user['email']
                flash('Compte créé avec succès!', 'success')
                return redirect(url_for('dashboard'))
        except Exception as e:
            if 'duplicate key' in str(e).lower() or 'unique' in str(e).lower():
                flash('Cet email est déjà utilisé', 'error')
            else:
                flash(f'Erreur lors de la création du compte: {e}', 'error')

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('login'))

# ============================================================================
# DASHBOARD
# ============================================================================

@app.route('/')
@login_required
def dashboard():
    """Page principale - Liste des annonces"""
    user_id = session.get('user_id')

    # Filtres
    status_filter = request.args.get('status', None)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')

    # Mode démo si pas de Supabase
    if not is_db_connected():
        flash('Base de données non configurée. Configurez SUPABASE_URL et SUPABASE_KEY.', 'warning')
        return render_template('dashboard.html', listings=[], stats={'total': 0, 'nouveau': 0, 'interesse': 0, 'pas_interesse': 0, 'visite': 0})

    # Récupérer les annonces
    try:
        query = db.client.table('listings').select('*').eq('user_id', user_id)

        # Appliquer filtre de statut
        if status_filter:
            query = query.eq('status', status_filter)

        # Appliquer tri
        query = query.order(sort_by, desc=(sort_order == 'desc'))

        result = query.execute()
        listings = result.data

        # Filtrer par recherche (côté client pour simplifier)
        if search_query:
            search_lower = search_query.lower()
            listings = [
                l for l in listings
                if search_lower in l['title'].lower()
                or search_lower in l['location'].lower()
            ]

        # Statistiques
        stats = {
            'total': len(listings),
            'nouveau': len([l for l in listings if l['status'] == 'Nouveau']),
            'interesse': len([l for l in listings if l['status'] == 'Intéressé']),
            'pas_interesse': len([l for l in listings if l['status'] == 'Pas intéressé']),
            'visite': len([l for l in listings if l['status'] == 'Visité']),
        }

        return render_template('dashboard.html',
                             listings=listings,
                             stats=stats,
                             current_status=status_filter,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order)
    except Exception as e:
        flash(f'Erreur lors du chargement des annonces: {e}', 'error')
        return render_template('dashboard.html', listings=[], stats={})

# ============================================================================
# LISTING MANAGEMENT
# ============================================================================

@app.route('/listing/<listing_id>')
@login_required
def view_listing(listing_id):
    """Voir les détails d'une annonce"""
    user_id = session.get('user_id')

    if not is_db_connected():
        flash('Base de données non configurée', 'error')
        return redirect(url_for('dashboard'))

    try:
        result = db.client.table('listings').select('*').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            listing = result.data[0]
            return render_template('listing_detail.html', listing=listing)
        else:
            flash('Annonce introuvable', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Erreur: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/listing/<listing_id>/status', methods=['POST'])
@login_required
def update_status(listing_id):
    """Mettre à jour le statut d'une annonce"""
    user_id = session.get('user_id')
    new_status = request.form.get('status')

    valid_statuses = ['Nouveau', 'Intéressé', 'Pas intéressé', 'Visité', 'Contact pris', 'Offre faite']

    if new_status not in valid_statuses:
        flash('Statut invalide', 'error')
        return redirect(url_for('dashboard'))

    if not is_db_connected():
        flash('Base de données non configurée', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Vérifier que l'annonce appartient à l'utilisateur
        result = db.client.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            db.update_listing_status(listing_id, user_id, new_status)
            flash(f'Statut mis à jour: {new_status}', 'success')
        else:
            flash('Annonce introuvable', 'error')
    except Exception as e:
        flash(f'Erreur: {e}', 'error')

    # Rediriger vers la page d'où on vient
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/listing/<listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    """Supprimer une annonce"""
    user_id = session.get('user_id')

    if not is_db_connected():
        flash('Base de données non configurée', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Vérifier que l'annonce appartient à l'utilisateur
        result = db.client.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            db.delete_listing(listing_id, user_id)
            flash('Annonce supprimée', 'success')
        else:
            flash('Annonce introuvable', 'error')
    except Exception as e:
        flash(f'Erreur: {e}', 'error')

    return redirect(url_for('dashboard'))

# ============================================================================
# SCRAPING
# ============================================================================

def run_scraping_task(user_id, ville, rayon, sites):
    """Tâche de scraping exécutée en arrière-plan"""
    try:
        update_scraping_status(user_id,
            running=True,
            progress=5,
            message=f'Démarrage du scraping pour {ville}...',
            started_at=datetime.now().isoformat(),
            finished_at=None,
            results=None
        )

        # Import des modules de scraping
        from utils.validator import validate_listing, deduplicate_by_url, deduplicate_by_signature, filter_agencies

        all_listings = []
        total_sites = len(sites)

        # Scraper chaque site sélectionné
        for i, site_name in enumerate(sites):
            # Vérifier si arrêté
            if not get_scraping_status(user_id).get('running'):
                return

            progress = 10 + int((i / total_sites) * 70)
            update_scraping_status(user_id,
                progress=progress,
                message=f'Scraping {site_name}... ({i+1}/{total_sites})'
            )

            try:
                if site_name == 'pap':
                    from scrapers.pap import PapScraper
                    scraper = PapScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
                    all_listings.extend(listings)
                elif site_name == 'figaro':
                    from scrapers.figaro_immo import FigaroImmoScraper
                    scraper = FigaroImmoScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
                    all_listings.extend(listings)
                elif site_name == 'leboncoin':
                    from scrapers.leboncoin import LeboncoinScraper
                    scraper = LeboncoinScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
                    all_listings.extend(listings)
                elif site_name == 'facebook':
                    from scrapers.facebook_marketplace import FacebookMarketplaceScraper
                    scraper = FacebookMarketplaceScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=1)
                    all_listings.extend(listings)
            except Exception as e:
                print(f"Erreur scraping {site_name}: {e}")
                continue

        # Validation et filtrage
        update_scraping_status(user_id,
            progress=85,
            message='Validation et filtrage des annonces...'
        )

        valid_listings = [l for l in all_listings if validate_listing(l)]
        particulier_listings = filter_agencies(valid_listings)
        dedup_url = deduplicate_by_url(particulier_listings)
        final_listings = deduplicate_by_signature(dedup_url)

        # Insertion en base de données
        update_scraping_status(user_id,
            progress=95,
            message='Enregistrement en base de données...'
        )

        inserted = 0
        updated = 0
        if final_listings:
            try:
                result = db.insert_listings(user_id, final_listings)
                inserted = result.get('inserted', 0) if result else 0
                updated = result.get('updated', 0) if result else 0
            except Exception as e:
                print(f"Erreur insertion DB: {e}")

        # Terminé
        update_scraping_status(user_id,
            running=False,
            progress=100,
            message=f'Terminé! {len(final_listings)} annonces trouvées.',
            finished_at=datetime.now().isoformat(),
            results={
                'total_scraped': len(all_listings),
                'valid': len(valid_listings),
                'particuliers': len(particulier_listings),
                'final': len(final_listings),
                'inserted': inserted,
                'updated': updated
            }
        )

    except Exception as e:
        update_scraping_status(user_id,
            running=False,
            progress=0,
            message=f'Erreur: {str(e)}',
            finished_at=datetime.now().isoformat(),
            results={'error': str(e)}
        )

@app.route('/scrape')
@login_required
def scrape_page():
    """Page de lancement du scraping"""
    user_id = session.get('user_id')
    status = get_scraping_status(user_id)
    return render_template('scrape.html', scraping_status=status)

@app.route('/scrape/run', methods=['POST'])
@login_required
def run_scrape():
    """Lancer le scraping en arrière-plan"""
    user_id = session.get('user_id')

    # Vérifier si un scraping est déjà en cours
    status = get_scraping_status(user_id)
    if status.get('running'):
        flash('Un scraping est déjà en cours. Patientez.', 'warning')
        return redirect(url_for('scrape_page'))

    # Récupérer les paramètres
    ville = request.form.get('ville', 'Paris')
    rayon = int(request.form.get('rayon', 10))
    sites = request.form.getlist('sites')

    if not sites:
        sites = ['pap', 'figaro']  # Sites par défaut (sans Playwright)

    # Lancer le scraping en arrière-plan
    thread = threading.Thread(
        target=run_scraping_task,
        args=(user_id, ville, rayon, sites)
    )
    thread.daemon = True
    thread.start()

    flash(f'Scraping lancé pour {ville}!', 'success')
    return redirect(url_for('scrape_page'))

@app.route('/scrape/status')
@login_required
def scrape_status():
    """API pour récupérer le statut du scraping (polling)"""
    user_id = session.get('user_id')
    status = get_scraping_status(user_id)
    return jsonify(status)

@app.route('/scrape/stop', methods=['POST'])
@login_required
def stop_scrape():
    """Arrêter le scraping"""
    user_id = session.get('user_id')
    update_scraping_status(user_id,
        running=False,
        message='Scraping arrêté.',
        finished_at=datetime.now().isoformat()
    )
    flash('Scraping arrêté.', 'info')
    return redirect(url_for('scrape_page'))

# ============================================================================
# API ENDPOINTS (pour PWA)
# ============================================================================

@app.route('/api/listings')
@login_required
def api_listings():
    """API pour récupérer les annonces (JSON)"""
    user_id = session.get('user_id')

    if not is_db_connected():
        return jsonify({'success': False, 'error': 'Base de données non configurée', 'listings': []}), 500

    try:
        result = db.client.table('listings').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify({'success': True, 'listings': result.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats')
@login_required
def api_stats():
    """API pour les statistiques"""
    user_id = session.get('user_id')

    if not is_db_connected():
        return jsonify({'success': False, 'error': 'Base de données non configurée'}), 500

    try:
        result = db.client.table('listings').select('status').eq('user_id', user_id).execute()
        listings = result.data

        stats = {
            'total': len(listings),
            'nouveau': len([l for l in listings if l['status'] == 'Nouveau']),
            'interesse': len([l for l in listings if l['status'] == 'Intéressé']),
            'pas_interesse': len([l for l in listings if l['status'] == 'Pas intéressé']),
            'visite': len([l for l in listings if l['status'] == 'Visité']),
        }

        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# PWA
# ============================================================================

@app.route('/manifest.json')
def manifest():
    """Manifeste PWA pour installation sur iPad"""
    return jsonify({
        'name': 'Prospection Immo',
        'short_name': 'Prospection',
        'description': 'Gestion des annonces immobilières',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#ffffff',
        'theme_color': '#4F46E5',
        'icons': [
            {
                'src': '/static/icon-192.png',
                'sizes': '192x192',
                'type': 'image/png'
            },
            {
                'src': '/static/icon-512.png',
                'sizes': '512x512',
                'type': 'image/png'
            }
        ]
    })

@app.route('/service-worker.js')
def service_worker():
    """Service Worker pour le mode offline"""
    return app.send_static_file('service-worker.js')

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🏠 Prospection Immo - Application Web")
    print("=" * 60)
    print()
    print("🌐 Application disponible sur: http://localhost:5000")
    print()
    print("📱 Pour installer sur iPad:")
    print("   1. Ouvre Safari sur iPad")
    print("   2. Va sur http://[ton-ip]:5000")
    print("   3. Clique sur Partager → Ajouter à l'écran d'accueil")
    print()
    print("Ctrl+C pour arrêter")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
