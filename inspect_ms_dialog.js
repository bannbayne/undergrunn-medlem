const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function MS(');
console.log(content.substring(idx + 1900, idx + 4000));
