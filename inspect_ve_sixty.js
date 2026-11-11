const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('if(Ve.type==="sixty"){');
console.log(content.substring(idx, idx + 1000));
