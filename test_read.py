import json

# print(dir(json))
# help(json.load)

with open('data/test.json', 'r') as file:

    article = json.load(file)

print("--- Article Loaded Successfully ---\n")
print(f"Title: {article['title']}")
print(f"Published on: {article['date']}")

print(f"Content Preview: {article['content'][:80]}...")