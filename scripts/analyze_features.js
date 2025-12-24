#!/usr/bin/env node

const fs = require('fs');

const features = JSON.parse(fs.readFileSync('feature_list.json', 'utf8'));

const failing = features.filter(f => !f.passes);

console.log(`Total failing features: ${failing.length}\n`);
console.log('First 15 failing features:\n');

failing.slice(0, 15).forEach((feature, i) => {
  const desc = feature.description.length > 80
    ? feature.description.substring(0, 80) + '...'
    : feature.description;
  console.log(`${i + 1}. ${desc}`);
  console.log(`   Category: ${feature.category || 'N/A'}`);
  console.log(`   Steps: ${feature.steps ? feature.steps.length : 0}`);
  console.log('');
});
