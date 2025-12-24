import json

with open('feature_list.json', 'r') as f:
    data = json.load(f)

total = len(data)
passing = sum(1 for f in data if f.get('passes', False))
remaining = total - passing

print(f'{total} features total')
print(f'{passing} features passing')
print(f'{remaining} features remaining')
print(f'{(passing/total*100):.1f}% complete')
