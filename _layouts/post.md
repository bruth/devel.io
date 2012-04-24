---
layout: default
---

<h1>{{ page.title }} <small>{{ page.content | number_of_words }} words</small></h1>

{{ content }}

<hr>

<h3>Potentially Related Articles</h3>

<ul>
{% for post in site.related_posts limit:3 %}
<li><em>{{ post.date | date_to_string }}</em> - <a href={{ post.url }}>{{ post.title }}</a>
{% endfor %}
</ul>
