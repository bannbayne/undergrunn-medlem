const fs = require('fs');

const content = fs.readFileSync('index-offline.js', 'utf8');

// Check g6 location
const g6Idx = content.indexOf('function g6(');
console.log('g6Idx:', g6Idx);

// Check Se location
const seIdx = content.indexOf('async function Se(t,e,n={}){');
console.log('seIdx:', seIdx);

// Check MS location
const msIdx = content.indexOf('function MS(');
console.log('msIdx:', msIdx);

// Check UL location
const ulIdx = content.indexOf('UL={');
console.log('ulIdx:', ulIdx);
