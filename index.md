---
layout: default
---

## Recent

{% for post in site.posts limit:5%}- _{{ post.date | date_to_string }}_ - [{{ post.title }}]({{ post.url }})
{% endfor %}

## Older

{% for post in site.posts offset:5 %}- _{{ post.date | date_to_string }}_ - [{{ post.title }}]({{ post.url }})
{% endfor %}

## C`0`de

[Spoon](https://bitbucket.org/spooning/).. err Fork me on [GitHub](https://github.com/bruth)

- [Synapse](https://github.com/bruth/synapse) - "Data binding for the rest of us"
- [restlib2](https://github.com/bruth/restliub2) - Hypermedia APIs for Django
- [avocado](https://github.com/cbmi/avocado) - Metadata APIs for Django
- [serrano](https://github.com/cbmi/serrano) - Hypermedia APIs for Avocado
- [cilantro](https://github.com/cbmi/cilantro) - Browser-based client for Serrano
- [modeltree](https://github.com/cbmi/modeltree) - Metadata-driven dynamic queries for Django
