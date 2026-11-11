const fs = require('fs');

const map = JSON.parse(fs.readFileSync('gordon/PRODUCTION-202006192205-424220153/map.json', 'utf8'));

const allLibs = new Set();
for (const [part, dict] of Object.entries(map)) {
    for (const [id, lib] of Object.entries(dict)) {
        allLibs.add(lib);
    }
}

console.log('Total unique libraries across map.json:', allLibs.size);
const existingDirs = new Set(fs.readdirSync('gordon/PRODUCTION-202006192205-424220153'));
const missing = [...allLibs].filter(l => !existingDirs.has(l));
console.log('Existing libraries:', existingDirs.size);
console.log('Missing libraries:', missing.length);

const coreLibs = [
    "hh_human_body", "hh_human_shirt", "hh_human_leg", "hh_human_hair",
    "hh_human_face", "hh_human_hats", "hh_human_item", "hh_human_shoe",
    "hh_human_acc_face", "hh_human_acc_head", "hh_human_acc_chest",
    "hh_human_acc_waist", "hh_human_acc_eye"
];

console.log('Missing core libs:', coreLibs.filter(c => !existingDirs.has(c)));
