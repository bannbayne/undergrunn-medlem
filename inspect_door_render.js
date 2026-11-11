const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

let idx = code.indexOf('const cY="furni/teleport_door.nitro"');
console.log(code.slice(idx - 100, idx + 1800));
