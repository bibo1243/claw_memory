const fs = require('fs');
const sql = fs.readFileSync('/Users/leegary/個人app/habit-snowball/update.sql', 'utf8');
const match = sql.match(/FROM_BASE64\('([^']+)'\)/);
if (match) {
  const b64 = match[1];
  const jsonStr = Buffer.from(b64, 'base64').toString('utf8');
  const data = JSON.parse(jsonStr);
  console.log('Habits count:', data.habits ? data.habits.length : 0);
  console.log('Records count:', data.records ? data.records.length : 0);
  console.log('Journal entries count:', data.journalEntries ? data.journalEntries.length : 0);
  
  console.log('\n--- Records Sample ---');
  (data.records || []).slice(0, 5).forEach((r, idx) => {
    console.log(`${idx + 1}. HabitId: ${r.habitId}, Action: ${r.action}, Date: ${r.timestamp}, Note excerpt: ${String(r.note || '').slice(0, 100)}`);
  });

  console.log('\n--- Journal Entries Sample ---');
  (data.journalEntries || []).slice(0, 5).forEach((j, idx) => {
    console.log(`${idx + 1}. Date: ${j.createdAt}, Title: ${j.title}, Content excerpt: ${String(j.content || '').slice(0, 100)}`);
  });
} else {
  console.log('No Base64 match found in update.sql');
}
