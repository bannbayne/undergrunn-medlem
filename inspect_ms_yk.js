const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('const N=yk(a,G=>{if(G)c=G;z()})');
console.log(content.substring(idx - 50, idx + 200));
