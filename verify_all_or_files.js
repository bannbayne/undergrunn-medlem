const fs = require('fs');
const Or = require('./scratch_Or.js')(1);

const missing = [];
for (const item of Or) {
    if (item.nitro && item.nitro.startsWith('derived:')) continue;
    const file = `furni/f_${item.id}.nitro`;
    if (!fs.existsSync(file)) {
        missing.push({ id: item.id, file });
    }
}
console.log('Or items missing furni/f_<id>.nitro:', missing);
