"""
Lecteur OCR Pro — Version tout-en-un (multi-images)
Flask + EasyOCR + PaddleOCR (optionnel) dans un seul fichier.

Lancement :
    pip install flask pillow numpy easyocr
    python app.py
Puis ouvrir http://localhost:5000

PaddleOCR est optionnel. Pour l'activer :
    pip install paddleocr paddlepaddle
"""

import io
import time
import traceback
from flask import Flask, request, jsonify, render_template_string
from PIL import Image
import numpy as np

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB total (multi-images)


# ============================================================
# DÉTECTION DES MOTEURS DISPONIBLES
# ============================================================

EASYOCR_AVAILABLE = False
PADDLEOCR_AVAILABLE = False

try:
    import easyocr  # noqa: F401
    EASYOCR_AVAILABLE = True
    print("✓ EasyOCR détecté")
except Exception as e:
    print(f"✗ EasyOCR non disponible : {type(e).__name__}: {e}")

try:
    import paddleocr  # noqa: F401
    PADDLEOCR_AVAILABLE = True
    print("✓ PaddleOCR détecté")
except Exception as e:
    print(f"✗ PaddleOCR non disponible (optionnel) : {type(e).__name__}: {e}")

if not (EASYOCR_AVAILABLE or PADDLEOCR_AVAILABLE):
    print("\n⚠️  Aucun moteur OCR installé ! Lancez : pip install easyocr")


# ============================================================
# CHARGEMENT PARESSEUX DES MOTEURS
# ============================================================

_easyocr_readers = {}
_paddleocr_readers = {}


def get_easyocr_reader(languages):
    key = tuple(sorted(languages))
    if key not in _easyocr_readers:
        import easyocr
        print(f"[EasyOCR] Chargement du modèle pour : {languages}…")
        _easyocr_readers[key] = easyocr.Reader(list(languages), gpu=False, verbose=False)
        print(f"[EasyOCR] ✓ Modèle chargé.")
    return _easyocr_readers[key]


def get_paddleocr_reader(language):
    if language not in _paddleocr_readers:
        from paddleocr import PaddleOCR
        print(f"[PaddleOCR] Chargement du modèle pour : {language}…")
        _paddleocr_readers[language] = PaddleOCR(
            use_angle_cls=True,
            lang=language,
            show_log=False
        )
        print(f"[PaddleOCR] ✓ Modèle chargé.")
    return _paddleocr_readers[language]


# ============================================================
# MAPPING DES LANGUES
# ============================================================

EASYOCR_LANGS = {
    'fra': ['fr'], 'eng': ['en'], 'fra+eng': ['fr', 'en'],
    'spa': ['es'], 'deu': ['de'], 'ita': ['it'], 'por': ['pt'],
    'ara': ['ar'], 'chi_sim': ['ch_sim'], 'jpn': ['ja'], 'rus': ['ru'],
}

PADDLEOCR_LANGS = {
    'fra': 'fr', 'eng': 'en', 'fra+eng': 'fr',
    'spa': 'es', 'deu': 'german', 'ita': 'it', 'por': 'pt',
    'ara': 'ar', 'chi_sim': 'ch', 'jpn': 'japan', 'rus': 'ru',
}


# ============================================================
# EXTRACTION
# ============================================================

def extract_with_easyocr(image_bytes, lang_key):
    languages = EASYOCR_LANGS.get(lang_key, ['en'])
    reader = get_easyocr_reader(languages)

    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image_np = np.array(image)

    results = reader.readtext(image_np, detail=1, paragraph=False)

    if not results:
        return {'text': '', 'confidence': 0, 'lines': 0}

    lines, confidences = [], []
    for bbox, text, conf in results:
        lines.append(text)
        confidences.append(conf)

    return {
        'text': '\n'.join(lines),
        'confidence': round((sum(confidences) / len(confidences)) * 100, 1),
        'lines': len(lines)
    }


