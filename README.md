# Baresg

A static site generator built from scratch in Python

---

## How it works

```
Markdown files + Templates
         │
         ▼
  [ Frontmatter parser ]  — extracts title, date, slug, tags, type
         │
         ▼
  [ Markdown → HTML ]     —  parse markdown to html
         │
         ▼
  [ Template engine ]     — compiles templates into Python functions, executes them
         │
         ▼
      public/             — static HTML output
```

### Markdown parser

Custom tokenizer → block parser → inline parser → HTML renderer pipeline, built without regex for the parsing stage. Handles headings (h1–h6), unordered lists, paragraphs, bold, italic, links, images, and inline code.

### The template engine

Templates are compiled into Python functions and executed. `compile_template()` scans the template source, translates `{{ variables }}`, `{% if %}`, and `{% for %}` blocks into Python code, then `exec()`s the generated function in a sandboxed namespace with restricted builtins.

### final output

- Individual post pages → `public/blog/<slug>/index.html`
- Static pages → `public/<slug>/index.html`
- Blog archive → `public/blog/index.html`
- Tag index + per-tag pages → `public/tags/`
- Home page → `public/index.html`

---

## Project structure

```
baresg/
├── content/              # Markdown source files
├── templates/            # HTML templates (base, post, index, blog, tags)
├── template_engine/      # Template compiler + engine
├── markdown_parser/      # Markdown → HTML
├── public/               # Generated output (don't edit)
├── site_generator.py     # Build pipeline
```

---

## Content format

Markdown files use frontmatter for metadata:

```
---
title: "My Post"
date: 2026-03-15
slug: my-post
tags: python,web
type: post
---

content....
```

`type: page` generates a static page. Everything else is treated as a blog post.

---

## Template syntax

```html
{{ title }}

{% if tags %}
  <ul>
    {% for tag in tags %}
      <li>{{ tag }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

---

## Usage

```bash
python site_generator.py
```

Output lands in `public/`.

---

## Influenced by

[A Template Engine — 500 Lines or Less](https://aosabook.org/en/500L/a-template-engine.html)
