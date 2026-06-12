---
layout: page
title: Tutorials
permalink: /tutorials/
# Add your own videos here later, e.g.:
#   - title: "My walkthrough"
#     id: "YOUTUBE_ID"
#     desc: "What it covers."
videos: []
---

Hands-on cyber how-to: videos and write-ups on the tools and techniques I use.

{% assign real_videos = page.videos | where_exp: "v", "v.id != 'VIDEO_ID_HERE'" %}
{% if real_videos.size > 0 %}
<h2 class="section-head">My Video Tutorials</h2>
<div class="video-grid">
  {% for v in real_videos %}
    <figure class="video-card">
      <div class="video-embed">
        <iframe src="https://www.youtube-nocookie.com/embed/{{ v.id }}"
                title="{{ v.title }}" loading="lazy" allowfullscreen
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
      </div>
      <figcaption><strong>{{ v.title }}</strong><br>{{ v.desc }}</figcaption>
    </figure>
  {% endfor %}
</div>
{% endif %}

<h2 class="section-head">From the Blog</h2>

<div class="posts tutorial-posts">
  {% assign tut_posts = site.posts | where_exp: "post", "post.tags contains 'cyber'" %}
  {% for post in tut_posts %}
    <article class="post">
      <h3><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h3>
      <p class="post-meta">{{ post.content | number_of_words | divided_by: 200 | plus: 1 }} min read &middot; {{ post.date | date: "%B %e, %Y" }}</p>
      <div class="entry">{{ post.excerpt }}</div>
      <a href="{{ site.baseurl }}{{ post.url }}" class="read-more">Read tutorial →</a>
    </article>
  {% endfor %}
</div>

<h2 class="section-head">Other Work</h2>

<div class="callout">
  <h3 class="callout__title">Cyberspatial on YouTube</h3>
  <p>Some of the work I'm proudest of happened during my time at <strong>Cyberspatial</strong>, where I
  contributed to the team behind <a href="https://teleseer.com">Teleseer</a>. The Cyberspatial team
  produces a fantastic YouTube channel packed with hands-on network-defense and cyber tutorials &mdash;
  <strong>the channel is entirely their creation</strong>, and I was lucky enough to contribute a few of
  the tutorials to it. I'm proud to have played a small part in the journey, and can't recommend the
  channel enough.</p>
  <p><a class="callout__link" href="https://www.youtube.com/@Cyberspatial/videos">Watch the Cyberspatial channel →</a></p>
</div>
