---
title: Pub/Sub in JavaScript
layout: post
---

I recently [wrote a post]({% post_url 2011-08-01-backbone-design-pattern-controller-delegate %}) about sprinkling various _controller-esque_ functionality in Backbone Collections for acting as the _event hub_ for the items within their respective collections. The one caveat to the example presented is the **tight-coupling** that the ``Domain``, ``SubDomain``, and ``Concept`` have to ``AppState``. While implementing this (in my real project), I became frustrated with needing to specify which objects needed to bind to other objects. The other issue with binding to specific objects _and_ loading data asynchronously from the server is needing to include the event binding (or worse initialization) of objects within AJAX success callbacks of dependent objects. Again, tight-coupling.

[wrote a post]: /backbone-design-pattern-controller-delegate

During my time of frustration I had stumbled upon the [PubSubHubbub protocol] [pubsubhubbub] project page which led me to read up about the [Publish/Subscribe messaging pattern] [pubsubwiki] in general. The pattern is quite simple:

[pubsubhubbub]: http://code.google.com/p/pubsubhubbub/
[pubsubwiki]: http://en.wikipedia.org/wiki/Publish/subscribe

- **Publishers** _publish_ content
- **Subscribers** _subscribe_ to content

But, wait?! That sounds a lot like binding (subscribing) and triggering (publishing) events?

Yes it is similar, but with one exception, subscribers and publishers are completely (and intentionally) unaware of each other. This is accomplished by having a central **Hub** that publishers can publish their content to and subscribers can subscribe to various content **feeds**. Let us modify the points:

- **Publishers** _publish_ content to the **Hub**
- **Subscribers** _subscribe_ to **topics** or **feeds** provided by the **Hub**
- The **Hub** pushes new content out to it's subscribers as it receives it from publishers

Having this central hub_ ensures loose-coupling between various objects that depend on or otherwise may respond to actions invoked by other objects._
This solves the first problem mentioned above, but what about managing asynchrony? One of the known disadvantages with a vanilla pub/sub architecture is it's requirement for subscribers to be online virtually all the time to receive incoming published content. Thus, if a subscriber does go offline, any content published during that time will be missed by the subscriber.

Having a dedicated central hub also gives it the optional capability of queuing published content per topic or feed. This allows for offline or _late_ subscribers to receive published content retroactively from the feed's queue. What this means in JavaScript terms is that subscribers can subscribe to content before or after publishers begin publishing content, thus mitigating the asynchrony issue.

Naturally after learning all of this and listening to <a href="http://thechangelog.com/post/1249379846/episode-0-3-7-pubsubhubbub-with-superfeedrs-julien-genes">a podcast</a> on PubSubHubbub, I felt the urge to write a pub/sub library for JavaScript. A common implementation referenced by many is <a href="https://github.com/phiggins42/bloody-jquery-plugins/blob/master/pubsub.js">one written by Peter Higgins</a>. While simple and clean, it does not have support queuing content.

I wrote a bit more powerful implementation which supports queues and thus late subscribers. It also has support for undoing/redoing content pushes. As first glance, that may sound a bit weird and unnecessary (which to some extent I agree), but it flowed while writing it. I intend to break out the undo/redo API as a separate branch for those who do not need or are uninterested of that extra layer.

Take a look at the repo on GitHub: <a href="https://github.com/bruth/pubsub">https://github.com/bruth/pubsub</a> and the annotated source code <a href="http://bruth.github.com/pubsub/docs/pubsub.html">http://bruth.github.com/pubsub/docs/pubsub.html</a>
