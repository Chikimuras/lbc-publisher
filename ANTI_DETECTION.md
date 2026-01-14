# Stratégies Anti-Détection pour Leboncoin

Ce document explique les techniques **légitimes et éthiques** implémentées pour réduire la détection par Leboncoin.

## ⚠️ Disclaimer Important

L'automatisation peut violer les Conditions d'Utilisation de Leboncoin. Utilisez cet outil de manière responsable :
- **Limitez le volume** : Ne publiez pas des dizaines d'annonces par jour
- **Respectez les délais** : Laissez du temps entre les publications
- **Compte réel** : Utilisez votre propre compte authentique
- **Contenu légitime** : Ne publiez que du contenu authentique et légal

## 🚨 Leboncoin utilise Datadome

**Datadome** est l'un des systèmes anti-bot les plus sophistiqués du marché en 2026. Il analyse **plus de 1000 signaux différents** pour détecter les bots :

### Signaux Analysés par Datadome

1. **TLS Fingerprinting (JA3)** : Analyse la poignée de main SSL/TLS
2. **Mouvements de souris** : Patterns, vitesse, accélération, trajectoires
3. **Timing des actions** : Vitesse de clic, délais entre actions
4. **JavaScript Runtime** : Propriétés navigator, window, document
5. **Hardware/OS** : Informations système, résolution, timezone
6. **Browser Fingerprinting** : Plugins, fonts, canvas, WebGL
7. **CDP Detection** : Détecte les commandes Chrome DevTools Protocol
8. **IP Reputation** : Type d'IP (datacenter vs résidentiel), historique
9. **Comportement HTTP** : Headers, ordre, versions, compression
10. **Patterns de requêtes** : Fréquence, volume, timing

### Pourquoi C'est Difficile

- **Machine Learning** : Datadome utilise l'IA pour détecter les patterns anormaux
- **Évolution Constante** : Les règles changent fréquemment
- **Multi-Layered** : Combine plusieurs techniques de détection
- **Scoring System** : Chaque signal contribue à un score de confiance

## 🛡️ Techniques Implémentées Contre Datadome

### 1. **Rate Limiting (Limitation du débit)**

```env
LBC_MAX_ADS_PER_RUN=5          # Maximum 5 annonces par exécution
LBC_DELAY_MIN=2                # Délai minimum de 2s entre actions
LBC_DELAY_MAX=5                # Délai maximum de 5s entre actions
```

**Impact** : Empêche les publications en masse, simule un utilisateur humain qui prend son temps.

### 2. **Délais Aléatoires (Human-like delays)**

- Délais aléatoires entre chaque action (clic, remplissage de formulaire)
- Délais prolongés (20-50s) entre chaque annonce
- Utilisation de `random.uniform()` pour éviter les patterns fixes

**Code** :
```python
def _human_delay(delay_min: int, delay_max: int) -> None:
    delay = random.uniform(delay_min, delay_max)
    time.sleep(delay)
```

### 3. **Frappe Réaliste Character-by-Character**

Au lieu de remplir les champs instantanément, le texte est tapé caractère par caractère avec des délais réalistes :

```python
# Titre : 80-180ms par caractère
for char in payload.title:
    title_field.type(char, delay=random.uniform(80, 180))

# Description : 30-80ms par caractère (plus rapide pour textes longs)
for char in chunk:
    desc_field.type(char, delay=random.uniform(30, 80))

# Prix : 100-200ms par chiffre
for digit in price_str:
    price_field.type(digit, delay=random.uniform(100, 200))
```

**Impact** : Simule une vitesse de frappe humaine réaliste, évite la détection de "superhuman clicking speed".

### 4. **Mouvements de Souris Aléatoires**

```python
def _move_mouse_randomly(page: Page) -> None:
    x = random.randint(100, 1800)
    y = random.randint(100, 1000)
    page.mouse.move(x, y, steps=random.randint(10, 30))
```

- Mouvements de souris entre chaque action
- Déplacements fluides avec plusieurs étapes
- Positionnement précis avant de cliquer sur les boutons

**Impact** : Simule le comportement naturel d'un utilisateur qui déplace sa souris.

### 5. **Scroll Aléatoire**

```python
def _random_scroll(page: Page, delay_min: int, delay_max: int) -> None:
    scroll_amount = random.randint(100, 500)
    page.evaluate(f"window.scrollBy(0, {scroll_amount})")
```

**Impact** : Simule la lecture de la page, un comportement humain naturel.

