const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

let idx = code.indexOf('j$=qn(e,');
console.log(code.slice(idx, idx + 2000));
