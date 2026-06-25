const path = require("path");
const express = require("express");
const mysql = require("mysql2/promise");
const compression = require("compression");

const app = express();
app.use(compression());
const port = Number(process.env.PORT || 8080);
const staticDir = __dirname;

app.use(express.json({ limit: "1mb" }));
app.use(express.static(staticDir));

let pool;
let schemaReady;

function getDbConfig() {
  const isZeabur = process.env.ZEABUR === "1";
  const host = isZeabur 
    ? "habit-snowball-mysql.default.svc.cluster.local" 
    : (process.env.MYSQL_HOST || "127.0.0.1");
    
  const user = isZeabur
    ? "habit_snowball"
    : (process.env.MYSQL_USER || "root");
    
  const password = isZeabur
    ? "hs-pass-20260622"
    : (process.env.MYSQL_PASSWORD || "");
    
  const database = isZeabur
    ? "habit_snowball"
    : (process.env.MYSQL_DATABASE || "habit_snowball");

  return {
    host,
    port: Number(process.env.MYSQL_PORT || 3306),
    user,
    password,
    database,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
  };
}

function getPool() {
  if (!pool) {
    pool = mysql.createPool(getDbConfig());
  }
  return pool;
}

async function ensureSchema() {
  if (schemaReady) return schemaReady;

  schemaReady = (async () => {
    const config = getDbConfig();
    const bootstrapPool = mysql.createPool({
      ...config,
      database: undefined
    });

    await bootstrapPool.query(
      `CREATE DATABASE IF NOT EXISTS \`${config.database}\`
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci`
    );
    await bootstrapPool.end();

    const db = getPool();
    await db.query(`
      CREATE TABLE IF NOT EXISTS user_states (
        user_key VARCHAR(120) NOT NULL PRIMARY KEY,
        payload JSON NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    `);
  })();

  return schemaReady;
}

function normalizeUserKey(raw) {
  const value = String(raw || "").trim();
  if (!value) return "default";
  return value.slice(0, 120);
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

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

function normalizePayload(payload) {
  const base = getDefaultData();
  if (!isPlainObject(payload)) {
    return base;
  }

  return {
    ...base,
    ...payload,
    habits: Array.isArray(payload.habits) ? payload.habits : [],
    records: Array.isArray(payload.records) ? payload.records : [],
    journalEntries: Array.isArray(payload.journalEntries) ? payload.journalEntries : [],
    stats: {
      ...base.stats,
      ...(isPlainObject(payload.stats) ? payload.stats : {})
    },
    settings: {
      ...base.settings,
      ...(isPlainObject(payload.settings) ? payload.settings : {})
    }
  };
}

function hasMeaningfulPayload(payload) {
  if (!isPlainObject(payload)) return false;
  const stats = isPlainObject(payload.stats) ? payload.stats : {};
  return (Array.isArray(payload.habits) && payload.habits.length > 0) ||
    (Array.isArray(payload.records) && payload.records.length > 0) ||
    (Array.isArray(payload.journalEntries) && payload.journalEntries.length > 0) ||
    (stats.totalPoints || 0) !== 0 ||
    (stats.totalResisted || 0) !== 0 ||
    (stats.currentStreak || 0) !== 0 ||
    (stats.longestStreak || 0) !== 0;
}

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value));
}

function preferRicherText(a, b) {
  const aa = typeof a === "string" ? a : "";
  const bb = typeof b === "string" ? b : "";
  if (!aa) return bb;
  if (!bb) return aa;
  return aa.length >= bb.length ? aa : bb;
}

function mergeStringArrays(a, b) {
  const out = [];
  [...(Array.isArray(a) ? a : []), ...(Array.isArray(b) ? b : [])].forEach((item) => {
    if (typeof item === "string" && item.trim() && !out.includes(item.trim())) {
      out.push(item.trim());
    }
  });
  return out;
}

function journalCompletenessScore(entry) {
  if (!isPlainObject(entry)) return 0;
  return (entry.content ? entry.content.length : 0) +
    (entry.polishedContent ? entry.polishedContent.length : 0) +
    (entry.aiSummary ? entry.aiSummary.length : 0) +
    (Array.isArray(entry.comments) ? entry.comments.length * 1000 : 0) +
    (Array.isArray(entry.keywords) ? entry.keywords.length * 50 : 0);
}

function mergeJournalEntry(existingEntry, incomingEntry) {
  const existingScore = journalCompletenessScore(existingEntry);
  const incomingScore = journalCompletenessScore(incomingEntry);
  const base = cloneValue(existingScore >= incomingScore ? existingEntry : incomingEntry);

  base.id = existingEntry.id || incomingEntry.id;
  base.author = existingEntry.author || incomingEntry.author || "小葦";
  base.createdAt = existingEntry.createdAt || incomingEntry.createdAt || new Date().toISOString();
  base.title = existingScore >= incomingScore
    ? (existingEntry.title || incomingEntry.title || "")
    : (incomingEntry.title || existingEntry.title || "");
  base.content = preferRicherText(existingEntry.content, incomingEntry.content);
  base.polishedContent = preferRicherText(existingEntry.polishedContent, incomingEntry.polishedContent);
  base.aiSummary = preferRicherText(existingEntry.aiSummary, incomingEntry.aiSummary);
  base.keywords = mergeStringArrays(existingEntry.keywords, incomingEntry.keywords);

  const commentsMap = new Map();
  [...(Array.isArray(existingEntry.comments) ? existingEntry.comments : []), ...(Array.isArray(incomingEntry.comments) ? incomingEntry.comments : [])].forEach((comment) => {
    if (!comment || !comment.id) return;
    commentsMap.set(comment.id, {
      ...(commentsMap.get(comment.id) || {}),
      ...cloneValue(comment)
    });
  });
  base.comments = Array.from(commentsMap.values())
    .sort((a, b) => new Date(a.createdAt || 0) - new Date(b.createdAt || 0));

  return base;
}

