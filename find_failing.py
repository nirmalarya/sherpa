#!/usr/bin/env python3
import json

with open('feature_list.json', 'r') as f:
    features = json.load(f)

failing = [f for f in features if not f['passes']]

print(f"Total failing tests: {len(failing)}\n")
for i, test in enumerate(failing, 1):
    print(f"{i}. {test['description']}")
