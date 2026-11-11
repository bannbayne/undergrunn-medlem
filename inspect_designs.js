const fs = require('fs');

if (fs.existsSync('designs/bundle.json')) {
    const b = JSON.parse(fs.readFileSync('designs/bundle.json', 'utf8'));
    console.log('designs/bundle.json keys:', Object.keys(b));
    console.log('Total designs:', Array.isArray(b) ? b.length : Object.keys(b).length);
} else {
    console.log('designs/bundle.json does not exist');
}
