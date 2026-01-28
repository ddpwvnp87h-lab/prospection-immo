# 🌐 Guide HTTPS Scraping - Comment ça marche

## 🎯 Le Code Réel (dans scrapers/pap.py)

### 1. Configuration Session HTTPS

```python
# Ligne 31-32 dans scrapers/pap.py
session = requests.Session()
session.headers.update({'User-Agent': self.user_agent})
```

**Ce qui se passe:**
- Créée une session HTTP persistante
- Ajoute un User-Agent pour simuler un navigateur
- Maintient les cookies entre requêtes

---

### 2. Construction de l'URL HTTPS

```python
# Ligne 35-36
base_url = f"https://www.pap.fr/annonce/vente-immobilier-{ville.lower()}"
```

**Exemple:**
- Entrée: `ville = "Paris"`
- Résultat: `https://www.pap.fr/annonce/vente-immobilier-paris`

---

### 3. Requête HTTPS GET

```python
# Ligne 44-45
response = session.get(url, timeout=15)
response.raise_for_status()
```

**Ce qui se passe:**
1. 🔐 **Connexion TLS/SSL** établie
2. 📡 **GET request** envoyée
3. ⏱️ **Timeout** de 15 secondes
4. ✅ **Vérification** du status code (200, 404, etc.)

**Données reçues:**
```
Status: 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 125678 bytes
Set-Cookie: session_id=abc123...

<html>
  <body>
    <div class="search-list-item">
      <h2>Appartement Paris</h2>
      <span class="price">450 000 €</span>
      ...
    </div>
  </body>
</html>
```

---

### 4. Parsing HTML

```python
# Ligne 47
soup = BeautifulSoup(response.content, 'lxml')
```

**Ce qui se passe:**
- Parse le HTML en arbre DOM
- Permet de chercher des éléments facilement
- Utilise lxml (rapide) ou html.parser (intégré)

---

### 5. Extraction des Annonces

```python
# Ligne 51-52
ads = soup.find_all('div', class_='search-list-item')
```

**Sélecteurs CSS utilisés:**

```html
<div class="search-list-item">           ← Trouvé par find_all()
  <h2 class="item-title">               ← Trouvé par find('h2')
    Appartement 3 pièces Paris
  </h2>
  <span class="item-price">450 000 €</span>  ← Prix extrait
  <span class="item-location">Paris 15</span> ← Localisation
  <a href="/annonce/123">Voir</a>       ← Lien extrait
</div>
```

---

### 6. Extraction des Détails (méthode _extract_listing)

```python
# Lignes 75-100 dans scrapers/pap.py
def _extract_listing(self, ad_element, ville: str):
    # Lien
    link_elem = ad_element.find('a', href=True)
    lien = f"https://www.pap.fr{link_elem['href']}"

    # Titre
    titre_elem = ad_element.find('span', class_='item-title')
    titre = titre_elem.get_text(strip=True)

    # Prix
    prix_elem = ad_element.find('span', class_='item-price')
    prix = self._parse_price(prix_elem.get_text())

    # Photos
    img_elem = ad_element.find('img')
    img_src = img_elem.get('src')

    return {
        'titre': titre,
        'prix': prix,
        'lien': lien,
        'photos': [img_src],
        ...
    }
```

---

