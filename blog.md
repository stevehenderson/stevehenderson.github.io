---
layout: page
title: Blog
permalink: /blog/
---


<ul>
  <li><a href="{{ site.baseurl }}/categoryview/">Category View</a></li>
  <li><a href="{{ site.baseurl }}/tagview/">Tag View</a></li>
</ul>

<hr>

<div class="posts">
  {% for post in site.posts %}
    <article class="post">

      <h1><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h1>

      <div class="entry">
        {{ post.excerpt }}
      </div>

      <a href="{{ site.baseurl }}{{ post.url }}" class="read-more">Read More</a>
    </article>
  {% endfor %}
</div>

