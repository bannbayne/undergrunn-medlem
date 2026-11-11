const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

console.log(code.slice(1229600, 1231500));
