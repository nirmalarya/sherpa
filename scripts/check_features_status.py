import json

with open('feature_list.json', 'r') as f:
    data = json.load(f)

total = len(data)
passing = sum(1 for f in data if f.get('passes', False))
failing = total - passing

print(f'{total} total features')
print(f'{passing} passing ({100*passing//total}%)')
print(f'{failing} failing ({100*failing//total}%)')
