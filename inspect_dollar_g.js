const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function $g(');
console.log(content.substring(idx, idx + 1200));