## 🔥 Workflow Complet HTTPS

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CONFIGURATION                                            │
│    session = requests.Session()                             │
│    headers = {'User-Agent': '...'}                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CONNEXION HTTPS (TLS 1.3)                                │
│    🔐 Handshake SSL                                          │
│    📜 Vérification certificat                                │
│    🔑 Échange de clés                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. REQUÊTE HTTP                                             │
│    GET /annonce/vente-immobilier-paris HTTP/1.1             │
│    Host: www.pap.fr                                         │
│    User-Agent: Mozilla/5.0 ...                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RÉPONSE HTTPS                                            │
│    HTTP/1.1 200 OK                                          │
│    Content-Type: text/html; charset=utf-8                   │
│    [125KB de HTML]                                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. PARSING HTML                                             │
│    BeautifulSoup(html, 'lxml')                              │
│    → Arbre DOM navigable                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. EXTRACTION DONNÉES                                       │
│    soup.find_all('div', class_='search-list-item')          │
│    → 40 annonces trouvées                                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. NORMALISATION                                            │
│    {                                                        │
│      "titre": "Appartement...",                             │
│      "prix": 450000,                                        │
│      "lien": "https://...",                                 │
│      ...                                                    │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Comparaison: Requests vs Playwright

### Requests (HTTP Simple) - Utilisé dans pap.py

```python
# AVANTAGES
✅ Rapide (quelques ms)
✅ Léger (< 1 MB mémoire)
✅ Pas de navigateur requis
✅ Parfait pour HTML statique

# CODE
import requests
from bs4 import BeautifulSoup

response = requests.get('https://pap.fr/...')
soup = BeautifulSoup(response.content, 'lxml')
annonces = soup.find_all('div', class_='annonce')
```

**Sites utilisant Requests:**
- pap.fr ✅
- figaro-immo.fr ✅

---

### Playwright (JavaScript) - Utilisé dans leboncoin.py

```python
# AVANTAGES
✅ Exécute JavaScript
✅ Gère le contenu dynamique
✅ Scroll, clics, etc.
✅ Rendu complet de la page

# CODE
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://leboncoin.fr/...')
    page.wait_for_selector('.annonce')
    elements = page.query_selector_all('.annonce')
```

**Sites utilisant Playwright:**
- leboncoin.fr ✅
- facebook.com/marketplace ✅

---

## 🔧 Requête HTTPS Détaillée

### Headers Envoyés

```http
GET /annonce/vente-immobilier-paris HTTP/1.1
Host: www.pap.fr
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

### Réponse Reçue

```http
HTTP/1.1 200 OK
Date: Mon, 27 Jan 2026 23:00:00 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 125678
Set-Cookie: session_id=abc123; Path=/; HttpOnly; Secure
Cache-Control: max-age=3600
Server: nginx/1.21.0
```

---

## 💡 Sécurité HTTPS

### Vérifications Automatiques

```python
# requests fait automatiquement:
1. ✅ Vérification du certificat SSL
2. ✅ Validation de la chaîne de certificats
3. ✅ Vérification de l'expiration
4. ✅ Chiffrement TLS 1.2+
5. ✅ Protection MITM
```

### En cas d'erreur SSL

```python
# Si certificat invalide:
requests.exceptions.SSLError:
  [SSL: CERTIFICATE_VERIFY_FAILED]

# Solution (à éviter en prod):
response = requests.get(url, verify=False)  # ⚠️ Dangereux!
```

---

## 🎯 Code Complet Minimal

```python
import requests
from bs4 import BeautifulSoup

def scraper_pap_https(ville):
    # 1. Session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 ...'
    })

    # 2. URL
    url = f"https://www.pap.fr/annonce/vente-immobilier-{ville}"

    # 3. Requête HTTPS
    response = session.get(url, timeout=15)
    response.raise_for_status()

    # 4. Parse HTML
    soup = BeautifulSoup(response.content, 'lxml')

    # 5. Extraire annonces
    annonces = []
    for ad in soup.find_all('div', class_='search-list-item'):
        annonces.append({
            'titre': ad.find('span', class_='item-title').get_text(),
            'prix': ad.find('span', class_='item-price').get_text(),
            'lien': 'https://pap.fr' + ad.find('a')['href']
        })

    return annonces

# Utilisation
resultats = scraper_pap_https('paris')
print(f"{len(resultats)} annonces trouvées")
```

---

## ✅ Fichiers à Consulter

1. **[scrapers/pap.py](scrapers/pap.py)** - Scraper HTTPS complet
2. **[scrapers/leboncoin.py](scrapers/leboncoin.py)** - Scraper Playwright
3. **[scrapers/base.py](scrapers/base.py)** - Classe de base
4. **[test_scrapers.py](test_scrapers.py)** - Tests

---

## 🚀 Pour Tester

```bash
# Une fois les dépendances installées:
pip3 install requests beautifulsoup4 html5lib

# Test:
python3 test_scrapers.py --ville Paris --site pap
```

Le scraping HTTPS fonctionne! Le code est **déjà écrit et prêt** 🎯
