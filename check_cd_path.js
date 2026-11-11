const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('cd-blodigoktober.mp3');
console.log(content.substring(idx - 50, idx + 100));
