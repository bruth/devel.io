---
title: Javascript Messaging Patterns - In Practice
layout: post
---

Addy Osmani wrote a very comprehension introduction (book) to
[JavaScript Design Patterns] [1]. This post is not intended to cover general
patterns, but rather hightlight a couple messaging patterns and how they work
and/or apply in a modularized application.

[1]: http://addyosmani.com/resources/essentialjsdesignpatterns/book/

The landscape in JavaScript application development is actually quite clear
these days. Although there seems to be an overwhelming number of new APIs and
techniques to learn to _keep up_ with modern JavaScript development, patterns
typically remain the same in practice.

Messaging
---------
So what exactly do I mean by _messaging_ patterns? Two common messaging patterns
are the [event-driven] [2] and [publish/subscribe] [3] (PubSub) patterns.
JavaScript has an event system built-in to use with the Document Object Model
(DOM). That is, an event _handler_ can be attached to an element and when
some event (action) occurs on or to that element (click, mouse over, focus, etc.),
the event handler is executed.

Pub/Sub is similar in this regard. Rather than an event, a _topic_ is subscribed
to by objects interested in the published content. Other objects may publish 
content for that topic in which case subscribers will receive this content.

[2]: http://en.wikipedia.org/wiki/Event-driven_programming
[3]: http://en.wikipedia.org/wiki/PubSub

They may sound identical aside from _the spelling_, but in practice they are
used in very different contexts.

Events
------
The event-driven pattern is not by any means limited to JavaScript's DOM API.
Many JavaScript libraries impement their own event system for not-DOM
objects. One example is the [Backbone.js events module] [4]. The usually named
suspects of the API include the `bind`, 'unbind` and `trigger` methods. Under
the hood each handler that is bound to a particular event is simply stored in
array for that event. Whenenver that event is triggered, all event handlers
are executed. [Here] [5] are the ~50 minimal lines that make up the entire
event system in Backbone.

[4]: http://documentcloud.github.com/backbone/#Events
[5]: https://github.com/documentcloud/backbone/blob/master/backbone.js#L58-120

The one thing to note with most event-driven systems is that event handlers
are typically bound _directly_ to those objects. Or to put it a different
way, the `bind`, `unbind` and `trigger` methods exist on the objects themselves.

I point this out for two reasons:

- Requiring objects' to have these methods means that not any object is
event-_ready_
- Object methods implies tight coupling, that is, if one object wants to bind
an event handler to three different objects, it must reference those objects

When building large JavaScript applications, using this as your primary
messaging pattern is a choice that will haunt you and your codebase in
your days to come.

PubSub
------
Great. I just ruined your day. So what is the solution? _A_ solution is to
used a more decoupled approach like the PubSub pattern. Rather than having
multiple objects referencing multiple other objects and having a hard
dependency on whether those referenced objects exist or not, a central
_hub_ is used. This hub contains the analogous methods `subscribe`,
`unsubscribe` and `publish`.

The difference?

A single object acts as a message broker for publishers and subscribers.
Publishers simply worry about publishing content, while other objects can
subscribe to topics of interest and receive the published content when
available. The job of the hub is keep track of both ends without requiring
either end be aware of the other.

If an object publishing content throws an exception or fails to load,
it does not break the subscribers since it did not need to directly
reference and _bind_ to the publisher. This enables a much more modular
and decoupled approach to messaging in JavaScript.

In Practice
-----------
So where exactly is the dividing line for these patterns? Working with a full
MVC (or MVVM) on the client seems much more intimidating than server-side
MVC stacks. Why you ask? The DOM. It's really like a 4th layer since it has
it's own APIs and constraints. You _must_ use or interface with it at some
point.

There are roughly three areas where a messaging pattern should be applied.
The lowest level one that _must_ be applied are the DOM event handlers.
There is no getting around it. Luckily we have wonderful libraries like
[jQuery] [6] that abstract away all the misery of dealing with cross-browser
inconsistencies between native DOM APIs.

[6]: http://jquery.com

Most Views (V of MVC) directly reference the DOM element they intend to
represent and attach their own methods as the event handlers for the DOM
events. This is good, abstractions are good.

The Model (M of MVC) side of things acts as the data source or store. This
means that it must interface with the View (and thus the DOM elements) in
some way. Controllers (C in MVC) typically fill that role for a given M-V
pair. For a non-one-to-one relationship between model and view, many
controllers can be defined for various combinations of these objects. In
either direction when a view or model changes it's state
a controller must be notified (or aware) of this change and react
appropriately.

Tight-Coupling
--------------
This is where a lightweight non-DOM event system, like Backbone's, comes
in. Since a controller references particular objects (rather than a type of
object) a tighter coupling may be appropriate in this scenario (though
certainly not required).

_As an aside, Backbone does not have a formal Controller class since the
interface between a view and model tends to be quite minimal. This
functionality can usually be added to the view which reduces the need to
have a third formal object. From now on when you read "controller", it refers
to the controller-like functionality rather than a formal object.
Read more here: http://documentcloud.github.com/backbone/#FAQ-mvc_

Loose-Coupling
--------------
Controllers are all fine and good for local objects (within the same view),
but when we think about an application with multiple blocks of
content and/or functionality on the page interactions between these objects
begin to get very complex.

Think of it this way. Break up your web app into logical sections, i.e. which
parts of the page can stand alone. This is sometimes a hard question to answer
when thinking from an end-user's perspective since the _whole_ page must work. 
Think of it from the stand point that if one of the parts of the page doesn't
load correctly, should it really break the other parts of the page. At varying
degrees that answer will also be no. These logical sections should be able
to function independently of the other sections of the page, period.

Use PubSub.

Having a central object that's sole purpose is to keep track of the content
publishers and subscribers will ensure a very decoupled and more dynamic
implementation of your application. Take a look at my [previous post] [7]
on the PubSub pattern.

[7]: /pub-sub-in-javascript/

Some purists may complain and say.. well now your sprinkling a reference
of the hub everywhere in your application. And I say, this is ok. It is
an essential core object that must exist in order for your app to work.

But, if you really want to go down that road in JavaScript, go write an
[Actor model] [8] implementation.

[8]: http://en.wikipedia.org/wiki/Actor_model
