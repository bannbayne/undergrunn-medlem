const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

let idx = 0;
while ((idx = code.indexOf('derived:', idx)) !== -1) {
  console.log('derived at ' + idx + ':', code.slice(Math.max(0, idx - 40), idx + 80));
  idx += 8;
}
