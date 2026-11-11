const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const regex = /Se\([^,]+,\s*["']([^"']+)["']/g;
const actions = new Set();
let match;
while ((match = regex.exec(content)) !== null) {
    actions.add(match[1]);
}

console.log(JSON.stringify(Array.from(actions).sort(), null, 2));
