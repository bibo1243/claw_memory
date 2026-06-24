const fs = require('fs');

// Recursive Firestore REST API format parser
function mapFirestoreValue(val) {
  if (val.mapValue) {
    const obj = {};
    const fields = val.mapValue.fields || {};
    for (const [k, fVal] of Object.entries(fields)) {
      if (fVal.stringValue !== undefined) {
        obj[k] = fVal.stringValue;
      } else if (fVal.integerValue !== undefined) {
        obj[k] = parseInt(fVal.integerValue, 10);
      } else if (fVal.booleanValue !== undefined) {
        obj[k] = fVal.booleanValue;
      } else if (fVal.arrayValue) {
        const arr = fVal.arrayValue.values || [];
        obj[k] = arr.map(item => {
          if (item.stringValue !== undefined) return item.stringValue;
          return mapFirestoreValue(item);
        });
      } else if (fVal.mapValue) {
        obj[k] = mapFirestoreValue(fVal);
      }
    }
    return obj;
  }
  return val;
}

function cleanHtmlTags(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/<span[^>]*>/g, '').replace(/<\/span>/g, '');
}

try {
  // 1. Read and parse Firestore Backup (output.txt)
  const firestoreRaw = fs.readFileSync('/Users/leegary/.gemini/antigravity/brain/1739244d-1a6e-418c-a745-e17a50069e01/.system_generated/steps/1035/output.txt', 'utf8');
  const firestoreData = JSON.parse(firestoreRaw);
  
  const fHabits = (firestoreData.fields.habits?.arrayValue?.values || []).map(mapFirestoreValue);
  const fRecords = (firestoreData.fields.records?.arrayValue?.values || []).map(mapFirestoreValue);
  const fJournals = (firestoreData.fields.journalEntries?.arrayValue?.values || []).map(mapFirestoreValue);
  
  const firestoreStats = mapFirestoreValue(firestoreData.fields.stats);
  const firestoreSettings = mapFirestoreValue(firestoreData.fields.settings);

  console.log('--- Firestore Backup ---');
  console.log(`Habits: ${fHabits.length}`);
  console.log(`Records: ${fRecords.length}`);
  console.log(`JournalEntries: ${fJournals.length}`);

  // 2. Read and parse MySQL Backup (mysql_base64_payloads.txt)
  const mysqlRawContent = fs.readFileSync('/Users/leegary/個人app/habit-snowball/mysql_base64_payloads.txt', 'utf8');
  const lines = mysqlRawContent.split('\n');
  const userPayloads = {};
  let currentUser = null;
  
  for (let line of lines) {
    line = line.trim();
    if (!line) continue;
    if (line.startsWith('bibo1243\t') || line.startsWith('bibo1243 ')) {
      currentUser = 'bibo1243';
      const parts = line.split(/\s+/);
      userPayloads[currentUser] = parts.slice(1).join('');
    } else if (line.startsWith('default\t') || line.startsWith('default ')) {
      currentUser = 'default';
      const parts = line.split(/\s+/);
      userPayloads[currentUser] = parts.slice(1).join('');
    } else {
      if (currentUser) {
        userPayloads[currentUser] += line;
      }
    }
  }

  const biboB64 = userPayloads['bibo1243'];
  let mysqlData = { habits: [], records: [], stats: {}, settings: {} };
  if (biboB64) {
    const decoded = Buffer.from(biboB64, 'base64').toString('utf8');
    mysqlData = JSON.parse(decoded);
  }

  console.log('\n--- MySQL Backup (bibo1243) ---');
  console.log(`Habits: ${mysqlData.habits?.length || 0}`);
  console.log(`Records: ${mysqlData.records?.length || 0}`);
  console.log(`JournalEntries: ${mysqlData.journalEntries?.length || 0}`);

  // 3. Merging
  // habits
  const habitsMap = new Map();
  mysqlData.habits.forEach(h => habitsMap.set(h.id, h));
  fHabits.forEach(h => habitsMap.set(h.id, h));
  const mergedHabits = Array.from(habitsMap.values());

  // records
  const recordsMap = new Map();
  mysqlData.records.forEach(r => recordsMap.set(r.id, r));
  fRecords.forEach(r => recordsMap.set(r.id, r));
  const mergedRecords = Array.from(recordsMap.values()).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  // journalEntries
  const journalsMap = new Map();
  (mysqlData.journalEntries || []).forEach(j => {
    j.content = cleanHtmlTags(j.content);
    j.polishedContent = cleanHtmlTags(j.polishedContent);
    journalsMap.set(j.id, j);
  });
  fJournals.forEach(j => {
    j.content = cleanHtmlTags(j.content);
    j.polishedContent = cleanHtmlTags(j.polishedContent);
    if (!j.author) j.author = '小葦'; // default
    journalsMap.set(j.id, j);
  });
  const mergedJournals = Array.from(journalsMap.values()).sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

  // stats calculation
  const totalPoints = mergedRecords.reduce((sum, r) => sum + (r.points || 0), 0);
  const totalResisted = mergedRecords.filter(r => r.action === 'resisted').length;
  
  // longestStreak & currentStreak
  const longestStreak = Math.max(mysqlData.stats.longestStreak || 0, firestoreStats.longestStreak || 0, 1);
  const currentStreak = firestoreStats.currentStreak || 0;
  
  let lastActiveDate = mysqlData.stats.lastActiveDate || null;
  if (mergedRecords.length > 0) {
    const latestRecord = mergedRecords[mergedRecords.length - 1];
    lastActiveDate = latestRecord.timestamp.split('T')[0];
  }

  const mergedStats = {
    totalPoints,
    totalResisted,
    currentStreak,
    longestStreak,
    lastActiveDate,
    milestones: mysqlData.stats.milestones || []
  };

  const mergedSettings = {
    createdAt: mysqlData.settings.createdAt || firestoreSettings.createdAt || new Date().toISOString()
  };

  const mergedPayload = {
    habits: mergedHabits,
    records: mergedRecords,
    journalEntries: mergedJournals,
    stats: mergedStats,
    settings: mergedSettings
  };

  console.log('\n--- Merged Data ---');
  console.log(`Habits: ${mergedPayload.habits.length}`);
  console.log(`Records: ${mergedPayload.records.length}`);
  console.log(`JournalEntries: ${mergedPayload.journalEntries.length}`);
  console.log('Stats:', mergedPayload.stats);

  // 4. Encode to Base64 and write SQL file
  const finalJson = JSON.stringify(mergedPayload);
  const finalB64 = Buffer.from(finalJson, 'utf8').toString('base64');
  
  const sql = `UPDATE user_states SET payload = CONVERT(FROM_BASE64('${finalB64}') USING utf8mb4) WHERE user_key = 'bibo1243';
UPDATE user_states SET payload = CONVERT(FROM_BASE64('${finalB64}') USING utf8mb4) WHERE user_key = 'default';
`;

  fs.writeFileSync('/Users/leegary/個人app/habit-snowball/update.sql', sql, 'utf8');
  console.log('\nSuccessfully generated /Users/leegary/個人app/habit-snowball/update.sql');

} catch (err) {
  console.error('Error:', err);
}
