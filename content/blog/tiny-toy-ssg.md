---
title: "Building a Tiny SSG"
description: "A tiny experimental static site generator built to explore template engines, markdown parsing, and rendering pipelines."
date: "2026-06-04"
slug: "tiny-ssg"
tags: "recreational-programming"
---

i was reading this article on [aosabook](https://aosabook.org/en/500L/a-template-engine.html) on building a template engine. i had used jinja and django templates before without really understanding what was happening under the hood.
so i thought let's build a tiny static site generator to build a mental model of static site generation.

we need two main things to get started:

- a template engine to render templates
- a markdown parser to convert markdown files to html

# template engine

i initially assumed that template engines just did string replacement with regex like `{{ user_name }}` gets replaced with the actual value from the context. but there are loops and if statements as well. 
the article's approach was to compile the template string to a python function then execute it with the context.

this is a template

```python
<p>Welcome, {{user_name}}!</p>
<p>Products:</p>
<ul>
{% if product_list %}
    {% for product in product_list %}
        <li>{{ product.name }}:
        {{ product.price|format_price }}</li>
{% endfor %}
</ul>
``` 


gets compiled into a function like this

```python
def render_template(context):
    result = []
    result.append("<p>Welcome, ")
    result.append(str(context["user_name"]))
    result.append("!</p> ")
    result.append("<p>Products:</p> ")
    result.append("<ul> ")
    if context["product_list"]:
        for product in context["product_list"]:
            result.append("<li>")
            result.append(str(product["name"]))
            result.append("</li> ")
    result.append("</ul>")
    return "".join(result)
```


then using exec() we can execute the function string with the context data as arguments.


```python
exec(compiled_template_string)
render_func = safe_namespace["render_template"]
render_func(context)
```

for markdown parser , i initially tried implmenting markdown parser from scratch using block parsing, building an AST and then i fried my brain (skill issue). switched to an existing library. code is in `markdown.py`.

so i started with a simple Python script that reads markdown files and parse them to html then renders them using a custom template engine.

the python script reads markdown files from the `content` directory, pass raw text to the markdown parser which returns an raw html string, pass that to the template engine which returns the final html then writes each files to the `output` directory in the specified subdirectory so server or any other static file server can serve the files over http.

content directory structure 
```
content/
├── about.md
├── blog
│   ├── hello-world.md
│   └── tiny-toy-ssg.md
├── index.md
└── reading_list.md
```

output directory structure. 
each markdown file will have their own directory with index.html of the rendered content. so the server can serve each directory as router. 
for example `http://localhost/about/` will serve the `about` directory and `http://localhost/blog/hello-world/` will serve the `hello-world` directory.
```
├── about
│   └── index.html
├── BingSiteAuth.xml
├── blog
│   ├── hello-world
│   │   └── index.html
│   ├── index.html
│   └── tiny-ssg
│       └── index.html
```


the final flow is straightforward, read markdown files from content/ directory , parse it to html , make context object , pass it to template engine , render final html and write it to output/ directory.


there are plenty of gaps to fill and edge cases to handle but the goal was never completeness. it was to understand the problem and how under the hood it can work.


source code : [mukul0x9/baresg](https://github.com/mukul0x9/baresg)
