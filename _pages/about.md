---
permalink: /
title: "Indira Sen"
excerpt: "About me"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

Hi! I am a member of the Junior Faculty at the [Chair of Data Science for the Social and Economic Sciences](https://www.bwl.uni-mannheim.de/en/information-systems/chairs/prof-dr-strohmaier/) in the [University of Mannheim](https://www.uni-mannheim.de/en/).  

My research lies at the intersection of Natural Language Processing (NLP) and Social Science. I investigate the social knowledge, values, and perspectives embedded in generative AI systems, e.g., [political values in Large Language Models (LLMs)](https://aclanthology.org/2025.acl-long.1529/) and [their ability to assist and simulate](https://aclanthology.org/2025.findings-acl.1136/) [different groups of people](https://aclanthology.org/2025.findings-emnlp.1261/). Finally, I design methods for [assessing social values in LLMs](https://aclanthology.org/2026.eacl-long.89/). By interrogating and improving social knowledge in these models, I hope to build language technology that supports and reflects diverse user bases and populations.

Before Mannheim, I was a postdoc and lecturer at the University of Konstanz in the Department of [Politics and Public Policy](https://www.polver.uni-konstanz.de/en/). I did my PhD at RWTH-Aachen and GESIS, Leibnitz Institute for the Social Sciences. I'm fortunate to have been advised by Prof. Claudia Wagner and Prof. Wil van der Aalst. My doctoral research drew from natural language processing and measurement theory, to study how researchers and policy-makers could draw better and more transparent insights from digital trace data.

Before my doctoral studies, I obtained my Master's in Computer Science from [IIIT Delhi](https://www.iiitd.ac.in/), where I was also a research assistant. And even before that, I did my Bachelor's (also in CS) at Vellore Institute of Technology.

## News

{% for item in site.data.news %}
* **{{ item.date }}**: {{ item.text | markdownify | remove: '<p>' | remove: '</p>' | strip }}
{% endfor %}
