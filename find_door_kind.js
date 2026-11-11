const fs = require('fs');
const code = fs.readFileSync('assets/index-offline.js', 'utf8');

let idx = code.indexOf('"derived:red_door"');
if (idx === -1) idx = code.indexOf("'derived:red_door'");
console.log('idx:', idx);
if (idx !== -1) {
  console.log(code.slice(idx - 100, idx + 100));
}
// Also search for "teleport_door"
let idx2 = 0;
while ((idx2 = code.indexOf('teleport_door', idx2)) !== -1) {
  console.log(code.slice(idx2 - 100, idx2 + 100));
  idx2 += 13;
}
