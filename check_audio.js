const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

const audioFiles = new Set(content.match(/["'][^"']+\.(mp3|wav|ogg)["']/g) || []);
console.log('Audio files referenced:');
const missingAudio = [];
for (let a of audioFiles) {
    a = a.replace(/['"]/g, '').replace(/^\.\//, '');
    if (!fs.existsSync(a)) {
        missingAudio.push(a);
    }
}
console.log('Missing audio files:', missingAudio);
