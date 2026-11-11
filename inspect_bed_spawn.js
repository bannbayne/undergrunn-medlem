const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

console.log(code.substring(1150350, 1154000));
