---
layout: post
title: Deep Copying Django Model Instances, What Does It Mean?
---

---

**UPDATE [2011-09-09]**: The django-data-proxy library has been (quickly) superseded by [https://github.com/cbmi/django-forkit] [0] which solves the more generic problem of creating shallow and deep copies of model instances. It recursively traverses all relationships during a deep _fork_ and defers saving those new objects until the end. It also provides a useful ``diff`` method for comparing objects of the same type.

[0]: https://github.com/cbmi/django-forkit

---

I have recently come across a need for making a copy of a model instance. There are [quite a few hits] [1] for solutions on how to create a copy or more interestingly a _deepcopy_ of a model instance.

[1]: http://www.google.com/search?q=copy+django+model+instance

My particular use case for creating a copy was to create a temporary proxy of the model instance for a session. The idea is to allow for the proxy to be altered without affecting the original instance (saved in the database). Of course one could say.. _"just alter the instance without saving it"_, but I wanted to be able to persist the changes across sessions.

# Initial Solution: django-data-proxy
So, I wrote a simple abstract model class to implement a instance-proxy API. It is available on GitHub: [https://github.com/cbmi/django-data-proxy] [2]. It implements common operations like: ``proxy`` to define the initial proxy instance, ``diff`` to return the difference between the original instance with the proxy, ``reset`` to reset back to the original instance data, ``push`` to apply the differences to the original object, and ``clear`` to return the proxy to it's default values for the model.
Currently the API supports only shallow proxying, i.e basic local fields and local foreign keys. However, I have a stable branch (<a href="https://github.com/cbmi/django-data-proxy/tree/deep-proxy)">https://github.com/cbmi/django-data-proxy/tree/deep-proxy)</a> that handles many-to-many and creating proxies for related objects which subclasses the ``DataProxyModel``. This is the beginnings of API for _deep proxying_.

[2]: https://github.com/cbmi/django-data-proxy

## Deep Proxy (Copy)
And then I started thinking&hellip; what does it mean to perform a deep proxy? What does it mean to perform a deep _copy_ for relational data in general? Starting with a simple example:

```python
class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

author = Author('John', 'Doe')
author.save()
```

For basic model like this, a copying an instance is trivial. Simply set the primary key to ``None`` and save:

```python
author.pk = None
author.save()
author.pk # 2
```

When dealing with related objects, though, things become a bit ambiguous.

## Foreign Keys
Let's add a ``Book`` model:

```python
class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Author)
    summary = models.TextField()
    pub_date = models.DateField()

book = Book('John Doe: The Autobiography', author,
    'A long, long time ago..', date(2011, 9, 3))
book.save()
```

What happens to the relationship to ``author`` when ``book`` is copied? It will still reference ``author``, which is expected. But, what would a deep copy of ``book`` be?

It depends, kind of.

In this example it doesn't make sense to have two author entries for _John Doe_, but for some data models it makes sense to create copies or _forks_ of other data. Social data that can be shared and then subsequently altered needs to be forked to ensure the source data is not changed. In this case, a true deep copy would make sense (distributed version control systems (DVCS) also come to mind).

That being said, from now on I am going say to **fork** for clarity, since _deep copy_ is somewhat ambiguous.

## Reverse Foreign Keys

What about reverse foreign keys e.g. ``Author`` to ``Book``? That is simple, those objects are not included in the fork. Since the ``Author`` model is _unaware_ of the ``Book`` model, it doesn't make sense to include the set of related books. (I would like for someone to share a data model that would argue against statement).

## One-to-One

An one-to-one relationships is a foreign key, but with the added constraint. Let's update our ``Book`` model:

```python
class Book(models.Model):
    author = models.OneToOneField(Author)
    ...
```

The constraint defines exclusivity between a single book and an author. That is, an author cannot be referenced by more than one book.
This complicates things a bit for a shallow copy. The ``book`` copy cannot retain the reference to the same ``author`` since the database would throw a unique constraint error. The simply solution for a shallow copy is to set any one-to-one relations to ``None``. If the field is nullable, then the copy can be saved, otherwise, as in this example, a new author would need to be defined and set on the book copy.
This is a bit awkward since it's not _really_ a copy, but the unique constraint undermines the implementation.

## Many-To-Many

The final relationship type is many-to-many. Let us update the ``Book`` model one more time.

```python
class Book(models.Model):
    authors = models.ManyToManyField(Author)
    ...
```

In either case, copy or fork, the set of authors for ``book`` can be applied to the ``book`` copy.

```python
authors = book.authors.all()
book.pk = None
book.save()
book.authors = authors
```

This makes sense since an entry in the _through_ table defines a unique constraint between ``Book`` and ``Author``. For this reason, it can be assumed that a copy or fork will simply reassign the ``authors`` set to the copy (shown above).
A caveat to this is handling custom ``through`` models since there may be additional data that needs to be copied.

# So what does this all mean?

Well first off, simply stating _"I want to implement a deep copy for model instances"_ is not good enough without a real use case. It may not be necessary or not actually representative of a real deep copy.
The bigger picture is the fact that handling related objects when attempting perform a deep copy (or proxy in my case) is not trivial. It is not as simple as ensuring nested mutable data structures are copied.
I think [https://github.com/cbmi/django-data-proxy](https://github.com/cbmi/django-data-proxy) contains a few solid first steps for solving this problem. If you feel like contributing in any way, you know the deal.
