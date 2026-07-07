/**
 * Habit Snowball — Main Application
 * 主應用邏輯：UI 渲染、事件處理、狀態管理
 */

const App = (() => {
  let data;
  let currentView = 'home';
  let pendingAction = null;
  let awarenessTimer = null;
  let awarenessTimeLeft = 10;
  let awarenessHabitId = null;
  let journalDraftKeywords = [];
  let journalDraftImages = [];
  let activeImageDetailId = null;
  let journalKeywordsTouched = false;
  let blockedJournalKeywords = new Set();
  let isGoogleApiKeyVisible = false;
  let selectedJournalDate = new Date();
  let editingJournalEntryId = null;
  let expandedJournalEntryIds = new Set();
  let isRunningJournalAi = false;
  let editingRecordId = null;
  let isJournalDatePickerOpen = false;
  let journalVisibleCount = 3;
  const journalBatchSize = 3;
  let isLoadingMoreJournalEntries = false;
  let hasDeferredSyncRender = false;
  let summaryLoadingStates = {};
  let activeCommentEdit = null;
  let ollamaTunnelUrl = '';
  let ollamaStatus = 'testing'; // 'testing' | 'connected' | 'disconnected'

  const WEEKDAY_LABELS = ['日', '一', '二', '三', '四', '五', '六'];
  const GOOGLE_API_KEY_STORAGE_KEY = 'habit-snowball-google-api-key';
  const TEXT_SCALE_STORAGE_KEY = 'habit-snowball-text-scale';
  const DEFAULT_TEXT_SCALE = 1;
  const MIN_TEXT_SCALE = 0.9;
  const MAX_TEXT_SCALE = 1.2;
  const TEXT_SCALE_STEP = 0.1;
  const TEXT_SCALE_LABELS = {
    '0.9': '小字',
    '1.0': '標準',
    '1.1': '大字',
    '1.2': '特大'
  };
  const OLLAMA_TUNNEL_TIMEOUT_MS = 10000;
  const GOOGLE_GEMINI_MODEL = 'gemini-2.5-flash';
  const KEYWORD_STOP_WORDS = new Set([
    '今天', '自己', '一個', '一些', '因為', '所以', '如果', '但是', '然後',
    '這樣', '那個', '這個', '還有', '可以', '需要', '開始', '完成', '覺得',
    '真的', '進行', '目前', '以及', '我們', '你們', '他們', '不是', '沒有',
    '已經', '就是', '事情', '時候', '自己', '比較', '讓自己', '習慣雪球'
  ]);
  const TITLE_FILLER_PATTERNS = [
    /^今天[^，。:：]*[，,：:]\s*/,
    /^我發現[^，。:：]*[，,：:]\s*/,
    /^我覺得[^，。:：]*[，,：:]\s*/,
    /^這篇文章[^，。:：]*[，,：:]\s*/,
    /^這篇日記[^，。:：]*[，,：:]\s*/
  ];

  function normalizeTextScale(scale) {
    const parsed = Number(scale);
    if (!Number.isFinite(parsed)) return DEFAULT_TEXT_SCALE;
    const rounded = Math.round(parsed * 10) / 10;
    return Math.min(MAX_TEXT_SCALE, Math.max(MIN_TEXT_SCALE, rounded));
  }

  function getSavedTextScale() {
    return normalizeTextScale(localStorage.getItem(TEXT_SCALE_STORAGE_KEY) || DEFAULT_TEXT_SCALE);
  }

  function getTextScaleLabel(scale) {
    const normalized = normalizeTextScale(scale).toFixed(1);
    return TEXT_SCALE_LABELS[normalized] || TEXT_SCALE_LABELS[DEFAULT_TEXT_SCALE.toFixed(1)];
  }

  function updateTextScaleControls(scale) {
    const label = getTextScaleLabel(scale);
    const downBtn = document.getElementById('btn-text-scale-down');
    const upBtn = document.getElementById('btn-text-scale-up');
    const resetBtn = document.getElementById('btn-text-scale-reset');

    if (downBtn) downBtn.disabled = scale <= MIN_TEXT_SCALE;
    if (upBtn) upBtn.disabled = scale >= MAX_TEXT_SCALE;
    if (resetBtn) {
      resetBtn.textContent = label;
      resetBtn.title = `目前字級：${label}，點擊恢復標準字級`;
      resetBtn.setAttribute('aria-label', `目前字級 ${label}，點擊恢復標準字級`);
    }
  }

  function applyTextScale(scale, options) {
    const normalized = normalizeTextScale(scale);
    document.documentElement.style.setProperty('--ui-font-scale', String(normalized));
    localStorage.setItem(TEXT_SCALE_STORAGE_KEY, String(normalized));
    updateTextScaleControls(normalized);

    if (!(options && options.skipLayoutRefresh)) {
      window.requestAnimationFrame(() => {
        if (window.SnowballVis && typeof window.SnowballVis.resize === 'function') {
          window.SnowballVis.resize();
        }
        if (typeof renderWeeklyChart === 'function') {
          renderWeeklyChart();
        }
      });
    }

    return normalized;
  }

  function adjustTextScale(delta) {
    return applyTextScale(getSavedTextScale() + delta);
  }

  function htmlToMarkdown(html) {
    if (!html || !html.trim()) return '';
    let md = html;
    md = md.replace(/<ol[^>]*>\s*([\s\S]*?)<\/ol>/gi, (_, inner) =>
      inner.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (_li, item) => `${normalizeEditorText(item.replace(/<[^>]+>/g, '')) ? '1. ' : '1. '}${item.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '').trim()}\n`)
    );
    md = md.replace(/<ul[^>]*>\s*([\s\S]*?)<\/ul>/gi, (_, inner) =>
      inner.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (_li, item) => `- ${item.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '').trim()}\n`)
    );
    md = md.replace(/<(b|strong)[^>]*>(.*?)<\/(b|strong)>/gi, '**$2**');
    md = md.replace(/<br\s*\/?>/gi, '\n');
    md = md.replace(/<\/p>\s*<p[^>]*>/gi, '\n\n');
    md = md.replace(/<p[^>]*>/gi, '');
    md = md.replace(/<\/p>/gi, '');
    md = md.replace(/<\/div>\s*<div[^>]*>/gi, '\n');
    md = md.replace(/<div[^>]*>/gi, '');
    md = md.replace(/<\/div>/gi, '');
    md = md.replace(/<[^>]+>/g, '');
    md = md.replace(/&nbsp;/g, ' ');
    md = md.replace(/&amp;/g, '&');
    md = md.replace(/&lt;/g, '<');
    md = md.replace(/&gt;/g, '>');
    md = md.replace(/\n{3,}/g, '\n\n');
    return md.trim();
  }

  function markdownToHtml(md) {
    if (!md) return '';
    let html = md.replace(/<[^>]+>/g, '');
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const lines = html.split('\n');
    const result = [];
    let inList = false;
    let listType = null;
    let listStart = 1;

    lines.forEach(line => {
      const orderedMatch = line.match(/^(\d+)\.\s?(.*)$/);
      const bulletMatch = line.match(/^- (.*)$/);
      const headingMatch = line.match(/^#{1,6}\s+(.*)$/);

      if (orderedMatch) {
        if (!inList || listType !== 'ol') {
          if (inList) result.push(listType === 'ol' ? '</ol>' : '</ul>');
          listType = 'ol';
          listStart = parseInt(orderedMatch[1], 10) || 1;
          result.push(`<ol start="${listStart}">`);
          inList = true;
        }
        result.push(`<li>${orderedMatch[2] || ''}</li>`);
      } else if (bulletMatch) {
        if (!inList || listType !== 'ul') {
          if (inList) result.push(listType === 'ol' ? '</ol>' : '</ul>');
          result.push('<ul>');
          listType = 'ul';
          inList = true;
        }
        result.push(`<li>${bulletMatch[1] || ''}</li>`);
      } else if (headingMatch) {
        if (inList) {
          result.push(listType === 'ol' ? '</ol>' : '</ul>');
          inList = false;
          listType = null;
        }
        result.push(`<p><strong>${headingMatch[1] || ''}</strong></p>`);
      } else {
        if (inList) {
          result.push(listType === 'ol' ? '</ol>' : '</ul>');
          inList = false;
          listType = null;
        }
        if (line.trim()) result.push(`<p>${line}</p>`);
      }
    });

    if (inList) result.push(listType === 'ol' ? '</ol>' : '</ul>');
    return result.join('');
  }

  function insertHtmlAtCursor(editorEl, html) {
    if (!editorEl || !html) return;
    editorEl.focus();

    var selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      editorEl.insertAdjacentHTML('beforeend', html);
      return;
    }

    var range = selection.getRangeAt(0);
    if (!editorEl.contains(range.commonAncestorContainer)) {
      editorEl.insertAdjacentHTML('beforeend', html);
      return;
    }

    range.deleteContents();

    var container = document.createElement('div');
    container.innerHTML = html;
    var fragment = document.createDocumentFragment();
    var lastNode = null;
    var node = null;

    while ((node = container.firstChild)) {
      lastNode = fragment.appendChild(node);
    }

    range.insertNode(fragment);

    if (lastNode) {
      var nextRange = document.createRange();
      nextRange.setStartAfter(lastNode);
      nextRange.collapse(true);
      selection.removeAllRanges();
      selection.addRange(nextRange);
    }
  }

  function handleEditorPaste(editorEl, event) {
    var clipboard = event.clipboardData || window.clipboardData;
    if (!clipboard) return;

    var plainText = clipboard.getData('text/plain');
    if (!plainText) return;

    event.preventDefault();
    var normalizedText = normalizeEditorText(plainText);
    if (!normalizedText) return;

    insertHtmlAtCursor(editorEl, markdownToHtml(normalizedText));
  }

  function formatAiSummaryHtml(summary) {
    var normalized = normalizeEditorText(summary || '');
    if (!normalized) return '';

    normalized = normalized
      .replace(/([：:])\s*(?=\d+\.\s*)/g, '$1\n')
      .replace(/\s*[；;]\s*(?=\d+\.\s*)/g, '\n')
      .replace(/\s*[，,]\s*(?=\d+\.\s*)/g, '\n')
      .replace(/\s+(?=\d+\.\s*)/g, '\n');

    if (/\d+\.\s*/.test(normalized)) {
      return markdownToHtml(normalized);
    }

    return markdownToHtml(normalized);
  }

  function escapeHtml(text) {
    return (text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatZhDate(dateLike) {
    const date = new Date(dateLike);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}（${WEEKDAY_LABELS[date.getDay()]}）`;
  }

  function formatDateInputValue(dateLike) {
    const date = new Date(dateLike);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }

  function getDateKey(dateLike) {
    return formatDateInputValue(dateLike);
  }

  function normalizeEditorText(raw) {
    return (raw || '')
      .replace(/\u00a0/g, ' ')
      .replace(/\r/g, '')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  function splitIntoThoughts(text) {
    return normalizeEditorText(text)
      .split(/\n+|(?<=[。！？!?；;])/)
      .map(part => part.trim())
      .filter(Boolean);
  }

  function getSelectedJournalDate() {
    return new Date(selectedJournalDate);
  }

  function setSelectedJournalDate(dateLike) {
    const nextDate = new Date(dateLike);
    if (Number.isNaN(nextDate.getTime())) return;
    selectedJournalDate = startOfDay(nextDate);

    const dateInput = document.getElementById('journal-date-input');
    const dateLabel = document.getElementById('journal-current-date');
    if (dateInput) dateInput.value = formatDateInputValue(selectedJournalDate);
    if (dateLabel) dateLabel.textContent = formatZhDate(selectedJournalDate);

    const modal = document.getElementById('journal-composer-modal');
    if (modal && modal.classList.contains('show')) {
      saveJournalDraftToStorage();
    }
  }

  function addDays(dateLike, days) {
    const date = startOfDay(dateLike);
    date.setDate(date.getDate() + days);
    return date;
  }

  function extractKeywords(text, limit = 5) {
    const normalizedText = normalizeEditorText(text);
    const matches = normalizedText.match(/[\u4e00-\u9fffA-Za-zA-Z0-9]{2,8}/g) || [];
    const counts = new Map();

    matches.forEach(token => {
      const normalized = token.toLowerCase();
      if (KEYWORD_STOP_WORDS.has(token) || KEYWORD_STOP_WORDS.has(normalized)) return;
      if (token.length > 8) return;
      counts.set(token, (counts.get(token) || 0) + 1);
    });

    const phrases = normalizedText.match(/[\u4e00-\u9fff]{2,6}/g) || [];
    phrases.forEach(phrase => {
      if (KEYWORD_STOP_WORDS.has(phrase)) return;
      if (phrase.length < 2 || phrase.length > 6) return;
      counts.set(phrase, (counts.get(phrase) || 0) + 1);
    });

    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1] || b[0].length - a[0].length)
      .slice(0, limit)
      .map(([keyword]) => keyword);
  }

  function summarizeSentenceForTitle(sentence) {
    let output = normalizeEditorText(sentence);
    TITLE_FILLER_PATTERNS.forEach(pattern => {
      output = output.replace(pattern, '');
    });
    output = output.replace(/[。！？!?；;]+$/g, '').trim();
    output = output.replace(/^(因此|所以|但是|而且|然後)\s*/, '').trim();
    return output;
  }

  function generateJournalSummary(text) {
    const blocks = normalizeEditorText(text).split(/\n{2,}/).map(block => block.trim()).filter(Boolean);
    const sentences = splitIntoThoughts(text)
      .map(item => item.replace(/^[\-•\d.、\s]+/, '').trim())
      .filter(Boolean);
    const candidates = [...blocks, ...sentences].map(summarizeSentenceForTitle).filter(Boolean);
    const best = candidates.find(item => item.length >= 8 && item.length <= 24)
      || candidates.find(item => item.length >= 6)
      || '';

    if (best) return best.slice(0, 24);

    const keywords = extractKeywords(text, 3);
    if (keywords.length >= 2) return `${keywords[0]}：${keywords[1]}`;
    if (keywords.length === 1) return keywords[0];
    return '未命名日記';
  }

  function generateJournalTitle(text, dateLike = new Date()) {
    return `${formatZhDate(dateLike)}-${generateJournalSummary(text)}`;
  }

  function polishJournalText(text) {
    const normalized = normalizeEditorText(text);
    if (!normalized) return '';

    const lines = normalized.split('\n');
    const result = [];
    let paragraphBuffer = [];

    function flushParagraph() {
      if (!paragraphBuffer.length) return;
      result.push(paragraphBuffer.join(' ').replace(/\s+/g, ' ').trim());
      paragraphBuffer = [];
    }

    lines.forEach(rawLine => {
      const line = rawLine.trim();
      if (!line) {
        flushParagraph();
        if (result[result.length - 1] !== '') result.push('');
        return;
      }

      if (/^(\d+)\.\s/.test(line) || /^- /.test(line)) {
        flushParagraph();
        result.push(line);
        return;
      }

      paragraphBuffer.push(line);
    });

    flushParagraph();

    return result
      .join('\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  function getGoogleApiKey() {
    try {
      return (localStorage.getItem(GOOGLE_API_KEY_STORAGE_KEY) || '').trim();
    } catch (error) {
      console.error('Failed to load Google API key:', error);
      return '';
    }
  }

  function saveGoogleApiKey(apiKey) {
    localStorage.setItem(GOOGLE_API_KEY_STORAGE_KEY, apiKey.trim());
  }

  function clearGoogleApiKey() {
    localStorage.removeItem(GOOGLE_API_KEY_STORAGE_KEY);
  }

  function hasGoogleAiFallback() {
    return Boolean(getGoogleApiKey());
  }

  function formatAiSourceLabel(meta) {
    if (meta && meta.provider && meta.model) {
      return `${meta.provider} (${meta.model})`;
    }
    if (meta && meta.provider) {
      return meta.provider;
    }
    return ollamaStatus === 'connected'
      ? '本地 AI (gemma4)'
      : (hasGoogleAiFallback() ? 'Google AI (Gemini)' : '本地 AI');
  }

  function updateGoogleApiKeyStatus(message = '', isError = false) {
    const statusEl = document.getElementById('google-api-key-status-msg');
    if (!statusEl) return;
    statusEl.style.display = message ? 'block' : 'none';
    statusEl.style.color = isError ? 'var(--accent-negative)' : 'var(--accent-1)';
    statusEl.textContent = message;
  }

  function hydrateGoogleApiKeyInput() {
    const input = document.getElementById('google-api-key-input');
    const toggleBtn = document.getElementById('btn-toggle-google-api-key');
    if (!input || !toggleBtn) return;

    const savedKey = getGoogleApiKey();
    input.value = savedKey;
    input.type = isGoogleApiKeyVisible ? 'text' : 'password';
    toggleBtn.textContent = isGoogleApiKeyVisible ? '隱藏' : '顯示';
    updateGoogleApiKeyStatus(savedKey ? '已載入本機儲存的 Google API Key' : '');
    updateJournalAiMode();
  }

  async function checkOllamaConnection() {
    ollamaStatus = 'testing';
    updateJournalAiMode();

    try {
      const res = await fetch('/api/ollama-tunnel');
      if (res.ok) {
        const payload = await res.json();
        ollamaTunnelUrl = payload.tunnelUrl ? payload.tunnelUrl.trim() : '';
      }
    } catch (e) {
      console.error('Failed to fetch Ollama tunnel URL:', e);
    }

    if (!ollamaTunnelUrl) {
      console.log('No Ollama tunnel URL configured in database.');
      ollamaStatus = 'disconnected';
      updateJournalAiMode();
      return;
    }

    try {
      console.log(`Checking if Ollama is reachable at tunnel: ${ollamaTunnelUrl}...`);
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), OLLAMA_TUNNEL_TIMEOUT_MS);
      const testRes = await fetch(ollamaTunnelUrl, {
        signal: controller.signal,
        headers: { 'Accept': 'text/plain' }
      });
      clearTimeout(timeoutId);
      if (testRes.ok) {
        const text = await testRes.text();
        if (text.includes('Ollama')) {
          console.log(`Ollama is reachable at tunnel: ${ollamaTunnelUrl}`);
          ollamaStatus = 'connected';
          updateJournalAiMode();
          return;
        }
      }
    } catch (e) {
      console.warn(`Ollama tunnel check failed: ${ollamaTunnelUrl}`, e);
    }

    ollamaStatus = 'disconnected';
    updateJournalAiMode();
  }

  function updateJournalAiMode() {
    const modeEl = document.getElementById('journal-ai-mode');
    if (!modeEl) return;

    if (ollamaStatus === 'testing') {
      modeEl.textContent = hasGoogleAiFallback()
        ? '檢測本地 AI 中 · Gemini 備援'
        : '正在檢測本地 AI...';
      modeEl.style.color = '#8e92b2';
      modeEl.style.backgroundColor = 'rgba(142, 146, 178, 0.1)';
      modeEl.style.borderColor = 'rgba(142, 146, 178, 0.2)';
    } else if (ollamaStatus === 'connected') {
      modeEl.textContent = hasGoogleAiFallback()
        ? '🟢 本地 AI 優先 · Gemini 備援'
        : '🟢 本地 AI (gemma4)';
      modeEl.style.color = '#10b981';
      modeEl.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
      modeEl.style.borderColor = 'rgba(16, 185, 129, 0.2)';
    } else {
      if (hasGoogleAiFallback()) {
        modeEl.textContent = '🟡 Gemini 備援（本地離線）';
        modeEl.style.color = '#f59e0b';
        modeEl.style.backgroundColor = 'rgba(245, 158, 11, 0.1)';
        modeEl.style.borderColor = 'rgba(245, 158, 11, 0.2)';
      } else {
        modeEl.textContent = '🔴 AI 未啟動 (無金鑰)';
        modeEl.style.color = '#ef4444';
        modeEl.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
        modeEl.style.borderColor = 'rgba(239, 68, 68, 0.2)';
      }
    }
  }

  function setJournalAiButtonsDisabled(disabled, label) {
    const buttonIds = [
      'btn-journal-polish',
      'btn-journal-keywords',
      'btn-journal-title',
      'btn-journal-run-all'
    ];

    buttonIds.forEach(id => {
      const button = document.getElementById(id);
      if (!button) return;
      button.disabled = disabled;
      if (id === 'btn-journal-run-all') {
        button.textContent = disabled ? (label || '生成中...') : '一鍵生成';
      }
    });
  }

  function saveCaretPosition(context) {
    var selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return null;
    var range = selection.getRangeAt(0);
    var preSelectionRange = range.cloneRange();
    preSelectionRange.selectNodeContents(context);
    preSelectionRange.setEnd(range.startContainer, range.startOffset);
    var start = preSelectionRange.toString().length;
    return {
      start: start,
      end: start + range.toString().length
    };
  }

  function restoreCaretPosition(context, savedSel) {
    if (!savedSel) return;
    var selection = window.getSelection();
    if (!selection) return;
    var charIndex = 0;
    var range = document.createRange();
    range.setStart(context, 0);
    range.collapse(true);
    var nodeStack = [context], node, foundStart = false, stop = false;

    while (!stop && (node = nodeStack.pop())) {
      if (node.nodeType === 3) {
        var nextCharIndex = charIndex + node.length;
        if (!foundStart && savedSel.start >= charIndex && savedSel.start <= nextCharIndex) {
          range.setStart(node, savedSel.start - charIndex);
          foundStart = true;
        }
        if (foundStart && savedSel.end >= charIndex && savedSel.end <= nextCharIndex) {
          range.setEnd(node, savedSel.end - charIndex);
          stop = true;
        }
        charIndex = nextCharIndex;
      } else {
        var i = node.childNodes.length;
        while (i--) {
          nodeStack.push(node.childNodes[i]);
        }
      }
    }

    selection.removeAllRanges();
    selection.addRange(range);
  }

  function setupWysiwygEditor(editorEl) {
    if (!editorEl) return;
    if (editorEl.dataset.wysiwygSetup === 'true') return;
    editorEl.dataset.wysiwygSetup = 'true';

    editorEl.addEventListener('keydown', function(e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        document.execCommand('bold', false, null);
        var evt = document.createEvent('HTMLEvents');
        evt.initEvent('input', true, true);
        editorEl.dispatchEvent(evt);
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i') {
        e.preventDefault();
        document.execCommand('italic', false, null);
        var evt = document.createEvent('HTMLEvents');
        evt.initEvent('input', true, true);
        editorEl.dispatchEvent(evt);
      }
    });
    editorEl.addEventListener('paste', function(event) {
      handleEditorPaste(editorEl, event);
    });
  }

  function autoFormatJournalOutline() {
    // Deprecated: replaced by setupWysiwygEditor
  }

  function setSummaryLoadingState(entryId, nextState) {
    if (!entryId) return;
    if (nextState) {
      summaryLoadingStates[entryId] = nextState;
    } else {
      delete summaryLoadingStates[entryId];
    }
  }

  async function callGoogleAiJson(systemPrompt, userPrompt, options) {
    options = options || {};
    var includeMeta = options.includeMeta === true;
    var onStatus = typeof options.onStatus === 'function' ? options.onStatus : null;

    // 1. Try local Ollama (via Cloudflare Tunnel) first if connected
    let useOllama = false;
    let targetOllamaUrl = ollamaTunnelUrl;

    if (ollamaStatus === 'connected' && targetOllamaUrl) {
      useOllama = true;
    } else {
      // Lazy synchronization check if not connected, in case the tunnel URL was just updated
      try {
        console.log('Ollama not connected. Performing lazy check for updated tunnel...');
        const res = await fetch('/api/ollama-tunnel');
        if (res.ok) {
          const payload = await res.json();
          const freshUrl = payload.tunnelUrl ? payload.tunnelUrl.trim() : '';
          if (freshUrl) {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), OLLAMA_TUNNEL_TIMEOUT_MS);
            const testRes = await fetch(freshUrl, {
              signal: controller.signal,
              headers: { 'Accept': 'text/plain' }
            });
            clearTimeout(timeoutId);
            if (testRes.ok) {
              const text = await testRes.text();
              if (text.includes('Ollama')) {
                useOllama = true;
                targetOllamaUrl = freshUrl;
                ollamaTunnelUrl = freshUrl;
                ollamaStatus = 'connected';
                updateJournalAiMode();
              }
            }
          }
        }
      } catch (e) {
        console.log('Lazy Ollama check failed or timed out:', e);
      }
    }

    if (useOllama && targetOllamaUrl) {
      try {
        const cleanUrl = targetOllamaUrl.replace(/\/$/, '');
        let response = null;
        let lastOllamaError = null;
        for (const model of ['gemma4:e2b', 'gemma4:e4b']) {
          let modelTimeoutId = null;
          try {
            if (onStatus) {
              onStatus({
                provider: '本地 AI',
                providerKey: 'ollama',
                model: model
              });
            }
            console.log(`Connecting to local Ollama via Tunnel: ${targetOllamaUrl}, trying model: ${model}`);
            const modelController = new AbortController();
            modelTimeoutId = setTimeout(() => {
              console.warn(`Ollama request for model ${model} timed out after 90 seconds. Aborting...`);
              modelController.abort();
            }, 90000);

            const res = await fetch(`${cleanUrl}/api/chat`, {
              method: 'POST',
              signal: modelController.signal,
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                model: model,
                messages: [
                  { role: 'system', content: systemPrompt },
                  { role: 'user', content: userPrompt }
                ],
                stream: false,
                options: {
                  temperature: 0.4
                },
                format: 'json'
              })
            });

            if (modelTimeoutId) clearTimeout(modelTimeoutId);

            if (res.status === 404) {
              console.warn(`Model ${model} not found on Ollama server (404). Trying next model...`);
              continue;
            }

            if (!res.ok) {
              throw new Error(`Ollama server returned status ${res.status}`);
            }

            res.__model = model;
            response = res;
            break;
          } catch (err) {
            if (modelTimeoutId) clearTimeout(modelTimeoutId);
            lastOllamaError = err;
            console.error(`Ollama call with model ${model} failed:`, err);
          }
        }

        if (!response) {
          throw lastOllamaError || new Error('All local Ollama models failed');
        }

        const result = await response.json();
        const content = result.message && result.message.content ? result.message.content.trim() : '';
        if (!content) {
          throw new Error('Ollama returned empty response content');
        }

        console.log('Successfully completed call using Ollama model via Tunnel');
        var parsedOllama = JSON.parse(content);
        if (includeMeta) {
          return {
            data: parsedOllama,
            meta: {
              provider: '本地 AI',
              providerKey: 'ollama',
              model: response && response.__model ? response.__model : 'gemma4'
            }
          };
        }
        return parsedOllama;
      } catch (ollamaError) {
        console.error('Ollama request failed, falling back to Gemini:', ollamaError);
        ollamaStatus = 'disconnected';
        updateJournalAiMode();
      }
    }

    // 2. Gemini fallback path
    console.log('Using Gemini API fallback...');
    const apiKey = getGoogleApiKey();
    if (!apiKey) {
      throw new Error('missing_api_key');
    }

    const models = [GOOGLE_GEMINI_MODEL, 'gemini-1.5-flash'];
    let lastError = null;

    for (const model of models) {
      try {
        if (onStatus) {
          onStatus({
            provider: 'Google AI',
            providerKey: 'gemini',
            model: model
          });
        }
        console.log(`Calling Gemini API using model: ${model}`);
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(apiKey)}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            contents: [
              {
                role: 'user',
                parts: [
                  {
                    text: `${systemPrompt}\n\n${userPrompt}`
                  }
                ]
              }
            ],
            generationConfig: {
              temperature: 0.4,
              responseMimeType: 'application/json'
            }
          })
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`google_ai_request_failed:${response.status}:${errorText}`);
        }

        const result = await response.json();
        const text = (result && result.candidates && result.candidates[0] && result.candidates[0].content && result.candidates[0].content.parts)
          ? result.candidates[0].content.parts.map(function(part) { return part.text || ''; }).join('').trim()
          : '';
        if (!text) {
          throw new Error('google_ai_empty_response');
        }

        console.log(`Successfully completed call using Gemini model: ${model}`);
        var parsedGemini = JSON.parse(text);
        if (includeMeta) {
          return {
            data: parsedGemini,
            meta: {
              provider: 'Google AI',
              providerKey: 'gemini',
              model: model
            }
          };
        }
        return parsedGemini;
      } catch (error) {
        console.error(`Google AI call with model ${model} failed:`, error);
        lastError = error;
      }
    }
    throw lastError || new Error('google_ai_failed_all_models');
  }

  async function generateAiJournalPolish(text, options) {
    var result = await callGoogleAiJson(
      '你是中文日記編輯。請把使用者原文潤成更順、更清楚、保留原意的繁體中文內容。必須保留原本的段落結構：一段文字就維持一段，原本是條列式就維持條列式。若是條列內容，請整理成 markdown 可辨識的大綱格式，例如 1. 2. 3. 或 - 。請同時提供一組對比清單，說明本次潤稿相較於原文進行了哪些重要的修正或改進。輸出 JSON 格式如下：{"polished":"...", "changes":["條列出本次潤稿的修改重點，包括修正錯字、調整語句、或重新排版的地方... (繁體中文)"]}，不要輸出其他內容。',
      `請潤稿這篇日記：\n${text}`,
      options
    );
    if (options && options.includeMeta) {
      return {
        polished: (result.data && result.data.polished) || '',
        changes: (result.data && Array.isArray(result.data.changes)) ? result.data.changes : [],
        meta: result.meta || null
      };
    }
    return result;
  }
  function getAllUniqueKeywords() {
    const journals = Storage.load().journalEntries || [];
    const unique = new Set();
    journals.forEach(j => {
      if (Array.isArray(j.keywords)) {
        j.keywords.forEach(k => {
          if (k) unique.add(k);
        });
      }
    });
    return Array.from(unique);
  }

  async function generateAiJournalKeywords(text, options) {
    const existingKeywords = getAllUniqueKeywords();
    const existingStr = existingKeywords.length > 0
      ? `我們目前已經有使用的關鍵字庫為：[${existingKeywords.join(', ')}]。請仔細分析日記內容，並「優先」且「儘可能」從已有的關鍵字庫中挑選最符合日記主題的關鍵字（完全相同字樣的字詞）。如果已有庫中確實沒有適合的，你才可以自己創造新的關鍵字。`
      : '請自行根據日記內容創造適合的關鍵字。';
    var result = await callGoogleAiJson(
      `你是中文 SEO 編輯與主題標籤設計師。請從日記中抽出 3 到 6 個最重要、可當作 SEO 標籤的繁體中文關鍵字。
每個關鍵字請控制在 2 到 8 個字之間，不能是完整句子或太長的片語。

${existingStr}

請務必返回 JSON 格式，例如：
{
  "keywords": ["關鍵字1", "關鍵字2", "關鍵字3"]
}`,
      `請抽取這篇日記的關鍵字：\n${text}`,
      options
    );
    if (options && options.includeMeta) {
      return {
        keywords: (result.data && result.data.keywords) || [],
        meta: result.meta || null
      };
    }
    return result;
  }
  async function generateAiJournalTitle(text, options) {
    var result = await callGoogleAiJson(
      '你是中文編輯。請根據整篇文章內容做總結，生成一個精煉、具主題感的繁體中文標題。不要照抄第一句，不要包含日期，標題長度控制在 10 到 24 個字。輸出 JSON：{"title":"..."}。',
      `請為這篇日記生成標題摘要：\n${text}`,
      options
    );
    if (options && options.includeMeta) {
      return {
        title: (result.data && result.data.title) || '',
        meta: result.meta || null
      };
    }
    return result;
  }

  function startOfDay(dateLike) {
    const date = new Date(dateLike);
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
  }

  function getDayDiff(fromDate, toDate) {
    return Math.floor((startOfDay(toDate) - startOfDay(fromDate)) / (1000 * 60 * 60 * 24));
  }

  function recomputeStatsFromRecords(records) {
    const sorted = [...records].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const stats = {
      ...Storage.getDefaultData().stats
    };

    let runningPoints = 0;

    sorted.forEach(record => {
      runningPoints = Math.max(0, runningPoints + (record.points || 0));

      if (record.action === 'resisted' || record.action === 'completed') {
        stats.totalResisted += 1;

        const recordDayIso = startOfDay(record.timestamp).toISOString();
        if (!stats.lastActiveDate) {
          stats.currentStreak = 1;
          stats.lastActiveDate = recordDayIso;
        } else {
          const diffDays = getDayDiff(stats.lastActiveDate, record.timestamp);
          if (diffDays === 0) {
            stats.lastActiveDate = recordDayIso;
          } else if (diffDays === 1) {
            stats.currentStreak += 1;
            stats.lastActiveDate = recordDayIso;
          } else {
            stats.currentStreak = 1;
            stats.lastActiveDate = recordDayIso;
          }
        }
        stats.longestStreak = Math.max(stats.longestStreak, stats.currentStreak);
      }

      if (record.action === 'relapsed') {
        stats.currentStreak = 0;
      }
    });

    stats.totalPoints = runningPoints;

    if (stats.lastActiveDate) {
      const streakResult = ScoringEngine.updateStreak(stats.lastActiveDate, stats.currentStreak);
      if (streakResult.updated) {
        stats.currentStreak = streakResult.currentStreak;
        stats.lastActiveDate = streakResult.lastActiveDate;
        stats.longestStreak = Math.max(stats.longestStreak, stats.currentStreak);
      }
    }

    return stats;
  }

  function rebuildHabitDerivedFields(habits, records) {
    return habits.map(habit => ({
      ...habit,
      totalActions: records.filter(record => record.habitId === habit.id).length
    }));
  }

  function initKeywordInput() {
    const input = document.getElementById('journal-keyword-input');
    const dropdown = document.getElementById('keyword-autocomplete-dropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', (e) => {
      const val = e.target.value.trim().toLowerCase();
      if (!val) {
        dropdown.style.display = 'none';
        return;
      }
      const existing = getAllUniqueKeywords();
      const matches = existing.filter(k => k.toLowerCase().includes(val) && !journalDraftKeywords.includes(k));
      
      if (matches.length > 0) {
        dropdown.innerHTML = matches.map(m => `<div class="keyword-dropdown-item" onclick="App.addJournalKeyword('${escapeHtml(m)}')" style="padding: 6px 12px; cursor: pointer; border-bottom: 1px solid var(--border-subtle); color: var(--text-primary); font-size: 12px;">${escapeHtml(m)}</div>`).join('');
        dropdown.style.display = 'block';
      } else {
        dropdown.style.display = 'none';
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = input.value.trim();
        if (val) {
          addJournalKeyword(val);
        }
      }
    });

    document.addEventListener('click', (e) => {
      if (e.target !== input && e.target !== dropdown && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  }

  function hideLoadingScreen() {
    const loader = document.getElementById('app-loading-screen');
    if (loader) {
      loader.style.opacity = '0';
      loader.style.visibility = 'hidden';
      setTimeout(function() {
        if (loader.parentNode) {
          loader.parentNode.removeChild(loader);
        }
      }, 450);
    }
  }

  async function init() {
    applyTextScale(getSavedTextScale(), { skipLayoutRefresh: true });

    var loginIdentity = localStorage.getItem('login-identity');
    if (!loginIdentity) {
      var overlay = document.getElementById('identity-picker-overlay');
      if (overlay) {
        overlay.style.display = 'flex';
      }
      return;
    }
    localStorage.setItem('last-selected-author', loginIdentity);

    // Apply saved theme preference (default to light)
    var savedTheme = localStorage.getItem('theme-preference') || 'light';
    applyTheme(savedTheme);

    // Hydrate remote state before local mutations such as streak updates.
    data = Storage.load();
    await Storage.hydrateFromRemote();
    data = Storage.load();
    setSelectedJournalDate(new Date());

    var lastAuthor = loginIdentity;
    document.querySelectorAll('.author-btn').forEach(function(btn) {
      btn.classList.toggle('active', btn.dataset.author === lastAuthor);
    });

    var activeAuthors = Storage.getActiveAuthors();
    if (!activeAuthors.length) {
      activeAuthors = ['小葦', '小花'];
      Storage.setActiveAuthors(activeAuthors);
    }
    document.querySelectorAll('.g-author-btn').forEach(function(btn) {
      btn.classList.toggle('active', activeAuthors.includes(btn.dataset.author));
    });

    initKeywordInput();
    updateActiveStats();

    var streakResult = ScoringEngine.updateStreak(
      activeStats.lastActiveDate,
      activeStats.currentStreak
    );
    if (streakResult.updated) {
      activeStats.currentStreak = streakResult.currentStreak;
      activeStats.lastActiveDate = streakResult.lastActiveDate;
      if (streakResult.currentStreak > (activeStats.longestStreak || 0)) {
        activeStats.longestStreak = streakResult.currentStreak;
      }
      Storage.updateStats(activeStats);
    }

    var canvas = document.getElementById('snowball-canvas');
    if (canvas) SnowballVis.init(canvas);

    var stage = ScoringEngine.getStage(activeStats.totalPoints);
    SnowballVis.setPoints(activeStats.totalPoints);
    SnowballVis.setStage(stage);
    SnowballVis.start();

    renderAll();
    bindEvents();

    Storage.setSyncCallback(renderAllUnlessTyping);
    Storage.startSync();

    var syncUserInput = document.getElementById('sync-user-input');
    if (syncUserInput) {
      var urlParams = new URLSearchParams(window.location.search);
      var user = urlParams.get('user') || localStorage.getItem('simulated-current-user') || 'default';
      syncUserInput.value = user === 'default' ? '' : user;
    }

    hydrateGoogleApiKeyInput();
    checkOllamaConnection();

    // No onboarding toast anymore
    /*
    if (data.habits.length === 0) {
      showOnboarding();
    }
    */
  }

  function selectLoginIdentity(author) {
    localStorage.setItem('login-identity', author);
    localStorage.setItem('last-selected-author', author);
    resetJournalVisibleCount();
    var overlay = document.getElementById('identity-picker-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
    init();
  }

  function applyTheme(theme) {
    var toggleBtnIcon = document.querySelector('#btn-theme-toggle .theme-icon');
    if (theme === 'light') {
      document.body.classList.add('light-theme');
      if (toggleBtnIcon) toggleBtnIcon.textContent = '🌙';
    } else {
      document.body.classList.remove('light-theme');
      if (toggleBtnIcon) toggleBtnIcon.textContent = '☀️';
    }
    localStorage.setItem('theme-preference', theme);
  }

  function toggleTheme() {
    var isLight = document.body.classList.contains('light-theme');
    applyTheme(isLight ? 'dark' : 'light');
  }

  let activeStats = null;

  function updateActiveStats() {
    const activeAuthor = localStorage.getItem('last-selected-author') || '小葦';
    
    // Filter records for the active author, also applying start date limit for Xiaohua
    const activeRecords = data.records.filter(r => {
      const author = r.author || '小葦';
      if (author !== activeAuthor) return false;
      if (activeAuthor === '小花') {
        const recordDate = new Date(r.timestamp);
        const startDate = new Date('2026-06-23T00:00:00+08:00');
        if (recordDate < startDate) return false;
      }
      return true;
    });

    activeStats = recomputeStatsFromRecords(activeRecords);
  }

  function renderAll() {
    data = Storage.load();
    updateActiveStats();
    renderScore();
    renderStage();
    renderHabits();
    renderHistory();
    renderJournal();
    renderStats();
    renderWeeklyChart();
    updateGlobalAuthorBadges();
    hideLoadingScreen();
  }

  function isTypingInEditor() {
    var activeEl = document.activeElement;
    if (!activeEl) return false;
    return activeEl.classList.contains('comment-content-input') ||
      activeEl.id === 'journal-input' ||
      activeEl.id === 'note-input' ||
      activeEl.tagName === 'INPUT' ||
      activeEl.tagName === 'TEXTAREA' ||
      activeEl.isContentEditable;
  }

  function renderAllUnlessTyping() {
    if (isTypingInEditor()) {
      hasDeferredSyncRender = true;
      return;
    }
    hasDeferredSyncRender = false;
    renderAll();
  }

  function flushDeferredSyncRender() {
    if (!hasDeferredSyncRender || isTypingInEditor()) return;
    hasDeferredSyncRender = false;
    renderAll();
  }

  function getVisibleComments(comments) {
    return (Array.isArray(comments) ? comments : []).filter(function(comment) {
      return comment && comment.id && !comment.deletedAt;
    });
  }

  function getActiveCommentEditForEntry(entryId, comments) {
    if (!activeCommentEdit || activeCommentEdit.entryId !== entryId) return null;
    var match = (Array.isArray(comments) ? comments : []).find(function(comment) {
      return comment && comment.id === activeCommentEdit.commentId && !comment.deletedAt;
    }) || null;
    if (!match) {
      activeCommentEdit = null;
    }
    return match;
  }

  function focusCommentEditor(entryId) {
    var editor = document.querySelector('.add-comment-box[data-comment-entry-id="' + entryId + '"] .comment-content-input');
    if (!editor) return;
    editor.focus();
    var selection = window.getSelection();
    if (!selection) return;
    var range = document.createRange();
    range.selectNodeContents(editor);
    range.collapse(false);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  function renderScore() {
    const scoreEl = document.getElementById('total-score');
    const oldScore = parseInt(scoreEl.textContent.replace(/,/g, ''), 10) || 0;
    if (oldScore !== activeStats.totalPoints) {
      Animations.countUp(scoreEl, oldScore, activeStats.totalPoints);
    } else {
      scoreEl.textContent = activeStats.totalPoints.toLocaleString();
    }
  }

  function renderStage() {
    const stage = ScoringEngine.getStage(activeStats.totalPoints);
    const progress = ScoringEngine.getStageProgress(activeStats.totalPoints);

    document.getElementById('stage-name').textContent = `${stage.emoji} ${stage.name}`;
    document.getElementById('stage-progress-fill').style.width = `${progress}%`;
    document.getElementById('stage-progress-fill').style.background =
      `linear-gradient(90deg, ${stage.color1}, ${stage.color2})`;

    const nextEl = document.getElementById('next-stage-info');
    if (stage.nextPoints) {
      nextEl.textContent = `距離下一階段還需 ${stage.nextPoints - activeStats.totalPoints} 分`;
    } else {
      nextEl.textContent = '🏆 已達最高階段！';
    }

    SnowballVis.setPoints(activeStats.totalPoints);
    SnowballVis.setStage(stage);
    document.documentElement.style.setProperty('--accent-1', stage.color1);
    document.documentElement.style.setProperty('--accent-2', stage.color2);
  }

  function renderHabits() {
    const container = document.getElementById('habits-list');
    if (!container) return;

    if (data.habits.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>還沒有習慣，點擊下方新增第一個！</p>
        </div>
      `;
      return;
    }

    container.innerHTML = data.habits.map(habit => {
      const habitRecords = Storage.getRecordsForHabit(habit.id);
      const resistCount = habitRecords.filter(r =>
        r.action === 'resisted' || r.action === 'completed'
      ).length;
      const nextPts = ScoringEngine.getResistPoints(resistCount + 1);

      return `
        <div class="habit-card" data-habit-id="${habit.id}">
          <div class="habit-header">
            <span class="habit-emoji">${habit.emoji}</span>
            <div class="habit-info">
              <h3 class="habit-name">${habit.name}</h3>
              <span class="habit-count">${habit.type === 'resist' ? '已進化' : '已完成'} ${resistCount} 次 · 下次 +${nextPts}</span>
            </div>
            <button class="habit-delete" onclick="App.deleteHabit('${habit.id}')" title="刪除">×</button>
          </div>
          <div class="habit-actions">
            ${habit.type === 'resist' ? `
              <button class="action-btn action-resist" onclick="App.promptAction('${habit.id}', 'resisted')">
                <span class="action-icon">🧬</span>
                <span>進化了</span>
              </button>
              <button class="action-btn action-urge" onclick="App.startAwareness('${habit.id}')">
                <span class="action-icon">⚡</span>
                <span>起念頭</span>
              </button>
              <button class="action-btn action-relapse" onclick="App.promptAction('${habit.id}', 'relapsed')">
                <span class="action-icon">💔</span>
                <span>破戒了</span>
              </button>
            ` : `
              <button class="action-btn action-resist" onclick="App.promptAction('${habit.id}', 'completed')">
                <span class="action-icon">✅</span>
                <span>做到了</span>
              </button>
              <button class="action-btn action-urge" onclick="App.startAwareness('${habit.id}')">
                <span class="action-icon">⚡</span>
                <span>想偷懶</span>
              </button>
              <button class="action-btn action-relapse" onclick="App.promptAction('${habit.id}', 'relapsed')">
                <span class="action-icon">❌</span>
                <span>沒做到</span>
              </button>
            `}
          </div>
        </div>
      `;
    }).join('');
  }

  function renderHistory() {
    const container = document.getElementById('history-list');
    if (!container) return;

    const records = Storage.getRecentRecords(15);
    if (records.length === 0) {
      container.innerHTML = '<div class="empty-state"><p>還沒有記錄</p></div>';
      return;
    }

    container.innerHTML = records.map(record => {
      const habit = data.habits.find(h => h.id === record.habitId);
      const habitName = habit ? habit.name : '已刪除的習慣';
      const habitEmoji = habit ? habit.emoji : '❓';
      const d = new Date(record.timestamp);
      const timeStr = `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;

      const actionLabels = {
        resisted: '進化了',
        completed: '做到了',
        urge: '念起了',
        relapsed: '破戒了'
      };

      const actionClasses = {
        resisted: 'positive',
        completed: 'positive',
        urge: 'warning',
        relapsed: 'negative'
      };

      const hasNote = record.note && record.note.trim() !== '';
      const noteHtml = hasNote ? `<div class="history-note">${markdownToHtml(record.note)}</div>` : '';
      const toggleIcon = hasNote ? '<span class="history-note-toggle-icon">▶</span>' : '';

      return `
        <div class="history-item ${actionClasses[record.action]} ${hasNote ? 'has-note' : ''}" ${hasNote ? 'onclick="this.classList.toggle(\'expanded\')"' : ''}>
          <div class="history-row">
            <span class="history-emoji">${habitEmoji}</span>
            <div class="history-info">
              <span class="history-habit">${habitName}</span>
              <span class="history-action">${actionLabels[record.action]}</span>
            </div>
            ${toggleIcon}
            <span class="history-points ${record.points >= 0 ? 'positive' : 'negative'}">
              ${record.points > 0 ? '+' : ''}${record.points}
            </span>
            <span class="history-time">${timeStr}</span>
            <button class="history-delete-btn" onclick="event.stopPropagation();App.editRecord('${record.id}')" title="編輯這筆記錄">編輯</button>
            <button class="history-delete-btn" onclick="event.stopPropagation();App.deleteRecord('${record.id}')" title="刪除此筆記錄">刪除</button>
          </div>
          ${noteHtml}
        </div>
      `;
    }).join('');
  }

  function renderStats() {
    document.getElementById('stat-streak').textContent = activeStats.currentStreak || 0;
    document.getElementById('stat-longest').textContent = activeStats.longestStreak || 0;
    document.getElementById('stat-resisted').textContent = activeStats.totalResisted || 0;

    const todayRecords = Storage.getTodayRecords();
    const todayPoints = todayRecords.reduce((sum, record) => sum + record.points, 0);
    document.getElementById('stat-today').textContent = `${todayPoints > 0 ? '+' : ''}${todayPoints}`;

    const streakBonusEl = document.getElementById('streak-bonus');
    if (streakBonusEl) {
      const bonus = ScoringEngine.getStreakBonus(activeStats.currentStreak);
      if (bonus > 0) {
        streakBonusEl.textContent = `每天額外 +${bonus}`;
        streakBonusEl.style.display = 'inline-block';
      } else {
        streakBonusEl.style.display = 'none';
      }
    }
  }

  function getJournalDayMap(entries) {
    const authorGroups = {};
    entries.forEach(entry => {
      const author = entry.author || '小葦';
      if (!authorGroups[author]) authorGroups[author] = [];
      authorGroups[author].push(entry);
    });

    const dayMap = new Map();

    Object.keys(authorGroups).forEach(author => {
      const groupEntries = authorGroups[author];
      const sortedAsc = [...groupEntries].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
      const uniqueDates = [];
      sortedAsc.forEach(entry => {
        const key = getDateKey(entry.createdAt);
        if (!uniqueDates.includes(key)) uniqueDates.push(key);
        dayMap.set(entry.id, uniqueDates.indexOf(key) + 1);
      });
    });

    return dayMap;
  }

  function resetJournalVisibleCount() {
    journalVisibleCount = journalBatchSize;
    isLoadingMoreJournalEntries = false;
  }

  function loadMoreJournalEntries() {
    if (isLoadingMoreJournalEntries) return;

    var marker = document.getElementById('journal-load-more-marker');
    if (!marker || marker.getAttribute('data-has-more') !== 'true') return;

    isLoadingMoreJournalEntries = true;
    renderJournal();

    window.setTimeout(function() {
      journalVisibleCount += journalBatchSize;
      isLoadingMoreJournalEntries = false;
      renderJournal();
    }, 220);
  }

  function handleJournalInfiniteScroll() {
    var journalView = document.getElementById('view-journal');
    if (!journalView || !journalView.classList.contains('active')) return;

    var marker = document.getElementById('journal-load-more-marker');
    if (!marker || marker.getAttribute('data-has-more') !== 'true') return;

    var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    var rect = marker.getBoundingClientRect();
    if (rect.top <= viewportHeight + 180) {
      loadMoreJournalEntries();
    }
  }

  function renderJournal() {
    const currentDateEl = document.getElementById('journal-current-date');
    const currentDayEl = document.getElementById('journal-current-day');
    const listEl = document.getElementById('journal-list');
    const loadMoreEl = document.getElementById('journal-pagination');
    if (!currentDateEl || !currentDayEl || !listEl) return;
    syncSearchAuthorFilterUI();

    const entries = Storage.getJournalEntries();
    const allEntries = Storage.load().journalEntries || [];
    const dayMap = getJournalDayMap(allEntries);

    const loginIdentity = localStorage.getItem('login-identity') || '小葦';
    const authorEntries = allEntries.filter(entry => (entry.author || '小葦') === loginIdentity);
    const selectedDateKey = getDateKey(getSelectedJournalDate());
    const uniqueDates = [...new Set(authorEntries.map(entry => getDateKey(entry.createdAt)))].sort();
    const selectedDayNumber = uniqueDates.includes(selectedDateKey)
      ? uniqueDates.indexOf(selectedDateKey) + 1
      : uniqueDates.filter(date => date < selectedDateKey).length + 1;

    currentDateEl.textContent = formatZhDate(getSelectedJournalDate());
    currentDayEl.textContent = `第 ${selectedDayNumber} 天`;

    syncJournalEditingState();

    if (entries.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state journal-empty-state">
          <p>從第 1 天開始，留下今天的精進紀錄。</p>
        </div>
      `;
      if (loadMoreEl) loadMoreEl.innerHTML = '';
      return;
    }

    // 1. Keyword search filtering
    const searchInput = document.getElementById('journal-search-input');
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    let filteredEntries = entries;
    if (query) {
      filteredEntries = entries.filter(entry => {
        const titleMatch = (entry.title || '').toLowerCase().indexOf(query) !== -1;
        const contentMatch = (entry.content || '').toLowerCase().indexOf(query) !== -1;
        const polishedMatch = (entry.polishedContent || '').toLowerCase().indexOf(query) !== -1;
        const keywordMatch = (entry.keywords || []).some(k => k.toLowerCase().indexOf(query) !== -1);
        const commentMatch = (entry.comments || []).some(c => (c.content || '').toLowerCase().indexOf(query) !== -1);
        return titleMatch || contentMatch || polishedMatch || keywordMatch || commentMatch;
      });
    }

    if (filteredEntries.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state journal-empty-state">
          <p>找不到符合「${escapeHtml(query)}」的日記紀錄。</p>
        </div>
      `;
      if (loadMoreEl) loadMoreEl.innerHTML = '';
      return;
    }

    // 2. Incremental list calculation
    if (journalVisibleCount < journalBatchSize) {
      journalVisibleCount = journalBatchSize;
    }
    const visibleLimit = Math.min(journalVisibleCount, filteredEntries.length);
    const pageEntries = filteredEntries.slice(0, visibleLimit);
    const hasMoreEntries = visibleLimit < filteredEntries.length;

    // 3. Render visible items
    listEl.innerHTML = pageEntries.map(entry => {
      const dayNumber = dayMap.get(entry.id) || 1;
      const keywords = Array.isArray(entry.keywords) ? entry.keywords : [];
      const author = entry.author || '小葦';
      const authorIcon = author === '小花' ? '👩🏻' : '👦🏻';
      const authorClass = author === '小花' ? 'author-tag-flower' : 'author-tag-wei';
      
      // Color-coding
      const cardAuthorClass = author === '小花' ? 'card-flower' : 'card-wei';

      // 4. Check for comments within last 24 hours
      var unreadCommentAuthors = [];
      var readCommentAuthors = [];
      var now = new Date();
      var entryComments = getVisibleComments(entry.comments);
      
      var readCommentIds = [];
      try {
        readCommentIds = JSON.parse(localStorage.getItem('read-comment-ids') || '[]');
      } catch(e) {
        readCommentIds = [];
      }

      entryComments.forEach(function(c) {
        var commentTime = new Date(c.createdAt);
        if (!isNaN(commentTime.getTime()) && (now - commentTime < 24 * 60 * 60 * 1000)) {
          var isRead = readCommentIds.indexOf(c.id) !== -1;
          if (isRead) {
            if (readCommentAuthors.indexOf(c.author) === -1) {
              readCommentAuthors.push(c.author);
            }
          } else {
            if (unreadCommentAuthors.indexOf(c.author) === -1) {
              unreadCommentAuthors.push(c.author);
            }
          }
        }
      });

      // Filter out authors from read list who also have unread comments
      readCommentAuthors = readCommentAuthors.filter(function(author) {
        return unreadCommentAuthors.indexOf(author) === -1;
      });

      var newCommentBadgeHtml = '';
      if (unreadCommentAuthors.length > 0) {
        newCommentBadgeHtml += `<span class="new-comment-badge">💬 ${unreadCommentAuthors.join('、')}新回饋！</span>`;
      }
      if (readCommentAuthors.length > 0) {
        newCommentBadgeHtml += `<span class="read-comment-hint">💬 ${readCommentAuthors.join('、')}已回饋</span>`;
      }

      // 5. Desktop expansion and toggle logic
      var isDesktop = window.innerWidth > 768;
      var isExpanded = isDesktop || expandedJournalEntryIds.has(entry.id);

      // 6. Highlight search keyword
      var rawTitle = entry.title || generateJournalTitle(entry.content || '', entry.createdAt);
      var displayTitle = escapeHtml(rawTitle);
      var displayContent = markdownToHtml(entry.polishedContent || entry.content || '');
      if (query) {
        displayTitle = highlightKeyword(displayTitle, query);
        displayContent = highlightKeyword(displayContent, query);
      }

      const images = Array.isArray(entry.images) ? entry.images : [];
      const imagesHtml = images.length > 0 ? `
        <div class="journal-entry-images-grid" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; margin-bottom: 12px;">
          ${images.map(img => `
            <div class="journal-entry-image-thumb" style="width: 80px; height: 80px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-subtle); cursor: pointer;" onclick="App.zoomJournalImageOnly('${img.url}', '${escapeHtml(img.caption || '')}')">
              <img src="${img.url}" style="width: 100%; height: 100%; object-fit: cover;" />
            </div>
          `).join('')}
        </div>
      ` : '';

      return `
        <div class="habit-card journal-entry-card ${cardAuthorClass}" onclick="App.handleJournalCardClick(event, '${entry.id}')">
          <div class="journal-entry-top">
            <div>
              <div class="journal-entry-day" style="display: flex; align-items: center; gap: 8px;">
                <span>第 ${dayNumber} 天</span>
                <span class="author-tag ${authorClass}">${authorIcon} ${author}</span>
                ${newCommentBadgeHtml}
              </div>
              <div class="journal-entry-date">${formatZhDate(entry.createdAt)}</div>
            </div>
            <div class="journal-entry-actions">
              <button class="history-delete-btn" onclick="App.editJournalEntry('${entry.id}')" title="編輯這篇日記">編輯</button>
              <button class="history-delete-btn" onclick="App.deleteJournalEntry('${entry.id}')" title="刪除此篇日記">刪除</button>
            </div>
          </div>
          <h3 class="journal-entry-title">${displayTitle}</h3>
          ${keywords.length > 0 ? `
            <div class="journal-keyword-list">
              ${keywords.map(keyword => {
                var displayKeyword = escapeHtml(keyword);
                if (query) displayKeyword = highlightKeyword(displayKeyword, query);
                return `<span class="journal-keyword-chip">${displayKeyword}</span>`;
              }).join('')}
            </div>
          ` : ''}
          ${isDesktop ? '' : `
            <button class="journal-expand-btn" onclick="App.toggleJournalEntry('${entry.id}')">
              ${isExpanded ? '收合內容' : '展開內容'}
            </button>
          `}
          <div class="journal-entry-body ${isExpanded ? 'expanded' : 'collapsed'}" id="journal-entry-body-${entry.id}">
            ${displayContent}
            ${renderCommentsSection(entry, query)}
          </div>
          ${imagesHtml}
          <div class="journal-card-actions">
            <button class="btn btn-secondary journal-card-btn" onclick="App.editJournalEntry('${entry.id}')" title="編輯這篇日記">編輯這篇日記</button>
            <button class="btn btn-secondary journal-card-btn journal-card-btn-danger" onclick="App.deleteJournalEntry('${entry.id}')" title="刪除此篇日記">刪除這篇日記</button>
          </div>
        </div>
      `;
    }).join('');

    // 7. Render infinite-load status
    if (loadMoreEl) {
      if (hasMoreEntries || isLoadingMoreJournalEntries) {
        var loadMoreText = isLoadingMoreJournalEntries
          ? '載入更多日精進...'
          : `往下滑載入更多，已顯示 ${visibleLimit} / ${filteredEntries.length} 則`;
        var loadMoreClass = isLoadingMoreJournalEntries
          ? 'journal-load-more-marker is-loading'
          : 'journal-load-more-marker';
        loadMoreEl.innerHTML = `
          <div id="journal-load-more-marker" class="${loadMoreClass}" data-has-more="${hasMoreEntries ? 'true' : 'false'}">
            <span class="journal-load-more-snowflake">❄</span>
            <span>${loadMoreText}</span>
          </div>
        `;
      } else {
        loadMoreEl.innerHTML = filteredEntries.length > journalBatchSize
          ? `<div id="journal-load-more-marker" class="journal-load-more-marker is-complete" data-has-more="false">已載入全部 ${filteredEntries.length} 則</div>`
          : '';
      }
    }

    // 8. Register WYSIWYG editor on each comment box
    document.querySelectorAll('.comment-content-input').forEach(function(el) {
      setupWysiwygEditor(el);
    });
  }

  function setJournalPage() {
    resetJournalVisibleCount();
    renderJournal();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function renderWeeklyChart() {
    const canvas = document.getElementById('weekly-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = 120 * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = '120px';
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = 120;
    const weekData = Storage.getWeeklyData();
    const labels = Object.keys(weekData);
    const values = Object.values(weekData);
    const maxVal = Math.max(...values, 1);

    ctx.clearRect(0, 0, w, h);

    const barWidth = (w - 40) / labels.length - 8;
    const chartH = h - 35;

    labels.forEach((label, i) => {
      const x = 20 + i * ((w - 40) / labels.length) + 4;
      const barH = (values[i] / maxVal) * chartH * 0.85;
      const y = chartH - barH + 5;

      const grd = ctx.createLinearGradient(x, y, x, chartH + 5);
      if (values[i] >= 0) {
        grd.addColorStop(0, 'rgba(52, 211, 153, 0.8)');
        grd.addColorStop(1, 'rgba(52, 211, 153, 0.2)');
      } else {
        grd.addColorStop(0, 'rgba(239, 68, 68, 0.8)');
        grd.addColorStop(1, 'rgba(239, 68, 68, 0.2)');
      }

      ctx.fillStyle = grd;
      ctx.beginPath();
      const radius = 4;
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + barWidth - radius, y);
      ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + radius);
      ctx.lineTo(x + barWidth, chartH + 5);
      ctx.lineTo(x, chartH + 5);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.fill();

      if (values[i] !== 0) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(values[i] > 0 ? `+${values[i]}` : values[i], x + barWidth / 2, y - 5);
      }

      ctx.fillStyle = '#64748b';
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(label, x + barWidth / 2, h - 5);
    });
  }

  function startAwareness(habitId) {
    const habit = data.habits.find(h => h.id === habitId);
    if (!habit) return;

    awarenessHabitId = habitId;
    awarenessTimeLeft = 10;
    document.getElementById('countdown-time').textContent = '10';
    document.getElementById('countdown-bar').style.strokeDashoffset = '0';
    document.getElementById('awareness-modal').classList.add('show');

    if (awarenessTimer) clearInterval(awarenessTimer);

    const startTime = Date.now();
    const duration = 10000;

    awarenessTimer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, duration - elapsed);
      awarenessTimeLeft = remaining / 1000;

      document.getElementById('countdown-time').textContent = Math.ceil(awarenessTimeLeft);
      const offset = 282.7 * (1 - remaining / duration);
      document.getElementById('countdown-bar').style.strokeDashoffset = offset;

      if (remaining <= 0) {
        clearInterval(awarenessTimer);
        awarenessTimer = null;
        hideAwarenessModal();
        promptAction(awarenessHabitId, 'urge');
      }
    }, 50);
  }

  function hideAwarenessModal() {
    if (awarenessTimer) {
      clearInterval(awarenessTimer);
      awarenessTimer = null;
    }
    document.getElementById('awareness-modal').classList.remove('show');
  }

  function handleAwarenessSuccess() {
    const habitId = awarenessHabitId;
    hideAwarenessModal();
    const habit = data.habits.find(h => h.id === habitId);
    const action = habit && habit.type === 'build' ? 'completed' : 'resisted';
    promptAction(habitId, action);
  }

  function promptAction(habitId, action) {
    recordAction(habitId, action, '');
  }

  function submitNote() {
    const editor = document.getElementById('note-input');
    const noteMarkdown = htmlToMarkdown(editor.innerHTML);
    if (editingRecordId) {
      Storage.updateRecord(editingRecordId, { note: noteMarkdown });
      renderAll();
      Animations.toast('記錄已更新', 'success');
    }
    hideNoteModal();
  }

  function skipNote() {
    hideNoteModal();
  }

  function hideNoteModal() {
    document.getElementById('note-modal').classList.remove('show');
    document.getElementById('note-input').innerHTML = '';
    document.getElementById('btn-submit-note').textContent = '✦ 儲存';
    document.getElementById('btn-cancel-note').textContent = '取消';
    pendingAction = null;
    editingRecordId = null;
  }

  function recordAction(habitId, action, note) {
    const prevStage = ScoringEngine.getStage(activeStats.totalPoints);
    const result = ScoringEngine.processAction(action, activeStats);

    if (action === 'resisted' || action === 'completed') {
      const streakResult = ScoringEngine.updateStreak(
        activeStats.lastActiveDate,
        result.newStats.currentStreak
      );
      result.newStats.currentStreak = streakResult.currentStreak;
      result.newStats.lastActiveDate = streakResult.lastActiveDate;
    }

    const activeAuthor = localStorage.getItem('last-selected-author') || '小葦';
    Storage.addRecord(habitId, action, result.points, result.breakdown, note || '', activeAuthor);
    Storage.updateStats(result.newStats);

    const heroEl = document.getElementById('hero-section');
    if (result.points > 0) {
      Animations.flyScore(heroEl, result.points, '#34d399');
      SnowballVis.pulse(1.2);
      const { x: cx, y: cy } = SnowballVis.getCenter();
      ParticleSystem.spawnBurst(cx, cy, '#34d399', 20, true);
    } else {
      Animations.flyScore(heroEl, result.points, '#ef4444');
      SnowballVis.shrink();
      Animations.shake(heroEl, Math.abs(result.points));
      const { x: cx, y: cy } = SnowballVis.getCenter();
      ParticleSystem.spawnBurst(cx, cy, '#ef4444', 15, false);
    }

    const newStage = ScoringEngine.getStage(result.newStats.totalPoints);
    if (newStage.id !== prevStage.id && result.points > 0) {
      setTimeout(() => {
        const { x: cx, y: cy } = SnowballVis.getCenter();
        ParticleSystem.spawnCelebration(cx, cy);
        Animations.stageUpCelebration(newStage.name, newStage.emoji);
      }, 500);
    }

    const actionLabels = {
      resisted: '🧬 進化了！',
      completed: '✅ 做到了！',
      urge: '😤 念起了...',
      relapsed: '💔 下次加油'
    };
    const toastType = result.points > 0 ? 'success' : (result.points < -10 ? 'error' : 'warning');
    Animations.toast(
      `${actionLabels[action]} ${result.points > 0 ? '+' : ''}${result.points} 分`,
      toastType
    );

    renderAll();
  }

  function addHabit(name, type, emoji) {
    if (!name.trim()) return;
    Storage.addHabit(name.trim(), type, emoji);
    renderAll();
    Animations.toast(`已新增「${name}」`, 'success');
  }

  function deleteHabit(habitId) {
    const habit = data.habits.find(h => h.id === habitId);
    if (!habit) return;
    if (!confirm(`確定要刪除「${habit.name}」嗎？相關記錄也會被刪除。`)) return;

    Storage.removeHabit(habitId);
    const nextData = Storage.load();
    nextData.stats = recomputeStatsFromRecords(nextData.records);
    nextData.habits = rebuildHabitDerivedFields(nextData.habits, nextData.records);
    Storage.replaceData(nextData);
    renderAll();
    Animations.toast(`已刪除「${habit.name}」`, 'info');
  }

  function deleteRecord(recordId) {
    const record = data.records.find(item => item.id === recordId);
    if (!record) return;
    if (!confirm('確定要刪除這筆記錄嗎？系統會一併重算積分與連續天數。')) return;

    const nextData = Storage.load();
    nextData.records = nextData.records.filter(item => item.id !== recordId);
    nextData.habits = rebuildHabitDerivedFields(nextData.habits, nextData.records);
    nextData.stats = recomputeStatsFromRecords(nextData.records);
    Storage.replaceData(nextData);
    renderAll();
    Animations.toast('已刪除記錄', 'info');
  }

  function editRecord(recordId) {
    const record = data.records.find(item => item.id === recordId);
    if (!record) return;

    editingRecordId = record.id;
    pendingAction = null;

    document.getElementById('note-modal-emoji').textContent = '✏️';
    document.getElementById('note-modal-title').textContent = '編輯記錄';
    document.getElementById('note-modal-subtitle').textContent = '可修改這筆記錄的備註內容';
    document.getElementById('btn-submit-note').textContent = '✦ 儲存修改';
    document.getElementById('btn-cancel-note').textContent = '取消';

    const editor = document.getElementById('note-input');
    editor.innerHTML = markdownToHtml(record.note || '');
    document.getElementById('note-modal').classList.add('show');
    setTimeout(() => editor.focus(), 200);
  }

  function getKeywordKey(keyword) {
    return normalizeEditorText(String(keyword || '')).toLowerCase();
  }

  function filterBlockedJournalKeywords(keywords) {
    if (!blockedJournalKeywords.size) return keywords;
    return keywords.filter(keyword => !blockedJournalKeywords.has(getKeywordKey(keyword)));
  }

  function updateJournalKeywordPanel(keywords, options) {
    const panel = document.getElementById('journal-keywords-panel');
    if (!panel) return;

    const nextKeywords = filterBlockedJournalKeywords(keywords);
    journalDraftKeywords = nextKeywords;
    if (options && options.markTouched) {
      journalKeywordsTouched = true;
    }

    if (!nextKeywords.length) {
      panel.innerHTML = '';
    } else {
      panel.innerHTML = nextKeywords
        .map(keyword => `
          <span class="journal-keyword-chip" style="display:inline-flex; align-items:center; gap:4px; padding:2px 8px; border-radius:12px; background:var(--bg-glass); border:1px solid var(--border-subtle); font-size:12px; color:var(--text-secondary);">
            ${escapeHtml(keyword)}
            <span class="keyword-remove" onclick="App.removeJournalKeyword('${escapeHtml(keyword)}')" style="cursor:pointer; color:var(--accent-negative); font-weight:bold;">&times;</span>
          </span>
        `)
        .join('');
    }

    const modal = document.getElementById('journal-composer-modal');
    if (modal && modal.classList.contains('show')) {
      saveJournalDraftToStorage();
    }
  }

  function removeJournalKeyword(keywordToRemove) {
    blockedJournalKeywords.add(getKeywordKey(keywordToRemove));
    journalKeywordsTouched = true;
    journalDraftKeywords = journalDraftKeywords.filter(k => k !== keywordToRemove);
    updateJournalKeywordPanel(journalDraftKeywords);
  }

  function addJournalKeyword(keyword) {
    const k = keyword.trim();
    if (k && !journalDraftKeywords.includes(k)) {
      blockedJournalKeywords.delete(getKeywordKey(k));
      journalKeywordsTouched = true;
      journalDraftKeywords.push(k);
      updateJournalKeywordPanel(journalDraftKeywords);
    }
    const input = document.getElementById('journal-keyword-input');
    const dropdown = document.getElementById('keyword-autocomplete-dropdown');
    if (input) input.value = '';
    if (dropdown) dropdown.style.display = 'none';
  }

  function normalizeSeoKeywords(keywords, limit = 5) {
    const unique = [];
    keywords.forEach(keyword => {
      const normalized = normalizeEditorText(String(keyword || ''))
        .replace(/[，。,！!？?；;：:\s]+/g, '')
        .slice(0, 8);
      if (normalized.length < 2 || normalized.length > 8) return;
      if (unique.includes(normalized)) return;
      unique.push(normalized);
    });
    return unique.slice(0, limit);
  }

  function getJournalDraftText() {
    const editor = document.getElementById('journal-input');
    return normalizeEditorText(htmlToMarkdown((editor ? editor.innerHTML : '') || ''));
  }

  function syncSearchAuthorFilterUI() {
    const active = Storage.getActiveAuthors();
    const optWei = document.getElementById('search-author-opt-wei');
    const optFlower = document.getElementById('search-author-opt-flower');
    if (optWei) optWei.classList.toggle('active', active.includes('小葦'));
    if (optFlower) optFlower.classList.toggle('active', active.includes('小花'));

    const filterBtn = document.getElementById('btn-search-author-filter');
    const filterCountDot = document.getElementById('search-filter-active-count');
    const isFiltered = active.length < 2;
    if (filterBtn) filterBtn.classList.toggle('active', isFiltered);
    if (filterCountDot) filterCountDot.style.display = isFiltered ? 'block' : 'none';
  }

  function syncJournalTitleHint() {
    return;
  }

  function syncJournalEditingState() {
    const banner = document.getElementById('journal-edit-banner');
    const label = document.getElementById('journal-edit-label');
    const saveBtn = document.getElementById('btn-journal-save');
    const prevBtn = document.getElementById('btn-edit-prev-journal');
    const nextBtn = document.getElementById('btn-edit-next-journal');
    if (!banner || !label || !saveBtn) return;

    if (!editingJournalEntryId) {
      banner.style.display = 'none';
      saveBtn.textContent = '儲存日記';
      return;
    }

    const entry = Storage.getJournalEntries().find(item => item.id === editingJournalEntryId);
    banner.style.display = 'flex';
    label.textContent = entry ? `正在編輯：${entry.title || formatZhDate(entry.createdAt)}` : '正在編輯日記';
    saveBtn.textContent = '更新日記';

    const entries = Storage.getJournalEntries();
    const currentIndex = entries.findIndex(item => item.id === editingJournalEntryId);
    if (prevBtn) prevBtn.disabled = currentIndex <= 0;
    if (nextBtn) nextBtn.disabled = currentIndex === -1 || currentIndex >= entries.length - 1;
  }

  function showPolishDiffModal(changes) {
    const list = document.getElementById('journal-polish-diff-list');
    const modal = document.getElementById('journal-polish-diff-modal');
    if (!list || !modal) return;
    
    const items = Array.isArray(changes) && changes.length > 0 ? changes : ['優化語意表達，使日記段落更為通順。'];
    list.innerHTML = items.map(item => `<li>${escapeHtml(item)}</li>`).join('');
    modal.classList.add('active');
  }

  async function handleJournalPolish() {
    const polished = polishJournalText(getJournalDraftText());
    const sourceText = getJournalDraftText();
    if (!sourceText) {
      Animations.toast('先寫一些內容再潤稿', 'warning');
      return;
    }

    const btn = document.getElementById('btn-journal-polish');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'AI 潤稿中...';
    }

    try {
      try {
        const aiResult = await generateAiJournalPolish(sourceText, { includeMeta: true });
        const aiText = normalizeEditorText((aiResult ? aiResult.polished : '') || '');
        if (aiText) {
          document.getElementById('journal-input').innerHTML = markdownToHtml(aiText);
          Animations.toast(`已使用 ${formatAiSourceLabel(aiResult.meta)} 完成潤稿`, 'success');
          showPolishDiffModal(aiResult.changes || ['優化了詞彙表達與句子結構', '修飾了語氣使其更為順暢']);
          return;
        }
      } catch (error) {
        console.error('AI polish failed:', error);
        updateGoogleApiKeyStatus('AI 潤稿暫時不可用，已改用本地規則。', true);
      }

      if (!polished) {
        Animations.toast('先寫一些內容再潤稿', 'warning');
        return;
      }
      document.getElementById('journal-input').innerHTML = markdownToHtml(polished);
      Animations.toast('已使用本地規則完成潤稿', 'success');
      showPolishDiffModal(['排版優化：修正換行與段落結構', '空行清理：移除重複的多餘空行']);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'AI 潤稿';
      }
      saveJournalDraftToStorage();
    }
  }

  async function handleJournalKeywords() {
    const sourceText = getJournalDraftText();
    if (!sourceText) {
      Animations.toast('先寫一些內容再生成關鍵字', 'warning');
      return;
    }

    const btn = document.getElementById('btn-journal-keywords');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '生成標籤中...';
    }

    try {
      try {
        const aiResult = await generateAiJournalKeywords(sourceText, { includeMeta: true });
        const aiKeywords = (aiResult && Array.isArray(aiResult.keywords))
          ? normalizeSeoKeywords(aiResult.keywords, 6)
          : [];
        if (aiKeywords.length) {
          updateJournalKeywordPanel(aiKeywords, { markTouched: true });
          Animations.toast(`已使用 ${formatAiSourceLabel(aiResult.meta)} 產生關鍵字`, 'success');
          return;
        }
      } catch (error) {
        console.error('AI keywords failed:', error);
        updateGoogleApiKeyStatus('AI 關鍵字生成暫時不可用，已改用本地規則。', true);
      }

      const keywords = extractKeywords(sourceText);
      updateJournalKeywordPanel(keywords, { markTouched: true });
      Animations.toast(keywords.length ? '已使用本地規則產生關鍵字' : '內容太少，暫時無法提取關鍵字', keywords.length ? 'success' : 'warning');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '關鍵字';
      }
    }
  }

  async function handleJournalTitle() {
    const text = getJournalDraftText();
    if (!text) {
      Animations.toast('先寫一些內容再生成標題', 'warning');
      return;
    }

    const btn = document.getElementById('btn-journal-title');
    if (btn) {
      btn.disabled = true;
      btn.textContent = '生成主題中...';
    }

    try {
      let generatedTitle = '';
      let titleSource = '';
      try {
        const aiResult = await generateAiJournalTitle(text, { includeMeta: true });
        const aiTitle = normalizeEditorText((aiResult ? aiResult.title : '') || '');
        if (aiTitle) {
          generatedTitle = `${formatZhDate(getSelectedJournalDate())}-${aiTitle}`;
          titleSource = formatAiSourceLabel(aiResult.meta);
        }
      } catch (error) {
        console.error('AI title failed:', error);
        updateGoogleApiKeyStatus('AI 主題生成暫時不可用，已改用本地規則。', true);
      }

      if (!generatedTitle) {
        generatedTitle = generateJournalTitle(text, getSelectedJournalDate());
      }

      const titleInput = document.getElementById('journal-title-input');
      if (titleInput) titleInput.value = generatedTitle;
      syncJournalTitleHint();
      Animations.toast(titleSource ? `已使用 ${titleSource} 生成主題` : '已使用本地規則生成主題', 'success');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = '生成主題';
      }
      saveJournalDraftToStorage();
    }
  }

  async function handleJournalRunAll() {
    const text = getJournalDraftText();
    if (!text) {
      Animations.toast('先寫一些內容再一鍵生成', 'warning');
      return;
    }
    if (isRunningJournalAi) return;

    isRunningJournalAi = true;
    setJournalAiButtonsDisabled(true, '一鍵生成中...');
    try {
      await handleJournalPolish();
      await handleJournalKeywords();
      await handleJournalTitle();
      Animations.toast('已完成 AI 一鍵生成', 'success');
    } finally {
      isRunningJournalAi = false;
      setJournalAiButtonsDisabled(false);
    }
  }

  function saveJournalDraftToStorage() {
    const titleInput = document.getElementById('journal-title-input');
    const editor = document.getElementById('journal-input');
    const activeAuthorBtn = document.querySelector('.author-btn.active');
    
    const title = titleInput ? titleInput.value : '';
    const content = getJournalDraftText();
    
    if (!title.trim() && !content.trim() && journalDraftKeywords.length === 0 && journalDraftImages.length === 0) {
      localStorage.removeItem('habit-snowball-journal-draft');
      return;
    }

    const draft = {
      editingJournalEntryId: editingJournalEntryId,
      title: title,
      content: content,
      keywords: journalDraftKeywords || [],
      images: journalDraftImages || [],
      author: activeAuthorBtn ? activeAuthorBtn.dataset.author : '小葦',
      date: getSelectedJournalDate() ? getSelectedJournalDate().toISOString() : new Date().toISOString()
    };
    
    try {
      localStorage.setItem('habit-snowball-journal-draft', JSON.stringify(draft));
    } catch (e) {
      console.warn('Failed to save draft to localStorage:', e);
    }
  }

  function restoreJournalDraft(draft) {
    if (!draft) return;
    
    editingJournalEntryId = draft.editingJournalEntryId;
    if (draft.date) {
      setSelectedJournalDate(new Date(draft.date));
    }
    
    const titleInput = document.getElementById('journal-title-input');
    const editor = document.getElementById('journal-input');
    
    if (titleInput) titleInput.value = draft.title || '';
    if (editor) {
      editor.innerHTML = markdownToHtml(draft.content || '');
    }
    
    journalKeywordsTouched = true;
    blockedJournalKeywords = new Set();
    journalDraftKeywords = draft.keywords || [];
    updateJournalKeywordPanel(journalDraftKeywords);
    
    // Restore images
    journalDraftImages = draft.images || [];
    renderJournalImageGrid();
    
    const currentAuthor = draft.author || '小葦';
    document.querySelectorAll('.author-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.author === currentAuthor);
    });
    
    syncJournalTitleHint();
    syncJournalEditingState();
  }

  function compressImageToDataUrl(file) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const objectUrl = URL.createObjectURL(file);
      img.src = objectUrl;
      img.onload = () => {
        URL.revokeObjectURL(objectUrl);
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        const MAX_LEN = 1200;
        if (width > MAX_LEN || height > MAX_LEN) {
          if (width > height) {
            height = Math.round(height * MAX_LEN / width);
            width = MAX_LEN;
          } else {
            width = Math.round(width * MAX_LEN / height);
            height = MAX_LEN;
          }
        }
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        let quality = 0.9;
        let dataUrl = canvas.toDataURL('image/jpeg', quality);
        while (dataUrl.length * 0.75 > 300 * 1024 && quality > 0.1) {
          quality -= 0.1;
          dataUrl = canvas.toDataURL('image/jpeg', quality);
        }
        resolve(dataUrl);
      };
      img.onerror = (e) => {
        URL.revokeObjectURL(objectUrl);
        reject(e);
      };
    });
  }

  function renderJournalImageGrid() {
    const grid = document.getElementById('journal-image-grid');
    if (!grid) return;
    grid.innerHTML = journalDraftImages.map(img => `
      <div class="journal-image-item">
        <img src="${img.url}" onclick="App.openImageDetail('${img.id}')" />
        <button type="button" class="journal-image-item-delete" onclick="App.deleteJournalImageDraft('${img.id}', event)">&times;</button>
      </div>
    `).join('');
  }

  async function handleJournalImageUpload(e) {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    if (journalDraftImages.length + files.length > 15) {
      Animations.toast('最多只能上傳 15 張圖片', 'warning');
      e.target.value = '';
      return;
    }

    Animations.toast('圖片壓縮處理中...', 'info');
    try {
      for (const file of files) {
        const dataUrl = await compressImageToDataUrl(file);
        journalDraftImages.push({
          id: Storage.generateId(),
          url: dataUrl,
          caption: ''
        });
      }
      renderJournalImageGrid();
      saveJournalDraftToStorage();
      Animations.toast('圖片上傳完成', 'success');
    } catch (err) {
      console.error('Image compression failed:', err);
      Animations.toast('部分圖片處理失敗', 'danger');
    }
    e.target.value = '';
  }

  function openImageDetail(id) {
    activeImageDetailId = id;
    const img = journalDraftImages.find(item => item.id === id);
    if (!img) return;

    const preview = document.getElementById('image-detail-preview');
    const captionInput = document.getElementById('image-detail-caption');
    if (preview) preview.src = img.url;
    if (captionInput) captionInput.value = img.caption || '';

    document.getElementById('image-detail-modal')?.classList.add('active');
  }

  function saveImageDetail() {
    if (!activeImageDetailId) return;
    const captionInput = document.getElementById('image-detail-caption');
    const img = journalDraftImages.find(item => item.id === activeImageDetailId);
    if (img && captionInput) {
      img.caption = captionInput.value.trim();
    }
    renderJournalImageGrid();
    saveJournalDraftToStorage();
    document.getElementById('image-detail-modal')?.classList.remove('active');
    activeImageDetailId = null;
  }

  async function handleImageReplace(e) {
    const file = e.target.files?.[0];
    if (!file || !activeImageDetailId) return;

    Animations.toast('新圖片處理中...', 'info');
    try {
      const dataUrl = await compressImageToDataUrl(file);
      const img = journalDraftImages.find(item => item.id === activeImageDetailId);
      if (img) {
        img.url = dataUrl;
        const preview = document.getElementById('image-detail-preview');
        if (preview) preview.src = dataUrl;
      }
      renderJournalImageGrid();
      saveJournalDraftToStorage();
      Animations.toast('替換圖片成功', 'success');
    } catch (err) {
      console.error('Image replace failed:', err);
      Animations.toast('圖片替換失敗', 'danger');
    }
    e.target.value = '';
  }

  function deleteActiveImageDetail() {
    if (!activeImageDetailId) return;
    journalDraftImages = journalDraftImages.filter(item => item.id !== activeImageDetailId);
    renderJournalImageGrid();
    saveJournalDraftToStorage();
    document.getElementById('image-detail-modal')?.classList.remove('active');
    activeImageDetailId = null;
    Animations.toast('圖片已刪除', 'success');
  }

  function deleteJournalImageDraft(id, event) {
    if (event) event.stopPropagation();
    journalDraftImages = journalDraftImages.filter(item => item.id !== id);
    renderJournalImageGrid();
    saveJournalDraftToStorage();
    Animations.toast('圖片已刪除', 'success');
  }

  function zoomJournalImageOnly(url, caption) {
    const zoomImg = document.getElementById('image-zoom-img');
    const zoomCaption = document.getElementById('image-zoom-caption');
    if (zoomImg) zoomImg.src = url;
    if (zoomCaption) {
      if (caption) {
        zoomCaption.textContent = caption;
        zoomCaption.style.display = 'block';
      } else {
        zoomCaption.textContent = '';
        zoomCaption.style.display = 'none';
      }
    }
    document.getElementById('image-zoom-modal')?.classList.add('active');
  }

  function clearJournalDraft() {
    const titleInput = document.getElementById('journal-title-input');
    const editor = document.getElementById('journal-input');
    if (titleInput) titleInput.value = '';
    if (editor) editor.innerHTML = '';
    updateJournalKeywordPanel([]);
    journalKeywordsTouched = false;
    blockedJournalKeywords = new Set();
    setSelectedJournalDate(new Date());
    editingJournalEntryId = null;
    const lastAuthor = localStorage.getItem('last-selected-author') || '小葦';
    document.querySelectorAll('.author-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.author === lastAuthor);
    });
    
    // Clear images
    journalDraftImages = [];
    renderJournalImageGrid();
    
    syncJournalTitleHint();
    syncJournalEditingState();
    hideJournalComposer();
    
    // Clear localStorage draft
    localStorage.removeItem('habit-snowball-journal-draft');
  }

  function saveJournalEntry() {
    const content = getJournalDraftText();
    if (!content) {
      Animations.toast('請先輸入日記內容', 'warning');
      return;
    }

    const titleInput = document.getElementById('journal-title-input');
    const entryDate = getSelectedJournalDate();
    const title = (titleInput ? titleInput.value.trim() : '') || generateJournalTitle(content, entryDate);
    const polishedContent = polishJournalText(content);
    const keywords = journalKeywordsTouched
      ? journalDraftKeywords
      : filterBlockedJournalKeywords(journalDraftKeywords.length ? journalDraftKeywords : extractKeywords(content));
    const wasEditing = Boolean(editingJournalEntryId);

    const activeAuthorBtn = document.querySelector('.author-btn.active');
    const selectedAuthor = activeAuthorBtn ? activeAuthorBtn.dataset.author : '小葦';

    if (wasEditing) {
      Storage.updateJournalEntry(editingJournalEntryId, {
        title,
        content,
        polishedContent,
        keywords,
        images: journalDraftImages,
        author: selectedAuthor,
        createdAt: entryDate.toISOString()
      });
    } else {
      Storage.addJournalEntry({
        title,
        content,
        polishedContent,
        keywords,
        images: journalDraftImages,
        author: selectedAuthor,
        createdAt: entryDate.toISOString()
      });
    }

    clearJournalDraft();
    renderAll();
    switchView('journal');
    Animations.toast(wasEditing ? '日記已更新' : '日記已儲存', 'success');
  }

  function editJournalEntry(entryId) {
    const entry = Storage.getJournalEntries().find(item => item.id === entryId);
    if (!entry) return;

    let restored = false;
    try {
      const saved = localStorage.getItem('habit-snowball-journal-draft');
      if (saved) {
        const draft = JSON.parse(saved);
        if (draft.editingJournalEntryId === entryId) {
          restoreJournalDraft(draft);
          restored = true;
        }
      }
    } catch (e) {
      console.error('Failed to restore edit draft:', e);
    }

    if (!restored) {
      editingJournalEntryId = entry.id;
      setSelectedJournalDate(entry.createdAt);

      const titleInput = document.getElementById('journal-title-input');
      const editor = document.getElementById('journal-input');
      if (titleInput) titleInput.value = entry.title || '';
      if (editor) editor.innerHTML = markdownToHtml(entry.content || entry.polishedContent || '');
      journalKeywordsTouched = false;
      blockedJournalKeywords = new Set();
      updateJournalKeywordPanel(Array.isArray(entry.keywords) ? entry.keywords : []);
      
      // Load images
      journalDraftImages = Array.isArray(entry.images) ? JSON.parse(JSON.stringify(entry.images)) : [];
      renderJournalImageGrid();

      const currentAuthor = entry.author || '小葦';
      document.querySelectorAll('.author-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.author === currentAuthor);
      });
      syncJournalTitleHint();
      syncJournalEditingState();
    }

    switchView('journal');
    showJournalComposer();
    var journalInput = document.getElementById('journal-input');
    if (journalInput) {
      journalInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(function() { journalInput.focus(); }, 250);
    }
  }

  function toggleJournalEntry(entryId) {
    if (expandedJournalEntryIds.has(entryId)) {
      expandedJournalEntryIds.delete(entryId);
    } else {
      expandedJournalEntryIds.add(entryId);
      markCommentsAsRead(entryId);
    }
    renderJournal();
  }

  function markCommentsAsRead(entryId) {
    var db = Storage.load();
    var entry = db.journalEntries.find(function(item) { return item.id === entryId; });
    if (!entry || !Array.isArray(entry.comments)) return;
    
    var readCommentIds = [];
    try {
      readCommentIds = JSON.parse(localStorage.getItem('read-comment-ids') || '[]');
    } catch(e) {
      readCommentIds = [];
    }
    
    var changed = false;
    var now = new Date();
    var twentyFourHoursAgo = now - 24 * 60 * 60 * 1000;

    getVisibleComments(entry.comments).forEach(function(c) {
      var commentTime = new Date(c.createdAt);
      if (!isNaN(commentTime.getTime()) && commentTime.getTime() > twentyFourHoursAgo) {
        if (readCommentIds.indexOf(c.id) === -1) {
          readCommentIds.push(c.id);
          changed = true;
        }
      }
    });
    
    if (changed) {
      var validCommentIds = [];
      db.journalEntries.forEach(function(e) {
        if (Array.isArray(e.comments)) {
          getVisibleComments(e.comments).forEach(function(cm) {
            var cmTime = new Date(cm.createdAt);
            if (!isNaN(cmTime.getTime()) && cmTime.getTime() > twentyFourHoursAgo) {
              validCommentIds.push(cm.id);
            }
          });
        }
      });

      readCommentIds = readCommentIds.filter(function(id) {
        return validCommentIds.indexOf(id) !== -1;
      });

      localStorage.setItem('read-comment-ids', JSON.stringify(readCommentIds));
      renderAll();
    }
  }

  function handleJournalCardClick(event, entryId) {
    var target = event.target;
    if (
      target.tagName === 'BUTTON' || 
      target.tagName === 'INPUT' || 
      target.tagName === 'TEXTAREA' || 
      target.closest('.journal-entry-actions') || 
      target.closest('.journal-card-actions') || 
      target.closest('.add-comment-box') || 
      target.closest('.comment-item') ||
      target.closest('.wysiwyg-toolbar') ||
      target.closest('.sticker-select-option')
    ) {
      return;
    }
    markCommentsAsRead(entryId);
  }

  function updateGlobalAuthorBadges() {
    var db = Storage.load();
    var entries = db.journalEntries || [];
    var now = new Date();
    var twentyFourHoursAgo = now - 24 * 60 * 60 * 1000;
    
    var readCommentIds = [];
    try {
      readCommentIds = JSON.parse(localStorage.getItem('read-comment-ids') || '[]');
    } catch(e) {
      readCommentIds = [];
    }

    var unreadCounts = {
      '小葦': 0,
      '小花': 0
    };

    entries.forEach(function(entry) {
      var entryAuthor = entry.author || '小葦';
      if (entryAuthor !== '小葦' && entryAuthor !== '小花') return;

      var comments = getVisibleComments(entry.comments);
      comments.forEach(function(c) {
        if (c.author === entryAuthor) return;

        var commentTime = new Date(c.createdAt);
        if (!isNaN(commentTime.getTime()) && commentTime.getTime() > twentyFourHoursAgo) {
          if (readCommentIds.indexOf(c.id) === -1) {
            unreadCounts[entryAuthor]++;
          }
        }
      });
    });

    var badgeWei = document.getElementById('badge-author-wei');
    var badgeFlower = document.getElementById('badge-author-flower');

    if (badgeWei) {
      if (unreadCounts['小葦'] > 0) {
        badgeWei.textContent = unreadCounts['小葦'];
        badgeWei.style.display = 'flex';
      } else {
        badgeWei.style.display = 'none';
      }
    }

    if (badgeFlower) {
      if (unreadCounts['小花'] > 0) {
        badgeFlower.textContent = unreadCounts['小花'];
        badgeFlower.style.display = 'flex';
      } else {
        badgeFlower.style.display = 'none';
      }
    }

    // 同步更新搜尋欄作者篩選選單內的未讀通知 Badge
    var searchBadgeWei = document.getElementById('search-badge-wei');
    var searchBadgeFlower = document.getElementById('search-badge-flower');

    if (searchBadgeWei) {
      if (unreadCounts['小葦'] > 0) {
        searchBadgeWei.textContent = unreadCounts['小葦'];
        searchBadgeWei.style.display = 'inline-block';
      } else {
        searchBadgeWei.style.display = 'none';
      }
    }

    if (searchBadgeFlower) {
      if (unreadCounts['小花'] > 0) {
        searchBadgeFlower.textContent = unreadCounts['小花'];
        searchBadgeFlower.style.display = 'inline-block';
      } else {
        searchBadgeFlower.style.display = 'none';
      }
    }
  }

  function deleteJournalEntry(entryId) {
    const entry = Storage.getJournalEntries().find(item => item.id === entryId);
    if (!entry) return;
    if (!confirm(`確定要刪除「${entry.title || '這篇日記'}」嗎？`)) return;
    Storage.removeJournalEntry(entryId);
    renderAll();
    Animations.toast('已刪除日記', 'info');
  }

  function toggleComposerMetaDrawer() {
    const drawer = document.getElementById('composer-meta-drawer');
    if (!drawer) return;
    const isHidden = drawer.style.display === 'none' || !drawer.style.display;
    drawer.style.display = isHidden ? 'flex' : 'none';
    const btn = document.getElementById('btn-toggle-composer-meta');
    if (btn) {
      btn.classList.toggle('active', isHidden);
    }
  }

  function showJournalComposer() {
    var modal = document.getElementById('journal-composer-modal');
    if (modal) modal.classList.add('show');
    
    // Ensure the settings drawer is hidden by default
    const drawer = document.getElementById('composer-meta-drawer');
    if (drawer) drawer.style.display = 'none';
    const btn = document.getElementById('btn-toggle-composer-meta');
    if (btn) btn.classList.remove('active');
  }

  function hideJournalComposer() {
    var modal = document.getElementById('journal-composer-modal');
    if (modal) modal.classList.remove('show');
  }

  function selectCommentAuthor(btn) {
    var selector = btn.parentElement;
    var buttons = selector.querySelectorAll('.comment-author-btn');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].classList.toggle('active', buttons[i] === btn);
    }
  }

  function selectCommentSticker(span, sticker) {
    var picker = span.parentElement;
    var container = picker.parentElement;
    while (container && !container.classList.contains('add-comment-box')) {
      container = container.parentElement;
    }
    if (!container) return;
    
    var hiddenInput = container.querySelector('.comment-selected-sticker');
    var alreadySelected = span.classList.contains('selected');
    
    var options = picker.querySelectorAll('.sticker-select-option');
    for (var i = 0; i < options.length; i++) {
      options[i].classList.remove('selected');
      options[i].style.background = 'transparent';
    }
    
    if (alreadySelected) {
      if (hiddenInput) hiddenInput.value = '';
    } else {
      span.classList.add('selected');
      span.style.background = 'rgba(168, 216, 234, 0.3)';
      if (hiddenInput) hiddenInput.value = sticker;
    }
  }

  function toggleQuickTag(span) {
    span.classList.toggle('active');
    if (span.classList.contains('active')) {
      span.style.background = 'rgba(168, 216, 234, 0.15)';
      span.style.borderColor = 'rgba(168, 216, 234, 0.5)';
      span.style.color = '#fff';
    } else {
      span.style.background = 'rgba(255,255,255,0.02)';
      span.style.borderColor = 'var(--border-subtle)';
      span.style.color = 'var(--text-secondary)';
    }
  }

  function editComment(entryId, commentId) {
    activeCommentEdit = {
      entryId: entryId,
      commentId: commentId
    };
    expandedJournalEntryIds.add(entryId);
    renderJournal();
    window.setTimeout(function() {
      focusCommentEditor(entryId);
    }, 60);
  }

  function cancelCommentEdit() {
    activeCommentEdit = null;
    renderJournal();
  }

  function submitComment(entryId, triggerEl) {
    var container = triggerEl;
    while (container && !container.classList.contains('add-comment-box')) {
      container = container.parentElement;
    }
    if (!container) return;
    
    var input = container.querySelector('.comment-content-input');
    var content = '';
    if (input) {
      content = htmlToMarkdown(input.innerHTML).trim();
    }
    if (!content) {
      Animations.toast('請輸入評論內容', 'warning');
      return;
    }
    
    var activeAuthorBtn = container.querySelector('.comment-author-btn.active');
    var author = activeAuthorBtn ? activeAuthorBtn.getAttribute('data-comment-author') : '小葦';
    
    var stickerInput = container.querySelector('.comment-selected-sticker');
    var sticker = stickerInput ? stickerInput.value : '';
    
    var tags = [];
    var activeTags = container.querySelectorAll('.quick-tag-option.active');
    for (var i = 0; i < activeTags.length; i++) {
      var text = activeTags[i].textContent.split(' ')[0].trim();
      tags.push(text);
    }
    
    var customInput = container.querySelector('.comment-custom-tags');
    var customText = customInput ? customInput.value.trim() : '';
    if (customText) {
      var customParts = customText.split(/[，,]+/);
      for (var j = 0; j < customParts.length; j++) {
        var cleaned = customParts[j].trim();
        if (cleaned && tags.indexOf(cleaned) === -1) {
          tags.push(cleaned);
        }
      }
    }
    
    var db = Storage.load();
    var originalEntry = db.journalEntries.find(function(item) { return item.id === entryId; });
    if (!originalEntry) return;
    
    if (!Array.isArray(originalEntry.comments)) {
      originalEntry.comments = [];
    }

    var editingComment = activeCommentEdit && activeCommentEdit.entryId === entryId
      ? originalEntry.comments.find(function(comment) {
          return comment && comment.id === activeCommentEdit.commentId && !comment.deletedAt;
        }) || null
      : null;

    var nowIso = new Date().toISOString();
    if (editingComment) {
      editingComment.author = author;
      editingComment.content = content;
      editingComment.sticker = sticker;
      editingComment.tags = tags;
      editingComment.updatedAt = nowIso;
    } else {
      var commentId = 'comment-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      var newComment = {
        id: commentId,
        author: author,
        content: content,
        sticker: sticker,
        tags: tags,
        createdAt: nowIso,
        updatedAt: nowIso
      };
      originalEntry.comments.push(newComment);
    }
    
    Storage.updateJournalEntry(entryId, {
      comments: originalEntry.comments
    });
    
    expandedJournalEntryIds.add(entryId);
    activeCommentEdit = null;
    
    renderAll();
    Animations.toast(editingComment ? '評論已更新' : '評論已發送', 'success');
  }

  function deleteComment(entryId, commentId) {
    if (!confirm('確定要刪除此條評論嗎？')) return;
    
    var db = Storage.load();
    var entry = db.journalEntries.find(function(item) { return item.id === entryId; });
    if (!entry) return;
    
    if (Array.isArray(entry.comments)) {
      var updated = entry.comments.map(function(comment) {
        if (!comment || comment.id !== commentId) return comment;
        return {
          ...comment,
          deletedAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
      });
      Storage.updateJournalEntry(entryId, {
        comments: updated
      });
      if (activeCommentEdit && activeCommentEdit.entryId === entryId && activeCommentEdit.commentId === commentId) {
        activeCommentEdit = null;
      }
      renderAll();
      Animations.toast('評論已刪除', 'info');
    }
  }

  async function generateAiJournalSummary(journalContent, comments, options) {
    var commentsText = comments.map(function(c) {
      var t = (c.tags || []).join(', ');
      var sticker = c.sticker ? ' [貼圖: ' + c.sticker + ']' : '';
      return c.author + ': ' + c.content + sticker + (t ? ' (標註: ' + t + ')' : '');
    }).join('\n') || '目前尚無評論，請先根據日記本身做總結，並在點評回應段落說明目前尚無評論可回應。';
    
    var userPrompt = '日記內容：\n' + journalContent + '\n\n對話評論：\n' + commentsText;
    
    var systemPrompt = '請分析給定的日記內容與下方的讀者對話評論。若目前尚無評論，仍要根據日記內容產生總結，並在「點評回應」段落簡短說明目前尚無評論可回應。請以繁體中文撰寫一段「AI 對話總結、點評與建議」，字數請控制在 300 字以內，口吻需客觀、溫暖、富有洞察力且有建設性。請嚴格依照以下格式輸出 summary 內容：第一段使用 `**日記總結：**` 作為粗體標題，後面直接接一小段總結日記的重點與作者的精進收穫；第二段使用 `**點評回應：**` 作為粗體標題，後面直接接一小段對評論區留言的點評與回應；第三段使用 `**個人成長建議：**` 作為粗體標題，標題後面換行，再提出至少三項具體行動方案，且只有這一段可以使用數字編號，格式必須是 `1. ...`、`2. ...`、`3. ...`，每一點都要獨立換行。除了「個人成長建議」這一段之外，其他段落都不得使用數字編號、條列或 `1. 2. 3.`。請務必輸出 JSON 格式：{"summary": "..."}。summary 欄位可以包含換行與 `**粗體**` markdown，但不要輸出 code fence、HTML 或其他額外標記。';
    
    var result = await callGoogleAiJson(systemPrompt, userPrompt, {
      includeMeta: true,
      onStatus: options && options.onStatus
    });
    return {
      summary: (result.data && result.data.summary) || '',
      meta: result.meta || null
    };
  }

  async function generateSummary(entryId) {
    var db = Storage.load();
    var entry = db.journalEntries.find(function(item) { return item.id === entryId; });
    if (!entry) return;
    
    var comments = getVisibleComments(entry.comments);
    
    if (!getGoogleApiKey() && ollamaStatus !== 'connected') {
      Animations.toast('請先連線至本地 AI 或填寫 Google AI API Key', 'error');
      return;
    }
    
    setSummaryLoadingState(entryId, {
      provider: ollamaStatus === 'connected' ? '本地 AI' : 'Google AI',
      model: ollamaStatus === 'connected' ? 'gemma4:e2b' : GOOGLE_GEMINI_MODEL
    });
    renderJournal();
    Animations.toast('AI 總結生成中...', 'info');
    try {
      var summaryResult = await generateAiJournalSummary(entry.polishedContent || entry.content || '', comments, {
        onStatus: function(status) {
          setSummaryLoadingState(entryId, {
            provider: status.provider,
            model: status.model
          });
          renderJournal();
        }
      });
      var summaryText = summaryResult.summary;
      if (summaryText) {
        var sourceMeta = summaryResult.meta || {};
        var sourceLabel = sourceMeta.provider && sourceMeta.model
          ? `${sourceMeta.provider} / ${sourceMeta.model}`
          : (ollamaStatus === 'connected' ? '本地 AI / gemma4:e4b' : 'Google AI / Gemini');
        var signedSummaryText = normalizeEditorText(summaryText) + '\n\n署名：' + sourceLabel;
        Storage.updateJournalEntry(entryId, {
          aiSummary: signedSummaryText
        });
        setSummaryLoadingState(entryId, null);
        renderAll();
        var source = sourceMeta.provider && sourceMeta.model
          ? `${sourceMeta.provider} (${sourceMeta.model})`
          : (ollamaStatus === 'connected' ? '本地 AI (gemma4)' : 'Google AI');
        Animations.toast(`已成功生成 ${source} 對話總結`, 'success');
      } else {
        throw new Error('empty_summary');
      }
    } catch (err) {
      setSummaryLoadingState(entryId, null);
      renderJournal();
      console.error('AI Summary generation failed:', err);
      Animations.toast('AI 總結生成失敗，請確認 API Key 是否正確及網路是否暢通', 'danger');
    }
  }

  function regenerateSummary(entryId) {
    generateSummary(entryId);
  }

  function renderCommentsSection(entry, searchQuery) {
    var allComments = Array.isArray(entry.comments) ? entry.comments : [];
    var comments = getVisibleComments(allComments);
    var aiSummary = entry.aiSummary || '';
    var summaryLoadingState = summaryLoadingStates[entry.id] || null;
    var editingComment = getActiveCommentEditForEntry(entry.id, allComments);
    
    var STICKERS = [
      '👍', '❤️', '👏', '🎉', '💪', '🔥', '🌟', '😍', '😂', '🤔',
      '💡', '😮', '😭', '🧘', '🚀', '🌸', '👑', '🐾', '☕', '💯'
    ];
    
    var commentsListHtml = '';
    if (comments.length > 0) {
      commentsListHtml = comments.map(function(c) {
        var stickerHtml = c.sticker ? '<span class="comment-sticker-display" style="font-size: 24px; margin-left: 8px;">' + c.sticker + '</span>' : '';
        var tagsHtml = '';
        if (Array.isArray(c.tags) && c.tags.length > 0) {
          tagsHtml = c.tags.map(function(t) {
            return '<span class="comment-tag-chip" style="font-size: 11px; padding: 2px 6px; border-radius: 4px; background: rgba(168, 216, 234, 0.12); border: 1px solid rgba(168, 216, 234, 0.2); color: var(--accent-1); margin-right: 4px;">' + escapeHtml(t) + '</span>';
          }).join('');
        }
        var authorIcon = c.author === '小花' ? '👩🏻' : '👦🏻';
        var authorClass = c.author === '小花' ? 'author-tag-flower' : 'author-tag-wei';
        
        var displayCommentContent = markdownToHtml(c.content);
        if (searchQuery) {
          displayCommentContent = highlightKeyword(displayCommentContent, searchQuery);
        }

        var isEditingThisComment = editingComment && editingComment.id === c.id;
        return '<div class="comment-item" style="display: flex; flex-direction: column; gap: 4px; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); margin-bottom: 8px; position: relative;">' +
               '<div style="position: absolute; top: 6px; right: 8px; display: flex; align-items: center; gap: 6px;">' +
                 '<button type="button" class="history-delete-btn" style="padding: 2px 8px; font-size: 10px;" onclick="App.editComment(\'' + entry.id + '\', \'' + c.id + '\')">' + (isEditingThisComment ? '編輯中' : '編輯') + '</button>' +
                 '<button type="button" class="comment-delete-btn" style="border: none; background: transparent; color: var(--text-muted); cursor: pointer; font-size: 16px;" onclick="App.deleteComment(\'' + entry.id + '\', \'' + c.id + '\')">&times;</button>' +
               '</div>' +
               '<div style="display: flex; align-items: center; justify-content: space-between;">' +
                 '<div style="display: flex; align-items: center; gap: 6px;">' +
                   '<span class="author-tag ' + authorClass + '" style="padding: 1px 6px; font-size: 11px;">' + authorIcon + ' ' + c.author + '</span>' +
                   '<span style="font-size: 11px; color: var(--text-muted);">' + formatZhDate(c.createdAt) + '</span>' +
                 '</div>' +
               '</div>' +
               '<div style="display: flex; align-items: flex-start; justify-content: space-between; margin-top: 4px;">' +
                 '<div style="flex: 1; font-size: 13px; color: var(--text-primary); line-height: 1.5;" class="comment-markdown-body">' + displayCommentContent + '</div>' +
                 stickerHtml +
               '</div>' +
               (tagsHtml ? '<div style="margin-top: 4px; display: flex; flex-wrap: wrap; gap: 4px;">' + tagsHtml + '</div>' : '') +
             '</div>';
      }).join('');
    } else {
      commentsListHtml = '<div style="text-align: center; color: var(--text-muted); padding: 12px; font-size: 13px;">目前尚無評論，點擊下方發送第一條評論吧 💬</div>';
    }

    var stickersSelectorHtml = STICKERS.map(function(s) {
      return '<span class="sticker-select-option' + ((editingComment && editingComment.sticker === s) ? ' selected' : '') + '" style="font-size: 22px; cursor: pointer; padding: 4px; border-radius: 4px; transition: background 0.2s;' + ((editingComment && editingComment.sticker === s) ? ' background: rgba(168, 216, 234, 0.3);' : '') + '" onclick="App.selectCommentSticker(this, \'' + s + '\')">' + s + '</span>';
    }).join('');

    var summaryStatusHtml = summaryLoadingState
      ? '<div class="ai-summary-status is-loading">' +
          '<span class="ai-summary-spinner"></span>' +
          '<div>' +
            '<div class="ai-summary-status-title">AI 正在總結中...</div>' +
            '<div class="ai-summary-status-model">目前模型：' + escapeHtml(summaryLoadingState.provider + ' / ' + summaryLoadingState.model) + '</div>' +
          '</div>' +
        '</div>'
      : '';
    var aiSummarySectionHtml = '';
    if (aiSummary) {
      aiSummarySectionHtml = '<div class="ai-summary-card" style="margin-top: 16px; padding: 14px; border-radius: var(--radius-md); background: rgba(168, 216, 234, 0.05); border: 1px solid rgba(168, 216, 234, 0.15);">' +
          '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">' +
            '<span style="font-size: 16px;">🤖</span>' +
            '<strong style="font-size: 14px; color: var(--accent-1);">AI 對話總結</strong>' +
            '<button type="button" class="history-delete-btn" style="margin-left: auto; padding: 2px 8px; font-size: 10px;" onclick="App.regenerateSummary(\'' + entry.id + '\')" ' + (summaryLoadingState ? 'disabled' : '') + '>' + (summaryLoadingState ? '總結中...' : '重新總結') + '</button>' +
          '</div>' +
          summaryStatusHtml +
          '<div class="ai-summary-body" style="font-size: 13px; color: var(--text-secondary); line-height: 1.75;">' + formatAiSummaryHtml(aiSummary) + '</div>' +
        '</div>';
    } else {
      aiSummarySectionHtml = '<div class="ai-summary-card" style="margin-top: 16px; padding: 14px; border-radius: var(--radius-md); background: rgba(168, 216, 234, 0.05); border: 1px solid rgba(168, 216, 234, 0.15);">' +
          (summaryLoadingState
            ? summaryStatusHtml + '<div style="font-size: 12px; color: var(--text-muted); line-height: 1.7;">正在分析日記' + (comments.length ? '與評論' : '') + '，完成後會自動顯示在這裡。</div>'
            : '<div style="text-align: center;">' +
                '<button type="button" class="btn btn-secondary" style="font-size: 12px; padding: 6px 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px;" onclick="App.generateSummary(\'' + entry.id + '\')">' +
                  '<span>✨</span> 生成 AI 對話總結' +
                '</button>' +
              '</div>') +
        '</div>';
    }

    var currentLoginIdentity = localStorage.getItem('login-identity') || '小葦';
    var selectedCommentAuthor = editingComment ? (editingComment.author || currentLoginIdentity) : currentLoginIdentity;
    var commentAuthorSelectorWeiActive = selectedCommentAuthor === '小葦' ? ' active' : '';
    var commentAuthorSelectorFlowerActive = selectedCommentAuthor === '小花' ? ' active' : '';
    var commentEditorTitle = editingComment ? '編輯評論' : '新增評論';
    var commentEditorHtml = editingComment ? markdownToHtml(editingComment.content || '') : '';
    var commentPrimaryAction = editingComment ? '更新評論' : '發送';
    var commentPlaceholder = editingComment ? '修改這則評論內容...' : '寫下評論 (支援 Markdown 快速鍵，Ctrl+Enter 發送)...';

    return '<div class="comments-section" style="margin-top: 20px; border-top: 1px dashed var(--border-subtle); padding-top: 16px;">' +
        '<h4 style="font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">' +
          '<span>💬</span> 評論與貼圖回饋 (' + comments.length + ')' +
        '</h4>' +
        aiSummarySectionHtml +
        '<div class="comments-list" style="max-height: 300px; overflow-y: auto; margin: 16px 0; padding-right: 4px;">' +
          commentsListHtml +
        '</div>' +
        '<div class="add-comment-box" data-comment-entry-id="' + entry.id + '" style="margin-top: 16px; padding: 12px; border-radius: var(--radius-md); background: var(--bg-comment-box); border: 1px solid var(--border-subtle);">' +
          '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">' +
            '<span style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">' + commentEditorTitle + '</span>' +
            '<div class="comment-author-selector" style="display: flex; gap: 6px;">' +
              '<button type="button" class="comment-author-btn' + commentAuthorSelectorWeiActive + '" data-comment-author="小葦" style="padding: 3px 8px; font-size: 11px; border-radius: 4px; border: 1px solid var(--border-subtle); background: rgba(255,255,255,0.02); color: var(--text-secondary); cursor: pointer; transition: all 0.2s;" onclick="App.selectCommentAuthor(this)">👦🏻 小葦</button>' +
              '<button type="button" class="comment-author-btn' + commentAuthorSelectorFlowerActive + '" data-comment-author="小花" style="padding: 3px 8px; font-size: 11px; border-radius: 4px; border: 1px solid var(--border-subtle); background: rgba(255,255,255,0.02); color: var(--text-secondary); cursor: pointer; transition: all 0.2s;" onclick="App.selectCommentAuthor(this)">👩🏻 小花</button>' +
            '</div>' +
          '</div>' +
          '<div style="margin-bottom: 8px;">' +
            '<label style="display: block; font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">選擇貼圖回饋 (選填)</label>' +
            '<div class="stickers-picker" style="display: flex; flex-wrap: wrap; gap: 4px; max-height: 60px; overflow-y: auto; padding: 4px; border-radius: 4px; background: var(--bg-sticker-picker);">' +
              stickersSelectorHtml +
            '</div>' +
            '<input type="hidden" class="comment-selected-sticker" value="' + escapeHtml(editingComment && editingComment.sticker ? editingComment.sticker : '') + '" />' +
          '</div>' +
          '<div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px; width: 100%;">' +
            '<div class="comment-content-input" contenteditable="true" data-placeholder="' + commentPlaceholder + '" style="width: 100%;" onkeydown="if((event.ctrlKey || event.metaKey) && event.key === \'Enter\') { event.preventDefault(); App.submitComment(\'' + entry.id + '\', this); }">' + commentEditorHtml + '</div>' +
            '<div style="display: flex; justify-content: flex-end; gap: 8px;">' +
              (editingComment ? '<button type="button" class="btn btn-secondary" style="padding: 0 14px; font-size: 12px; height: 34px; font-weight: 600;" onclick="App.cancelCommentEdit()">取消編輯</button>' : '') +
              '<button type="button" class="btn btn-primary" style="padding: 0 14px; font-size: 12px; height: 34px; font-weight: 600;" onclick="App.submitComment(\'' + entry.id + '\', this)">' + commentPrimaryAction + '</button>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }

  function highlightKeyword(text, keyword) {
    if (!text || !keyword) return text;
    var regex = new RegExp('(' + escapeRegExp(keyword) + ')', 'gi');
    var parts = text.split(/(<[^>]+>)/g);
    for (var i = 0; i < parts.length; i++) {
      if (parts[i] && parts[i].charAt(0) !== '<') {
        parts[i] = parts[i].replace(regex, '<mark class="search-highlight">$1</mark>');
      }
    }
    return parts.join('');
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function toggleActiveAuthor(author) {
    let active = Storage.getActiveAuthors();

    if (active.includes(author)) {
      if (active.length > 1) {
        active = active.filter(a => a !== author);
      } else {
        Animations.toast('必須至少選擇一位填寫人', 'warning');
        return;
      }
    } else {
      active.push(author);
    }

    Storage.setActiveAuthors(active);

    document.querySelectorAll('.g-author-btn').forEach(b => {
      b.classList.toggle('active', active.includes(b.dataset.author));
    });

    resetJournalVisibleCount();
    renderAll();
  }

  function handleGlobalAuthorToggle(e) {
    const btn = e.currentTarget;
    if (!btn) return;
    toggleActiveAuthor(btn.dataset.author);
  }

  function handleSaveGoogleApiKey() {
    const input = document.getElementById('google-api-key-input');
    const apiKey = (input ? input.value.trim() : '') || '';
    if (!apiKey) {
      updateGoogleApiKeyStatus('請先輸入 API Key', true);
      Animations.toast('請先輸入 API Key', 'warning');
      return;
    }
    saveGoogleApiKey(apiKey);
    updateGoogleApiKeyStatus('Google API Key 已儲存在這台裝置的瀏覽器中');
    updateJournalAiMode();
    Animations.toast('API Key 已儲存', 'success');
  }

  function handleToggleGoogleApiKeyVisibility() {
    isGoogleApiKeyVisible = !isGoogleApiKeyVisible;
    hydrateGoogleApiKeyInput();
  }

  function handleClearGoogleApiKey() {
    clearGoogleApiKey();
    const input = document.getElementById('google-api-key-input');
    if (input) input.value = '';
    updateGoogleApiKeyStatus('Google API Key 已清除');
    updateJournalAiMode();
    Animations.toast('API Key 已清除', 'info');
  }

  function applyJournalDateSelection(dateLike) {
    setSelectedJournalDate(dateLike);
    const titleInput = document.getElementById('journal-title-input');
    if (titleInput && titleInput.value.trim()) {
      const rawText = titleInput.value.trim();
      const suffix = rawText.includes('-') ? rawText.split('-').slice(1).join('-').trim() : rawText;
      titleInput.value = `${formatZhDate(getSelectedJournalDate())}-${suffix}`;
      syncJournalTitleHint();
    }
    renderJournal();
    setJournalDatePickerOpen(false);
  }

  function setJournalDatePickerOpen(isOpen) {
    isJournalDatePickerOpen = isOpen;
  }

  function openJournalDatePicker() {
    const input = document.getElementById('journal-date-input');
    if (input) {
      const currentValue = formatDateInputValue(getSelectedJournalDate());
      input.value = currentValue;
      if (typeof input.showPicker === 'function') {
        input.showPicker();
      } else {
        input.click();
      }
    }
  }

  function handleJournalDateChange(event) {
    const value = event.target.value;
    if (!value) return;
    applyJournalDateSelection(new Date(`${value}T00:00:00`));
  }

  function choosePreviousJournalDate() {
    applyJournalDateSelection(addDays(getSelectedJournalDate(), -1));
  }

  function chooseNextJournalDate() {
    applyJournalDateSelection(addDays(getSelectedJournalDate(), 1));
  }

  function cancelJournalEdit() {
    clearJournalDraft();
    renderJournal();
    Animations.toast('已取消編輯', 'info');
  }

  function jumpToAdjacentJournal(direction) {
    if (!editingJournalEntryId) return;
    const entries = Storage.getJournalEntries();
    const currentIndex = entries.findIndex(item => item.id === editingJournalEntryId);
    if (currentIndex === -1) return;
    const targetIndex = currentIndex + direction;
    if (targetIndex < 0 || targetIndex >= entries.length) return;
    editJournalEntry(entries[targetIndex].id);
  }

  function forceRefreshPage() {
    const version = window.HABIT_SNOWBALL_VERSION || `${Date.now()}`;
    const url = new URL(window.location.href);
    url.searchParams.set('refresh', version);
    window.location.replace(url.toString());
  }

  async function resetAllData() {
    if (!confirm('確定要清除所有資料嗎？此操作無法復原！')) return;

    const resetBtn = document.getElementById('btn-reset-all-data');
    if (resetBtn) {
      resetBtn.disabled = true;
      resetBtn.textContent = '清除中...';
    }

    try {
      await Storage.clearAllData();
      data = Storage.load();
      renderAll();
      SnowballVis.setStage(ScoringEngine.getStage(0));
      Animations.toast('所有資料已清除', 'success');
    } catch (error) {
      console.error('Failed to reset all data:', error);
      Animations.toast('清除失敗，請稍後再試', 'error');
    } finally {
      if (resetBtn) {
        resetBtn.disabled = false;
        resetBtn.textContent = '清除所有資料';
      }
    }
  }

  function showAddHabitModal() {
    const modal = document.getElementById('add-habit-modal');
    modal.classList.add('show');
    document.getElementById('habit-name-input').focus();
  }

  function hideAddHabitModal() {
    const modal = document.getElementById('add-habit-modal');
    modal.classList.remove('show');
    document.getElementById('habit-name-input').value = '';
  }

  function submitNewHabit() {
    const name = document.getElementById('habit-name-input').value;
    const typeChecked = document.querySelector('input[name="habit-type"]:checked');
    const type = (typeChecked ? typeChecked.value : '') || 'resist';
    const emoji = document.getElementById('habit-emoji-input').value || (type === 'resist' ? '🚫' : '✅');

    if (!name.trim()) {
      Animations.shake(document.getElementById('habit-name-input'));
      return;
    }

    addHabit(name, type, emoji);
    hideAddHabitModal();
  }

  function showOnboarding() {
    setTimeout(() => {
      Animations.toast('歡迎！試著新增你的第一個習慣 ✨', 'info', 4000);
    }, 1000);
  }

  function switchView(view) {
    currentView = view;
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.dataset.view === view);
    });
    document.querySelectorAll('.view-section').forEach(el => {
      el.classList.toggle('active', el.id === `view-${view}`);
    });
  }

  function bindEvents() {
    function addEvent(id, type, handler) {
      var el = document.getElementById(id);
      if (el) el.addEventListener(type, handler);
    }

    document.querySelectorAll('.nav-item').forEach(el => {
      el.addEventListener('click', () => switchView(el.dataset.view));
    });

    addEvent('btn-add-habit', 'click', showAddHabitModal);
    addEvent('btn-submit-habit', 'click', submitNewHabit);
    addEvent('btn-cancel-habit', 'click', hideAddHabitModal);

    addEvent('add-habit-modal', 'click', e => {
      if (e.target.id === 'add-habit-modal') hideAddHabitModal();
    });

    addEvent('habit-name-input', 'keydown', e => {
      if (e.key === 'Enter') submitNewHabit();
    });

    document.querySelectorAll('.emoji-option').forEach(el => {
      el.addEventListener('click', () => {
        document.querySelectorAll('.emoji-option').forEach(node => node.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('habit-emoji-input').value = el.textContent;
      });
    });

    addEvent('btn-submit-note', 'click', submitNote);
    addEvent('btn-cancel-note', 'click', skipNote);
    addEvent('note-modal', 'click', e => {
      if (e.target.id === 'note-modal') hideNoteModal();
    });

    addEvent('toolbar-bullet', 'click', () => {
      document.getElementById('note-input').focus();
      document.execCommand('insertUnorderedList', false, null);
    });
    addEvent('toolbar-bold', 'click', () => {
      document.getElementById('note-input').focus();
      document.execCommand('bold', false, null);
    });

    addEvent('btn-awareness-evolve', 'click', handleAwarenessSuccess);
    addEvent('awareness-modal', 'click', e => {
      if (e.target.id === 'awareness-modal') hideAwarenessModal();
    });

    addEvent('btn-save-sync-user', 'click', () => {
      const input = document.getElementById('sync-user-input');
      const val = input ? input.value.trim() : 'default';
      const currentUser = localStorage.getItem('simulated-current-user') || 'default';
      const targetUser = val || 'default';

      if (targetUser !== currentUser) {
        // 1. 立即停止背景同步，防止將舊資料或空資料上傳覆蓋新帳號
        if (window.Storage && typeof window.Storage.stopSync === 'function') {
          window.Storage.stopSync();
        }

        // 2. 清除本地快取，避免與新帳號資料混雜合併造成污染
        localStorage.removeItem('habit-snowball-data');

        // 3. 更新同步帳號
        localStorage.setItem('simulated-current-user', targetUser);
      }

      const statusMsg = document.getElementById('sync-status-msg');
      if (statusMsg) statusMsg.style.display = 'block';

      // 4. 立即重整以防任何背景延遲觸發
      window.location.reload();
    });


    addEvent('btn-reset-all-data', 'click', resetAllData);
    addEvent('btn-text-scale-down', 'click', () => adjustTextScale(-TEXT_SCALE_STEP));
    addEvent('btn-text-scale-reset', 'click', () => applyTextScale(DEFAULT_TEXT_SCALE));
    addEvent('btn-text-scale-up', 'click', () => adjustTextScale(TEXT_SCALE_STEP));

    function handleAuthorChange(authorName) {
      localStorage.setItem('last-selected-author', authorName);
      document.querySelectorAll('.author-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.author === authorName);
      });
      resetJournalVisibleCount();
      renderAll();
      saveJournalDraftToStorage();
    }

    document.querySelectorAll('.author-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        handleAuthorChange(btn.dataset.author);
      });
    });

    document.querySelectorAll('.g-author-btn').forEach(btn => {
      btn.addEventListener('click', handleGlobalAuthorToggle);
    });

    const mainSearchInput = document.getElementById('journal-search-input');
    const searchSuggestions = document.getElementById('search-keyword-suggestions');
    if (mainSearchInput) {
      mainSearchInput.addEventListener('input', (e) => {
        resetJournalVisibleCount();
        renderJournal();

        const val = e.target.value.trim().toLowerCase();
        if (!val || !searchSuggestions) {
          if (searchSuggestions) searchSuggestions.style.display = 'none';
          return;
        }

        const existing = getAllUniqueKeywords();
        const matches = existing.filter(k => k.toLowerCase().includes(val));

        if (matches.length > 0) {
          searchSuggestions.innerHTML = matches.map(m => `<div class="keyword-dropdown-item" onclick="document.getElementById('journal-search-input').value = '${escapeHtml(m)}'; document.getElementById('journal-search-input').dispatchEvent(new Event('input')); document.getElementById('search-keyword-suggestions').style.display='none';" style="padding: 8px 14px; cursor: pointer; border-bottom: 1px solid var(--border-subtle); color: var(--text-primary); font-size: 13px;">🔍 ${escapeHtml(m)}</div>`).join('');
          searchSuggestions.style.display = 'block';
        } else {
          searchSuggestions.style.display = 'none';
        }
      });

      document.addEventListener('click', (e) => {
        if (searchSuggestions && e.target !== mainSearchInput && !searchSuggestions.contains(e.target)) {
          searchSuggestions.style.display = 'none';
        }
      });

      mainSearchInput.addEventListener('focus', (e) => {
        if (e.target.value.trim() && searchSuggestions && searchSuggestions.innerHTML !== '') {
          searchSuggestions.style.display = 'block';
        }
      });

      // 填寫人篩選下拉選單事件綁定
      const authorFilterBtn = document.getElementById('btn-search-author-filter');
      const authorDropdown = document.getElementById('search-author-dropdown');
      if (authorFilterBtn && authorDropdown) {
        authorFilterBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const isHidden = authorDropdown.style.display === 'none';
          authorDropdown.style.display = isHidden ? 'block' : 'none';
          if (isHidden && searchSuggestions) {
            searchSuggestions.style.display = 'none';
          }
        });

        document.querySelectorAll('.search-author-option').forEach(opt => {
          opt.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleActiveAuthor(opt.dataset.author);
          });
        });

        document.addEventListener('click', (e) => {
          if (authorDropdown && e.target !== authorFilterBtn && !authorDropdown.contains(e.target)) {
            authorDropdown.style.display = 'none';
          }
        });
      }
    }

    addEvent('btn-open-composer', 'click', () => {
      let restored = false;
      try {
        const saved = localStorage.getItem('habit-snowball-journal-draft');
        if (saved) {
          const draft = JSON.parse(saved);
          if (!draft.editingJournalEntryId && (draft.title.trim() || draft.content.trim() || draft.keywords.length > 0 || (draft.images && draft.images.length > 0))) {
            restoreJournalDraft(draft);
            restored = true;
          }
        }
      } catch (e) {
        console.error('Failed to restore draft:', e);
      }
      
      if (!restored) {
        clearJournalDraft();
      }
      showJournalComposer();
    });
    addEvent('btn-close-composer', 'click', hideJournalComposer);
    addEvent('journal-composer-modal', 'click', e => {
      if (e.target.id === 'journal-composer-modal') hideJournalComposer();
    });

    // Auto save draft on any input or change inside the modal
    addEvent('journal-composer-modal', 'input', () => {
      saveJournalDraftToStorage();
    });
    addEvent('journal-composer-modal', 'change', () => {
      saveJournalDraftToStorage();
    });

    // Image upload events
    addEvent('btn-journal-upload-image', 'click', () => {
      document.getElementById('journal-image-input')?.click();
    });
    addEvent('journal-image-input', 'change', handleJournalImageUpload);
    addEvent('btn-image-detail-replace', 'click', () => {
      document.getElementById('image-detail-replace-input')?.click();
    });
    addEvent('image-detail-replace-input', 'change', handleImageReplace);
    addEvent('btn-image-detail-delete', 'click', deleteActiveImageDetail);
    addEvent('btn-image-detail-save', 'click', saveImageDetail);

    addEvent('btn-save-google-api-key', 'click', handleSaveGoogleApiKey);
    addEvent('btn-toggle-google-api-key', 'click', handleToggleGoogleApiKeyVisibility);
    addEvent('btn-clear-google-api-key', 'click', handleClearGoogleApiKey);
    addEvent('btn-cancel-journal-edit', 'click', cancelJournalEdit);
    addEvent('btn-edit-prev-journal', 'click', () => jumpToAdjacentJournal(-1));
    addEvent('btn-edit-next-journal', 'click', () => jumpToAdjacentJournal(1));
    addEvent('btn-journal-date-picker', 'click', openJournalDatePicker);
    addEvent('btn-journal-date-prev', 'click', choosePreviousJournalDate);
    addEvent('btn-journal-date-next', 'click', chooseNextJournalDate);
    addEvent('journal-date-input', 'change', handleJournalDateChange);
    addEvent('btn-toggle-composer-meta', 'click', toggleComposerMetaDrawer);
    addEvent('btn-force-refresh-page', 'click', forceRefreshPage);
    addEvent('btn-journal-polish', 'click', handleJournalPolish);
    addEvent('btn-journal-keywords', 'click', handleJournalKeywords);
    addEvent('btn-journal-title', 'click', handleJournalTitle);
    addEvent('btn-journal-run-all', 'click', handleJournalRunAll);
    addEvent('btn-journal-clear', 'click', clearJournalDraft);
    addEvent('btn-journal-save', 'click', saveJournalEntry);
    addEvent('journal-title-input', 'input', syncJournalTitleHint);
    addEvent('journal-input', 'input', autoFormatJournalOutline);

    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && (e.key === '/' || e.code === 'Slash')) {
        const modal = document.getElementById('journal-composer-modal');
        if (modal && modal.classList.contains('show')) {
          e.preventDefault();
          toggleComposerMetaDrawer();
        }
      }
    });

    setupWysiwygEditor(document.getElementById('journal-input'));

    document.addEventListener('focusout', function() {
      window.setTimeout(flushDeferredSyncRender, 0);
    });

    window.addEventListener('resize', () => {
      SnowballVis.resize();
      renderWeeklyChart();
    });
    window.addEventListener('scroll', handleJournalInfiniteScroll, false);
  }

  return {
    init,
    recordAction,
    promptAction,
    startAwareness,
    addHabit,
    deleteHabit,
    deleteRecord,
    editJournalEntry,
    toggleJournalEntry,
    handleJournalCardClick,
    deleteJournalEntry,
    resetAllData,
    showAddHabitModal,
    hideAddHabitModal,
    switchView,
    selectLoginIdentity,
    toggleTheme,
    selectCommentAuthor,
    selectCommentSticker,
    toggleQuickTag,
    editComment,
    cancelCommentEdit,
    submitComment,
    deleteComment,
    generateSummary,
    regenerateSummary,
    setJournalPage,
    showJournalComposer,
    hideJournalComposer,
    removeJournalKeyword,
    addJournalKeyword,
    openImageDetail,
    deleteJournalImageDraft,
    zoomJournalImageOnly
  };
})();

document.addEventListener('DOMContentLoaded', App.init);
