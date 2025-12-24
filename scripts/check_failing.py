#!/usr/bin/env python3
import json

with open('feature_list.json') as f:
    features = json.load(f)

print(f"Total features: {len(features)}")
print(f"Passing: {sum(1 for f in features if f['passes'])}")
print(f"Failing: {sum(1 for f in features if not f['passes'])}")
print("\nFirst 10 failing tests:")
print("=" * 80)

count = 0
for i, feature in enumerate(features):
    if not feature['passes']:
        count += 1
        if count <= 10:
            print(f"\n{count}. Test #{i+1}: {feature['description'][:80]}")
            print(f"   Category: {feature['category']}")
