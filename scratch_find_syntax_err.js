const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

const lines = code.split('\n');
console.log('Total lines:', lines.length);
for (let i = Math.max(0, lines.length - 20); i < lines.length; i++) {
  console.log((i+1) + ': ' + lines[i].slice(0, 100));
}
