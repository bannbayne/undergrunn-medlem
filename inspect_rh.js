const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('refreshHeader', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 200)));
    console.log('--- refreshHeader ---');
    pos += 13;
}
