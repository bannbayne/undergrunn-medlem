const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function MS(');
const zIdx = content.indexOf('function z()', idx);
const endMs = content.indexOf('return{close:me}}', zIdx);
console.log(content.substring(endMs - 300, endMs + 20));
