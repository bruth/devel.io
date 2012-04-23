---
layout: post
title: Data Binding From The Ground Up
---

_Follow along with the examples on jsFiddle: [http://jsfiddle.net/bruth/z4urM/](http://jsfiddle.net/bruth/z4urM/)_

---

**Update [09/21/2011]**: Most other approaches to data binding each rely on the ``data-bind``
attribute on DOM elements. Having an explicit attribute (rather than making
secondary use of ``name`` or, arbitrarily, ``role``) denotes that this element
is intended to be driven by some data source via a binding.

I like it. My initial thought in writing this article was _semantics_, but this
still holds true with this approach. It is more consistent than dealing with
various other attributes.

The next article will reflect these changes.

## Now A Rant
That being said, one issue that this imposes on existing HTML is needing
to modify it to work with the bindings. This is one of my biggest complaints
about existing solutions to data binding: either you have no or limited control
over your HTML (e.g. [SproutCore] []) or you have to cruft it up with
_declarative_ code that **should** live in JavaScript (e.g. [KnockoutJS] []).
Both solutions make use of a templating system for applying bits of conditional
logic which I personally think should exist in the JavaScript code.

One may argue that it's powerful. Which I agree with, but that HTML (and equally
JavaScript) is now tightly coupled to each other. HTML won't ever _break_, but
all that extra stuff in it will be of no use to anything except for original
library and/or code that understands it.

I prefer to take a more loose approach to solving the problem by ensuring my
HTML and JavaScript can still be useful independently of each other. If I
want to swap out or add additional HTML I can do so. The JavaScript doesn't
care. This also allows reuse of the HTML elsewhere since it is still HTML
rather than what you see on the [KnockoutJS][] homepage.

To reinforce my argument, based on experience, new technologies are cropping
up _all the time_, so writing your HTML/templates to fit into the mold of
one those will slow you down when trying out the next best thing.

[SproutCore]: http://www.sproutcore.com/
[KnockoutJS]: http://knockoutjs.com/

---

# What Is It?

