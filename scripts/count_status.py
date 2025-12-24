import json

with open('feature_list.json', 'r') as f:
    data = json.load(f)

total = len(data)
passing = sum(1 for f in data if f.get('passes', False))
failing = total - passing

print(f"Total features: {total}")
print(f"Passing: {passing} ({passing*100/total:.1f}%)")
print(f"Failing: {failing} ({failing*100/total:.1f}%)")
