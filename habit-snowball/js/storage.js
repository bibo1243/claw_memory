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

  // ---------- Local Storage Helpers ----------

  function loadLocal() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return getDefaultData();
      const data = JSON.parse(raw);
      return {
        ...getDefaultData(),
        ...data,
        journalEntries: Array.isArray(data.journalEntries) ? data.journalEntries : [],
        stats: { ...getDefaultData().stats, ...(data.stats || {}) },
        settings: { ...getDefaultData().settings, ...(data.settings || {}) }
      };
    } catch (e) {
      console.error('Failed to load local data:', e);
      return getDefaultData();
    }
  }

  function saveLocal(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      console.error('Failed to save local data:', e);
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
    return data.habits.length > 0 ||
      data.records.length > 0 ||
      data.journalEntries.length > 0 ||
      (data.stats.totalPoints || 0) !== 0 ||
      (data.stats.totalResisted || 0) !== 0 ||
      (data.stats.currentStreak || 0) !== 0 ||
      (data.stats.longestStreak || 0) !== 0;
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

  async function hydrateFromRemote() {
    try {
      const remoteData = await fetchRemoteState();
      const localData = loadLocal();

      if (!remoteData) {
        if (hasMeaningfulLocalData(localData)) {
          await uploadRemoteState(localData);
        }
        return;
      }

      const isDifferent =
        JSON.stringify(remoteData.habits || []) !== JSON.stringify(localData.habits || []) ||
        JSON.stringify(remoteData.records || []) !== JSON.stringify(localData.records || []) ||
        JSON.stringify(remoteData.journalEntries || []) !== JSON.stringify(localData.journalEntries || []) ||
        JSON.stringify(remoteData.stats || {}) !== JSON.stringify(localData.stats || {}) ||
        JSON.stringify(remoteData.settings || {}) !== JSON.stringify(localData.settings || {});

      if (isDifferent) {
        if (pendingSyncTimeout) {
          clearTimeout(pendingSyncTimeout);
          pendingSyncTimeout = null;
        }
        isSyncingFromRemote = true;
        saveLocal(remoteData);
        if (onSyncCallback) {
          onSyncCallback();
        }
        isSyncingFromRemote = false;
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
    return ['小葦', '小花'];
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
    const journalEntry = {
      id: generateId(),
      createdAt: new Date().toISOString(),
      ...entry,
      author: activeAuthor
    };
    data.journalEntries.push(journalEntry);
    save(data);
    return journalEntry;
  }

  function updateJournalEntry(entryId, updates) {
    const data = load();
    const index = data.journalEntries.findIndex(entry => entry.id === entryId);
    if (index === -1) return null;
    const activeAuthor = updates.author || data.journalEntries[index].author || localStorage.getItem('last-selected-author') || '小葦';
    data.journalEntries[index] = {
      ...data.journalEntries[index],
      ...updates,
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

  function getJournalEntries() {
    const data = load();
    const filtered = filterByActiveAuthor(data.journalEntries, true);
    return [...filtered].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  }

  return {
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
    hydrateFromRemote,
    setSyncCallback,
    removeRecord,
    updateRecord,
    addJournalEntry,
    updateJournalEntry,
    removeJournalEntry,
    getJournalEntries,
    getActiveAuthors
  };
})();

