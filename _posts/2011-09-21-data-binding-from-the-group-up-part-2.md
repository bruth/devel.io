---
title: Data Binding From The Ground Up, Part II
layout: post
---

_Follow along with the examples on jsFiddle: [http://jsfiddle.net/bruth/nGBVh/](http://jsfiddle.net/bruth/nGBVh/)_

This is a continuation from [the first article]({% post_url 2011-09-20-data-binding-from-the-ground-up %})
on writing a data binding implementation in JavaScript.

To review where we left off, here are the outstanding issues left over from
the initial article:

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
- Migrate element binding to use the more common ``data-bind`` attribute by
default, but provide the option to define alternate means of _targeting_ the
elements.

# State Of The Code

Note this has been updated to use ``data-bind`` by default per update from
[the first article]({% post_url 2011-09-20-data-binding-from-the-ground-up %}).

```javascript
function setValue(elem, value) {
    elem = $(elem);
    if (elem.is('input, textarea')) {
        elem.val(value);
    } else {
        elem.text(value);
    }
}

function createChangeHandler(view, attr) {
    return function(model, value, options) {
        view.find('[data-bind=' + attr + ']').each(function(i, elem) {
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

Thus given a template:

```html
<div id="detail-template">
    <h1 data-bind="title"></h1>
    <em>Published by <span data-bind="author"></span> on <span data-bind="pubDate"></span></em>
    <div data-bind="summary"></div>
</div>
```

and some data:

```javascript
var data = {
    title: 'Secrets of a JavaScript Ninja',
    author: 'John Resig',
    pubDate: 'Duke Nukem Forever baby..',
    summary: 'The untold secrets of the elite JavaScript programmers distilled for intermediate JavaScript programmers, bringing them completely up to speed with the challenges of modern JavaScript development. Explores specific techniques, strategies, and solutions to developing robust, cross-browser, JavaScript code.'
};
```

we can have an auto-updating view:

```javascript
var model = new Backbone.Model(data);
var detailView = $('#detail-template');

bindViewToModel(detailView, model);
```

Great! Let's move on.

# Encapsulation and Common API

Up to this point, it has been assumed our _view_ is a document fragment (or
single element). Going back to the original definition of per
[Wikipedia](http://en.wikipedia.org/wiki/Data_binding):

> Data binding is a general technique that binds two data/information sources
together and maintains synchronization of data. --Wikipedia

A view is one type of data source, but what if the _other_ data source
was a second``Backbone.Model`` instance? Our ``bindViewToModel`` breaks down
slightly in that ``createChangeHandler`` is a fixed function that assumes
handling our traditional view.

The end goal of this is not having to worry about which two sources are
interfacing, only that they are able to. Based on the current types we
support, we can create interfaces for them.

- ``ModelInterface`` - interface for ``Backbone.Model`` instances
- ``ElementInterface`` - interface for DOM elements (via jQuery)
    - ``InputInterface`` - sub-interface specific to ``input``-like elements
    - ... other specialized element interfaces
- ``FragmentInterface`` - sort of a pseudo-interface since it's merely a proxy
    for it's descendent elements (we have been doing this for all examples
    up to this point).
- ``ViewInterface`` - something new, the interface for ``Backbone.View``
    instances which encapsulate some DOM element. This also is basically a
    proxy to either ``FragmentInterface`` or ``ElementInterface``

An interface must be able to perform certain operations including the ability
to notify when it's data changes and the ability to observe other sources' data.
A high-level interface _stub_ may look like this:

```javascript
var InterfaceStub = {
    notify: function(interface, ...) {
        // .. sets up a communication channel from this interface to the target
        // 'interface'
    },

    observe: function(interface, ...) {
        // .. sets up a communication channel from the target 'interface' to
        // to this interface
    }
};
```

These two methods are conceptually identical with the exception of
directionality, thus we should be able to do this:

```javascript
// hypothentical interface classes for the sake of example
var modelInt = ModelInterface(model),
    fragInt = FragmentInterface(detailView);

// functionally equivalent
modelInt.notify(fragInt);
fragInt.observe(modelInt);
```
