const fs = require('fs');
const features = JSON.parse(fs.readFileSync('feature_list.json', 'utf8'));

const passing = features.filter(f => f.passes).length;
const failing = features.filter(f => !f.passes).length;
const total = features.length;
const completion = ((passing / total) * 100).toFixed(1);

console.log('\n═══════════════════════════════════════════════════════');
console.log('  SESSION 88 - FINAL STATISTICS');
console.log('═══════════════════════════════════════════════════════');
console.log('');
console.log(`  Passing Features:  ${passing}/${total}`);
console.log(`  Failing Features:  ${failing}/${total}`);
console.log(`  Completion Rate:   ${completion}%`);
console.log('');
console.log('═══════════════════════════════════════════════════════');
