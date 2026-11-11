const fs = require('fs');

// Test if furni/f_sofa.nitro exists
console.log('furni/f_sofa.nitro exists:', fs.existsSync('furni/f_sofa.nitro'));
console.log('size:', fs.statSync('furni/f_sofa.nitro').size);
