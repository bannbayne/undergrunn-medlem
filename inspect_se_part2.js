const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('if (e === "buyRoomUpgrade") {');
console.log(content.substring(idx, idx + 4000));
