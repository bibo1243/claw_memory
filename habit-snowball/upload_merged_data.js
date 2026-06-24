const fs = require('fs');

async function run() {
  const sql = fs.readFileSync('/Users/leegary/個人app/habit-snowball/update.sql', 'utf8');
  const match = sql.match(/FROM_BASE64\('([^']+)'\)/);
  if (!match) {
    console.error('Base64 payload not found in update.sql');
    return;
  }

  const b64 = match[1];
  const jsonStr = Buffer.from(b64, 'base64').toString('utf8');
  const payload = JSON.parse(jsonStr);

  const cleanHtmlTags = (str) => {
    if (typeof str !== 'string') return str;
    return str.replace(/<span[^>]*>/g, '').replace(/<\/span>/g, '');
  };

  // Clean records notes
  if (Array.isArray(payload.records)) {
    payload.records.forEach(r => {
      if (r.note) r.note = cleanHtmlTags(r.note);
    });
  }

  // Clean journal entries content
  if (Array.isArray(payload.journalEntries)) {
    payload.journalEntries.forEach(j => {
      if (j.content) j.content = cleanHtmlTags(j.content);
      if (j.polishedContent) j.polishedContent = cleanHtmlTags(j.polishedContent);
    });
  }

  console.log('Cleaned payload. Records count:', payload.records?.length, 'JournalEntries count:', payload.journalEntries?.length);

  const users = ['default', 'bibo1243'];
  for (const user of users) {
    console.log(`Uploading state to Zeabur for user: ${user}...`);
    try {
      const response = await fetch(`https://habit-snowball.zeabur.app/api/state/${user}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ data: payload })
      });

      if (response.ok) {
        console.log(`Successfully uploaded state for user: ${user}`);
      } else {
        console.error(`Failed to upload for user: ${user}. Status: ${response.status}`);
      }
    } catch (error) {
      console.error(`Error uploading for user: ${user}:`, error.message);
    }
  }
}

run();
