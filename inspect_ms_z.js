const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function MS(');
const zIdx = content.indexOf('function z()', idx);
console.log(content.substring(zIdx, zIdx + 500));
