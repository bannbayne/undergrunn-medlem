const fs = require('fs');
const code = fs.readFileSync('index-offline.js', 'utf8');

// Find Ce["sofa"] and Ce["f_sofa"]
console.log('pos f_sofa in code:');
const p1 = code.indexOf('"f_sofa"');
const p2 = code.indexOf('f_sofa:');
console.log('p1:', p1, 'p2:', p2);

// Check FURNI_NITRO_MAP
const pMap = code.indexOf('FURNI_NITRO_MAP');
console.log('FURNI_NITRO_MAP pos:', pMap);
if (pMap !== -1) {
  console.log(code.slice(pMap, pMap + 300));
}
