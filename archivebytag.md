---
layout: page
title: Post by Tag
permalink: /tagview/
sitemap: false
---

<div>
    {% assign tags = site.tags | sort %}
    {% for tag in tags %}
     <span class="site-tag">
        <a href="#{{ tag | first | slugify }}">
           {{ tag[0] | replace:'-', ' ' }} ({{ tag | last | size }})
        </a>
    </span>
    {% endfor %}
</div>

<div id="index">
	{% for tag in tags %}
		<a name="{{ tag[0] }}"></a>
		<h2>{{ tag[0] | replace:'-', ' ' }} ({{ tag | last | size }}) </h2>
		{% assign sorted_posts = site.posts | sort: 'title' %}
		{% for post in sorted_posts %}
		{%if post.tags contains tag[0]%}
		  <h3><a href="{{ site.url }}{{site.baseurl}}{{ post.url }}" title="{{ post.title }}">{{ post.title }} 
		  <p class="date">{{ post.date |  date: "%B %e, %Y" }}</p></a></h3>
		  <p>{{ post.excerpt | strip_html | truncate: 160 }}</p>
		{%endif%}
	{% endfor %}
{% endfor %}
</div>
