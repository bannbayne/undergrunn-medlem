const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('return{id:is,name:r?"Butikken":"Shop"');
console.log(content.substring(idx - 600, idx + 400));
