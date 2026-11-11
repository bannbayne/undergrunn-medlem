const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('buySixty', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== buySixty ===');
    pos += 8;
}

pos = 0;
while ((pos = content.indexOf('buyClothes', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== buyClothes ===');
    pos += 10;
}