function mergeById(existingItems, incomingItems, mergeItem) {
  const map = new Map();
  (Array.isArray(existingItems) ? existingItems : []).forEach((item) => {
    if (item && item.id) map.set(item.id, cloneValue(item));
  });
  (Array.isArray(incomingItems) ? incomingItems : []).forEach((item) => {
    if (!item || !item.id) return;
    if (map.has(item.id)) {
      map.set(item.id, mergeItem ? mergeItem(map.get(item.id), item) : { ...map.get(item.id), ...cloneValue(item) });
    } else {
      map.set(item.id, cloneValue(item));
    }
  });
  return Array.from(map.values());
}

function mergePayloads(existingPayload, incomingPayload) {
  const existing = normalizePayload(existingPayload);
  const incoming = normalizePayload(incomingPayload);
  if (!hasMeaningfulPayload(incoming) && hasMeaningfulPayload(existing)) {
    return existing;
  }
  if (!hasMeaningfulPayload(existing)) {
    return incoming;
  }

  const records = mergeById(existing.records, incoming.records)
    .sort((a, b) => new Date(a.timestamp || 0) - new Date(b.timestamp || 0));
  return {
    ...existing,
    ...incoming,
    habits: mergeById(existing.habits, incoming.habits),
    records,
    journalEntries: mergeById(existing.journalEntries, incoming.journalEntries, mergeJournalEntry)
      .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0)),
    stats: {
      ...existing.stats,
      ...incoming.stats,
      totalPoints: records.reduce((sum, record) => sum + (record.points || 0), 0),
      totalResisted: records.filter((record) => record.action === "resisted").length
    },
    settings: {
      ...existing.settings,
      ...incoming.settings
    },
    lastModified: new Date().toISOString()
  };
}

app.get("/api/health", async (_req, res) => {
  try {
    await getPool().query("SELECT 1");
    res.json({ ok: true });
  } catch (error) {
    console.error("Health check failed:", error);
    res.status(500).json({ ok: false, error: "database_unavailable" });
  }
});

app.get("/api/state/:userKey", async (req, res) => {
  try {
    const userKey = normalizeUserKey(req.params.userKey);
    const [rows] = await getPool().query(
      "SELECT payload, updated_at FROM user_states WHERE user_key = ? LIMIT 1",
      [userKey]
    );

    if (!rows.length) {
      res.status(404).json({ error: "not_found" });
      return;
    }

    res.json({
      userKey,
      data: normalizePayload(rows[0].payload),
      updatedAt: rows[0].updated_at
    });
  } catch (error) {
    console.error("Failed to load state:", error);
    res.status(500).json({ error: "load_failed" });
  }
});

app.put("/api/state/:userKey", async (req, res) => {
  try {
    const userKey = normalizeUserKey(req.params.userKey);
    const incomingData = normalizePayload(req.body ? req.body.data : null);
    const [existingRows] = await getPool().query(
      "SELECT payload FROM user_states WHERE user_key = ? LIMIT 1",
      [userKey]
    );
    const existingData = existingRows.length ? normalizePayload(existingRows[0].payload) : null;
    const data = existingData ? mergePayloads(existingData, incomingData) : incomingData;

    await getPool().query(
      `INSERT INTO user_states (user_key, payload)
       VALUES (?, ?)
       ON DUPLICATE KEY UPDATE payload = VALUES(payload)`,
      [userKey, JSON.stringify(data)]
    );

    res.json({ ok: true, userKey });
  } catch (error) {
    console.error("Failed to save state:", error);
    res.status(500).json({ error: "save_failed" });
  }
});

app.delete("/api/state/:userKey", async (req, res) => {
  try {
    const userKey = normalizeUserKey(req.params.userKey);
    await getPool().query("DELETE FROM user_states WHERE user_key = ?", [userKey]);
    res.json({ ok: true, userKey });
  } catch (error) {
    console.error("Failed to delete state:", error);
    res.status(500).json({ error: "delete_failed" });
  }
});

app.get("/api/ollama-tunnel", async (req, res) => {
  try {
    const [rows] = await getPool().query(
      "SELECT payload FROM user_states WHERE user_key = 'ollama_tunnel' LIMIT 1"
    );
    if (rows.length) {
      res.json(rows[0].payload);
    } else {
      res.json({ tunnelUrl: "" });
    }
  } catch (error) {
    console.error("Failed to get ollama-tunnel:", error);
    res.status(500).json({ error: "db_error" });
  }
});

app.post("/api/ollama-tunnel", async (req, res) => {
  try {
    const { tunnelUrl } = req.body || {};
    await getPool().query(
      `INSERT INTO user_states (user_key, payload)
       VALUES ('ollama_tunnel', ?)
       ON DUPLICATE KEY UPDATE payload = VALUES(payload)`,
      [JSON.stringify({ tunnelUrl: tunnelUrl || "" })]
    );
    res.json({ ok: true, tunnelUrl: tunnelUrl || "" });
  } catch (error) {
    console.error("Failed to save ollama-tunnel:", error);
    res.status(500).json({ error: "db_error" });
  }
});

app.get("*", (_req, res) => {
  res.sendFile(path.join(staticDir, "index.html"));
});

async function startServer() {
  try {
    console.log("Initializing database schema...");
    await ensureSchema();
    console.log("Database schema initialized successfully.");

    app.listen(port, () => {
      console.log(`Habit Snowball server listening on port ${port}`);
    });
  } catch (error) {
    console.error("Fatal error during server startup:", error);
    process.exit(1);
  }
}

startServer();
