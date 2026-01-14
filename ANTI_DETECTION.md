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

### 3. **Anti-Automation Headers**

```python
browser = p.chromium.launch(
    headless=False,  # Navigateur visible
    args=[
        "--disable-blink-features=AutomationControlled",  # Masque l'automatisation
    ],
)
```

**Impact** : Supprime les flags JavaScript qui identifient Playwright/Selenium.

### 4. **User Agent Réaliste**

```python
context = browser.new_context(
    viewport={"width": 1920, "height": 1080},
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36..."
)
```

**Impact** : Se fait passer pour un vrai navigateur Chrome sur macOS.

### 5. **Session Persistante**

- Sauvegarde de l'état de session (cookies, localStorage)
- Réutilisation de la même session entre les exécutions
- Évite les logins répétés qui sont suspects

**Code** :
```python
context = browser.new_context(
    storage_state=storage_state_path if os.path.exists(storage_state_path) else None
)
```

### 6. **Mode Non-Headless par Défaut**

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

**Actions à prendre** :
1. Arrêtez immédiatement l'automatisation
2. Attendez 24-48h
3. Réduisez drastiquement les paramètres
4. Envisagez de contacter le support Leboncoin

## 🎯 Conclusion

L'objectif est de simuler un **comportement humain raisonnable**, pas de contourner agressivement les protections. Si Leboncoin vous bloque, c'est probablement parce que vous publiez trop rapidement ou en trop grand volume.

**Rappelez-vous** : L'automatisation n'est pas un droit, c'est une tolérance. Utilisez-la avec modération et respect.