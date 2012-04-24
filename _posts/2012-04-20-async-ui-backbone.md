---
layout: post
title: Async UIs with Backbone
---

Alex MacCaw wrote an article on strategies for building [asynchronous UIs](http://alexmaccaw.com/posts/async_ui).
He argues that perceived speed is what ultimately is important for users. I agree. Since we
are dealing with asynchronous requests on the client, the UI can update independently
of what happens on the server. A few things need to be handled when the user _drives_ the
updates on the page:

1. Prevent the [lost update](http://en.wikipedia.org/wiki/Concurrency_control#.27Why_is_concurrency_control_needed.27.3F) problem
2. Prevent pending requests from being aborted
3. Prevent redundant requests

I've adapted and expanded on his concepts (and some of his code from [Spine](http://spinejs.com/))
to [Backbone](http://backbonejs.org/).

## Process Ajax requests serially

To handle the first point, a generic solution could involved sending async requests serially. That is, async requests are not sent in parallel.

_The code below requires Backbone as of commit [87c9b17a](https://github.com/braddunbar/backbone/commit/87c9b17aa722fb3d6b34d5b92c564eeba5516334) which uses `Backbone.ajax` rather than `$.ajax` in the `Backbone.sync` method._

```coffeescript
# Cache Backbone ajax function, by default, which is $.ajax by default
_ajax = Backbone.ajax

# Override Backbone.ajax to queue all requests to prevent lost updates.
Backbone.ajax = (options) ->
    @ajax.queue options

Backbone.ajax.pending = false
Backbone.ajax.requests = []

# Process the next request if one exists
Backbone.ajax.requestNext = ->
    if (next = @requests.shift())
        @request(next)
    else
        @pending = false

# Sends the request and sends the next request when complete
Backbone.ajax.request = (options) ->
    complete = (xhr, status) =>
        if options.complete then options.complete(arguments)
        @requestNext()

    options.complete = complete
    _ajax(options)

# Queue up requests
Backbone.ajax.queue = (options) ->
    if @pending
        @requests.push options
    else
        @pending = true
        @request options
```

### Hmm, what about `GET` requests?

`GET` requests are safe, so I prefer them to not be queued and be sent in parallel to the requests in queue (`PUT`, `POST`, etc.). Here is the modified `queue` method and a slightly modified `request` method to prevent processing the queue.

```coffeescript
Backbone.ajax.queue = (options) ->
    # If type is undefined, it defaults to GET
    type = (options.type or 'GET').toUpperCase()

    if type is 'GET'
        @request options, false
    else if @pending
        @requests.push options
    else
        @pending = true
        @request options

Backbone.ajax.request = (options, trigger=true) ->
    complete = (xhr, status) =>
        if options.complete then options.complete(arguments)
        if trigger then @requestNext()

    options.complete = complete
    _ajax(options)
```

### What about timeouts?

Timeouts should rarely occur, but if they do it's nice to have a _retry_ mechanism in place. This is applied in the `complete` handler and uses `_ajax` directly (derived from [this example](http://www.zeroedandnoughted.com/?p=185)).

```coffeescript
MAX_ATTEMPTS = 3
ATTEMPTS = 0

Backbone.ajax.request = (options, trigger=true) ->
    complete = (xhr, status) =>
        if status is 'timeout'
            if ATTEMPTS < MAX_ATTEMPTS
                ATTEMPTS++
                return _ajax(options)

        if options.complete then options.complete(arguments)
        if trigger then @requestNext()

    # Each new request from the queue will reset the number of attempts
    # that have been made.
    ATTEMPTS = 1

    options.complete = complete
    _ajax(options)
```

## Prevent pending requests from being aborted

Using the code from above, we can check if there are pending (non-`GET`) requests. For the off chance a user _beats the server_, this ensures they are
aware of it. Attach a handler to `window`'s [onbeforeunload](https://developer.mozilla.org/en/DOM/window.onbeforeunload) event.

```coffeescript
$(window).on 'beforeunload', ->
	if Backbone.ajax.pending
		return "Whoa you're quick! We are saving your stuff, "
			"it will only take a moment."
```

## Prevent redundant requests

To have a truly responsive UI, `click` and `keyup` events are typically bound to provide immediate feedback to the user. A common example is editing a value in a input field which is being displayed in some other element on the page. As the user changes the value in the text input, the other element is updating immediately. This provides a nice user experience, but if naively handled, this could result in a whole lot of unnecessary requests.

[Debounce](http://unscriptable.com/2009/03/20/debouncing-javascript-methods/) is a function wrapper that rolls up multiple invocations of the same function and defers execution of the function after some amount of time. Here is a common Backbone pattern:

```coffeescript
class Model extends Backbone.Model
	initialize: ->
		@on 'change', @save
```

This is pretty self-explanatory, but may be a poor solution when data is constantly changing. Using the debounce function ([Underscore](http://documentcloud.github.com/underscore/) conveniently has [an implementation](http://documentcloud.github.com/underscore/#debounce), our code now looks like this:

```coffeescript
class Model extends Backbone.Model
	initialize: ->
		@on 'change', _.debounce =>
			@save()
		, 500
```

In this case only the last `change` event matters. After 500 milliseconds pass, the function will execute calling the `@save` method.

This solution is great because it does not interfere with the `change` event directly and allows for other handlers (that are not debounced) to be executed immediately, such as updating the UI.

```coffeescript
# An input field may be constantly setting a value on the bound model
class Input extends Backbone.Model
	events:
		'keyup': 'update'

	update: ->
		# The change event is fired on every set that alters the value
		@model.set 'title', @$el.val()

#... while an H1 element is displaying a value elsewhere
class H1 extends Backbone.Model
	initialize: ->
		# Executes render immediately which updates the UI immediately
		@model.on 'change:title', @render
	
	render: =>
		@$el.text @model.get 'title'
```

### More TODO

- Handle response errors, should the queue continue to be processed?
- Implement logic for having separate queues for different endpoints. This enables passing a `greedy` option to not wait for the whole queue, but rather simply wait for it's own queue to finish.
