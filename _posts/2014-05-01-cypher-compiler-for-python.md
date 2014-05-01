---
layout: post
title: "Cypher: Compiler for Python"
---

[cypher](https://github.com/bruth/cypher/) is a Python library for composing [Cypher](http://www.neo4j.org/learn/cypher) queries for [Neo4j](http://neo4j.org). The goal of the project is to serve as a foundation for building simpler domain-specific APIs. It prevents needing to use string formatting or concentation for building a Cypher statement programmatically. Simply compose the parts of the query as needed.


## Example

Let's start with a Cypher query and work our way backwards.

```
MERGE (bob {name: 'Bob'}) ON CREATE SET bob.title = 'Programmer'
WITH bob
OPTIONAL MATCH (joe:Boss {name: 'Joe'})
WITH bob, joe WHERE joe IS NOT NULL
MERGE (joe)-[:MANAGES]->(bob)
RETURN joe IS NOT NULL
```

This query does the following:

- Ensures Bob exists (identified by his name), setting his title if created
- Attempt to find boss Joe
- If Joe exists, ensure Joe manages Bob
- Return true is Joe exists

We can start by importing the classes from the `cypher` package and defining the primary entities Bob, Joe, and the relationship between them, along with a couple helper expressions.

```python
from cypher import *

# Nodes
bob = Node({'name': 'Bob'}, identifier='bob')
joe = Node({'name': 'Joe'}, identifier='joe', labels=['Boss'])

# Properties
programmer_bob = Property('title', 'Programmer', identifier=bob.identifier)

# Relationship
manages = Rel(joe.identifier, bob.identifier, 'MANAGES')

# Predicates
joe_exists = Predicate(joe.identifier, 'IS NOT NULL')
```

Each class is derived from a generic `Token` class which implements the `tokenize` method. This returns a list of tokens that will be joined together when the instance of `str`ified. For example, stringifying the above instances produces the below strings:

```
(bob {name: 'Bob'})
(joe:Boss {name: 'Joe'})

bob.title = 'Programmer'

(joe)-[:MANAGES]->(bob)

joe IS NOT NULL
```

Next we simply step through the query and initialize each statements:

*Merge Bob*

```python
Merge(bob)
```

*Set Bob's Title*

```python
OnCreate(Set(programmer_bob))
```

*Pass along Bob*

```python
With(Identifier(bob.identifier))
```

*Attempt to find Joe*

```python
OptionalMatch(joe)
```

*Pass along Bob and Joe*

```python
With([Identifier(bob.identifier),
      Identifier(joe.identifier)])
```

*Condition on Joe*

```python
Where(joe_exists)
```

*Ensure Joe manages Bob*

```python
Merge(manages)
```

*Return true if Joe exists*

```python
Return(joe_exists)
```

All the statements are wrapped in a `Query`:

```python
Query([
    Merge(bob),
    OnCreate(Set(programmer_bob)),
    With(Identifier(bob.identifier)),
    OptionalMatch(joe),
    With([Identifier(bob.identifier),
          Identifier(joe.identifier)]), 
    Where(joe_exists),
    Merge(manages),
    Return(joe_exists),
])
```

When stringified, this produces the target query:

```
MERGE (bob {name: 'Bob'}) ON CREATE SET bob.title = 'Programmer'
WITH bob
OPTIONAL MATCH (joe:Boss {name: 'Joe'})
WITH bob, joe WHERE joe IS NOT NULL
MERGE (joe)-[:MANAGES]->(bob)
RETURN joe IS NOT NULL
```


## Utility Functions

`cypher` comes with a utilities module (imported as `utils` from the above import statement) that contains various functions for doing common operations, such as getting a value or checking if it exists.

```python
utils.exists(bob)
```

will return a `Query` that produces this query:

```
MATCH (bob {name: 'Bob'})
RETURN bob IS NOT NULL
LIMIT 1
```

This is a very basic example of how `cypher` can serve as a low-level API for building higher level tooling such as utlities or domain-specific APIs.


## Status

At the time of this writing, this project is a few days old, however [most of the Cypher syntax is supported](https://github.com/bruth/cypher#supported-syntax). The current status:

- Alpha stage of API design
    - More Pythonic without risking ambiguity in assumptions
- Incomplete set of token classes
    - Formalize use of operators
    - Add support for indexes
    - Parameters?
- Only minimal protection against composing invalid tokens

I am looking for contributions in the way of the overall approach, API design, and/or code. Please create [issues on GitHub](https://github.com/bruth/cypher/issues) or reply [the announcement on the Neo4j mailing list](https://groups.google.com/forum/#!topic/neo4j/Dfo_lrzOvfg).
