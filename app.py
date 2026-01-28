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
    return db.connected

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
# DEBUG ENDPOINT
# ============================================================================

@app.route('/debug')
def debug_page():
    """Page de diagnostic - affiche l'état de la connexion Supabase"""
    import os

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    flask_secret = os.getenv('FLASK_SECRET_KEY')

    # Construire le HTML de diagnostic
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug - Prospection Immo</title>
        <style>
            body { font-family: monospace; padding: 20px; background: #1a1a2e; color: #eee; }
            .ok { color: #00ff00; }
            .error { color: #ff4444; }
            .warning { color: #ffaa00; }
            .box { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; }
            h1 { color: #4F46E5; }
            .value { background: #0f3460; padding: 5px 10px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>🔧 Diagnostic Supabase</h1>
    """

    # Check SUPABASE_URL
    html += '<div class="box">'
    html += '<h3>SUPABASE_URL</h3>'
    if supabase_url:
        html += f'<p class="ok">✅ Défini</p>'
        html += f'<p>Valeur: <span class="value">{supabase_url[:50]}...</span></p>'
        html += f'<p>Longueur: {len(supabase_url)} caractères</p>'
    else:
        html += '<p class="error">❌ NON DÉFINI</p>'
    html += '</div>'

    # Check SUPABASE_KEY
    html += '<div class="box">'
    html += '<h3>SUPABASE_KEY</h3>'
    if supabase_key:
        html += f'<p class="ok">✅ Défini</p>'
        html += f'<p>Longueur: {len(supabase_key)} caractères</p>'
        html += f'<p>Commence par: <span class="value">{supabase_key[:20]}...</span></p>'
    else:
        html += '<p class="error">❌ NON DÉFINI</p>'
    html += '</div>'

    # Check FLASK_SECRET_KEY
    html += '<div class="box">'
    html += '<h3>FLASK_SECRET_KEY</h3>'
    if flask_secret:
        html += f'<p class="ok">✅ Défini ({len(flask_secret)} caractères)</p>'
    else:
        html += '<p class="warning">⚠️ Non défini (utilise valeur par défaut)</p>'
    html += '</div>'

    # Check DB connection
    html += '<div class="box">'
    html += '<h3>Connexion Base de Données</h3>'

    # Info from DatabaseManager
    html += f'<p>URL trouvée au démarrage: {"✅ Oui" if db.supabase_url_found else "❌ Non"}</p>'
    html += f'<p>KEY trouvée au démarrage: {"✅ Oui" if db.supabase_key_found else "❌ Non"}</p>'

    if db.connection_error:
        html += f'<p class="error">❌ Erreur de connexion: {db.connection_error}</p>'

    if db.connected:
        html += '<p class="ok">✅ Connecté à Supabase</p>'
        try:
            result = db.table('users').select('id').execute()
            html += f'<p class="ok">✅ Test requête OK ({len(result.data)} users)</p>'
        except Exception as e:
            html += f'<p class="error">❌ Erreur requête: {str(e)[:100]}</p>'
    else:
        html += '<p class="error">❌ Non connecté à Supabase</p>'
        if db.connection_error:
            html += f'<p class="warning">Erreur: {db.connection_error}</p>'
    html += '</div>'

    # Show all environment variables (filtered)
    html += '<div class="box">'
    html += '<h3>Toutes les variables d\'environnement (filtrées)</h3>'
    html += '<ul>'
    for key in sorted(os.environ.keys()):
        if any(x in key.upper() for x in ['SUPABASE', 'FLASK', 'DATABASE', 'DB', 'SECRET']):
            value = os.environ[key]
            if 'KEY' in key.upper() or 'SECRET' in key.upper():
                display_value = value[:10] + '...' if len(value) > 10 else value
            else:
                display_value = value[:50] + '...' if len(value) > 50 else value
            html += f'<li><strong>{key}</strong>: <span class="value">{display_value}</span></li>'
    html += '</ul>'
    html += '</div>'

    html += '<p><a href="/" style="color: #4F46E5;">← Retour à l\'application</a></p>'
    html += '</body></html>'

    return html

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
    # Vérifier la connexion DB
    if not is_db_connected():
        flash('Base de données non configurée. Contactez l\'administrateur.', 'error')
        return render_template('login.html', db_error=True)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return render_template('login.html')

        try:
            result = db.table('users').select('*').eq('email', email).execute()

            if result.data:
                user = result.data[0]
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
            flash(f'Erreur: {e}', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    # Vérifier la connexion DB
    if not is_db_connected():
        flash('Base de données non configurée. Contactez l\'administrateur.', 'error')
        return render_template('register.html', db_error=True)

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

        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            result = db.table('users').insert({
                'email': email,
                'password_hash': password_hash
            }).execute()

            if result.data:
                user = result.data[0]
                session['user_id'] = user['id']
                session['email'] = user['email']
                flash('Compte créé avec succès!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Erreur lors de la création du compte', 'error')
        except Exception as e:
            if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                flash('Cet email est déjà utilisé', 'error')
            else:
                flash(f'Erreur: {e}', 'error')

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

    if not is_db_connected():
        flash('Base de données non configurée.', 'error')
        return render_template('dashboard.html', listings=[], stats={'total': 0, 'nouveau': 0, 'interesse': 0, 'pas_interesse': 0, 'visite': 0})

    try:
        query = db.table('listings').select('*').eq('user_id', user_id)

        if status_filter:
            query = query.eq('status', status_filter)

        query = query.order(sort_by, desc=(sort_order == 'desc'))
        result = query.execute()
        listings = result.data

        if search_query:
            search_lower = search_query.lower()
            listings = [l for l in listings if search_lower in l.get('title', '').lower() or search_lower in l.get('location', '').lower()]

        # Statistiques basées sur toutes les annonces (pas filtrées)
        all_result = db.table('listings').select('status').eq('user_id', user_id).execute()
        all_listings = all_result.data

        stats = {
            'total': len(all_listings),
            'nouveau': len([l for l in all_listings if l.get('status') == 'Nouveau']),
            'interesse': len([l for l in all_listings if l.get('status') == 'Intéressé']),
            'pas_interesse': len([l for l in all_listings if l.get('status') == 'Pas intéressé']),
            'visite': len([l for l in all_listings if l.get('status') == 'Visité']),
        }

        return render_template('dashboard.html',
                             listings=listings,
                             stats=stats,
                             current_status=status_filter,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order)
    except Exception as e:
        flash(f'Erreur: {e}', 'error')
        return render_template('dashboard.html', listings=[], stats={'total': 0, 'nouveau': 0, 'interesse': 0, 'pas_interesse': 0, 'visite': 0})

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
        result = db.table('listings').select('*').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            return render_template('listing_detail.html', listing=result.data[0])
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
        result = db.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            db.update_listing_status(listing_id, user_id, new_status)
            flash(f'Statut mis à jour: {new_status}', 'success')
        else:
            flash('Annonce introuvable', 'error')
    except Exception as e:
        flash(f'Erreur: {e}', 'error')

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
        result = db.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

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
                elif site_name == 'entreparticuliers':
                    from scrapers.entreparticuliers import EntreParticuliersScraper
                    scraper = EntreParticuliersScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
                    all_listings.extend(listings)
                elif site_name == 'paruvendu':
                    from scrapers.paruvendu import ParuvenduScraper
                    scraper = ParuvenduScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
                    all_listings.extend(listings)
                elif site_name == 'moteurimmo':
                    from scrapers.moteurimmo import MoteurImmoScraper
                    scraper = MoteurImmoScraper()
                    listings = scraper.scrape(ville, rayon, max_pages=2)
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
        return jsonify({'success': False, 'error': 'Base de données non configurée'}), 500

    try:
        result = db.table('listings').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
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
        result = db.table('listings').select('status').eq('user_id', user_id).execute()
        listings = result.data

        stats = {
            'total': len(listings),
            'nouveau': len([l for l in listings if l.get('status') == 'Nouveau']),
            'interesse': len([l for l in listings if l.get('status') == 'Intéressé']),
            'pas_interesse': len([l for l in listings if l.get('status') == 'Pas intéressé']),
            'visite': len([l for l in listings if l.get('status') == 'Visité']),
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
