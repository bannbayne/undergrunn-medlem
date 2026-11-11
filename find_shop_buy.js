const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('Kjøp for', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== Kjøp for ===');
    pos += 8;
}

pos = 0;
while ((pos = content.indexOf('Køb for', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== Køb for ===');
    pos += 7;
}