def extract_with_paddleocr(image_bytes, lang_key):
    language = PADDLEOCR_LANGS.get(lang_key, 'en')
    reader = get_paddleocr_reader(language)

    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image_np = np.array(image)

    results = reader.ocr(image_np, cls=True)

    if not results or not results[0]:
        return {'text': '', 'confidence': 0, 'lines': 0}

    lines, confidences = [], []
    for line in results[0]:
        text = line[1][0]
        conf = line[1][1]
        lines.append(text)
        confidences.append(conf)

    return {
        'text': '\n'.join(lines),
        'confidence': round((sum(confidences) / len(confidences)) * 100, 1),
        'lines': len(lines)
    }


# ============================================================
# TEMPLATE HTML
# ============================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>OCR Pro — Multi-images</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='80' font-size='80'>🐍</text></svg>" />
  <style>
    :root {
      --bg: #0f1419; --surface: #1a2028; --surface-2: #232a35;
      --border: #2d3642; --text: #e8eaed; --text-dim: #9aa3ad;
      --accent: #6366f1; --accent-hover: #818cf8;
      --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
      --radius: 10px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg); color: var(--text);
      min-height: 100vh; padding: 24px; line-height: 1.5;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 24px; }
    header h1 { font-size: 28px; font-weight: 600; margin-bottom: 8px; }
    header p { color: var(--text-dim); font-size: 14px; }
    .controls {
      display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
      margin-bottom: 16px; padding: 14px 16px;
      background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    }
    .controls label { font-size: 13px; color: var(--text-dim); }
    select, button {
      background: var(--surface-2); color: var(--text);
      border: 1px solid var(--border); border-radius: 6px;
      padding: 8px 14px; font-size: 14px; font-family: inherit;
      cursor: pointer; transition: all 0.15s;
    }
    select:hover, button:hover:not(:disabled) {
      border-color: var(--accent); background: #2a3340;
    }
    button.primary {
      background: var(--accent); border-color: var(--accent);
      color: white; font-weight: 500;
    }
    button.primary:hover:not(:disabled) {
      background: var(--accent-hover); border-color: var(--accent-hover);
    }
    button:disabled { opacity: 0.4; cursor: not-allowed; }

    /* Dropzone */
    #dropzone {
      border: 2px dashed var(--border); border-radius: var(--radius);
      padding: 32px; text-align: center; cursor: pointer;
      transition: all 0.15s; background: var(--surface);
      margin-bottom: 16px;
    }
    #dropzone:hover, #dropzone.dragover {
      border-color: var(--accent); background: #1e2530;
    }
    #dropzone svg { margin-bottom: 12px; opacity: 0.6; color: var(--text-dim); }
    #dropzone p { font-size: 14px; color: var(--text-dim); margin-bottom: 4px; }
    #dropzone small { font-size: 12px; color: #6b7280; }

    /* Liste des images */
    .images-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .image-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .image-card.processing { border-color: var(--accent); }
    .image-card.done { border-color: var(--success); }
    .image-card.error { border-color: var(--danger); }
    .image-card.pending { opacity: 0.7; }

    .image-header {
      display: flex; justify-content: space-between; align-items: center;
      gap: 8px;
    }
    .image-name {
      font-size: 12px; color: var(--text-dim);
      overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
      flex: 1;
    }
    .image-status-icon {
      font-size: 14px; flex-shrink: 0;
    }
    .image-thumb {
      width: 100%; height: 120px; object-fit: contain;
      background: var(--surface-2); border-radius: 6px;
    }
    .image-text {
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px;
      font-family: 'SF Mono', Menlo, monospace;
      font-size: 11px;
      max-height: 120px;
      overflow-y: auto;
      white-space: pre-wrap;
      color: var(--text);
    }
    .image-text.empty { color: var(--text-dim); font-style: italic; font-family: inherit; }
    .image-meta {
      font-size: 11px; color: var(--text-dim);
      display: flex; justify-content: space-between;
    }
    .image-card-actions {
      display: flex; gap: 6px;
    }
    .image-card-actions button {
      flex: 1; padding: 5px 8px; font-size: 11px;
    }
    .remove-btn {
      background: transparent; border: none; color: var(--text-dim);
      cursor: pointer; font-size: 14px; padding: 0 4px;
    }
    .remove-btn:hover { color: var(--danger); background: transparent; }

    /* Progression globale */
    .global-progress {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 12px 16px;
      margin-bottom: 16px; display: none;
    }
    .global-progress.show { display: block; }
    .global-progress-text {
      font-size: 13px; margin-bottom: 8px; color: var(--text);
    }
    .progress-bar-container {
      height: 6px; background: var(--surface-2);
      border-radius: 3px; overflow: hidden;
    }
    .progress-bar-fill {
      height: 100%; background: var(--accent);
      transition: width 0.3s ease;
    }

    /* Actions globales */
    .global-actions {
      display: flex; gap: 8px; flex-wrap: wrap;
      padding: 14px 16px;
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius);
      display: none;
    }
    .global-actions.show { display: flex; }

    .badge {
      display: inline-block; padding: 2px 8px; background: var(--surface-2);
      border: 1px solid var(--border); border-radius: 4px;
      font-size: 11px; color: var(--text-dim);
    }

    .info-banner {
      background: var(--surface-2); border: 1px solid var(--border);
      border-left: 3px solid var(--accent); border-radius: var(--radius);
      padding: 10px 14px; font-size: 13px; color: var(--text-dim);
      margin-bottom: 16px; display: none;
    }
    .info-banner.show { display: block; }

    .empty-state {
      text-align: center; padding: 40px 20px; color: var(--text-dim);
      font-size: 14px;
    }

    footer { text-align: center; margin-top: 32px; font-size: 12px; color: var(--text-dim); }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🐍 Lecteur OCR Pro — Multi-images</h1>
      <p>Sélectionnez plusieurs images à traiter en lot — 100% local, illimité</p>
    </header>

    <div class="info-banner" id="warmupBanner">
      ⏳ Premier lancement : le modèle d'IA est en cours de téléchargement (peut prendre 1-2 min). Les utilisations suivantes seront instantanées.
    </div>

    <div class="controls">
      <label for="engine">Moteur :</label>
      <select id="engine">
        {% if easyocr_available %}<option value="easyocr">EasyOCR (polyvalent, recommandé)</option>{% endif %}
        {% if paddleocr_available %}<option value="paddleocr">PaddleOCR (très précis, 1 langue à la fois)</option>{% endif %}
      </select>

      <label for="lang">Langue :</label>
      <select id="lang">
        <option value="fra">Français</option>
        <option value="eng">Anglais</option>
        <option value="fra+eng" selected>Français + Anglais</option>
        <option value="spa">Espagnol</option>
        <option value="deu">Allemand</option>
        <option value="ita">Italien</option>
        <option value="por">Portugais</option>
        <option value="ara">Arabe</option>
        <option value="chi_sim">Chinois (simplifié)</option>
        <option value="jpn">Japonais</option>
        <option value="rus">Russe</option>
      </select>

      <button id="extractBtn" class="primary" disabled>Extraire tout</button>
      <button id="resetBtn">Tout effacer</button>
      <span class="badge" id="countBadge">0 image</span>
    </div>

    <div id="dropzone">
      <input type="file" id="fileInput" accept="image/*" multiple style="display: none;" />
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <circle cx="9" cy="9" r="2"/>
        <path d="M21 15l-5-5L5 21"/>
      </svg>
      <p>Glissez plusieurs images ici</p>
      <small>ou cliquez pour parcourir (sélection multiple) / Ctrl+V pour coller</small>
    </div>

    <div class="global-progress" id="globalProgress">
      <div class="global-progress-text" id="globalProgressText">Traitement en cours…</div>
      <div class="progress-bar-container">
        <div class="progress-bar-fill" id="globalProgressBar" style="width: 0%;"></div>
      </div>
    </div>

    <div class="global-actions" id="globalActions">
      <button id="copyAllBtn">📋 Copier tout le texte</button>
      <button id="downloadAllBtn">💾 Télécharger un seul .txt</button>
      <button id="downloadSeparateBtn">📁 Télécharger un .txt par image</button>
    </div>

    <div id="imagesList" class="images-list"></div>

    <div id="emptyState" class="empty-state">
      Aucune image chargée. Glissez ou sélectionnez des images pour commencer.
    </div>

    <footer>
      Propulsé par Flask + EasyOCR{% if paddleocr_available %} + PaddleOCR{% endif %} — open-source, zéro API.
    </footer>
  </div>

  <script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const extractBtn = document.getElementById('extractBtn');
    const resetBtn = document.getElementById('resetBtn');
    const langSelect = document.getElementById('lang');
    const engineSelect = document.getElementById('engine');
    const countBadge = document.getElementById('countBadge');
    const imagesList = document.getElementById('imagesList');
    const emptyState = document.getElementById('emptyState');
    const globalProgress = document.getElementById('globalProgress');
    const globalProgressText = document.getElementById('globalProgressText');
    const globalProgressBar = document.getElementById('globalProgressBar');
    const globalActions = document.getElementById('globalActions');
    const copyAllBtn = document.getElementById('copyAllBtn');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    const downloadSeparateBtn = document.getElementById('downloadSeparateBtn');
    const warmupBanner = document.getElementById('warmupBanner');

    // images : [{ id, file, dataUrl, status, text, confidence, lines, elapsed, error }]
    let images = [];
    let nextId = 1;
    const usedEngines = new Set();
    let isProcessing = false;

    // Restauration des préférences
    const savedEngine = localStorage.getItem('engine');
    if (savedEngine && [...engineSelect.options].some(o => o.value === savedEngine)) {
      engineSelect.value = savedEngine;
    }
    langSelect.value = localStorage.getItem('lang') || 'fra+eng';

    engineSelect.addEventListener('change', () => localStorage.setItem('engine', engineSelect.value));
    langSelect.addEventListener('change', () => localStorage.setItem('lang', langSelect.value));

    function updateUI() {
      countBadge.textContent = images.length + (images.length <= 1 ? ' image' : ' images');
      extractBtn.disabled = images.length === 0 || isProcessing;
      emptyState.style.display = images.length === 0 ? 'block' : 'none';

      const hasResults = images.some(img => img.status === 'done' && img.text);
      globalActions.classList.toggle('show', hasResults && !isProcessing);
    }

    function renderImages() {
      imagesList.innerHTML = '';
      images.forEach(img => {
        const card = document.createElement('div');
        card.className = 'image-card ' + img.status;

        const statusIcons = {
          pending: '⏳',
          processing: '⚙️',
          done: '✓',
          error: '❌'
        };

        card.innerHTML = `
          <div class="image-header">
            <span class="image-name" title="${escapeHtml(img.file.name)}">${escapeHtml(img.file.name)}</span>
            <span class="image-status-icon">${statusIcons[img.status] || '⏳'}</span>
            <button class="remove-btn" data-id="${img.id}" title="Retirer">✕</button>
          </div>
          <img class="image-thumb" src="${img.dataUrl}" alt="" />
          <div class="image-text ${!img.text ? 'empty' : ''}">${
            img.status === 'error' ? ('Erreur : ' + escapeHtml(img.error || 'inconnue')) :
            img.text ? escapeHtml(img.text) :
            img.status === 'processing' ? 'Lecture en cours…' :
            img.status === 'done' ? '[Aucun texte détecté]' :
            'En attente…'
          }</div>
          ${img.status === 'done' ? `
            <div class="image-meta">
              <span>${img.lines} ligne(s) · ${img.confidence}%</span>
              <span>${img.elapsed}s</span>
            </div>
            <div class="image-card-actions">
              <button data-action="copy" data-id="${img.id}">Copier</button>
              <button data-action="download" data-id="${img.id}">Télécharger</button>
            </div>
          ` : ''}
        `;
        imagesList.appendChild(card);
      });

      // Event listeners pour les boutons des cartes
      imagesList.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', () => removeImage(parseInt(btn.dataset.id)));
      });
      imagesList.querySelectorAll('[data-action]').forEach(btn => {
        const id = parseInt(btn.dataset.id);
        const action = btn.dataset.action;
        btn.addEventListener('click', () => {
          const img = images.find(i => i.id === id);
          if (!img) return;
          if (action === 'copy') copyText(img.text, btn);
          if (action === 'download') downloadText(img.text, img.file.name);
        });
      });
    }

    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    function copyText(text, btn) {
      navigator.clipboard.writeText(text).then(() => {
        if (btn) {
          const original = btn.textContent;
          btn.textContent = '✓ Copié';
          setTimeout(() => { btn.textContent = original; }, 1500);
        }
      });
    }

    function downloadText(text, filename) {
      const baseName = filename.replace(/\.[^/.]+$/, '');
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = baseName + '.txt';
      a.click();
      URL.revokeObjectURL(url);
    }

    function addFiles(fileList) {
      const newFiles = [...fileList].filter(f => f.type.startsWith('image/'));
      if (newFiles.length === 0) return;

      newFiles.forEach(file => {
        const reader = new FileReader();
        const imgObj = {
          id: nextId++,
          file: file,
          dataUrl: '',
          status: 'pending',
          text: '',
          confidence: 0,
          lines: 0,
          elapsed: 0,
          error: null
        };
        reader.onload = (e) => {
          imgObj.dataUrl = e.target.result;
          renderImages();
        };
        reader.readAsDataURL(file);
        images.push(imgObj);
      });

      updateUI();
      renderImages();
    }

    function removeImage(id) {
      if (isProcessing) return;
      images = images.filter(i => i.id !== id);
      updateUI();
      renderImages();
    }

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      addFiles(e.target.files);
      fileInput.value = ''; // reset pour permettre de re-sélectionner les mêmes fichiers
    });
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) addFiles(e.dataTransfer.files);
    });

    document.addEventListener('paste', (e) => {
      const items = [...e.clipboardData.items].filter(i => i.type.startsWith('image/'));
      if (items.length === 0) return;
      const files = items.map(i => i.getAsFile()).filter(f => f);
      addFiles(files);
    });

    resetBtn.addEventListener('click', () => {
      if (isProcessing) return;
      images = [];
      updateUI();
      renderImages();
      globalProgress.classList.remove('show');
      warmupBanner.classList.remove('show');
    });

    extractBtn.addEventListener('click', async () => {
      if (images.length === 0 || isProcessing) return;

      isProcessing = true;
      updateUI();
      globalProgress.classList.add('show');

      // Marquer les images non traitées comme "à traiter"
      const toProcess = images.filter(img => img.status !== 'done');

      const engineKey = engineSelect.value + ':' + langSelect.value;
      const isFirstUse = !usedEngines.has(engineKey);

      if (isFirstUse) {
        warmupBanner.classList.add('show');
      }

      let processed = 0;
      const total = toProcess.length;

      for (const img of toProcess) {
        img.status = 'processing';
        renderImages();

        const stepText = isFirstUse && processed === 0
          ? `Chargement du modèle puis traitement de "${img.file.name}" (1/${total})…`
          : `Traitement de "${img.file.name}" (${processed + 1}/${total})…`;
        globalProgressText.textContent = stepText;
        globalProgressBar.style.width = ((processed / total) * 100) + '%';

        const formData = new FormData();
        formData.append('image', img.file);
        formData.append('engine', engineSelect.value);
        formData.append('lang', langSelect.value);

        try {
          const response = await fetch('/api/ocr', { method: 'POST', body: formData });
          const data = await response.json();

          if (!response.ok) {
            throw new Error(data.error || 'HTTP ' + response.status);
          }

          img.text = data.text || '';
          img.confidence = data.confidence;
          img.lines = data.lines;
          img.elapsed = data.elapsed;
          img.status = 'done';
          usedEngines.add(engineKey);
          warmupBanner.classList.remove('show');
        } catch (err) {
          img.status = 'error';
          img.error = err.message;
        }

        processed++;
        renderImages();
      }

      globalProgressBar.style.width = '100%';
      const successCount = toProcess.filter(i => i.status === 'done').length;
      const errorCount = toProcess.filter(i => i.status === 'error').length;
      globalProgressText.textContent = `✓ Terminé — ${successCount} réussite(s)${errorCount > 0 ? `, ${errorCount} erreur(s)` : ''}`;

      isProcessing = false;
      updateUI();

      // Cacher la barre de progression après 3s si tout va bien
      if (errorCount === 0) {
        setTimeout(() => globalProgress.classList.remove('show'), 3000);
      }
    });

    // ===== ACTIONS GLOBALES =====
    function getCombinedText() {
      return images
        .filter(img => img.status === 'done' && img.text)
        .map(img => `========== ${img.file.name} ==========\n${img.text}`)
        .join('\n\n');
    }

    copyAllBtn.addEventListener('click', () => {
      const text = getCombinedText();
      navigator.clipboard.writeText(text).then(() => {
        const original = copyAllBtn.textContent;
        copyAllBtn.textContent = '✓ Copié';
        setTimeout(() => { copyAllBtn.textContent = original; }, 1500);
      });
    });

    downloadAllBtn.addEventListener('click', () => {
      const text = getCombinedText();
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ocr-tout-' + Date.now() + '.txt';
      a.click();
      URL.revokeObjectURL(url);
    });

    downloadSeparateBtn.addEventListener('click', () => {
      // Téléchargement séquentiel d'un fichier par image
      const successImages = images.filter(img => img.status === 'done' && img.text);
      successImages.forEach((img, i) => {
        // Petit délai entre chaque téléchargement pour que le navigateur les accepte
        setTimeout(() => {
          downloadText(img.text, img.file.name);
        }, i * 200);
      });
    });

    updateUI();
    renderImages();
  </script>
