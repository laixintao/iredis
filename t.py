from tomlkit import loads

with open("pyproject.toml") as f:
    result = loads(f.read())


for t in result['tool']['poetry']['classifiers']:
    print(t)
