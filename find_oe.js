const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

let idx = 1080000;
while ((idx = code.indexOf('Oe', idx)) !== -1 && idx < 1100000) {
  console.log('Oe at ' + idx + ':', code.slice(Math.max(0, idx - 40), idx + 80));
  idx += 2;
}
