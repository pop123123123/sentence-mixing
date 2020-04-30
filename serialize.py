import json

def save(*args, name='save.json'):
  with open(name, 'w') as f:
    json.dump(args, f)

def load(name='save.json'):
  with open(name, 'r') as f:
    return tuple(json.load(f))