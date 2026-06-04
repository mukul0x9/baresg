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

the naive assumption is that a template engine just does string replacement like find {{ user_name }} and replaces it with the actual value from the context. but what about if statements and loops? you cant do regex for control flow.
the actual insight from the article was one way to make a template engine work is to compile the template string to a python function then execute it with the context.

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


the pipeline is: ``` template string → generate that function as a code string → exec() it into existence → call it with your context data.```


# markdown parser

```
raw markdown
→ block_tokenizer() → [ HEADING, TEXT_LINE, LIST_ITEM, ...]
→ block_parser() → [ Heading{}, Paragraph{}, List{}, ...]
→ attach_inline() → inline parse each node's raw_text
→ render_all() → html string
```

**1. block tokenizer** — splits raw text line by line and classifies each line into a token type: `HEADING`, `LIST_ITEM`, `TEXT_LINE`, or `BLANK`.

**2. block parser** — walks the token list and builds an AST of block-level nodes
like `Heading`, `Paragraph`, and `List`. the only stateful part here is list
handling — consecutive `LIST_ITEM` tokens need to be grouped under a single `List` node, so there's a `current_list` buffer that gets flushed whenever a non-list token appears.

**3. inline parser** — runs on the `raw_text` of each block node and handles
`**bold**`, `*italic*`, `` `code` ``, `[links](url)`, and `![images](src)`. this
one uses a small stack to handle nesting — when you hit `**` you push a new `Bold`
node onto the stack, collect children until you hit the closing `**`, then pop it
and attach it to the parent.

after writing it i realized there are lots of edge cases to handle, so i moved to an established markdown parser for the actual blog.

so i started with a simple Python script that reads markdown files and parse them to html then renders them using a custom template engine.

then added some ssg like thing which loops through directories and renders markdown files and create html files in the output directory in certain subdirectories so you can serve the static files over http.just like any other static site generator output.

there are plenty of gaps to fill and edge cases to handle but the goal was never completeness. it was to understand the problem and how under the hood it can work.


source is at [mukul0x9/baresg](https://github.com/mukul0x9/baresg)
