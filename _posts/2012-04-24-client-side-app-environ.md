---
layout: post
title: Client-side App Environment
---

Setting up the base environment for a client-side Web app may make or break your development process. There are a plethora of great client-side libraries, when they be full frameworks, _micro-libs_, or anything in between. Although each library in your stack may be great at what it does, attempting to bundle the libraries together and make them work fluidly can be a non-trivial task.

## Patterns

[Addy Osmani](http://addyosmani.com/blog/) has written "many a guide" regarding various JavaScript patterns, best practices and code modularity. I have read most of them and they all provide great insight as to what your stack should generally look like and how to structure your code. As with most things, the caveat here is which libraries you ultimately choose for your stack. Addy [described](http://addyosmani.com/scalablejs/) and [implemented](https://github.com/addyosmani/backbone-aura) an approach to generalize things a bit. In a nutshell, there are three patterns involved:

- Module
- Facade
- Mediator

The details can be read in his article above, but the bottom line is:

**Modularize your code.** Each self-contained piece should be in a separate file and wrapped in a `define` method.

```javascript
define([/* deps */], function() {
	// expose some functionality of this module
	return {...};
});
```

**Not everything needs or should be exposed to every module.** Using a facade allows for controlling which parts of your stack is actually exposed to the modules. I don't personally use this because I am quite happy with my development stack. In Addy's Q&A section of his article, he articulates why using the facade pattern may not be necessary or appropriate for your project.

**Decouple your code.** Prior to browsers getting incredibly fast, large Web apps were few and far between and certainly not mainstream due to the complexity of the implementations. The rest of us were using jQuery as our means of writing "large-scale" apps. jQuery solves so many problems and we all love using it.

An unfortunate side-effect emerged from having jQuery so ingrained in our heads: _event callbacks are not the best solution_. Why? Large-scale apps usually require a significant number of modules up front, but are typically designed to allow for adding new modules later or integrating external modules. Here is a simple _data-binding_ example:

```javascript
var input = $('input'),
	h1 = $('h1');

input.on('keyup', function() {
	h1.text(input.val());
});
```

An app which requires a responsive UI will have this kind of code **all over** the place. The problem? It doesn't scale.. well. What if there are other parts of the page that need the `input`'s value? We could just shove all of them into the callback, but that means every time we want to add something to the application, we need to edit existing code. **This doesn't scale.**

Rather than having the two objects interact directly, we can use a simple Publisher/Subscriber implementation. This provides a _mediator_ of sorts who keeps track of subscribers of particular messages or topics. When a message is published, it forwards that message to all subscribers. The above code now looks like this:

```javascript
var input = $('input');

input.on('keyup', function() {
	mediator.publish('input-value', input.val());
});
```

Publishers don't (and shouldn't) care who receives the message. On the other end, subscribers can simply do this:

```javascript
var h1 = $('h1');

mediator.subscribe('input-value', function(value) {
	h1.text(value);
});
```

As one can infer, the `mediator` object should be available to all modules to enable seamless message passing. This reduces the complexity of individual modules because other code sources do need to be involved or referenced within the publisher's module.

## Boilerplate Code

A few days ago, I wrote about a few things to consider when building [Asynchronous UIs with Backbone]({% post_url 2012-04-20-async-ui-backbone %}). We can use this code along with a few other defaults for my particular environment.

### CSRF &amp; Ajax

I primarily use [Django](https://www.djangoproject.com/) for my server-side needs and they (of course) have an implementation to [protect against CSRF](https://docs.djangoproject.com/en/1.4/ref/contrib/csrf/). The docs have example JavaScript code, using jQuery, to set the `X-CSRFToken` request header before an Ajax request is sent. Here is a very slightly tweaked version of this which doesn't depend on having a cookie set with the token, but rather looks for a global constant.

```coffeescript
if (CSRF_TOKEN = @CSRF_TOKEN) is undefined
	throw Error 'Global "CSRF_TOKEN" not defined'

# Determines if a URL is of the same origin
sameOrigin = (url) ->
	host = document.location.host
	protocol = document.location.protocol
	sr_origin = '//' + host
	origin = protocol + sr_origin
	(url is origin or url.slice(0, origin.length + 1) is origin + '/') or (url is sr_origin or url.slice(0, sr_origin.length + 1) is sr_origin + '/') or not (/^(\/\/|http:|https:).*/.test(url))

# Simple check for whether a request method is safe
safeMethod = (method) ->
	/^(GET|HEAD|OPTIONS|TRACE)$/.test method

$(document).ajaxSend (event, xhr, settings) ->
	# For all same origin, non-safe requests add the X-CSRFToken header
	if not safeMethod(settings.type) and sameOrigin(settings.url)
		xhr.setRequestHeader 'X-CSRFToken', CSRF_TOKEN
```

### Ajax Request Management

As described in my [previous post]({% post_url 2012-04-20-async-ui-backbone %}), here is the finished code with a DOM element for displaying the status of the requests.

```coffeescript
# Ajax states
LOADING = 'Loading'
SYNCING = 'Syncing'
SAVED = 'Saved'
OFFLINE = 'Offline'
ERROR = 'Error'

STATUS = null

MAX_ATTEMPTS = 3
ATTEMPTS = 0

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

# GET requests are processed independent of the queue, all other
# requests are queued up.
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

# Execute a request, retry on timeouts up to MAX_ATTEMPTS. When
# complete (error or success), process the next request.
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


syncStatus = null

$ ->
	syncStatus = $('#sync-status')
	
	# Handle a few common cases if the server if there are still pending
    # requests or if the max attempts have been made.
    $(window).on 'beforeunload', ->
        if Backbone.ajax.pending
			if ATTEMPTS is MAX_ATTEMPTS
				return "Unfortunately, your data hasn't been saved. The server
					or your Internet connection is acting up. Sorry!"
			else
				syncStatus.fadeIn(200)
				return "Wow, you're quick! Your stuff is being saved.
					It will only take a moment."

	$(document)
		.ajaxSend (event, xhr, settings) ->
        	type = (settings.type or 'get').toLowerCase()
            if type is 'get'
               syncStatus.text LOADING
			else
				syncStatus.text SYNCING

		.ajaxStop ->
			visible = syncStatus.is(':visible')
			# Show the current state if the max attempts have been reached
			if ATTEMPTS is MAX_ATTEMPTS and not visible
				syncStatus.fadeIn(200)
			else if visible
				syncStatus.fadeOut(200)

		.ajaxError (event, xhr, settings, error) ->
			# On any error, show the status
			if error is 'timeout'
				syncStatus.text OFFLINE
			else if xhr.status >= 500
				syncStatus.text ERROR

```

### Defend Against Redundant Requests

Use the [debounce function](http://documentcloud.github.com/underscore/#debounce) to roll up redundant event handler executions.

```coffeescript
class Model extends Backbone.Model
    initialize: ->
        @on 'change', _.debounce =>
            @save()
        , 500
```
