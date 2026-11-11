const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

// Search for where clicking a furniture in the shop opens y9 (furni-buy)
let pos = 0;
while ((pos = content.indexOf('y9(', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 250)));
    console.log('=== y9 ===');
    pos += 3;
}
