const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

// Find g6 definition in index-offline.js
const idx = content.indexOf('function g6(');
const endIdx = content.indexOf('const b6=', idx);
const g6Code = content.substring(idx, endIdx);

console.log('g6 code:');
console.log(g6Code);
