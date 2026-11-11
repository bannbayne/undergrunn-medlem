const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('is="shop"', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 100), Math.min(content.length, pos + 300)));
    console.log('--- is=shop ---');
    pos += 9;
}

pos = 0;
while ((pos = content.indexOf('_s=', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 50), Math.min(content.length, pos + 200)));
    console.log('=== _s ===');
    pos += 3;
}
