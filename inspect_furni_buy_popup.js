const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const idx = content.indexOf('m=o("button",{class:"btn primary",onclick:()=>void w()}');
console.log(content.substring(idx + 700, idx + 2000));
