---
layout: post
title: Backbone Design Pattern, Controller Delegate
---
The guys over at SupportBee <a href="http://devblog.supportbee.com/2011/07/29/backbone-js-tips-lessons-from-the-trenches/">wrote a post</a> (here is the <a href="http://news.ycombinator.com/item?id=2820813">HN submission</a>) about a few of the patterns and conventions they have been following while implementing their app using <a href="http://documentcloud.github.com/backbone/">Backbone</a>. Their post inspired me to write one myself.
## Things to Consider
One of the over simplifications <a href="http://news.ycombinator.com/item?id=2820989">made by some</a> is that Backbone is simply an MVC stack, so one should use it as such. Although true, this <a href="http://news.ycombinator.com/item?id=2821082">doesn't help or infer anything</a> about the implementation of an app _using_ Backbone. I will be using an event-driven approach to explain this particular pattern.
## Model-View-?
Backbone has native support for <a href="http://documentcloud.github.com/backbone/#Model">Models</a> and <a href="http://documentcloud.github.com/backbone/#View">Views</a>, but nothing called a Controller. So why is it considered an MVC stack (the Backbone FAQ doesn't actually consider it to be an MVC <a href="http://documentcloud.github.com/backbone/#FAQ-mvc">in the traditional sense</a>)? Don't fear, a controller is relatively subjective in it's purpose and implementation. After reading, whiteboarding and evaluating, I have come to a relatively simple, yet abstract convention for defining a controller in Backbone. Well.. kind of.
## Layers
One component of an application I am working on has three different models. Each model has a relationship with each other model is some way. Complexity in event-driven programming comes when one tries to consider all possible scenarios for invocation of events for all models.. all at once.
[[posterous-content:kqHzzmsjbHJbyirJfyfn]]
Each model, of course, has a corresponding view class since they are all represented in the DOM. Now, here is where things can get a bit ambiguous. Backbone has this notion of a _Collection_. A collection is simply an ordered set of models that provides a couple convenient hooks for managing, fetching and filtering the models. Well.. so what? It sounds like a glorified array to me.
## Contr..err Collection
All that aside, there is a higher purpose a collection can serve and how we can solve the event-driven complexity woes. It can act as a controller for it's models.. or more specifically a <a href="http://en.wikipedia.org/wiki/Delegation_(programming)">delegate</a> to the models which improves the separation of concerns in your app and overall simplifies it. Likewise, I more or less formalized the notion of a CollectionView in my app as well.
[[posterous-content:GvvnBvrtiaqjFfkxngiH]]
Keeping a pure event-driven approach with a central source of truth e.g. AppState, ensures the event trigger _path_ is deterministic.
## Example
Here is some (incomplete) code for the domain data model (written in CoffeeScript):
```coffeescript
AppState = new Backbone.Model
    domain: null


class Domain extends Backbone.Model
    

class DomainCollection extends Backbone.Collection
    model: Domain

    initialize: ->
        AppState.bind 'change:domain', @changeDomain

    # delegator/controller responsibilities..
    changeDomain: (state, model, options) ->
        if (previous = state.previous('domain'))
            previous.trigger 'deactivate'

        model.trigger 'activate'


class DomainView extends Backbone.View
    events:
        'click': 'click'

    initialize: ->
        @model.bind 'activate', @activate
        @model.bind 'deactivate', @deactivate

    activate: => $(@el).addClass 'active'
    deactivate: => $(@el).removeClass 'active'

    click: -> AppState.set 'domain', @model
    

class DomainCollectionView extends Backbone.View
    el: '#domains'

    initialize: ->
        # some bind to listeners to the collection it represents..
        @collection.bind 'reset', @reset

    add: (collection, model, options) =>
        view = new DomainView
            model: model
        $(@el).append view.render().el

    reset: (collection, model, options) =>
        collection.each @add


domains = new DomainCollection

$ ->
    new DomainCollectionView
        collection: domains

    domains.fetch()
```

Although this only represents a single model, you can see how the Domain model and view mind their own business and do what they need to do in order to reflect the current state of the app with respect to themselves. The ``DomainCollection`` and ``DomainCollectionView`` handles delegating to the domains and views being affected.
Also notice the click handler on the ``DomainView`` sets the ``AppState``'s domain property rather than attempting to manage triggering state changes itself. This is a common mistake when starting out with event-driven programming and dealing with multiple <a href="http://en.wikipedia.org/wiki/Accepting_state#Acceptors_and_recognizers">accepting states</a>. An end-user click is merely a trigger for a state change and should be treated as such. The actualy UI changes will happen at a later stage.
## Watch Out
An idea I kicked around previous to this pattern was to not have a controller (or delegate). This required having a condition in every event handler to test whether the current domain was the domain being evaluated. This also meant that _N_ event handlers would have to fire where _N_ is the number of models in the collection since every model was independely listening for a change on the ``AppState``. This obviously was must less performant than the current solution where a model is only delegated to when necessary.
## Disclaimer
As Jeremy Ashkenas (one of the authors of Backbone) <a href="http://news.ycombinator.com/item?id=2821780">pointed out</a>, there is no single gospel truth. This is merely an approach that has worked for me for this particular use case. I intend to evolve this post as I see necessary to better explain, add more code or to refine the diagrams.
<span style="font-size: x-small;">The diagrams were created using <a href="http://www.linowski.ca/sketching">Linowski Interactive Sketching Notation</a>.
