---
layout: archive
title: "Research"
permalink: /research/
author_profile: true
redirect_from:
  - /publications/
---

{% include base_path %}

You can also find my articles on my [Google Scholar profile]({{ site.author.googlescholar }}). If you can't access a paper, [email me](mailto:{{ site.author.email }}) for a pdf copy.

{% assign pubs_by_year = site.data.publications | group_by: "year" | sort: "name" | reverse %}
{% for year in pubs_by_year %}
<h2 id="year-{{ year.name | default: 'undated' }}">{{ year.name | default: "Undated" }}</h2>
{% for pub in year.items %}
<p class="publication">
  {% if pub.url %}<a href="{{ pub.url }}"><strong>{{ pub.title }}</strong></a>{% else %}<strong>{{ pub.title }}</strong>{% endif %}{% if pub.pdf %} [<a href="{{ pub.pdf }}">PDF</a>]{% endif %}<br>
  {{ pub.authors | replace: "Indira Sen", "<strong>Indira Sen</strong>" }}<br>
  {% if pub.venue != "" %}<em>{{ pub.venue }}</em>{% endif %}{% if pub.note %} · <strong>{{ pub.note }}</strong>{% endif %}
</p>
{% endfor %}
{% endfor %}
