const fs = require('fs');

const lines = fs.readFileSync('asset_list.txt', 'utf8').split('\n').map(l => l.trim()).filter(Boolean);
const missing = [];
for (const l of lines) {
    if (l.includes('*') || l === 'audio/mpeg' || l === 'audio/wav') continue;
    if (!fs.existsSync(l)) {
        missing.push(l);
    }
}
console.log('Missing assets from asset_list.txt:', missing);
