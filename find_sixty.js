const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

// Find where Gt / sixty is clicked or interacted with
let pos = 0;
while ((pos = content.indexOf('sixty', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 200)));
    console.log('=== sixty ===');
    pos += 5;
}
