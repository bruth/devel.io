---
layout: post
title: Backbone Ajax Queue
---

**This is an update to an article I previously wrote about [Async UIs with Backbone]({% post_url 2012-04-20-async-ui-backbone %}).**

The one glaring issue with this queue implementation is not having the _deferred_ object returned from `Backbone.ajax`. We can fix this by creating a deferred object that acts as a proxy to the `xhr` object when the Ajax request is sent.


```coffeescript
# Cache Backbone ajax function, which is $.ajax by default
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

Backbone.ajax.request = (_options, proxy, trigger=true) ->
    options = _.extend {}, _options

    # Reference existing handlers
    success = options.success
    error = options.error
    complete = options.complete

    params =
        complete: (xhr, status) =>
            if status is 'timeout'
                # If this does not pass, this is considered a failed request
                if ATTEMPTS < MAX_ATTEMPTS then return _ajax params
            else if 200 <= xhr.status < 300
                if complete then complete.apply @, arguments
                if trigger then @requestNext()
            else
                # Last resort, ensure this is turned off
                @pending = false

        success: ->
            if success then success.apply @, arguments
            proxy.resolveWith @, arguments

        error: (xhr, status, err) ->
            if status is 'timeout' and ATTEMPTS < MAX_ATTEMPTS
                ATTEMPTS++
            else
                if error then error.apply @, arguments
                proxy.rejectWith @, arguments

    # Each new request from the queue will reset the number of attempts
    # that have been made.
    ATTEMPTS = 1

    params = _.extend options, params

    # Add custom complete for handling retries for this particular
    # request. This ensures the queue won't be handled out of order
    _ajax params


Backbone.ajax.queue = (options) ->
    # If type is undefined, it defaults to GET
    type = (options.type or 'GET').toUpperCase()

    # Since requests are being queued, the `xhr` is not being created
    # immediately and thus no way of adding deferred callbacks. This
    # deferred object acts as a proxy for the request's `xhr` object.
    proxy = $.Deferred()

    if type is 'GET'
        @request options, proxy, false
    else if @pending
        @requests.push [options, proxy]
    else
        @pending = true
        @request options, proxy 

    return proxy
```
