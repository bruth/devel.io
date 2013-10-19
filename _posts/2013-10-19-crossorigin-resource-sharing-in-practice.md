---
layout: post
title: "Cross-Origin Resource Sharing in Practice"
permalink: "cors-in-practice"
---

This is a quick summary of what is required by the client and server for CORS with credentials.

## Server

At a minimum, your server needs to set these headers on the responses:

```
Access-Control-Allow-Origin: http://example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE
Access-Control-Allow-Headers: accept, content-type
Access-Control-Allow-Credentials: true
```

If the request origin is allowed, `Access-Control-Allow-Origin` must contain the host. A value of `*` is allowed, but an explicit host is required when used in combination with `Access-Control-Allow-Credentials`.

The `Access-Control-Allow-Methods` contains the methods that are allowed to be requested by the client. In pre-flight requests, the client may send a `Access-Control-Request-Method` header which specifies the method the follow-up request will be.

`Access-Control-Allow-Headers` must contain the headers that are allowed to be sent in the request. Fortunately, browsers send a `Access-Control-Request-Headers` header which contains the request headers the client wants to send in the request. If the server doesn't care which headers are allowed, this can simply be echoed back in `Access-Control-Allow-Headers`.

The `Access-Control-Allow-Credentials` allows the client to send [user credentials](http://www.w3.org/TR/access-control/#user-credentials) i.e. "cookies, HTTP authentication, and client-side SSL certifciates". Note, if the server does not want to support user credentials, this header should be omitted.

## Client

_This assumes you are using jQuery 1.5.1+._ When sending an XMLHttpRequest, the `withCredentials` flag must be set to have the browser send credentials in the request. As noted above, if the `Access-Control-Allow-Credentials` header is not present, the browser will complain.

```javascript
$.ajax({
    ...
    xhrFields: {
        withCredentials: true
    }
});
```

For a more transparent way to ensure these settings are defined for outgoing requests, register an Ajax prefilter to augment the settings prior to the request being sent out:

```javascript
$.ajaxPrefilter(function(settings) {
    settings.xhrFields = {
        withCredentials: true
    };
});
```

_**Internet Explorer Caveat.**  CORS support prior to version 10 is limited.. meaning it won't work in most cases._
