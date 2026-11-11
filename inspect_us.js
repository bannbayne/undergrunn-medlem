const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function uS(');
console.log(content.substring(idx + 2400, idx + 4500));
