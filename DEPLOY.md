# 🚀 Guide de déploiement pas à pas

## Étape 1 — Préparer GitHub

### Créer le repo sur GitHub
1. Allez sur https://github.com/new
2. **Nom du repo** : `textify` (ou un autre nom de votre choix)
3. **Description** : "Lecteur OCR web — extraction de texte d'images"
4. **Public** ou Private (au choix)
5. ⚠️ **NE COCHEZ PAS** "Initialize with README" (on a déjà tout)
6. Cliquez sur **Create repository**

GitHub vous montre une page avec des commandes. Gardez-la ouverte.

### Pousser le code (depuis votre dossier local)

Ouvrez un terminal dans le dossier qui contient `app.py`, `requirements.txt`, etc., puis :

```bash
# 1. Initialiser Git
git init
git branch -M main

# 2. Configurer votre identité (si pas déjà fait)
git config user.name "Arthur Nguekeu"
git config user.email "votre.email@example.com"

# 3. Ajouter les fichiers
git add .
git commit -m "Initial commit — Textify OCR app"

# 4. Lier au repo GitHub (remplacer VOTRE-USERNAME)
git remote add origin https://github.com/VOTRE-USERNAME/textify.git

# 5. Pousser
git push -u origin main
```

⚠️ **Si Git demande un mot de passe** : depuis 2021, GitHub n'accepte plus les mots de passe pour le push. Utilisez un **Personal Access Token** :
1. https://github.com/settings/tokens
2. **Generate new token (classic)**
3. Cochez **repo** (toutes les sous-cases)
4. Copiez le token et utilisez-le comme mot de passe

---

## Étape 2 — Déployer sur Render

### Créer le service
1. Allez sur https://render.com et créez un compte (connexion via GitHub recommandée)
2. Sur le dashboard, cliquez sur **New +** → **Web Service**
3. Cliquez sur **Connect GitHub** et autorisez Render à voir vos repos
4. Sélectionnez votre repo `textify`
5. Render lit automatiquement `render.yaml` et pré-remplit la configuration :
   - **Name** : `textify` (modifiable, ça donnera l'URL `textify.onrender.com`)
   - **Region** : Frankfurt (le plus proche pour la France/Europe)
   - **Branch** : `main`
   - **Runtime** : Python
   - **Plan** : **Free** ✅
6. Cliquez sur **Create Web Service**

### Premier déploiement
- ⏱️ Le build prend **10-15 minutes** la première fois (téléchargement de PyTorch ~500 MB)
- Vous voyez les logs en direct
- Quand vous voyez `Your service is live 🎉`, c'est prêt
- L'URL est en haut : `https://textify.onrender.com` (ou similaire)

### Premier accès
- ⏳ La première requête prendra ~1-2 min (téléchargement du modèle EasyOCR)
- Les requêtes suivantes seront rapides (~3-5s par image)
- Après 15 min d'inactivité, l'app dort. Le réveil prend ~30s.

---

## Étape 3 — Mises à jour futures

Quand vous modifiez le code :

```bash
git add .
git commit -m "Description de votre changement"
git push
```

Render redéploie automatiquement. ✨

---

## ⚠️ Problèmes possibles et solutions

### "Build failed: out of memory"
PyTorch est gros. Si le build du plan gratuit n'y arrive pas :
- Solution 1 : Passer au plan **Starter** ($7/mois, 512 MB → 2 GB RAM pendant le build)
- Solution 2 : Utiliser une version plus légère d'OCR (à voir si nécessaire)

### "Application failed to respond"
Le timeout par défaut peut être trop court au démarrage à froid.
La config `--timeout 300` dans `render.yaml` devrait suffire, mais si le souci persiste, augmentez à 600.

### L'app est lente
Normal sur le plan gratuit (CPU partagé, 512 MB RAM). Pour de meilleures perfs :
- Plan Starter ($7/mois) → CPU dédié
- Ou héberger sur votre propre VPS (Hetzner ~5€/mois avec beaucoup plus de RAM)

### "Application Error" après mise en veille
Le réveil prend du temps. Patientez 30-60s et réessayez.

---

## 💡 Astuces

### Garder l'app éveillée 24/7 (optionnel)
Le plan gratuit met l'app en veille après 15 min. Solutions :
- **UptimeRobot** (gratuit) : ping votre URL toutes les 5 min → reste éveillée
- **Cron-job.org** (gratuit) : pareil, ping HTTP toutes les X minutes

⚠️ Mais utiliserez vos 750h/mois plus vite. Sur le plan gratuit, c'est OK : 750h = ~31 jours non-stop.

### Domaine personnalisé
Render permet d'ajouter un domaine perso gratuitement (ex: `textify.votredomaine.com`). Settings → Custom Domains.

### Logs en direct
Dashboard Render → votre service → onglet **Logs**. Très utile pour débugger.
