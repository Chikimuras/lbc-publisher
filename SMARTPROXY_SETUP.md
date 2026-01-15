# Guide de Configuration Smartproxy

Ce guide vous aide à configurer Smartproxy pour publier vos annonces Leboncoin sans les erreurs 402 de Bright Data.

## 🎯 Pourquoi Smartproxy?

✅ **Avantages vs Bright Data**:
- Pas d'erreurs 402 sur les ressources JavaScript
- Compatible avec les applications React/SPA modernes
- Setup plus simple (pas de certificat CA requis)
- Support réactif
- Prix similaire: ~15€ pour 2GB (suffisant pour 300 annonces)

## 📋 Étape 1: Créer un compte Smartproxy

1. **Allez sur**: https://smartproxy.com
2. **Cliquez sur**: "Sign Up" ou "Get Started"
3. **Choisissez un plan**:
   - **Recommandé**: Residential Proxies - 2GB (~15€)
   - Alternative: 5GB (~28€) si vous prévoyez plus de 500 annonces

## 🔑 Étape 2: Récupérer vos credentials

1. **Connectez-vous** au dashboard Smartproxy
2. **Allez dans**: Dashboard > Residential Proxies
3. **Notez ces informations**:
   ```
   Endpoint: gate.smartproxy.com:7000
   Username: votre_username (ex: spXXXXXX)
   Password: votre_password
   ```

## ⚙️ Étape 3: Configuration

### Option A: Configuration automatique avec le filtre France

Dans votre `.env`, remplacez la configuration Bright Data par:

```env
# 🔴 PROXY RÉSIDENTIEL (Smartproxy avec IP française)
PROXY_SERVER=http://gate.smartproxy.com:7000
PROXY_USERNAME=votre_username-country-fr
PROXY_PASSWORD=votre_password
```

**Note**: Le suffixe `-country-fr` force une IP française.

### Option B: Configuration simple (IPs aléatoires)

Si Option A ne fonctionne pas, essayez sans le filtre pays:

```env
# 🔴 PROXY RÉSIDENTIEL (Smartproxy)
PROXY_SERVER=http://gate.smartproxy.com:7000
PROXY_USERNAME=votre_username
PROXY_PASSWORD=votre_password
```

**Note**: Smartproxy attribue souvent des IPs européennes par défaut.

## 🧪 Étape 4: Tester le proxy

Testez que le proxy fonctionne:

```bash
uv run python test_proxy.py
```

**Résultat attendu**:
```
✓ IP Info retrieved:
{
  "ip": "xx.xx.xx.xx",
  "city": "Paris",  # ou autre ville française
  "country": "FR",
  "org": "AS12345 Orange S.A."  # ou Free, Bouygues, etc.
}

✓ Leboncoin title: leboncoin, site de petites annonces gratuites
✅ No Datadome challenge detected!
🎉 Proxy test completed successfully!
```

## 🚀 Étape 5: Publier votre première annonce

```bash
uv run python -m src.main
```

Le navigateur va s'ouvrir et:
1. ✅ Se connecter via IP française Smartproxy
2. ✅ Charger Leboncoin sans blocage Datadome
3. ✅ Afficher le formulaire de dépôt d'annonce
4. ⏸️ **Se mettre en pause** si vous n'êtes pas connecté (connectez-vous manuellement)
5. ✅ Remplir le formulaire automatiquement
6. ✅ Publier l'annonce

## ❓ Problèmes courants

### Erreur 407 (Proxy Authentication Required)

**Cause**: Username ou password incorrect

**Solution**:
1. Vérifiez vos credentials dans le dashboard Smartproxy
2. Assurez-vous de copier-coller sans espaces
3. Vérifiez que votre compte n'est pas suspendu

### Erreur "No IPs available for country FR"

**Cause**: Le plan ne supporte pas les IPs françaises

**Solution**: Utilisez Option B (sans `-country-fr`)

### Page se charge mais reste en spinner

**Cause**: Rarement avec Smartproxy, mais si ça arrive:

**Solution**:
```bash
# Augmentez les timeouts dans .env
LBC_DELAY_MIN=10
LBC_DELAY_MAX=20
```

## 💰 Estimation des coûts

| Nombre d'annonces | Consommation estimée | Coût Smartproxy |
|-------------------|---------------------|-----------------|
| 50 annonces       | ~300MB              | ~5€ (1GB)       |
| 100 annonces      | ~600MB              | ~7€ (1GB)       |
| 300 annonces      | ~2GB                | ~15€ (2GB)      |
| 500 annonces      | ~3-4GB              | ~28€ (5GB)      |

**Note**: Chaque annonce consomme ~5-10MB de bande passante proxy.

## 📞 Support

### Smartproxy Support
- Email: support@smartproxy.com
- Chat: Disponible dans le dashboard
- Documentation: https://help.smartproxy.com

### Issues du projet
- GitHub: https://github.com/Chikimuras/lbc-publisher/issues

## ✅ Checklist avant publication massive

Avant de publier vos 300 annonces:

- [ ] Compte Smartproxy créé et plan acheté
- [ ] Credentials configurés dans `.env`
- [ ] `test_proxy.py` réussit (IP française obtenue)
- [ ] Test de publication d'1 annonce réussi
- [ ] Compte Leboncoin connecté (session sauvegardée)
- [ ] `LBC_MAX_ADS_PER_RUN=10` configuré (ne pas tout faire d'un coup)
- [ ] Attendre 1-2h entre chaque batch de 10 annonces

## 🎉 Félicitations!

Une fois configuré, vous pouvez publier vos annonces en toute sérénité:
- ✅ IP française résidentielle
- ✅ Contournement Datadome
- ✅ Mouvements de souris réalistes (Bézier)
- ✅ Anti-détection complet (14 techniques)
- ✅ Automatisation fiable

**Bonne chance avec vos publications!** 🚀
