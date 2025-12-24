import json

with open('feature_list.json') as f:
    data = json.load(f)

total = len(data)
passing = sum(1 for f in data if f['passes'])
failing = total - passing

print(f'Total features: {total}')
print(f'Passing: {passing}')
print(f'Failing: {failing}')
print(f'Progress: {passing}/{total} ({100*passing//total}%)')