### 6. **Anti-Automation Headers**

```python
browser = p.chromium.launch(
    headless=False,
    args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-web-security",
    ],
)
```

**Impact** : Supprime les flags qui identifient Playwright/Selenium.

### 7. **Injection JavaScript Anti-Détection**

```python
context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    window.chrome = {
        runtime: {}
    };

    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });

    Object.defineProperty(navigator, 'languages', {
        get: () => ['fr-FR', 'fr', 'en-US', 'en']
    });
""")
```

**Impact** : Masque les propriétés JavaScript qui révèlent l'automatisation.

### 8. **Vérification JavaScript**

```python
def _verify_javascript(page: Page) -> None:
    result = page.evaluate("() => { return navigator.userAgent && typeof window !== 'undefined' }")
```

**Impact** : S'assure que JavaScript fonctionne correctement, évite les erreurs "JavaScript blocking".

### 9. **User Agent et Contexte Réalistes**

```python
context = browser.new_context(
    viewport={"width": 1920, "height": 1080},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...",
    locale="fr-FR",
    timezone_id="Europe/Paris",
    geolocation={"longitude": 2.3522, "latitude": 48.8566},  # Paris
    permissions=["geolocation"],
)
```

**Impact** : Se fait passer pour un vrai navigateur Chrome sur macOS, en France, à Paris.

### 10. **Session Persistante**

- Sauvegarde de l'état de session (cookies, localStorage)
- Réutilisation de la même session entre les exécutions
- Évite les logins répétés qui sont suspects

**Code** :
```python
context = browser.new_context(
    storage_state=storage_state_path if os.path.exists(storage_state_path) else None
)
```

### 11. **Playwright-Stealth (🆕 2026)**

```python
from playwright_stealth import stealth_sync

page = context.new_page()
stealth_sync(page)  # Applique automatiquement tous les patches
```

**Ce qu'il fait** :
- Masque plus de **200 signaux d'automatisation**
- Patch `navigator.webdriver`, `navigator.plugins`, etc.
- Modifie les propriétés Chrome DevTools Protocol
- Hide automation flags dans Chromium

**Impact** : **CRITIQUE** pour contourner Datadome. C'est la première ligne de défense contre la détection CDP.

**Limites** :
- Ne protège pas contre l'analyse TLS (nécessite des proxies)
- Ne protège pas contre l'analyse comportementale (nécessite des délais réalistes)
- Open-source, donc Datadome peut l'étudier

### 12. **Ghost Cursor - Mouvements Réalistes avec Bézier (🆕 2026)**

```python
from python_ghost_cursor.playwright_sync import create_cursor

cursor = create_cursor(page)

# Mouvement naturel avec courbe de Bézier
cursor.move_to(x, y)

# Clic ultra-réaliste (mouvement + clic)
cursor.click(element)
```

**Pourquoi c'est crucial** :
- Datadome analyse **les trajectoires de souris** en temps réel
- Les mouvements en ligne droite sont **instantanément détectés**
- Les courbes de Bézier imitent les mouvements humains naturels
- Vitesse variable et accélération réaliste

**Comparaison** :
```python
# ❌ MAUVAIS (détecté par Datadome)
page.mouse.move(x, y, steps=10)  # Ligne droite, vitesse constante

# ✅ BON (passe Datadome)
cursor.move_to(x, y)  # Courbe Bézier, accélération variable
```

**Impact** : **ESSENTIEL** contre Datadome. Les mouvements de souris sont l'un des signaux les plus analysés.

### 13. **Mode Non-Headless par Défaut**

```env
LBC_HEADLESS=false  # Navigateur visible
```

**Impact** : Les sites détectent facilement le mode headless. Le mode visible est plus sûr.

## 📋 Recommandations Supplémentaires

### 1. **🔴 CRITIQUE : Proxies Résidentiels**

**⚠️ SANS PROXIES RÉSIDENTIELS, DATADOME VOUS DÉTECTERA PRESQUE À COUP SÛR**

Datadome analyse votre IP et détecte immédiatement :
- Les IPs datacenter (AWS, OVH, Digital Ocean, etc.)
- Les VPNs commerciaux (NordVPN, ExpressVPN, etc.)
- Les proxies gratuits
- Les IPs déjà flaggées comme suspectes

#### Pourquoi les Proxies Résidentiels ?

Les proxies résidentiels utilisent de **vraies IPs de particuliers** :
- ✅ Indétectables par Datadome (IPs légitimes de FAI)
- ✅ Localisation française réaliste
- ✅ Pas de flagging automatique
- ✅ Meilleur taux de succès (90%+ selon les sources)

