const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

const target = '"6IX"';
const idx = code.indexOf(target);
console.log('Status bar at', idx);
console.log(code.slice(idx - 100, idx + 200));
