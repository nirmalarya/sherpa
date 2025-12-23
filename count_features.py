import json

with open('feature_list.json', 'r') as f:
    data = json.load(f)

total = len(data)
passing = sum(1 for f in data if f.get('passes', False))
remaining = total - passing

print(f'Total features: {total}')
print(f'Passing: {passing}')
print(f'Remaining: {remaining}')
print(f'Progress: {passing/total*100:.1f}%')