#### Fournisseurs Recommandés (2026)

**Premium (Chers mais Fiables)** :
1. **Bright Data** (ex-Luminati) - 40M+ IPs résidentielles
   - Prix : ~500€/mois pour 40GB
   - Qualité : Excellente
   - France : Oui

2. **Oxylabs** - 100M+ IPs résidentielles
   - Prix : ~300€/mois
   - Qualité : Excellente
   - France : Oui

3. **Smartproxy** - Plus abordable
   - Prix : ~75€/mois pour 5GB
   - Qualité : Bonne
   - France : Oui

**Budget** :
- **Proxy-Cheap** : ~50€/mois pour 5GB
- **IPRoyal** : ~40€/mois pour 5GB

⚠️ **Évitez** :
- ❌ Proxies gratuits (100% détectés)
- ❌ Proxies datacenter (détectés instantanément)
- ❌ VPNs grand public (flaggés par Datadome)

#### Configuration dans le Code

**Option 1 : Configuration Manuelle**

Ajoutez à votre `.env` :
```env
# Proxy résidentiel français
PROXY_SERVER=http://gate.smartproxy.com:7000
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
```

**Option 2 : Modifier `src/lbc.py`**

```python
# Dans publish_ad(), ajouter le proxy au contexte
context = browser.new_context(
    storage_state=(...),
    viewport={"width": 1920, "height": 1080},
    user_agent="Mozilla/5.0...",
    locale="fr-FR",
    timezone_id="Europe/Paris",
    geolocation={"longitude": 2.3522, "latitude": 48.8566},
    permissions=["geolocation"],
    # 🆕 Ajouter le proxy résidentiel
    proxy={
        "server": os.getenv("PROXY_SERVER"),
        "username": os.getenv("PROXY_USERNAME"),
        "password": os.getenv("PROXY_PASSWORD"),
    } if os.getenv("PROXY_SERVER") else None,
)
```

#### Test de Votre Proxy

Avant d'utiliser votre proxy, testez-le :

```python
import requests

proxies = {
    "http": "http://username:password@gate.smartproxy.com:7000",
    "https": "http://username:password@gate.smartproxy.com:7000",
}

# Vérifier l'IP
r = requests.get("https://api.ipify.org?format=json", proxies=proxies)
print(f"IP visible: {r.json()['ip']}")

# Vérifier le pays
r = requests.get("https://ipapi.co/json/", proxies=proxies)
print(f"Pays: {r.json()['country_name']}")  # Devrait être "France"
```

#### Configuration Optimale

```env
# Dans .env
PROXY_SERVER=http://gate.smartproxy.com:7000
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password

# Réduire encore plus les délais car le proxy ajoute de la latence
LBC_DELAY_MIN=5
LBC_DELAY_MAX=10
LBC_MAX_ADS_PER_RUN=3
```

**💡 Pro Tip** : Utilisez des proxies français avec géolocalisation à Paris pour être cohérent avec la config du navigateur.

### 2. **Rotation de Proxies (Avancé)**

Si vous avez un pool de proxies résidentiels, implémentez la rotation :

```python
import random

PROXY_POOL = [
    {"server": "http://gate1.proxy.com:7000", "username": "user1", "password": "pass1"},
    {"server": "http://gate2.proxy.com:7000", "username": "user2", "password": "pass2"},
    # ... plus de proxies
]

# Dans publish_ad()
proxy = random.choice(PROXY_POOL)
context = browser.new_context(
    # ...
    proxy=proxy
)
```

⚠️ **Attention** : La rotation peut être suspecte si elle est trop fréquente. Gardez le même proxy pour toute une session.

### 2. **Limiter la Fréquence**

Planifiez les publications de manière espacée :

```bash
# Publie 5 annonces le matin
0 9 * * * cd /path/to/project && uv run python -m src.main

# Publie 5 annonces l'après-midi
0 15 * * * cd /path/to/project && uv run python -m src.main
```

### 3. **Monitoring des Erreurs**

Si vous recevez des erreurs fréquentes :
- **Augmentez les délais** : `LBC_DELAY_MIN=5`, `LBC_DELAY_MAX=10`
- **Réduisez le volume** : `LBC_MAX_ADS_PER_RUN=2`
- **Espacez les exécutions** : Attendez plusieurs heures entre les runs

### 4. **Comportement Humain**

