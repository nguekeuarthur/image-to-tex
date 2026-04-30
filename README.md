# 📖 Textify — Lecteur OCR Web

Application web open-source pour extraire le texte d'images. 100% local, multi-images, gratuit, sans clé API.

> Propulsé par [EasyOCR](https://github.com/JaidedAI/EasyOCR) — moteur de deep learning, bien plus précis que Tesseract.

## ✨ Fonctionnalités

- 🖼️ **Multi-images** : sélectionnez et traitez plusieurs images en lot
- 🌍 **11 langues** : français, anglais, arabe, chinois, japonais, etc.
- 🎯 **Haute précision** : utilise des réseaux de neurones (deep learning)
- 📋 **Export flexible** : copier tout, télécharger en .txt unique ou séparé
- 🔒 **Privé** : vos images sont traitées par votre serveur, pas par un tiers
- ♾️ **Illimité** : aucun quota, aucune clé API requise
- 🌐 **Interface moderne** : drag & drop, paste (Ctrl+V), aperçu en temps réel

## 🚀 Démo en ligne

👉 **[https://textify.onrender.com](https://textify.onrender.com)** *(remplacer par votre URL après déploiement)*

> ⏱️ Premier chargement après inactivité : 30-60 secondes (instance gratuite Render).

## 📸 Aperçu

![Aperçu](docs/screenshot.png)

## 🏠 Installation locale

### Prérequis
- Python 3.11 ou 3.12 (⚠️ Python 3.13 n'est pas encore supporté par toutes les dépendances)

### Installation
```bash
git clone https://github.com/VOTRE-USERNAME/textify.git
cd textify
pip install -r requirements.txt
python app.py
```

Ouvrez http://localhost:5000

⏳ **Premier lancement** : le téléchargement du modèle EasyOCR (~64 MB) prend 1-2 minutes. Les utilisations suivantes sont instantanées.

## ☁️ Déploiement sur Render

1. Forkez ce repo sur votre compte GitHub
2. Allez sur [render.com](https://render.com) et créez un compte gratuit
3. Cliquez sur **New → Web Service**
4. Connectez votre repo GitHub
5. Render détecte automatiquement le fichier `render.yaml` et configure tout
6. Cliquez sur **Create Web Service**

⏱️ Le premier déploiement prend ~10-15 minutes (installation de PyTorch + EasyOCR).

### Limites du plan gratuit Render
- 512 MB de RAM (suffisant pour EasyOCR en CPU)
- 750 heures/mois (largement suffisant)
- Mise en veille après 15 min d'inactivité (réveil en ~30s à la requête suivante)

## 🛠️ Stack technique

- **Backend** : Flask + Gunicorn
- **OCR** : EasyOCR (PyTorch)
- **Frontend** : HTML/CSS/JS vanilla (zéro framework)
- **Déploiement** : Render (Python)

## 🌐 Langues supportées

Français, Anglais, Espagnol, Allemand, Italien, Portugais, Arabe, Chinois (simplifié), Japonais, Russe, et combinaison FR+EN.

[Plus de langues disponibles](https://www.jaided.ai/easyocr/) — il suffit de les ajouter dans le sélecteur de `app.py`.

## 📝 Licence

MIT — Faites-en ce que vous voulez.

## 🤝 Contribuer

Les PRs sont bienvenues ! N'hésitez pas à ouvrir une issue pour discuter de vos idées.

## 🙏 Crédits

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — moteur OCR
- [Flask](https://flask.palletsprojects.com/) — framework web
- [PyTorch](https://pytorch.org/) — deep learning
