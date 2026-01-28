#!/bin/bash

# Script de démarrage - Prospection Immo Team Maureen

echo "=========================================="
echo "🏠 Prospection Immo - Démarrage"
echo "=========================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 trouvé"

# Vérifier .env
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env introuvable"
    echo ""
    echo "Configuration requise:"
    echo "  1. Copier .env.example vers .env"
    echo "     cp .env.example .env"
    echo ""
    echo "  2. Configurer Supabase dans .env"
    echo "     Voir: SUPABASE_SETUP.md"
    echo ""
    exit 1
fi

echo "✓ Fichier .env trouvé"

# Vérifier les dépendances
echo ""
echo "Vérification des dépendances..."

MISSING_DEPS=0

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask manquant"
    MISSING_DEPS=1
fi

if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "❌ python-dotenv manquant"
    MISSING_DEPS=1
fi

if ! python3 -c "import supabase" 2>/dev/null; then
    echo "❌ supabase manquant"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "Installation des dépendances..."
    pip3 install flask python-dotenv supabase
fi

echo "✓ Toutes les dépendances sont installées"

# Lancer l'application
echo ""
echo "=========================================="
echo "🚀 Lancement de l'application web"
echo "=========================================="
echo ""
echo "📱 Ouvre ton navigateur sur:"
echo "   http://localhost:5000"
echo ""
echo "📱 Pour iPad (sur le même réseau WiFi):"
IP=$(ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}' | head -n 1)
if [ ! -z "$IP" ]; then
    echo "   http://$IP:5000"
fi
echo ""
echo "🛑 Pour arrêter: Ctrl+C"
echo ""

# Lancer Flask
python3 app.py
