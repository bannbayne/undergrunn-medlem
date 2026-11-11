const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

const pOr = code.indexOf('{id:"sofa"');
console.log('Or entry:', code.slice(pOr, pOr + 200));
