const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('UL={');
console.log(content.substring(idx, idx + 400));
