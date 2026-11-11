const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('function yk(');
if (idx !== -1) {
    console.log(content.substring(idx, idx + 500));
} else {
    const idx2 = content.indexOf('yk=');
    console.log(content.substring(idx2, idx2 + 500));
}
