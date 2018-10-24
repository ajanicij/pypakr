from random import choice

def random():
  jokes = []
  jokes.append('''
Q. What do you call a psychic midget who has escaped from prison?
A. A SMALL MEDIUM AT LARGE!
''')
  jokes.append('''
Q. What do you do with a sick boat?
A. TAKE IT TO THE DOC!
''')
  jokes.append('''
Moses had the first tablet that could connect to the cloud.
''')
  jokes.append('''
Q. Why did the blonde stare at a frozen orange juice can for 2 hours?
A. Because it said "concentrate"!
''')
  return choice(jokes)
