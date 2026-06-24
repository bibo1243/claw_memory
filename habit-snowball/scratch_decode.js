const fs = require('fs');

try {
  const content = fs.readFileSync('/Users/leegary/個人app/habit-snowball/mysql_base64_payloads.txt', 'utf8');
  const lines = content.split('\n');
  
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
  if (biboB64) {
    const decoded = Buffer.from(biboB64, 'base64').toString('utf8');
    const parsed = JSON.parse(decoded);
    fs.writeFileSync('/Users/leegary/個人app/habit-snowball/mysql_bibo1243_payload.json', JSON.stringify(parsed, null, 2), 'utf8');
    console.log('Saved bibo1243 payload to mysql_bibo1243_payload.json');
  }
} catch (err) {
  console.error('Error:', err);
}
