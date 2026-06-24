const fs = require('fs');

try {
  const mysqlRaw = fs.readFileSync('/Users/leegary/.gemini/antigravity/scratch/db_bibo1243_payload.json', 'utf8');
  console.log('mysqlRaw JSON file length:', mysqlRaw.length);
  console.log('First 500 characters:');
  console.log(mysqlRaw.slice(0, 500));
} catch (err) {
  console.error('Error:', err);
}
