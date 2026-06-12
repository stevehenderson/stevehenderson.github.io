---
layout: page
title: Search
permalink: /search/
search: false
sitemap: false
---

<div class="site-search">
  <input type="search" id="search-input" class="site-search__input"
         placeholder="Search posts and pages…" aria-label="Search this site"
         autocomplete="off" autocapitalize="off" spellcheck="false">
  <p id="search-status" class="site-search__status" aria-live="polite"></p>
  <ul id="search-results" class="site-search__results"></ul>
</div>

<noscript>Search requires JavaScript. You can browse the <a href="{{ '/blog/' | relative_url }}">blog</a> or use the navigation instead.</noscript>

<script src="{{ '/search.js' | relative_url }}" data-index="{{ '/search.json' | relative_url }}" defer></script>
