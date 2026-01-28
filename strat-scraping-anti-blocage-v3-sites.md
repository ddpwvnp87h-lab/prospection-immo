# strat-scraping-anti-blocage-v3-sites.md
## V3 — Réglages recommandés par site + “quand basculer en Playwright”

> Cette V3 complète la V2 : ici on définit des **profils concrets par site**.
> Toujours “propre et durable” : rythme, cache, résilience. Pas de contournements agressifs.

---

## 1) Philosophie par type de site

### 1.1 Sites “classiques” (HTML stable)
Ex : PAP, ParuVendu (souvent)
- Mode : `http`
- RPS : 1.5–2.5
- Pagination : ok
- Détail : only new/stale
- Captcha : rare

### 1.2 Sites “mi-JS” (données souvent en JSON injecté)
Ex : Leboncoin, certains agrégateurs
- Mode : `hybrid`
- HTTP first (si JSON accessible), Playwright uniquement si nécessaire
- RPS : 0.8–1.5
- Backoff plus agressif

### 1.3 Agrégateurs “bruités”
Ex : Figaro Immo, MoteurImmo
- Mode : `http` ou `hybrid`
- Peu de pages max
- Validation localisation stricte (sinon uncertain)
- Détail moins fréquent

### 1.4 Marketplaces “hostiles”
Ex : Facebook Marketplace
- Par défaut : **désactivé** (`enabled=false`)
- Si activé : `browser` best-effort, très lent, très peu de pages
- Accepter que ce soit instable

---

## 2) Profils conseillés (valeurs de départ)

### 2.1 PAP (pap.fr)
- Mode : `http`
- RPS : 1.5 (burst 2)
- Jitter : 200–800ms
- List refresh : 15–25 min
- Detail refresh : 72h
- Max list pages : 10–15
- Stop pagination early : oui (si page 1 inchangée)
- Retry :
  - 429/5xx : backoff 10/30/60/120
- Circuit breaker :
  - 10 fails → pause 20 min

**Pourquoi ça marche :**
- HTML stable, champs structurés propres.
- Tu peux extraire CP/ville sans navigateur.

---

### 2.2 ParuVendu (paruvendu.fr) — profil “classique”
- Mode : `http`
- RPS : 1.5 (burst 2)
- Jitter : 250–900ms
- List refresh : 20–30 min
- Detail refresh : 72h
- Max list pages : 8–12
- Retry/backoff : identique PAP

**Note :**
- Si tu vois contenu manquant côté HTTP (JS), basculer en `hybrid`.

---

### 2.3 Leboncoin (leboncoin.fr) — profil “hybrid safe”
- Mode : `hybrid`
- RPS : 1.0 (burst 1)
- Jitter : 400–1200ms
- List refresh : 20–40 min
- Detail refresh : 72–96h (éviter de spammer les détails)
- Max list pages : 4–8
- Retry :
  - 429/5xx : backoff 20/60/120/240/300
- Circuit breaker :
  - 8 fails → pause 30 min

**Règle d’extraction :**
1) Chercher la localisation dans JSON (`lat/lng` si possible)  
2) Sinon CP/ville → géocoding  
3) Si pas de localisation structurée → `uncertain`

**Playwright**
- `use_only_when_needed=true`
- réutiliser un context/cookies
- bloquer `media` et `font` (souvent safe)

---

### 2.4 Figaro Immo — profil “agrégateur strict”
- Mode : `http` (puis `hybrid` si rendu JS)
- RPS : 1.0 (burst 1)
- Jitter : 300–1100ms
- List refresh : 30–60 min
- Detail refresh : 96h
- Max list pages : 4–6
- Retry/backoff : 20/60/120/240
- Circuit breaker : 8 fails → 30 min

**Validation localisation**
- Accepter uniquement si CP ou GPS ou ville exploitable (géocoding)
- Sinon `uncertain` (masqué)

---

### 2.5 MoteurImmo — profil “agrégateur strict”
Même profil que Figaro Immo.

---

### 2.6 Facebook Marketplace — profil “best effort”
- enabled : false (par défaut)
- Si activé :
  - Mode : `browser`
  - RPS : 0.3 (burst 1)
  - Jitter : 800–2500ms
  - List refresh : 60–180 min
  - Max list pages : 1–2 (oui c’est petit, sinon ban/captcha)
  - Circuit breaker : 5 fails → 60 min

**Politique de données**
- Sans CP/ville claire → `uncertain`
- Ne jamais afficher uncertain par défaut

---

## 3) Quand basculer en Playwright (règles claires)

### 3.1 Signaux “HTTP suffit”
- Tu vois `title/price/city/cp` dans le HTML
- Les requêtes retournent 200 stables
- Pas de contenu vide

✅ Reste en `http`.

### 3.2 Signaux “hybrid nécessaire”
- HTML incomplet (liste vide)
- Les champs clés n’existent que dans un script JSON runtime
- La pagination est “Load more” via JS
- Les pages détail affichent mais sans données structurées en HTTP

➡️ Passe en `hybrid` et utilise Playwright **uniquement** pour :
- récupérer le JSON/HTML rendu
- cliquer “charger plus” 1–2 fois
- extraire ensuite comme d’hab

### 3.3 Signaux “browser only” (rare, à éviter)
- Tout est derrière rendu JS + interactions obligatoires
- L’accès HTTP direct renvoie des pages génériques
- L’API interne est inaccessible

➡️ Mode `browser`, best effort, lent, avec risques captcha.

---

## 4) “Kill switch” (très important)
Chaque site doit pouvoir être désactivé instantanément :
- config `enabled=false`
- `disabled_reason`
- `disabled_at`

Exemples raisons :
- 429 constant
- captcha systématique
- parsing cassé
- site trop instable

---

## 5) Micro-checklist d’implémentation
- [ ] 1 worker par domaine
- [ ] rate limit + jitter
- [ ] backoff 429/5xx
- [ ] circuit breaker
- [ ] cache + 304
- [ ] two-pass (liste vs détail)
- [ ] mode hybrid + switch automatique si HTML incomplet
- [ ] validation localisation par distance (universelle)

---
