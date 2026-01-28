"""
Vercel Serverless Function Entry Point
Application Web - Prospection Immo Team Maureen

Cette version est adaptée pour fonctionner sur Vercel (serverless).
"""

import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from dotenv import load_dotenv
from database.manager import DatabaseManager
import hashlib

# Charger .env
load_dotenv()

# Create Flask app
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Database manager
db = DatabaseManager()

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

        try:
            result = db.client.table('users').select('*').eq('email', email).execute()

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

    status_filter = request.args.get('status', None)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')

    try:
        query = db.client.table('listings').select('*').eq('user_id', user_id)

        if status_filter:
            query = query.eq('status', status_filter)

        query = query.order(sort_by, desc=(sort_order == 'desc'))

        result = query.execute()
        listings = result.data

        if search_query:
            search_lower = search_query.lower()
            listings = [
                l for l in listings
                if search_lower in l['title'].lower()
                or search_lower in l['location'].lower()
            ]

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

    try:
        result = db.client.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            db.update_listing_status(listing_id, new_status)
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

    try:
        result = db.client.table('listings').select('id').eq('id', listing_id).eq('user_id', user_id).execute()

        if result.data:
            db.delete_listing(listing_id)
            flash('Annonce supprimée', 'success')
        else:
            flash('Annonce introuvable', 'error')
    except Exception as e:
        flash(f'Erreur: {e}', 'error')

    return redirect(url_for('dashboard'))

# ============================================================================
# SCRAPING
# ============================================================================

@app.route('/scrape')
@login_required
def scrape_page():
    """Page de lancement du scraping"""
    return render_template('scrape.html')

@app.route('/scrape/run', methods=['POST'])
@login_required
def run_scrape():
    """Lancer le scraping"""
    flash('Le scraping n\'est pas disponible sur Vercel. Utilisez le script en local: python3 main.py', 'warning')
    return redirect(url_for('dashboard'))

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/listings')
@login_required
def api_listings():
    """API pour récupérer les annonces (JSON)"""
    user_id = session.get('user_id')

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
    """Manifeste PWA"""
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
    """Service Worker"""
    return app.send_static_file('service-worker.js')

# ============================================================================
# VERCEL HANDLER (Required for Vercel)
# ============================================================================

# This is required for Vercel to work
handler = app
