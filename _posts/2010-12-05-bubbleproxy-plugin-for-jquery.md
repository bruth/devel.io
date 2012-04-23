---
title: BubbleProxy Plugin For jQuery
layout: post
---

---

**UPDATE [09-21-2011]**: This library has been deprecated. Ultimately bubbling up the DOM is [terribly inefficient](http://weblog.bocoup.com/publishsubscribe-with-jquery-custom-events). Read [this Pub/Sub post](/pub-sub-in-javascript/) instead. I also wrote a simple Pub/Sub implementation in JavaScript to address this need for de-coupling modules on the page: [https://github.com/bruth/synapse](https://github.com/bruth/synapse)

---

## Preface
Many people have been hopping on the <a href="http://www.sproutcore.com">SproutCore</a> <a href="http://bit.ly/hBFgb9">bandwagon</a> recently. I have two opposing viewpoints. One being that SproutCore is a seemingly excellent framework that has been elegantly designed to have true separation of concerns between the Model, View and Controller layers that ultimately reduces "spaghetti code". For many projects it seems to be a great solution (note that I am prefacing my statements with the word "seems" or "seemingly" since I have don't have enough experience with creating projects using SproutCore).

That being said, the documentation is terrible. Well I should be fair, it _may_ not be terrible, but I don't know which <a href="http://docs.sproutcore.com/">one</a> <a href="http://www.sproutcore.com/static/sc_docs/">of</a> <a href="http://wiki.sproutcore.com/">these</a> doc references are actually the correct one. The wiki (the last link) seems to have the most recent pieces of documentation, but the pages are riddled with references to SproutCore 1.0 and the current version is 1.4.4. The other two doc references shows that they were auto-generated long ago in January 2010 and August 2008 (o.O), respectively.

I attempted to take on the challenge of converting an existing large project by reading the source and gradually learning the ins and outs as I go (which in some cases I prefer), but time quickly became a luxury and it became impractical to convert.

## BubbleProxy
Now to the point of the post. Even though I have issues with the docs and overall adoption of the framework for my normal development, I still do find it very intriguing and having some clever design principles.

<a href="http://yehudakatz.com/">Yehuda Katz</a> gave a <a href="http://blog.sproutcore.com/post/1711425620/first-san-francisco-meetup-in-a-long-time-yehuda">talk</a> regarding a project he has been called Amber and some general SproutCore examples. His primary example was based on the Twitter interface and how there are many different sections of the page that may be depend on each other in some way (e.g. if you add a follower from the "Suggestions" section, not only does the avatar need to be removed from "Suggestions", but it needs to be added to the "Following" section). The typical way to handle this situation is to write an event handler for the click event that trigger the handlers for all the sections that need to be "aware" that the event has occurred.

```javascript
$('.follow-links').click(function(evt) {
    // do stuff relative to this link
    
    // remove element from suggestions

    // add element to following
});
```

My neurotic tendency to constantly rename classes and change the layouts of web apps has led me to realize that maintaining event handlers and the references to all the objects that need to be altered as a result of an event is obnoxious and not practical.

I wanted a more generic way of having an event be triggered and for other elements to merely listen for those events. That is, if a 'click' event occurs somewhere on the page, that 'click' event can be propagated not only up through the ancestors (via bubbling) but proxied to arbitrary locations on the page. Here is the basic API:

```javascript
$.bubbleproxy({
    click: {
        listeners: ['#suggestions', '#following']
    }
});
```

The object that gets passed in has event types for keys (e.g. 'click', 'custom', 'custom.namespaced') and a list of listeners of that event. This can be read as, "for any click event that occurs, trigger the event handlers bound to #div1 and #div2".

One should note that the above example is pretty impractical in terms of having a "click" event being proxied to multiple listeners. This is much more suitable for custom events such as:

```javascript
$.bubbleproxy({
    follow: {
        listeners: ['#suggestions', '#following']
    }
});

$('.follow-links').click(function(evt) {
    $(this).trigger('follow');
});

$('#suggestions').bind('follow', function(evt) {
    // remove from suggestions
});

$('#following').bind('follow', function(evt) {
    // add to following
});
```

As shown above, a convention of mine is to separate out the events that drive the behavior of the app as custom events that are implicitly triggered by a user event (or a different custom event). The structure of the above code insinuates the ease of writing completely independent event handlers for each of the elements.

## How Does It Work
The first phase is "bubbling", not different than any other normal event bubbling. That is, the target that triggered the event bubbles the event up the DOM tree. Behind the scenes, ``bubbleproxy`` uses the ``body`` tag as the "catch-all" element; this of course can be changed either by passing a second argument (CSS selector) to ``$.bubbleproxy`` or by using the ``$(...).bubbleproxy`` signature.

The second phase is "proxying" the event to all the listeners. The event handlers for the given event are triggered for each listener and maintains the originating ``event.target`` element (the target of the event). Thus, there is the effect that the listeners received the event trigger via normal bubbling.
Check out the source code and an example: <a href="https://bitbucket.org/bruth/jquery-bubbleproxy">https://bitbucket.org/bruth/jquery-bubbleproxy</a>. Please feel free to provide feedback.
