---
layout: post
title: Async UIs with Backbone
---

#### Ajax queue for pending requests

_TODO implement logic for having separate queues for different endpoints. This enables passing the `greedy` option for not wait for the whole queue, but rather simply wait for it's own queue to finish._

```coffeescript
# Override `Backbone.ajax` to queue all requests.
# Cache Backbone ajax function, by default, just $.ajax
_ajax = Backbone.ajax

# Override Backbone.ajax to queue all requests to prevent
# lost updates. Inspired by @maccman's Spine implementation.
Backbone.ajax = (options) ->
    @ajax.queue options

Backbone.ajax.pending = false
Backbone.ajax.requests = []

Backbone.ajax.requestNext = ->
    if (next = @requests.shift())
        @request(next)
    else
        @pending = false

Backbone.ajax.request = (options, trigger=true) ->
    _ajax(options).complete =>
        if trigger then @requestNext()

# For GET requests, the order is not terribly important.
# The `pending` flag is not set since it does not deal with
# saving changes to the server. This prevents observers from
# blocking navigation due to a GET request.
Backbone.ajax.queue = (options) ->
    type = (options.type or 'get').toLowerCase()
    if type is 'get'
        @request options, false
    else if @pending
        @requests.push options
    else
        @pending = true
        @request options
```

#### Bind `window.onbeforeunload` to prevent pending requests from being aborted

Using the code from above, we can check if there are pending (non-GET) requests. For the off chance a user _beats the server_, this ensures they are aware of it.

```coffeescript
$(window).on 'beforeunload', ->
	if Backbone.ajax.pending
		return "Whoa you're quick! We are saving your stuff, "
			"it will only take a moment."
```

#### Use [debounce](http://unscriptable.com/2009/03/20/debouncing-javascript-methods/) for controlling the flow of events	

In conjunction with Backbone's `change` events, a model or collection can be _saved_ on each event. Using debounce prevents having multiple redundant saves from ocurring within a particular time frame.

An example is firing a model `change` event on every `keyup` when a user is filling out a form. The `change` event can invoke UI updates (via a view), but the handler that will ultimately save the data can be deferred until the end.

```coffeescript
class Model extends Backbone.Model
	initialize: ->
		@on 'change', _.debounce =>
			@save()
		, 500
```
