const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

const pos = code.indexOf('function kk(');
console.log(code.slice(pos, pos + 400));
