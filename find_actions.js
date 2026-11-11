const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

// Search for buyFurni in offline action handler
let pos = 0;
while ((pos = content.indexOf('buyFurni', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 150), Math.min(content.length, pos + 300)));
    console.log('--- buyFurni ---');
    pos += 8;
}

// Search for "[OFFLINE ACTION]"
pos = 0;
while ((pos = content.indexOf('[OFFLINE ACTION]', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos), Math.min(content.length, pos + 1000)));
    console.log('=== OFFLINE ACTION ===');
    pos += 16;
}
