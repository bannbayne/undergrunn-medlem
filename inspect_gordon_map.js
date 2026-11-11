const fs = require('fs');

const map = JSON.parse(fs.readFileSync('gordon/PRODUCTION-202006192205-424220153/map.json', 'utf8'));
const libs = Object.values(map.libraries || map);
const uniqueLibs = [...new Set(libs.map(l => typeof l === 'string' ? l : l.id || l.name))];
console.log('Total libraries in map.json:', uniqueLibs.length);
console.log('Some libraries:', uniqueLibs.slice(0, 30));

const existingDirs = fs.readdirSync('gordon/PRODUCTION-202006192205-424220153');
const missing = uniqueLibs.filter(l => !existingDirs.includes(l));
console.log('Libraries in map.json that are missing on disk:', missing.length);
console.log('First 20 missing:', missing.slice(0, 20));
