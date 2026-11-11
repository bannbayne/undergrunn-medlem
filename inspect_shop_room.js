const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('id:"shop"');
if (idx !== -1) {
    console.log(content.substring(idx - 50, idx + 600));
} else {
    const idx2 = content.indexOf('is="shop"');
    console.log(content.substring(idx2 - 50, idx2 + 600));
}
