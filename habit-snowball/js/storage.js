/**
 * Habit Snowball — Storage Layer
 * LocalStorage 持久化 與 MySQL API 同步
 */

const Storage = (() => {
  const STORAGE_KEY = 'habit-snowball-data';
  const SYNC_POLL_INTERVAL = 15000;
  let onSyncCallback = null;
  let isSyncingFromRemote = false;
  let syncTimer = null;
  let pendingSyncPromise = null;
  let pendingSyncTimeout = null;

  function getDefaultData() {
    return {
      habits: [],
      records: [],
      journalEntries: [],
      stats: {
        totalPoints: 0,
        totalResisted: 0,
        currentStreak: 0,
        longestStreak: 0,
        lastActiveDate: null,
        milestones: []
      },
      settings: {
        createdAt: new Date().toISOString()
      }
    };
  }

  function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 9);
  }

  // ---------- IndexedDB / Local Storage Helpers ----------

  const DB_NAME = 'HabitSnowballDB';
  const DB_VERSION = 1;
  const STORE_NAME = 'states';
  const KEY_NAME = 'current_state';

  let localCache = null;

  function initDb() {
    return new Promise((resolve) => {
      if (localCache) {
        resolve(localCache);
        return;
      }
      
      try {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onupgradeneeded = (event) => {
          const db = event.target.result;
          if (!db.objectStoreNames.contains(STORE_NAME)) {
            db.createObjectStore(STORE_NAME);
          }
        };
        
        request.onsuccess = (event) => {
          const db = event.target.result;
          const transaction = db.transaction(STORE_NAME, 'readonly');
          const store = transaction.objectStore(STORE_NAME);
          const getReq = store.get(KEY_NAME);
          
          getReq.onsuccess = () => {
            if (getReq.result) {
              localCache = getReq.result;
              console.log('IndexedDB loaded successfully.');
              resolve(localCache);
            } else {
              // Fallback to localStorage if IndexedDB is empty
              const raw = localStorage.getItem(STORAGE_KEY);
              if (raw) {
                try {
                  localCache = JSON.parse(raw);
                  console.log('Migrated data from localStorage to IndexedDB.');
                  saveDb(localCache);
                } catch (e) {
                  localCache = getDefaultData();
                }
              } else {
                localCache = getDefaultData();
              }
              resolve(localCache);
            }
          };
          
          getReq.onerror = () => {
            localCache = fallbackToLocalStorage();
            resolve(localCache);
          };
        };
        
        request.onerror = () => {
          localCache = fallbackToLocalStorage();
          resolve(localCache);
        };
      } catch (err) {
        console.error('Failed to open IndexedDB:', err);
        localCache = fallbackToLocalStorage();
        resolve(localCache);
      }
    });
  }

  function fallbackToLocalStorage() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        return JSON.parse(raw);
      } catch (e) {
        return getDefaultData();
      }
    }
    return getDefaultData();
  }

  function saveDb(data) {
    try {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction(STORE_NAME, 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        store.put(data, KEY_NAME);
      };
    } catch (e) {
      console.error('Failed to save to IndexedDB:', e);
    }
  }

  function loadLocal() {
    if (!localCache) {
      return fallbackToLocalStorage();
    }
    return localCache;
  }

  function saveLocal(data, keepTimestamp = false) {
    try {
      if (!keepTimestamp) {
        data.lastModified = new Date().toISOString();
      }
      localCache = data;
      saveDb(data);

      // Save a lightweight copy in localStorage (without large images) as backup
      const lightweightData = {
        ...data,
        journalEntries: (data.journalEntries || []).map(entry => ({
          ...entry,
          images: []
        }))
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lightweightData));
    } catch (e) {
      // Ignore quota errors for localStorage backup
    }
  }

  // ---------- MySQL API Sync ----------

  function getCurrentUser() {
    const urlParams = new URLSearchParams(window.location.search);
    const user = urlParams.get('user') || localStorage.getItem('simulated-current-user') || 'default';
    return (user || 'default').trim() || 'default';
  }

  function getApiBase() {
    return `/api/state/${encodeURIComponent(getCurrentUser())}`;
  }

  function hasMeaningfulLocalData(data) {
    if (!data) return false;
    const stats = data.stats || {};
    return (Array.isArray(data.habits) && data.habits.length > 0) ||
      (Array.isArray(data.records) && data.records.length > 0) ||
      (Array.isArray(data.journalEntries) && data.journalEntries.length > 0) ||
      (stats.totalPoints || 0) !== 0 ||
      (stats.totalResisted || 0) !== 0 ||
      (stats.currentStreak || 0) !== 0 ||
      (stats.longestStreak || 0) !== 0;
  }

  async function fetchRemoteState() {
    const response = await fetch(getApiBase(), {
      headers: {
        'Accept': 'application/json'
      }
    });

    if (response.status === 404) {
      return null;
    }
    if (!response.ok) {
      throw new Error(`Remote fetch failed: ${response.status}`);
    }

    const payload = await response.json();
    return payload.data || getDefaultData();
  }

  async function uploadRemoteState(data) {
    const response = await fetch(getApiBase(), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data })
    });

    if (!response.ok) {
      throw new Error(`Remote save failed: ${response.status}`);
    }
  }

  function scheduleSync(data) {
    if (!hasMeaningfulLocalData(data)) {
      console.warn('Skip empty state upload to protect remote data from accidental overwrite.');
      return;
    }

    if (pendingSyncTimeout) {
      clearTimeout(pendingSyncTimeout);
    }

    pendingSyncTimeout = setTimeout(() => {
      pendingSyncPromise = uploadRemoteState(data)
        .catch(err => {
          console.error('Failed to upload data to MySQL API:', err);
        })
        .finally(() => {
          pendingSyncPromise = null;
          pendingSyncTimeout = null;
        });
    }, 300);
  }

  function cloneValue(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function preferRicherText(a, b) {
    const aa = typeof a === 'string' ? a : '';
    const bb = typeof b === 'string' ? b : '';
    if (!aa) return bb;
    if (!bb) return aa;
    return aa.length >= bb.length ? aa : bb;
  }

  function getTimestampValue(value) {
    const time = new Date(value || 0).getTime();
    return Number.isFinite(time) ? time : 0;
  }

  function mergeAiSummary(primaryEntry, secondaryEntry, preferredSource) {
    const primarySummary = typeof primaryEntry.aiSummary === 'string' ? primaryEntry.aiSummary : '';
    const secondarySummary = typeof secondaryEntry.aiSummary === 'string' ? secondaryEntry.aiSummary : '';
    const primaryUpdatedAt = primaryEntry.aiSummaryUpdatedAt || '';
    const secondaryUpdatedAt = secondaryEntry.aiSummaryUpdatedAt || '';
    const primaryUpdatedTime = getTimestampValue(primaryUpdatedAt);
    const secondaryUpdatedTime = getTimestampValue(secondaryUpdatedAt);

    if (primarySummary && secondarySummary) {
      if (primaryUpdatedTime !== secondaryUpdatedTime) {
        return primaryUpdatedTime > secondaryUpdatedTime
          ? { summary: primarySummary, updatedAt: primaryUpdatedAt || secondaryUpdatedAt }
          : { summary: secondarySummary, updatedAt: secondaryUpdatedAt || primaryUpdatedAt };
      }

      if (preferredSource === 'primary') {
        return { summary: primarySummary, updatedAt: primaryUpdatedAt || secondaryUpdatedAt };
      }
      if (preferredSource === 'secondary') {
        return { summary: secondarySummary, updatedAt: secondaryUpdatedAt || primaryUpdatedAt };
      }

      const richerSummary = preferRicherText(primarySummary, secondarySummary);
      return richerSummary === primarySummary
        ? { summary: primarySummary, updatedAt: primaryUpdatedAt || secondaryUpdatedAt }
        : { summary: secondarySummary, updatedAt: secondaryUpdatedAt || primaryUpdatedAt };
    }

    if (secondarySummary) {
      return { summary: secondarySummary, updatedAt: secondaryUpdatedAt };
    }
    if (primarySummary) {
      return { summary: primarySummary, updatedAt: primaryUpdatedAt };
    }

    return { summary: '', updatedAt: secondaryUpdatedAt || primaryUpdatedAt || '' };
  }

  function mergeStringArrays(a, b) {
    const out = [];
    (Array.isArray(a) ? a : []).concat(Array.isArray(b) ? b : []).forEach(item => {
      if (typeof item === 'string' && item.trim() && !out.includes(item.trim())) {
        out.push(item.trim());
      }
    });
    return out;
  }

  function normalizeStringArray(items) {
    const out = [];
    (Array.isArray(items) ? items : []).forEach(item => {
      if (typeof item === 'string' && item.trim() && !out.includes(item.trim())) {
        out.push(item.trim());
      }
    });
    return out;
  }

  function mergeKeywordField(remoteEntry, localEntry, preferredSource) {
    const remoteHasKeywords = Array.isArray(remoteEntry.keywords);
    const localHasKeywords = Array.isArray(localEntry.keywords);
    if (!remoteHasKeywords && !localHasKeywords) return [];
    if (!remoteHasKeywords) return normalizeStringArray(localEntry.keywords);
    if (!localHasKeywords) return normalizeStringArray(remoteEntry.keywords);

    const remoteTime = getTimestampValue(remoteEntry.keywordsUpdatedAt || remoteEntry.updatedAt);
    const localTime = getTimestampValue(localEntry.keywordsUpdatedAt || localEntry.updatedAt);
    if (localTime > remoteTime) return normalizeStringArray(localEntry.keywords);
    if (remoteTime > localTime) return normalizeStringArray(remoteEntry.keywords);

    return preferredSource === 'local'
      ? normalizeStringArray(localEntry.keywords)
      : normalizeStringArray(remoteEntry.keywords);
  }

  function getMergedKeywordUpdatedAt(remoteEntry, localEntry, preferredSource) {
    const remoteUpdatedAt = remoteEntry.keywordsUpdatedAt || remoteEntry.updatedAt || '';
    const localUpdatedAt = localEntry.keywordsUpdatedAt || localEntry.updatedAt || '';
    const remoteTime = getTimestampValue(remoteUpdatedAt);
    const localTime = getTimestampValue(localUpdatedAt);
    if (localTime > remoteTime) return localUpdatedAt;
    if (remoteTime > localTime) return remoteUpdatedAt;
    return preferredSource === 'local' ? localUpdatedAt : remoteUpdatedAt;
  }

  function journalCompletenessScore(entry) {
    if (!entry) return 0;
    return (entry.content ? entry.content.length : 0) +
      (entry.polishedContent ? entry.polishedContent.length : 0) +
      (entry.aiSummary ? entry.aiSummary.length : 0) +
      (Array.isArray(entry.comments) ? entry.comments.length * 1000 : 0) +
      (Array.isArray(entry.keywords) ? entry.keywords.length * 50 : 0);
  }

  function mergeJournalEntry(remoteEntry, localEntry, preferredSummarySource = 'richer') {
    const remoteTime = getTimestampValue(remoteEntry.updatedAt || remoteEntry.createdAt);
    const localTime = getTimestampValue(localEntry.updatedAt || localEntry.createdAt);

    // Choose the version with the newer updatedAt timestamp as the base
    const base = cloneValue(localTime >= remoteTime ? localEntry : remoteEntry);

    base.id = remoteEntry.id || localEntry.id;
    base.author = localTime >= remoteTime ? (localEntry.author || remoteEntry.author) : (remoteEntry.author || localEntry.author);
    base.createdAt = remoteEntry.createdAt || localEntry.createdAt || new Date().toISOString();
    base.updatedAt = localTime >= remoteTime ? (localEntry.updatedAt || new Date().toISOString()) : (remoteEntry.updatedAt || new Date().toISOString());

    // Title, content, polishedContent, and images are strictly taken from the newer version to prevent edit reversion.
    if (localTime >= remoteTime) {
      base.title = localEntry.title !== undefined ? localEntry.title : (remoteEntry.title || '');
      base.content = localEntry.content !== undefined ? localEntry.content : (remoteEntry.content || '');
      base.polishedContent = localEntry.polishedContent !== undefined ? localEntry.polishedContent : (remoteEntry.polishedContent || '');
      base.images = Array.isArray(localEntry.images) ? localEntry.images : (remoteEntry.images || []);
    } else {
      base.title = remoteEntry.title !== undefined ? remoteEntry.title : (localEntry.title || '');
      base.content = remoteEntry.content !== undefined ? remoteEntry.content : (localEntry.content || '');
      base.polishedContent = remoteEntry.polishedContent !== undefined ? remoteEntry.polishedContent : (localEntry.polishedContent || '');
      base.images = Array.isArray(remoteEntry.images) ? remoteEntry.images : (localEntry.images || []);
    }

    const summaryMeta = mergeAiSummary(
      remoteEntry,
      localEntry,
      preferredSummarySource === 'remote' ? 'primary' : preferredSummarySource === 'local' ? 'secondary' : 'richer'
    );
    base.aiSummary = summaryMeta.summary;
    if (summaryMeta.updatedAt) {
      base.aiSummaryUpdatedAt = summaryMeta.updatedAt;
    } else {
      delete base.aiSummaryUpdatedAt;
    }
    
    base.keywords = mergeKeywordField(remoteEntry, localEntry, preferredSummarySource);
    const keywordUpdatedAt = getMergedKeywordUpdatedAt(remoteEntry, localEntry, preferredSummarySource);
    if (keywordUpdatedAt) {
      base.keywordsUpdatedAt = keywordUpdatedAt;
    }

    const commentsMap = new Map();
    (Array.isArray(remoteEntry.comments) ? remoteEntry.comments : []).forEach(c => {
      if (c && c.id) commentsMap.set(c.id, cloneValue(c));
    });
    (Array.isArray(localEntry.comments) ? localEntry.comments : []).forEach(c => {
      if (!c || !c.id) return;
      const existing = commentsMap.get(c.id);
      commentsMap.set(c.id, existing ? { ...existing, ...cloneValue(c) } : cloneValue(c));
    });
    base.comments = Array.from(commentsMap.values())
      .sort((a, b) => new Date(a.createdAt || 0) - new Date(b.createdAt || 0));

    return base;
  }

  function mergeStates(local, remote) {
    if (!local) return remote || getDefaultData();
    if (!remote) return local || getDefaultData();
    if (!hasMeaningfulLocalData(local) && hasMeaningfulLocalData(remote)) {
      return cloneValue(remote);
    }
    if (hasMeaningfulLocalData(local) && !hasMeaningfulLocalData(remote)) {
      return cloneValue(local);
    }

    const remoteTime = new Date(remote.lastModified || 0).getTime();
    const localTime = new Date(local.lastModified || 0).getTime();
    const preferredSummarySource = localTime > remoteTime
      ? 'local'
      : remoteTime > localTime
        ? 'remote'
        : 'richer';

    const habitsMap = new Map();
    (remote.habits || []).forEach(h => habitsMap.set(h.id, cloneValue(h)));
    (local.habits || []).forEach(h => {
      habitsMap.set(h.id, { ...(habitsMap.get(h.id) || {}), ...cloneValue(h) });
    });
    const mergedHabits = Array.from(habitsMap.values());

    const recordsMap = new Map();
    (remote.records || []).forEach(r => recordsMap.set(r.id, cloneValue(r)));
    (local.records || []).forEach(r => recordsMap.set(r.id, { ...(recordsMap.get(r.id) || {}), ...cloneValue(r) }));
    const mergedRecords = Array.from(recordsMap.values())
      .sort((a, b) => new Date(a.timestamp || 0) - new Date(b.timestamp || 0));

    const journalsMap = new Map();
    (remote.journalEntries || []).forEach(j => {
      journalsMap.set(j.id, cloneValue(j));
    });

    (local.journalEntries || []).forEach(localEntry => {
      const remoteEntry = journalsMap.get(localEntry.id);
      if (!remoteEntry) {
        journalsMap.set(localEntry.id, cloneValue(localEntry));
      } else {
        journalsMap.set(localEntry.id, mergeJournalEntry(remoteEntry, localEntry, preferredSummarySource));
      }
    });
    
    const mergedJournals = Array.from(journalsMap.values())
      .sort(compareJournalEntries);

    const totalPoints = mergedRecords.reduce((sum, r) => sum + (r.points || 0), 0);
    const totalResisted = mergedRecords.filter(r => r.action === 'resisted').length;
    
    const mergedStats = {
      ...getDefaultData().stats,
      ...(remote.stats || {}),
      ...(local.stats || {}),
      totalPoints: totalPoints,
      totalResisted: totalResisted
    };

    const mergedSettings = {
      ...getDefaultData().settings,
      ...(remote.settings || {}),
      ...(local.settings || {})
    };

    const lastModified = localTime > remoteTime 
      ? (local.lastModified || new Date().toISOString())
      : (remote.lastModified || new Date().toISOString());

    return {
      habits: mergedHabits,
      records: mergedRecords,
      journalEntries: mergedJournals,
      stats: mergedStats,
      settings: mergedSettings,
      lastModified: lastModified
    };
  }

  async function hydrateFromRemote() {
    try {
      if (pendingSyncTimeout || pendingSyncPromise) {
        console.log('Skipping remote hydration because local has pending upload.');
        return;
      }
      const remoteData = await fetchRemoteState();
      const localData = loadLocal();

      if (!remoteData) {
        if (hasMeaningfulLocalData(localData)) {
          await uploadRemoteState(localData);
        }
        return;
      }

      if (!hasMeaningfulLocalData(localData) && hasMeaningfulLocalData(remoteData)) {
        console.log('Local cache is empty while remote has data. Hydrating local without uploading.');
        isSyncingFromRemote = true;
        saveLocal(remoteData, true);
        if (onSyncCallback) {
          onSyncCallback();
        }
        isSyncingFromRemote = false;
        return;
      }

      if (hasMeaningfulLocalData(localData) && !hasMeaningfulLocalData(remoteData)) {
        console.warn('Remote state is empty while local has data. Restoring remote from local cache.');
        await uploadRemoteState(localData);
        return;
      }

      const remoteTime = new Date(remoteData.lastModified || 0).getTime();
      const localTime = new Date(localData.lastModified || 0).getTime();

      if (localTime !== remoteTime) {
        console.log('Syncing: local timestamp is ' + localTime + ', remote is ' + remoteTime + '. Performing无损合并 (Merge)...');
        const mergedData = mergeStates(localData, remoteData);
        
        const localStr = JSON.stringify(localData);
        const remoteStr = JSON.stringify(remoteData);
        const mergedStr = JSON.stringify(mergedData);

        const localChanged = mergedStr !== localStr;
        const remoteChanged = mergedStr !== remoteStr;

        if (localChanged) {
          console.log('Updating local storage with merged state.');
          if (pendingSyncTimeout) {
            clearTimeout(pendingSyncTimeout);
            pendingSyncTimeout = null;
          }
          isSyncingFromRemote = true;
          saveLocal(mergedData, true);
          if (onSyncCallback) {
            onSyncCallback();
          }
          isSyncingFromRemote = false;
        }

        if (remoteChanged) {
          console.log('Uploading merged state to remote server.');
          await uploadRemoteState(mergedData);
        }
      } else {
        const isDifferent =
          JSON.stringify(remoteData.habits || []) !== JSON.stringify(localData.habits || []) ||
          JSON.stringify(remoteData.records || []) !== JSON.stringify(localData.records || []) ||
          JSON.stringify(remoteData.journalEntries || []) !== JSON.stringify(localData.journalEntries || []) ||
          JSON.stringify(remoteData.stats || {}) !== JSON.stringify(localData.stats || {}) ||
          JSON.stringify(remoteData.settings || {}) !== JSON.stringify(localData.settings || {});

        if (isDifferent) {
          console.log('Timestamp matches but content differs. Merging states to resolve inconsistency.');
          const mergedData = mergeStates(localData, remoteData);
          saveLocal(mergedData, true);
          await uploadRemoteState(mergedData);
        }
      }
    } catch (err) {
      console.error('MySQL synchronization error:', err);
    }
  }

  function startSync() {
    hydrateFromRemote();

    if (syncTimer) {
      clearInterval(syncTimer);
    }

    syncTimer = setInterval(() => {
      if (!pendingSyncPromise && !isSyncingFromRemote) {
        hydrateFromRemote();
      }
    }, SYNC_POLL_INTERVAL);

    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !pendingSyncPromise && !isSyncingFromRemote) {
        hydrateFromRemote();
      }
    });
  }

  function stopSync() {
    if (syncTimer) {
      clearInterval(syncTimer);
      syncTimer = null;
    }
  }


  function syncRemote(data) {
    if (!isSyncingFromRemote) {
      scheduleSync(data);
    }
  }

  function setSyncCallback(callback) {
    onSyncCallback = callback;
  }

  // ---------- Public Interface (API compatible) ----------

  function load() {
    return loadLocal();
  }

  function save(data) {
    saveLocal(data);
    syncRemote(data);
  }

  function getTaipeiDateStr(dateLike) {
    const date = new Date(dateLike);
    if (Number.isNaN(date.getTime())) return '';
    const tzOffset = 8 * 60 * 60 * 1000;
    const tDate = new Date(date.getTime() + tzOffset);
    return tDate.getUTCFullYear() + '-' +
      String(tDate.getUTCMonth() + 1).padStart(2, '0') + '-' +
      String(tDate.getUTCDate()).padStart(2, '0');
  }

  function getActiveAuthors() {
    const saved = localStorage.getItem('active-global-authors');
    if (saved) {
      try {
        const arr = JSON.parse(saved);
        if (Array.isArray(arr)) {
          const valid = arr.filter(author => author === '小葦' || author === '小花');
          if (valid.length) return Array.from(new Set(valid));
        }
      } catch (e) {
        console.error('Failed to parse active-global-authors:', e);
      }
    }
    return ['小葦', '小花'];
  }

  function setActiveAuthors(authors) {
    if (!Array.isArray(authors)) return;
    localStorage.setItem('active-global-authors', JSON.stringify(authors));
  }

  function filterByActiveAuthor(recordsOrEntries, isJournal = false) {
    const activeAuthors = getActiveAuthors();
    return recordsOrEntries.filter(item => {
      const author = item.author || '小葦';
      if (!activeAuthors.includes(author)) return false;
      if (author === '小花') {
        const dateStr = isJournal ? item.createdAt : item.timestamp;
        if (getTaipeiDateStr(dateStr) < '2026-06-23') return false;
      }
      return true;
    });
  }


  function addHabit(name, type, emoji) {
    const data = load();
    const habit = {
      id: generateId(),
      name,
      type, // "resist" or "build"
      emoji: emoji || (type === 'resist' ? '🚫' : '✅'),
      createdAt: new Date().toISOString(),
      totalActions: 0
    };
    data.habits.push(habit);
    save(data);
    return habit;
  }

  function removeHabit(habitId) {
    const data = load();
    data.habits = data.habits.filter(h => h.id !== habitId);
    data.records = data.records.filter(r => r.habitId !== habitId);
    save(data);
  }

  function addRecord(habitId, action, points, breakdown, note, author) {
    const data = load();
    const activeAuthor = author || localStorage.getItem('last-selected-author') || '小葦';
    const record = {
      id: generateId(),
      habitId,
      action,
      points,
      breakdown,
      note: note || '',
      author: activeAuthor,
      timestamp: new Date().toISOString()
    };
    data.records.push(record);

    const habit = data.habits.find(h => h.id === habitId);
    if (habit) {
      habit.totalActions = (habit.totalActions || 0) + 1;
    }

    save(data);
    return record;
  }

  function updateStats(newStats) {
    const data = load();
    data.stats = { ...data.stats, ...newStats };
    save(data);
  }

  function addMilestone(milestone) {
    const data = load();
    if (!data.stats.milestones) data.stats.milestones = [];
    data.stats.milestones.push({
      ...milestone,
      unlockedAt: new Date().toISOString()
    });
    save(data);
  }

  function getRecordsForHabit(habitId) {
    const data = load();
    const records = data.records.filter(r => r.habitId === habitId);
    return filterByActiveAuthor(records);
  }

  // Limit to 30 for visualization and timeline performance
  function getRecentRecords(limit = 30) {
    const data = load();
    const filtered = filterByActiveAuthor(data.records);
    return filtered.slice(-limit).reverse();
  }

  function getTodayRecords() {
    const data = load();
    const todayStr = getTaipeiDateStr(new Date());
    const filtered = filterByActiveAuthor(data.records);
    return filtered.filter(r => getTaipeiDateStr(r.timestamp) === todayStr);
  }

  function getWeeklyData() {
    const data = load();
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const dailyPoints = {};

    for (let i = 6; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      const key = `${d.getMonth() + 1}/${d.getDate()}`;
      dailyPoints[key] = 0;
    }

    const filtered = filterByActiveAuthor(data.records);
    filtered
      .filter(r => new Date(r.timestamp) >= weekAgo)
      .forEach(r => {
        const d = new Date(r.timestamp);
        const key = `${d.getMonth() + 1}/${d.getDate()}`;
        if (key in dailyPoints) {
          dailyPoints[key] += r.points;
        }
      });

    return dailyPoints;
  }

  function clearAllData() {
    localStorage.removeItem(STORAGE_KEY);
    localCache = getDefaultData();
    try {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onsuccess = (event) => {
        const db = event.target.result;
        const transaction = db.transaction(STORE_NAME, 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        store.delete(KEY_NAME);
      };
    } catch (e) {
      console.error('Failed to clear IndexedDB:', e);
    }
    fetch(getApiBase(), { method: 'DELETE' }).catch(err => {
      console.error('Failed to delete remote data:', err);
    });
  }

  function replaceData(data) {
    save(data);
  }

  function removeRecord(recordId) {
    const data = load();
    const nextRecords = data.records.filter(record => record.id !== recordId);
    if (nextRecords.length === data.records.length) return null;
    data.records = nextRecords;
    save(data);
    return data;
  }

  function updateRecord(recordId, updates) {
    const data = load();
    const index = data.records.findIndex(record => record.id === recordId);
    if (index === -1) return null;
    data.records[index] = {
      ...data.records[index],
      ...updates,
      id: data.records[index].id
    };
    save(data);
    return data.records[index];
  }

  function addJournalEntry(entry) {
    const data = load();
    const activeAuthor = entry.author || localStorage.getItem('last-selected-author') || '小葦';
    const now = new Date().toISOString();
    const journalEntry = {
      id: generateId(),
      createdAt: now,
      updatedAt: now,
      ...entry,
      author: activeAuthor
    };
    if (Object.prototype.hasOwnProperty.call(journalEntry, 'keywords') && !journalEntry.keywordsUpdatedAt) {
      journalEntry.keywordsUpdatedAt = now;
    }
    data.journalEntries.push(journalEntry);
    save(data);
    return journalEntry;
  }

  function updateJournalEntry(entryId, updates) {
    const data = load();
    const index = data.journalEntries.findIndex(entry => entry.id === entryId);
    if (index === -1) return null;
    const normalizedUpdates = {
      ...updates
    };
    const now = new Date().toISOString();
    normalizedUpdates.updatedAt = now;
    if (Object.prototype.hasOwnProperty.call(normalizedUpdates, 'keywords') && !normalizedUpdates.keywordsUpdatedAt) {
      normalizedUpdates.keywordsUpdatedAt = now;
    }
    if (Object.prototype.hasOwnProperty.call(normalizedUpdates, 'aiSummary') && !normalizedUpdates.aiSummaryUpdatedAt) {
      normalizedUpdates.aiSummaryUpdatedAt = now;
    }
    const activeAuthor = updates.author || data.journalEntries[index].author || localStorage.getItem('last-selected-author') || '小葦';
    data.journalEntries[index] = {
      ...data.journalEntries[index],
      ...normalizedUpdates,
      author: activeAuthor,
      id: data.journalEntries[index].id
    };
    save(data);
    return data.journalEntries[index];
  }

  function removeJournalEntry(entryId) {
    const data = load();
    data.journalEntries = data.journalEntries.filter(entry => entry.id !== entryId);
    save(data);
  }

  function compareJournalEntries(a, b) {
    const dateA = new Date(a.createdAt || 0);
    const dateB = new Date(b.createdAt || 0);
    
    const dayA = new Date(dateA.getFullYear(), dateA.getMonth(), dateA.getDate()).getTime();
    const dayB = new Date(dateB.getFullYear(), dateB.getMonth(), dateB.getDate()).getTime();
    
    if (dayB !== dayA) {
      return dayB - dayA;
    }
    
    const timeA = new Date(a.updatedAt || a.createdAt || 0).getTime();
    const timeB = new Date(b.updatedAt || b.createdAt || 0).getTime();
    return timeB - timeA;
  }

  function getJournalEntries() {
    const data = load();
    const filtered = filterByActiveAuthor(data.journalEntries, true);
    return [...filtered].sort(compareJournalEntries);
  }

  return {
    initDb,
    load,
    save,
    replaceData,
    getDefaultData,
    generateId,
    addHabit,
    removeHabit,
    addRecord,
    updateStats,
    addMilestone,
    getRecordsForHabit,
    getRecentRecords,
    getTodayRecords,
    getWeeklyData,
    clearAllData,
    startSync,
    stopSync,
    hydrateFromRemote,
    setSyncCallback,
    removeRecord,
    updateRecord,
    addJournalEntry,
    updateJournalEntry,
    removeJournalEntry,
    getJournalEntries,
    getActiveAuthors,
    setActiveAuthors
  };
})();
