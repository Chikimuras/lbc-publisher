# Stratégies Anti-Détection pour Leboncoin

Ce document explique les techniques **légitimes et éthiques** implémentées pour réduire la détection par Leboncoin.

## ⚠️ Disclaimer Important

L'automatisation peut violer les Conditions d'Utilisation de Leboncoin. Utilisez cet outil de manière responsable :
- **Limitez le volume** : Ne publiez pas des dizaines d'annonces par jour
- **Respectez les délais** : Laissez du temps entre les publications
- **Compte réel** : Utilisez votre propre compte authentique
- **Contenu légitime** : Ne publiez que du contenu authentique et légal

## 🛡️ Techniques Implémentées

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

### 11. **Mode Non-Headless par Défaut**

```env
LBC_HEADLESS=false  # Navigateur visible
```

**Impact** : Les sites détectent facilement le mode headless. Le mode visible est plus sûr.

## 📋 Recommandations Supplémentaires

### 1. **Rotation de Proxies (Non implémenté)**

Pour éviter le ban d'IP, utilisez des proxies résidentiels :

```python
context = browser.new_context(
    proxy={
        "server": "http://proxy-server:port",
        "username": "user",
        "password": "pass"
    }
)
```

⚠️ **Attention** : Utilisez uniquement des proxies légitimes et évitez les proxies gratuits.

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