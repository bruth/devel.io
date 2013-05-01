---                                                                             
layout: post                                                                    
title: "Model-View Synchronization (or not)"
summary: "Strucuturing large scale client-side apps is itself a challenge. Another challenge can be determining when models and view should be initialized or when views should be rendered. This post addresses these questions with a few of my best practices."

---

There are plenty of great resources and guides out there to follow when structuring a large client-side web application. In fact I feel that I have gotten quite good at structuring my projects. However, a reoccurring set of questions always pop into my head when determining _when_ and _how_ to initialize various components:

- when should models and collections be initialized?
- should this happen before views are initialized?
- when should the model and collection be fetched?
- when should views get initialized?
- when should views get rendered?
- when should views get injected into the DOM (if they aren't already)?

The caveat to many of these questions is, _it depends_. Different applications have, of course, different requirements, but I've determined a few guidelines to follow.

### When should models and collections be initialized?

They should be initialized right away since they are the driving force (and data) behind your views (note, I didn't say the data should be fetched or loaded into the model/collection.. keep reading).

### Should this happen before views are initialized?

Yes. Yes. _Yes._ Why? Models and collection and data drive the view's content and state to some extent. Views need to be able to reference their corresponding models and collections in order to `listenTo` their events.

Although I felt the need to repeat _yes_ three times above, this approach isn't the whole story. There are [other](http://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) [patterns](http://www.html5rocks.com/en/tutorials/async/deferred/) that can be used to prevent needing to reference objects directly. However, in practice references typically work just fine and in fact the other approaches are complementary rather than strict alternatives.

Read more below in the **When should views get rendered?** section.

### When should the model and collection data be fetched?

When it needs to be. No seriously. There should be no requirement that data exists are the page or at any point in time **prior to anything else happening**. This a big _faux pas_ when it comes to thinking about the model-view architecture.

_Why?_

Because data will be slow to load or completely fail to load. Assuming data will be present introduces [race conditions](http://en.wikipedia.org/wiki/Race_condition) in your code which means the condition is [non-deterministic](http://en.wikipedia.org/wiki/Nondeterministic_algorithm) which means there is no guarantee the app will work consistently.

### When should views get initialized?

When they need to be. If you _know_ which views need to be rendered up front, you can initialize them right after the models and collections and set up any necessary references between them.

For views that get loaded later, well.. they will be initialized later.

### When should views get rendered?

Immediately or when it's ready to be injected.

To take a step back to the initialization phase, a view should not assume it will be initialized with a model/collection that already contains (or does not contain) data. It should be implemented to **work with what it has** and respond to changes when they occur. A common mistake is as follows:

```javascript
var MyView = Backbone.View.extend({
    initialize: function() {
        // keep the view up to date!
        this.listenTo(this.model, 'change', this.render, this);
    },

    render: function() {
        // fancy rendering base on model data..
        ...
    }
});

// Initialize with the model of interest
var view = new MyView({
    model: model
});

// Insert into the DOM
$('body').html(view.el);
```

So what's the issue? `view.render()` wasn't called. This subtle mistake is due to an assumption that "once `model` fires it's change event, _it_ will call `render`, so I don't have to".

**Wrong.**

Render the view. Always. If you are thinking to yourself "but data may be missing and it won't render correctly", then your `render()` method is broken.

If you always assume data is never guaranteed to be present, you will have better _default/empty_ representations of your views which will make your users happier.

### When should views get injected into the DOM?

Assuming your fetching data from the server and assuming you don't want your user to see a blank screen, the earlier the view gets injected into the DOM (with an excellent default/empty representation) the better.

**However.**

Once the view's model data is _ready_, build a [DOM fragment](http://ejohn.org/blog/dom-documentfragments/) in memory then inject or replace the contents of the view in one step. Manipulating lots of elements while already in the DOM is slow, but the greater concern is the poor responsiveness the user may experience when using the app while the rendering is occurring.

## What does it all mean?

Although I described many assumptions you _should not_ have, here are ones you _should_ have (and other advice):

- Never assume data is available
- Never wait for data to render
- Always assume the data you _do_ have is all you're getting
- Test re-rendering views with twice as much data you think you will have when rendering a view
    - this primarily applies to collection-based views of lists or tables
