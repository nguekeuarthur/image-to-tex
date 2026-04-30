---
title: Textify OCR
emoji: 📖
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
license: mit
short_description: Lecteur OCR multi-images, 100% local, sans clé API
---

# 📖 Textify — Lecteur OCR Web

Extraction de texte depuis vos images. Multi-images, 100% local, gratuit, sans clé API.

> Propulsé par [EasyOCR](https://github.com/JaidedAI/EasyOCR) — moteur de deep learning, bien plus précis que Tesseract.

## ✨ Fonctionnalités

- 🖼️ **Multi-images** : sélectionnez et traitez plusieurs images en lot
- 🌍 **11 langues** : français, anglais, arabe, chinois, japonais, etc.
- 🎯 **Haute précision** : utilise des réseaux de neurones (deep learning)
- 📋 **Export flexible** : copier tout, télécharger en .txt unique ou séparé
- 🔒 **Privé** : vos images sont traitées en mémoire, jamais stockées
- ♾️ **Illimité** : aucun quota, aucune clé API requise

## 🚀 Utilisation

1. Glissez plusieurs images (ou cliquez pour parcourir / Ctrl+V pour coller)
2. Choisissez la langue
3. Cliquez sur « Extraire tout »
4. Copiez ou téléchargez le résultat

## 🛠️ Stack

- **Backend** : Flask + Gunicorn
- **OCR** : EasyOCR (PyTorch)
- **Frontend** : HTML/CSS/JS vanilla
- **Hébergement** : Hugging Face Spaces (Docker, CPU Basic)

## 🏠 Installation locale

```bash
git clone https://huggingface.co/spaces/VOTRE-USERNAME/textify
cd textify
pip install -r requirements.txt
python app.py
```

Ouvrez http://localhost:7860

## 📝 Licence

MIT
