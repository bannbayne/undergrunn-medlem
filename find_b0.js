const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('B0(', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== B0 ===');
    pos += 3;
}
