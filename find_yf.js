const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('Yf', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 50), Math.min(content.length, pos + 100)));
    console.log('--- Yf ---');
    pos += 2;
}