Choses **à faire** :
- ✅ Variez les heures de publication (pas toujours à 9h pile)
- ✅ Publiez pendant les heures ouvrables (9h-18h)
- ✅ Évitez les publications le week-end/nuit
- ✅ Prenez des pauses (pas de publication tous les jours)

Choses **à éviter** :
- ❌ Publier 50 annonces d'un coup
- ❌ Publier à intervalles fixes (ex: toutes les 5 minutes)
- ❌ Utiliser des patterns répétitifs (mêmes titres, descriptions similaires)

### 5. **Contact Leboncoin (Solution Légitime)**

La meilleure approche est de **contacter Leboncoin** :
- Demandez s'il existe une **API officielle** pour les professionnels
- Expliquez votre cas d'usage légitime
- Demandez une **autorisation** pour l'automatisation

## 🔧 Configuration Recommandée

Pour un usage **sûr et respectueux** :

```.env
# Conservatif (recommandé pour éviter les bans)
LBC_MAX_ADS_PER_RUN=3
LBC_DELAY_MIN=5
LBC_DELAY_MAX=10
LBC_HEADLESS=false

# Modéré
LBC_MAX_ADS_PER_RUN=5
LBC_DELAY_MIN=3
LBC_DELAY_MAX=7
LBC_HEADLESS=false

# Agressif (risque de détection)
LBC_MAX_ADS_PER_RUN=10
LBC_DELAY_MIN=1
LBC_DELAY_MAX=3
LBC_HEADLESS=true  # ⚠️ Plus facilement détectable
```

## 🚫 Ce Qui N'est PAS Implémenté (Volontairement)

Ces techniques sont plus "agressives" et potentiellement problématiques :

- ❌ **Fingerprinting bypass avancé** : Manipulation de canvas, WebGL, fonts
- ❌ **CAPTCHA solving** : Contournement automatique de CAPTCHAs
- ❌ **Rotation IP agressive** : Changement d'IP à chaque requête
- ❌ **Obfuscation de trafic** : Tunneling, VPN switching
- ❌ **Exploitation de vulnérabilités** : Aucune tentative de hack

## 📊 Signes de Détection

Si vous êtes détecté, vous verrez :
- 🚫 **CAPTCHA** : Leboncoin vous demande de prouver que vous êtes humain
- 🚫 **Ban temporaire** : "Trop de tentatives, réessayez plus tard"
- 🚫 **Ban de compte** : Compte suspendu ou bloqué
- 🚫 **Rate limiting** : Annonces refusées sans raison claire
- 🚫 **Message de blocage** : "Quelque chose dans le comportement du navigateur nous a intrigué"

### Message de Blocage Spécifique

Si vous voyez ce message :
```
Pourquoi ce blocage ? Quelque chose dans le comportement du navigateur nous a intrigué.
Diverses possibilités :
- vous surfez et cliquez à une vitesse surhumaine
- quelque chose bloque le fonctionnement de javascript sur votre ordinateur
- un robot est sur le même réseau (IP X.X.X.X) que vous
```

**Ce que cela signifie** :
1. **Vitesse surhumaine** : Leboncoin a détecté que vos actions étaient trop rapides
2. **JavaScript bloqué** : Problème avec l'exécution JavaScript (maintenant résolu avec `_verify_javascript()`)
3. **IP flaggée** : Votre adresse IP a été marquée comme suspecte

**Actions à prendre** :
1. **Arrêtez immédiatement** l'automatisation
2. **Attendez 24-48h** pour que votre IP soit "refroidie"
3. **Augmentez drastiquement les délais** :
   ```env
   LBC_DELAY_MIN=8
   LBC_DELAY_MAX=15
   LBC_MAX_ADS_PER_RUN=2
   ```
4. **Vérifiez que JavaScript fonctionne** : Les nouvelles fonctions de vérification le font automatiquement
5. **Considérez un proxy résidentiel** : Si votre IP est définitivement bannie
6. **Testez manuellement** : Essayez de publier une annonce manuellement pour voir si votre compte fonctionne
7. **Contactez le support Leboncoin** : Expliquez votre situation et demandez une autorisation

## 🎯 Conclusion

L'objectif est de simuler un **comportement humain raisonnable**, pas de contourner agressivement les protections. Si Leboncoin vous bloque, c'est probablement parce que vous publiez trop rapidement ou en trop grand volume.

**Rappelez-vous** : L'automatisation n'est pas un droit, c'est une tolérance. Utilisez-la avec modération et respect.