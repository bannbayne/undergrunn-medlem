const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('counter', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 250)));
    console.log('--- counter ---');
    pos += 7;
}
