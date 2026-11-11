const fs = require('fs');

if (fs.existsSync('asset_list.txt')) {
    const lines = fs.readFileSync('asset_list.txt', 'utf8').split('\n').filter(Boolean);
    console.log('asset_list.txt lines count:', lines.length);
    console.log('first 20 lines:', lines.slice(0, 20));
} else {
    console.log('asset_list.txt does not exist');
}
