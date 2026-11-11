const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('async function GD(){');
console.log(content.substring(idx, idx + 1500));
