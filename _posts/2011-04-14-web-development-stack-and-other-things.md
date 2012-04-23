---
layout: post
title: Web Development Stack And Other Things
---

The web provides a very unique environment to develop in due to the numerous layers it has. At a fundamental level, there is a client and a server, but there can be many layers within both the client and server individually.

I intend this to be an evolving collection of notes on various programming languages, libraries, concepts and implementation details that I use (or would like to eventually use) for the projects I have worked on.

## Server

### Python
My language of choice is <a href="http://python.org/">Python</a>. Python is a dynamic scripting language that has an incredible standard library and a plethora of third-party libraries available. Development time is short due to it's terseness and simple grammar, yet since Python requires whitespace for indentation your code stays clean and readable.

### Django
I use the <a href="http://www.djangoproject.com/">Django</a> web framework as the foundation to many of my web sites and web applications. It has a very active community and the codebase is constantly improving.

### PostgreSQL
<a href="http://www.postgresql.org/">PostgreSQL</a> is my relational database of choice. I have used MySQL in the past and haven't had too many issues (that is, after I realized how to enable transactions...), but my gut tells me Postgres is simply better. Oracle is expensive. SQL Server is a Microsoft product (though it is one of there better ones). SQLite is excellent for quick setups and testing, but not suitable for database-heavy applications.

### MongoDB

I have very little experience in this area, but from the limited usage (and a lot of reading), <a href="http://www.mongodb.org/">MongoDB</a> seems to be a pretty solid non-relational database. 10gen seems to be very serious about improving the speed and scalability of it and the query API is very solid.
## Client

### jQuery
I don't need to say much about this special JavaScript library.. since it's the most widely used on on the Web, but I want to ensure <a href="http://ejohn.org">Resig</a> and the <a href="http://jquery.com">jQuery</a> team get all the praise they deserve.

### RequireJS
When the amount of JavaScript gets to be significant for a given project, modularizing code quickly becomes necessary for maintainability. <a href="http://requirejs.org/">RequireJS</a> implements the <a href="http://wiki.commonjs.org/wiki/Modules/AsynchronousDefinition">Asynchronous Module Definition</a> as proposed on the <a href="http://wiki.commonjs.org/wiki/CommonJS">CommonJS wiki</a> which provides a means of loading scripts "on demand" in an asynchronous fashion. One of the most powerful features of the library is the <a href="http://requirejs.org/docs/optimization.html">optimization tool</a> which combines the scripts by tracking the dependents on each script and (optionally) including them as part of the main script. During this process the combined scripts can be run through UglifyJS (default) or Google's Closure Compiler.

My typical setup looks like the following:

```bash
static/
    coffee/
        ...
    js/
        min/
        src/
            page1/
            page2/
            ...
```

Each page directory contains a ``main.js`` and any other scripts applicable to that page. I use the optimization tool to combine all scripts into the ``main.js`` file for each page, that way I only need to define a single script for the web page.

### Backbone
I am a big advocate of developing RESTful APIs and using JavaScript as the client to dynamically load content (when appropriate) into the page... one might call these AJAX requests. I personally don't think many people use AJAX requests in sensible ways, but rather implement them for the sake of saying they have an AJAXy website.

I digress.. when I have published APIs and want a dynamic web app, <a href="http://documentcloud.github.com/backbone/">BackboneJS</a> provides a solid, yet simple MVC framework. The ``Backbone.Model`` and ``Backbone.Collection`` classes exists to encapsulates the application's data. Collections can fetch the data from the server (or any other persistence layer) via a GET and can POST new data to the server when a Model instance has been added to the collection. Model instances handle sending updates to their data to the server via PUT requests and if a model instance is deleted, the DELETE request is made.

``Backbone.View`` provides the view layer in MVC and should contain all the necessary logic that interacts directly with the DOM (as suppose to the model layer, which should not). Backbone has an <a href="http://documentcloud.github.com/backbone/#Events">event system</a> that fires all event handlers when certain actions occur on model or collection instances. The views that represents these objects can then bind their own even handlers to update the DOM when certain properties change or when models are created or destroyed.

### Underscore
I did not know about <a href="http://documentcloud.github.com/underscore/">Underscore</a> before learning Backbone (since it is a dependency), but it acts as a utility belt for JavaScript in general. I highly recommend it taking a look at it.

### CoffeeScript
<a href="http://jashkenas.github.com/coffee-script/">CoffeeScript</a> is a new language that compiles to JavaScript which provides a much nicer syntax and quite a few shortcuts. I find it easier to read and write, but it still feels like I am writing JavaScript.. which I want. I am usually never for having "language x" compile to "language y" just because you can or want it to (I'm looking at you Objective-J), but CS makes it a delight to code JavaScript. The fact that the syntax is actually more simple and regular (significant whitespace, no curly braces, no semicolons) the code variability between developers reduces. The other plus is that the output JavaScript is consistent and optimized (at least that is one of the goals of the compiler) which makes debugging it not bad at all.
Compiling CS files is trivial:

```bash
$ coffee -w -b -o static/js/src -c static/coffee
```

This command watches the ``static/coffee`` directory for ``.coffee`` files that are created or modified and compiles them to ``static/js/src`` mimicking there path. Thus ``static/coffee/foo/main.coffee`` is compiled and written to ``static/js/src/foo/main.js``. The ``-b`` flag means "bare" and tells the compiler **not** to wrap all the code in a closure. In most cases this would be desirable, but since I use the RequireJS optimization tool, this is redundant.
