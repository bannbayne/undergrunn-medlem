const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('PRODUCTION-202006192205-424220153', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 200)));
    console.log('--- gordon ref ---');
    pos += 33;
}
