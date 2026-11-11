const fs = require('fs');
const list = JSON.parse(fs.readFileSync('scratch_danish_strings.json', 'utf8'));

console.log('Total:', list.length);
list.forEach((item, idx) => {
  console.log(`${idx + 1}: ${item.str}`);
});
