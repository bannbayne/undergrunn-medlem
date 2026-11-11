const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('6ix-offline-inventory', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 250)));
    console.log('--- inventory init ---');
    pos += 21;
}
