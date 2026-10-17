---
layout: archive
title: "Research"
permalink: /research/
author_profile: true
redirect_from:
  - /publications/
---

{% include base_path %}

This list is pulled automatically from my [Google Scholar profile]({{ site.author.googlescholar }}). If you can't access a paper, [email me](mailto:{{ site.author.email }}) for a pdf copy.

{% assign pubs_by_year = site.data.publications | group_by: "year" | sort: "name" | reverse %}
{% for year in pubs_by_year %}
<h2 id="year-{{ year.name | default: 'undated' }}">{{ year.name | default: "Undated" }}</h2>
{% for pub in year.items %}
<p class="publication">
  <a href="{{ pub.url }}"><strong>{{ pub.title }}</strong></a><br>
  {{ pub.authors | replace: "I Sen", "<strong>I Sen</strong>" }}<br>
  <em>{{ pub.venue }}</em>{% if pub.citations > 0 %} · Cited by {{ pub.citations }}{% endif %}
</p>
{% endfor %}
{% endfor %}
