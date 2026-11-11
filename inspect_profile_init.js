const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('nameColor: "#00ffcc"');
console.log(content.substring(idx + 350, idx + 800));
