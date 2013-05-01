---                                                                             
layout: post                                                                    
title: "Marky: Reborn"
summary: "Quick re-introduction of the much snappier, serverless [Marky](http://marky.devel.io) Markdown previewer"

---

I [wrote about Marky](http://devel.io/2012/09/04/marky/) back in September. I was pretty excited about it, however the performance sucked. Doing round trips to the server only when the user stopped typing for a few hundred milliseconds resulted in a choppy experience.

I was recently in the market for a JavaScript Markdown renderer and came across [marked](https://github.com/chjj/marked). I was pleasantly surprised [the author](https://github.com/chjj) was particularly interested in speed (he even has a benchmark showing it's faster than a renderer implementation in C...). I saw this as a two-fold gain since it was on the client which could utilize the user's machine and no need for a server (nor the network).

The one thing I thought I would be missing is syntax highlighting. Well that is covered too with [Highlight.js](http://softwaremaniacs.org/soft/highlight/en/). I search around for quite a few syntax highlighters and they all assumed the code block would already be present on the page. It was rare the code would expose the actual parse function (or didn't document) that took the text and spat out markup.

The beauty of these two libraries is how simple and harmonious they work together:

```javascript
// Set the desired options
marked.setOptions({
    gfm: true,
    tables: true,
    breaks: true,
    pedantic: false,
    sanitize: true,
    smartLists: true,
    langPrefix: 'lang-',
    highlight: function(code, lang) {
        if (lang != null) {
            return hljs.highlight(lang, code).value;
        } else {
            return code;
        }
    }
});

// Render away..
var html = marked(text);
```

Check out the new much snappier serverless [Marky](http://marky.devel.io).
