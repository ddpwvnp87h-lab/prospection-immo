.PHONY: install test clean help

help:
	@echo "📋 Commandes disponibles:"
	@echo ""
	@echo "  make install       - Installer les dépendances"
	@echo "  make test-leboncoin - Tester leboncoin.fr"
	@echo "  make test-pap      - Tester pap.fr"
	@echo "  make test-all      - Tester tous les scrapers"
	@echo "  make scrape        - Lancer une prospection (VILLE=Paris)"
	@echo "  make cleanup       - Nettoyer la base de données (USER_ID=test)"
	@echo "  make clean         - Supprimer les fichiers temporaires"
	@echo ""

install:
	@echo "📦 Installation des dépendances..."
	pip install -r requirements.txt
	playwright install
	@echo "✅ Installation terminée!"

test-leboncoin:
	@echo "🧪 Test de leboncoin.fr..."
	python test_scrapers.py --ville Paris --site leboncoin --max-pages 2

test-pap:
	@echo "🧪 Test de pap.fr..."
	python test_scrapers.py --ville Paris --site pap --max-pages 2

test-facebook:
	@echo "🧪 Test de Facebook Marketplace..."
	python test_scrapers.py --ville Paris --site facebook --max-pages 2

test-all:
	@echo "🧪 Test de tous les scrapers..."
	python test_scrapers.py --ville Paris --all --max-pages 2

scrape:
	@if [ -z "$(VILLE)" ]; then \
		echo "❌ Erreur: VILLE non spécifiée"; \
		echo "Usage: make scrape VILLE=Paris USER_ID=test"; \
		exit 1; \
	fi
	@if [ -z "$(USER_ID)" ]; then \
		echo "❌ Erreur: USER_ID non spécifié"; \
		echo "Usage: make scrape VILLE=Paris USER_ID=test"; \
		exit 1; \
	fi
	@echo "🚀 Lancement de la prospection..."
	python main.py --user-id $(USER_ID) --ville "$(VILLE)" --rayon 10

cleanup:
	@if [ -z "$(USER_ID)" ]; then \
		echo "❌ Erreur: USER_ID non spécifié"; \
		echo "Usage: make cleanup USER_ID=test"; \
		exit 1; \
	fi
	@echo "🧹 Nettoyage de la base..."
	python main.py --cleanup --user-id $(USER_ID)

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Nettoyage terminé!"
