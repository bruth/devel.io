---
published: true
title: "Python Tip: Dedent Multi-line Strings"
---

I've wanted to know this for a long time..

```python
>>> import textwrap

>>> multiline = """
...		I am a few lines of text:
...    	
...    		with open('file.txt') as f:
...        		f.write('a code block inside')
...		
...	    demonstrating the use of `textwrap.dedent`.
... """

>>> print(textwrap.dedent(multiline))
I am a few lines of text:

    with open('file.txt') as f:
        f.write('a code block inside')

demonstrating the use of `textwrap.dedent`.
```