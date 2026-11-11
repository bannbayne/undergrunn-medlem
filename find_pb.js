const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

function find(t) {
  let idx = 0;
  while ((idx = code.indexOf(t, idx)) !== -1) {
    console.log(t, 'at', idx, ':', code.slice(Math.max(0, idx - 40), idx + t.length + 60));
    idx += t.length;
  }
}

find('pb=');
find('reddoor');
find('pb');