So what is [data binding](http://en.wikipedia.org/wiki/Data_binding) exactly?

> Data binding is a general technique that binds two data/information sources
together and maintains synchronization of data. --Wikipedia

Note that the terminology _sources_ includes representations of data as well.
That is to say, a newspaper and a database are both data sources, but the
capabilities of reading/writing data to each differs greatly. Likewise, one
source may depend on the other source which represents a one-way relationship.

Moving on.

# The Scenario

I have a some raw JSON data:

```javascript
var json = {
    title: 'Secrets of a JavaScript Ninja',
    author: 'John Resig',
    pubDate: 'Duke Nukem Forever baby..',
    summary: 'The untold secrets of the elite JavaScript programmers distilled for intermediate JavaScript programmers, bringing them completely up to speed with the challenges of modern JavaScript development. Explores specific techniques, strategies, and solutions to developing robust, cross-browser, JavaScript code.'
}
```

and it needs to be represented in various ways on a page, including:

- a list item view, which displays minimal information
- a detail view, which shows all information
- an edit view, which display a form with editable fields

Each attribute may be displayed one or more times in each in view (we'll come
back to that). Here are a few example templates:

## List Item Template

```html
<li id="list-item-template">
    <strong role="title"></strong>
    by <span role="author"></span>
    published <span role="pubDate"></span>
</li>
```

## Detail Template

```html
<div id="detail-template">
    <h1 role="title"></h1>
    <em>Published by <span role="author"></span> on <span role="pubDate"></span></em>
    <div role="summary"></div>
</div>
```

## Edit Template

```html
<form id="edit-template">
    <table>
        <tr>
            <th>Title</th>
            <td><input name="title"></td>
        </tr>
        <tr>
            <th>Publish Date</th>
            <td><input name="pubDate"></td>
        </tr>
        <tr>
            <th>Summary</th>
            <td><textarea name="summary"></textarea></td>
        </tr>
    </table>
</form>
```

For each template, each element has been marked-up with an appropriate attribute
("role" or "name") corresponding to a JSON attribute.

# On-Demand View Load/Refresh

Let's start simple. This function simply iterates over each attribute in
``json`` and find all elements that are intending to represent that attribute:

```javascript
function loadViewWithJson(view, json) {
    var value;
    for (var attr in json) {
        value = json[attr];
        view.find('[role=' + attr + ']').text(value);
    }
}
```

Now we can apply it.

```javascript
var listItemView = $(listItemTemplate);
loadViewWithJson(listItemView, json);
```

Every time new data is fetched, this function can be called and the view will
be updated.

```javascript
$.loadJSON('/some/api', function(json) {
    loadViewWithJson(listItemView, json);
});
```

This represents a crude, non-automatic, one-way binding from ``json`` &rarr;
``view``. ``view`` will have to be manually updated each time the ``json``
data changes.

**Limitations to this approach:**

1. inflexible, crude method of updating target elements
2. application code needs to keep track of every time ``json`` is altered so that
``loadViewWithJson`` is executed
3. each call to ``loadViewWithJson`` results in an all or nothing update to
``view``. we are working with a small about of data here, but for a JSON
structure containing hundreds or thousands of data points, a full refresh
(depending on the frequency) is execessive

# 1. Interfaces: Abstract Away APIs 

The above function, ``loadViewWithJson``, roughly performs the below
operation. Each ``json`` attribute targets a specific element with the
correpsonding "role" attribute. The operation as a whole can be thought
of a _signal cycle_ (just go with it).

```bash
json.title -> [role=title]
json.author -> [role=author]
json.date -> [role=pubDate]
```

Each one of these objects is a _terminal_, that is, it acts as an endpoint for
another terminal to interface with. ``json`` is the data source (each attribute
points to some data) while each element is the receiving terminal of that
data.

In order for data to flow between any two terminals, both must have an
appropriate interface for transmission, otherwise the signal (data) will not
flow. The ``json`` interface for sending ``title`` may look like this:

```javascript
function getTitle() {
    return model.get('title');
}
```

and likewise, the receiver interface would look like this:

```javascript
function setTitle(title) {
    $('[role=title]').text(title);
}
```

These functions abstract away each objects' APIs allowing for a simple
and generic invocation:

```javascript
setTitle(getTitle());
```

In the case of the form fields in ``#edit-template``, we run into this problem.
The attribute being compared against is ``name`` rather than ``role``. Thus our
``loadViewWithJson`` breaks down. Let us refactor:

```javascript
// gets a value for the given attribute from the source terminal
function getValue(attr) {
    return json[attr];
}

// sets a value for the given attribute on the receiving terminal
function setValue(elem, value) {
    elem = $(elem);
    if (elem.is('input, textarea')) {
        elem.val(value);
    } else {
        elem.text(value);
    }
}

// returns all relevent and/or active attributes from the source terminal
function targetAttrs() {
    var attr, attrs = [];
    for (attr in json) {
        attrs.push(attr);
    }
    return attrs;
}

// loads a view with data
function loadView(view) {
    var value, attrs = targetAttrs();
    for (var attr, i=0; i < attrs.length; i++) {
        attr = attrs[i];
        value = getValue(attr);
        // any element that matches our semantic rules
        view.find('[role=' + attr + '], [name=' + attr + ']').each(function(i, elem) {
            setValue(elem, value);
        });
    }
}
```

The only assumption ``loadView`` now makes is that the target of the data are
the child elements of ``view``. This is a fine assumption for now.

**Recap:**

- In order to handle various data targets, a layer must be added to abstract
away the operations required for a signal cycle to occur, otherwise data
sources and targets cannot be interchanged.

# 2. Auto-Updating Targets

To prevent from going outside the scope of this article, I am going to
introduce a new data structure for convenience, the [Backbone] [] Model
(merely chosen being I have been working with Backbone quite a bit recently).

[Backbone]: http://documentcloud.github.com/backbone/

The Backbone Model gives us:

- storage for our data
- get/set interface for data attributes
- a simple and clean event system
- tracking data changes

This may sound like a lot, but it's not. We will break down each part.

## Storage

A Model is defined like this:

```javascript
var model = new Backbone.Model({
    title: 'Secrets of a JavaScript Ninja',
    author: 'John Resig',
    pubDate: 'Duke Nukem Forever baby..',
    summary: 'The untold secrets of the elite JavaScript programmers distilled for intermediate JavaScript programmers, bringing them completely up to speed with the challenges of modern JavaScript development. Explores specific techniques, strategies, and solutions to developing robust, cross-browser, JavaScript code.'
});
```

A Model is merely a wrapper for our data. Our simple and familiar looking
raw data lives in ``model.attributes``.

## Get And Set

We already wrote the ``getValue`` for our ``json`` data source. ``Model.get``
is the same thing. ``Model.set`` is the equivalent to our ``setValue`` function,
but for ``model`` rather than a DOM element. Thus we can do this:

```javascript
model.get('author'); // 'John Resig'
model.set({'pubDate': 'March 2012'});
```

## Events

Backbone models have a simple event API including the ``bind``, ``unbind``
and ``trigger`` methods. Event _handlers_ can be registered for an event and
any time that event is triggered, every registered handler executes.

```javascript
model.bind('greet', function() {
    console.log('hello!');
});
model.bind('greet', function() {
    console.log('hola!');
});
model.trigger('greet'); // 'hello!', 'hola!'
model.unbind('greet'); // no more greetings
```

## Tracking Data Changes

This feature depends on the above two features, ``get``/``set`` and
events. Whenever ``model.set`` is executed, for each value that is changed,
a ``change:<attr>`` event is triggered for that attribute.

What this means is that we can attach handlers to those events and they will
only be fired when a value has _changed_, not every time a value is set.

```javascript
// extra arguments are passed in...
model.bind('change:author', function(model, value, options) {
    console.log('changed to "' + value + '"');
});
model.set({'author': 'John Resig'}); // nothing triggered
model.set({'author': 'John Deer'}); // 'changed to "John Deer"'
```

This built-in trigger for data changes removes the need of having to manually
execute ``loadView`` or ``loadViewWithJson`` from the above examples.

**Recap:**

- The Backbone Model class can be used to wrap raw data providing it a useful
API for keeping track of data changes.
- ``Model.set`` conveniently triggers ``change`` events when a data value
changes which provides an avenue for attaching attribute specific handlers
to those events.

# Refactor Using Backbone Models

We can swap out the ``json`` object and replace it with a Model instance:

```javascript
var model = new Backbone.Model(
    title: 'Secrets of a JavaScript Ninja',
    author: 'John Resig',
    pubDate: 'Duke Nukem Forever baby..',
    summary: 'The untold secrets of the elite JavaScript programmers distilled for intermediate JavaScript programmers, bringing them completely up to speed with the challenges of modern JavaScript development. Explores specific techniques, strategies, and solutions to developing robust, cross-browser, JavaScript code.'
});

function getValue(attr) {
    return model.get(attr);
}

// returns all relevent and/or active attributes from the source terminal
function targetAttrs() {
    var attr, attrs = [];
    for (attr in model.attributes) {
        attrs.push(attr);
    }
    return attrs;
}
```

Notice how we didn't have to touch ``loadView``. This is what a layer of
abstraction provides, however the above changes don't show much benefit yet,
until we integrate change handlers to ``loadView``.

For clarity, I am temporarily going to remove the abstraction and simply assume
Model instances will be used.

```javascript
function createChangeHandler(view, attr) {
    return function(model, value, options) {
        view.find('[role=' + attr + '], [name=' + attr + ']').each(function(i, elem) {
            setValue(elem, value);
        });
    }
}

function bindViewToModel(view, model) {
    var attr, value, event;
    for (attr in model.attributes) {
        event = 'change:' + attr;
        handler = createChangeHandler(view, attr);
        model.bind(event, handler);
        // mimic set trigger to populate initial data
        model.trigger(event, model, model.get(attr), {});
    }
}
```

The new ``bindViewToModel`` is very simple. Iterate over each attribute
in ``model.attributes`` and create a change handler for that attribute (a
separate function was created to create the handlers to properly scope
``attr``). Now, every time the ``model`` data changes, the respective
views will be updated.

See all the code here: [http://jsfiddle.net/bruth/z4urM/](http://jsfiddle.net/bruth/z4urM/)

# What's Next?

I am so glad you asked! A couple things are lacking still:

- The view abstraction is poor, but actually not terrible (aside from
form fields, there aren't many other _typical_ ways of interfacing with
a DOM element). There should be more encapsulation and similar APIs like what
Backbone Models provides us (ahem.. Backbone View).
- An extension of the first point, the interface for each DOM element should
be able to be specified. For example ``setValue`` assumes to set the ``innerText``
for non-form fields. What if the data is HTML? ``innerHTML`` should be able to be
specified instead (or at least detected).
- For those with a keen eye, you may have noticed ``bindViewToModel`` depends
on the fact that ``model.attributes`` is filled, meaning if it wasn't, no
elements in the ``view`` would have been bound. Thus we need support for either
dynamically bound views (on every change event, the view is setup for new
attributes) and/or the ability to explicitly define which data attributes to be
setup for ahead of time.

I will be writing a follow-up article addressing most, if not all, of these
issues, as well as posting incremental bits of code on GitHub.
