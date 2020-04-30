import json

def save(*args):
  with open('save.json', 'w') as f:
    json.dump(args, f)

def load():
  with open('save.json', 'r') as f:
    return tuple(json.load(f))