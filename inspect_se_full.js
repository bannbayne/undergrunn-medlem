const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('async function Se(t,e,n={}){');
console.log(content.substring(idx, idx + 4000));