</body>
</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        easyocr_available=EASYOCR_AVAILABLE,
        paddleocr_available=PADDLEOCR_AVAILABLE
    )


@app.route('/api/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image fournie'}), 400

    image_file = request.files['image']
    engine = request.form.get('engine', 'easyocr')
    lang = request.form.get('lang', 'fra+eng')

    if not image_file or image_file.filename == '':
        return jsonify({'error': 'Fichier image vide'}), 400

    try:
        image_bytes = image_file.read()
        start = time.time()

        if engine == 'easyocr':
            if not EASYOCR_AVAILABLE:
                return jsonify({'error': 'EasyOCR non installé. Lancez : pip install easyocr'}), 500
            result = extract_with_easyocr(image_bytes, lang)
        elif engine == 'paddleocr':
            if not PADDLEOCR_AVAILABLE:
                return jsonify({'error': 'PaddleOCR non installé. Lancez : pip install paddleocr paddlepaddle'}), 500
            result = extract_with_paddleocr(image_bytes, lang)
        else:
            return jsonify({'error': f'Moteur inconnu : {engine}'}), 400

        elapsed = round(time.time() - start, 2)

        return jsonify({
            'text': result['text'],
            'confidence': result['confidence'],
            'lines': result['lines'],
            'elapsed': elapsed,
            'engine': engine,
            'lang': lang,
        })

    except Exception as e:
        print("=" * 60)
        print("❌ ERREUR DÉTAILLÉE :")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({'error': f'{type(e).__name__}: {str(e)}'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("  📖 Lecteur OCR Pro — Multi-images (tout-en-un)")
    print("=" * 60)
    print(f"  EasyOCR    : {'✓ disponible' if EASYOCR_AVAILABLE else '✗ non installé'}")
    print(f"  PaddleOCR  : {'✓ disponible' if PADDLEOCR_AVAILABLE else '✗ non installé (optionnel)'}")
    print("=" * 60)
    print("  Ouvrir : http://localhost:5000")
    print("  Pour arrêter : Ctrl+C")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
