const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

let pos = 0;
while ((pos = content.indexOf('return{id:is,name:r?"Butikken":"Shop"', pos)) !== -1) {
    console.log(content.substring(Math.max(0, pos - 200), Math.min(content.length, pos + 50)));
    console.log('---');
    pos += 30;
}
