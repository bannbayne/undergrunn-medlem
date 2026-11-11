const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('bayne', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 150)));
    console.log('---');
    pos += 5;
}
