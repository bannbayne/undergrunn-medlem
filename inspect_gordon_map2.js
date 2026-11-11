const fs = require('fs');
const map = JSON.parse(fs.readFileSync('gordon/PRODUCTION-202006192205-424220153/map.json', 'utf8'));
console.log('Keys of map.json:', Object.keys(map).slice(0, 30));
console.log('Sample entry:', Object.entries(map).slice(0, 5));
