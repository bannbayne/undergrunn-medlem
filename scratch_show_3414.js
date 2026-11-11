const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

const lines = code.split('\n');
for (let i = 3405; i < 3425; i++) {
  console.log((i+1) + ': ' + (lines[i] ? lines[i].slice(0, 120) : ''));
}
