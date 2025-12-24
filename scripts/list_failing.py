#!/usr/bin/env python3
import json

with open('feature_list.json') as f:
    data = json.load(f)
    failing = [(i+1, test['description']) for i, test in enumerate(data) if not test['passes']]
    print(f'Total failing: {len(failing)}\n')
    for idx, desc in failing:
        print(f'{idx}. {desc}')
