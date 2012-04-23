---
title: Introducing django-restlib And The Refactor To Come
layout: post
---

---

**UPDATE [09-21-2011]**: The RESTlib repository has been moved to GitHub: [https://github.com/bruth/django-restlib](https://github.com/bruth/django-restlib)

---

Over the past few months, I have developed a library to make it easier to create class-based "resource" APIs adhering to the HTTP spec closely (though much work is needed). There are quite a few active libraries available that provide a framework to build RESTful APIs including [django-piston] [], [django-tastypie] [], and [django-rest-framework] [].

My tendency to adopt existing libraries is heavily dependent on the appearance and structure of the source code (yes, I judge) and how quickly I can understand how to write something more complicated than the "Hello World!" examples in the tutorial. I want flexibility where appropriate in the API as well as sensible defaults for those things I don't want to think about up front.

[django-piston]: https://bitbucket.org/jespern/django-piston
[django-tastypie]: https://github.com/toastdriven/django-tastypie
[django-rest-framework]: https://bitbucket.org/tomchristie/django-rest-framework/

## A bit more diverse than one thinks
There are a few contexts that come to mind when handling an HTTP request (the term "method" below refers to HTTP methods):

- method-independent checks (authentication, authorization, Content-* headers, etc.)
- method-dependent conditions (method allowed?, entity body checks, Content-Type, Accept-*, etc.)
- resource-dependent tests (resource exist? or moved? or conflict? or cached?)

There are quite a few steps when handling an HTTP request, but depending on the resource some of these conditions may or may not apply. Many of these frameworks (again I skimmed) handle the high-level concepts when creating web APIs like auth/authz, caching, and serialization, but the sequence of evaluation of the request is hidden within the implementation of the library. Quick and (really) dirty APIs can easily be thrown together in this fashion (and in many cases will suffice), but the granularity and care given to the definition of a resource is limited.

## The State of the RESTlib (it really needs a better name)
Currently [RESTlib] [] has only a few features implemented the above libraries already provide. The notable ones include:

[RESTlib]: https://bitbucket.org/bruth/django-restlib/src/3507935583eb

- Resource, ModelResource, ResourceCollection and ModelResourceCollection classes (uses metaclasses internally)
- Representation classes that are registered with particular mimetypes
- canonical resources that are used by other "referencing" resources
- model instance resolution

### Resources and Collections

> Although I am using the term _collection_, it still is it's own resource by definition. The class is defined only to provide a conceptual differentiation between some resource and a collection of resources of the same _type_.

There are four classes, two of which are merely convenience classes for Django models. For all resources, class methods can be defined representing the HTTP methods the resource supports. Currently, what one does within these methods is typically only dealing with operations the HTTP method implies for the given resource, i.e. not usually dealing with HTTP response codes directly. Unfortunately, though, there are cases when the line is blurred between resource evaluation and returning the appropriate status code for non-successful requests.

### Representations
A _Representation_ class is pretty much equivalent to TastyPie's serializers or Piston's emitters. Very simply, representation classes are associated with a particular mimetype (defined by the 'Content-Type' and 'Accept' headers) which can define an ``encode`` and ``decode`` method. On incoming requests, the 'Content-Type' is evaluated (if it exists) and determined whether the mimetype is supported for that resource and if a representation class is available to decode the request body. Likewise, the 'Accept' header is evaluated and determined if the resource supports the requested encoding for the response body.

### Canonical Resources
In many cases (especially with relational content) resources will reference other resources such as the author of a blog post (yes, I know, blog examples are way overused). The way the reference is represented in a resource is dependent on how the content will be consumed by the majority of clients. The three content representations include:

- some sort of key (primary key or natural key)
- a URL to the author's resource (HATEOAS)
- the author's resource content directly embedded in the blog post content

Defining a canonical resource allows for easily cross-referencing resources without needing to redefine the resource's content.

### Model Instance (and QuerySet) Resolution
For ModelResources and ModelResourceCollections, any model instances or QuerySets that are returned for response will be resolved and converted into a simple Python data structure (that then will be encoded by the requested representation).

## Refactor Ideas
As I am reviewing my arbitrarily constructed ``__call__`` ([source][]) method, the request processing modularity becomes quite obvious and should be broken down into individual request handling _hooks_. Why _hooks_? Well I don't have a better word for it at the moment.

[source]: https://bitbucket.org/bruth/django-restlib/src/3507935583eb/restlib/http/resources/base.py#cl-196
Very simply each hook will be a class that defines a _process_ method (again, an arbitrary name). Each hook class also has an HTTP status code associated with it. When the request is being processed, it either passes or fails. An HTTP response with that status is returned by the resource if the request hook fails otherwise the request processing continues. The resource itself and the request are passed into the process method. Information can be augmented on the request object for downstream hooks to take into account.

For each resource, a list of hooks can be defined based on the resources' needs:

- public APIs may require authentication, but not authorization, but may limit the representations of the data to only certain encodings
- private APIs may require auth and/or authz such as a username and password (basic auth) or an API token (such as with OAuth)
- certain resources may need to be cross-domain ready in order for browsers' <a href="https://developer.mozilla.org/en/HTTP_access_control">pre-flight requests</a> succeed
- only requests with an ``X-Requested-With: XMLHttpRequest`` header will be accepted

The sequence of evaluation is also important since by doing certain things in a particular order (e.g. checking if the method is supported before checking if the requesting user is authorized to act on the resource) may provide varying insight to the capabilities of the resource to the client. In one case, testing the method first and failing early may prevent a database hit, but may uncover information about that resource (that is does not support a certain method) to a non-authorized client. By defining a list of request hooks that get sequentially applied to the request will ensure only the necessary processing is being performed for that resource and in the appropriate order.

## Onward
These concepts will mature once some code is written, but I do believe this approach will provide a much more flexible and powerful interface for defining resources without giving up simplicity.

_Have any thoughts on this? I will be at <a href="http://us.pycon.org/2011/home/">PyCon</a>, so email me or track me down to discuss._
