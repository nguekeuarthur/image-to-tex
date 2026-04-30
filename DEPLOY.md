# 🚀 Guide de déploiement Hugging Face Spaces

## Étape 1 — Créer un compte HF (si pas déjà fait)

1. Allez sur https://huggingface.co/join
2. Créez un compte (gratuit, juste email + mot de passe)
3. Vérifiez votre email

## Étape 2 — Créer le Space

1. Allez sur https://huggingface.co/new-space
2. Remplissez :
   - **Owner** : votre username
   - **Space name** : `textify`
   - **License** : MIT
   - **Select the Space SDK** : **Docker** → **Blank**
   - **Hardware** : **CPU basic · Free** (16 GB RAM, 2 vCPU, gratuit ✅)
   - **Visibility** : Public (gratuit) ou Private (gratuit aussi !)
3. Cliquez sur **Create Space**

Vous arrivez sur la page de votre Space, vide pour l'instant.

## Étape 3 — Pousser votre code

HF Spaces fonctionne comme GitHub : un repo Git. Deux façons de faire :

### Option A — Cloner et pousser (recommandée)

```bash
# 1. Cloner le repo vide créé par HF
git clone https://huggingface.co/spaces/VOTRE-USERNAME/textify
cd textify

# 2. Copier vos fichiers dedans : app.py, Dockerfile, requirements.txt, README.md, .gitignore
# (Vous pouvez les glisser dans le dossier via votre explorateur de fichiers)

# 3. Configurer Git si pas déjà fait
git config user.name "Votre Nom"
git config user.email "votre@email.com"

# 4. Commit + push
git add .
git commit -m "Initial commit — Textify OCR"
git push
```

⚠️ **Pour le mot de passe** : HF n'accepte plus les mots de passe normaux pour Git. Créez un **Access Token** :
1. https://huggingface.co/settings/tokens
2. **New token** → Type **Write** → **Generate**
3. Copiez le token, utilisez-le quand Git demande le mot de passe

### Option B — Upload direct via le navigateur

1. Sur la page de votre Space, cliquez sur **Files** (en haut)
2. Cliquez sur **Add file** → **Upload files**
3. Glissez : `app.py`, `Dockerfile`, `requirements.txt`, `README.md`
4. Commit message : "Initial commit"
5. **Commit changes**

⚠️ Plus lent, à éviter si beaucoup de fichiers.

## Étape 4 — Attendre le build

- HF détecte automatiquement le Dockerfile et lance le build
- ⏱️ Le premier build prend **8-12 minutes** (PyTorch + EasyOCR + pré-téléchargement du modèle FR+EN)
- Vous voyez les logs en direct dans l'onglet **Logs**
- Statuts possibles : `Building` → `Running` ✅
- Si vous voyez `Build error`, regardez les logs pour comprendre

## Étape 5 — Utiliser l'app

Quand le statut est **Running** :
- L'URL est `https://VOTRE-USERNAME-textify.hf.space`
- Aussi accessible via le repo : `https://huggingface.co/spaces/VOTRE-USERNAME/textify`
- L'app **NE DORT PAS** sur le tier gratuit Docker ✅
- Premier appel : rapide (le modèle est déjà préchargé dans le Docker)

## 🛠️ Mises à jour futures

Quand vous modifiez le code :
```bash
git add .
git commit -m "Description du changement"
git push
```
HF rebuild et redéploie automatiquement (~5 min). 🎉

## ⚠️ Problèmes courants

### "Build failed" — out of memory
Le tier gratuit a 16 GB de RAM mais le **build** est plus limité. Si problème :
- Retirez le pré-téléchargement du modèle dans le Dockerfile (la ligne `RUN python -c "import easyocr..."`)
- Le modèle se téléchargera au premier appel utilisateur (1-2 min d'attente la 1ère fois)

### "Application error" au démarrage
Regardez l'onglet **Logs** :
- Si erreur de port : vérifiez que `app_port: 7860` est bien dans le README.md
- Si erreur d'import : vérifiez requirements.txt
- Si timeout : augmentez `--timeout 600` dans le Dockerfile

### L'app est lente
Sur le tier CPU basic, comptez 3-8s par image (vs 1-2s en local). C'est normal.
Pour aller plus vite : passez à **CPU upgrade** ($0.03/h, ~22€/mois si 24/7)

### Garder une copie sur GitHub aussi (optionnel)
Vous pouvez avoir le même code sur GitHub ET sur HF Spaces. Ajoutez juste un second remote :
```bash
git remote add github https://github.com/VOTRE-USERNAME/textify.git
git push github main
```

## 💡 Bonus

### Mode privé
Dans Settings de votre Space → **Visibility** → **Private**. L'app reste accessible via votre URL si vous êtes connecté à HF.

### Mot de passe sur l'app
Si vous voulez protéger l'accès, ajoutez Flask-BasicAuth dans `app.py`. Demandez-moi si besoin.

### Stats d'utilisation
HF Spaces affiche le nombre de visiteurs et requêtes dans Settings → Analytics.

### Limite réelle
Sur le free tier CPU basic : pas de quota strict de requêtes. Si votre app fait beaucoup de bruit (>1000 visites/jour), HF peut vous demander de passer en payant.
