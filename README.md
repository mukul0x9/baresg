# Baresg

A static site generator built from scratch in Python — no external dependencies, no frameworks, nothing outside the standard library.

The goal wasn't to ship a tool. It was to understand how the pieces actually work.

---

## How it works

```
Markdown files + Templates
         │
         ▼
  [ Frontmatter parser ]  — extracts title, date, slug, tags, type
         │
         ▼
  [ Markdown → HTML ]     — custom parser, stdlib only
         │
         ▼
  [ Template engine ]     — compiles templates into Python functions, executes them
         │
         ▼
      public/             — static HTML output
```

### The template engine

Templates aren't interpreted at render time — they're compiled into Python functions and executed. `compile_template()` scans the template source, translates `{{ variables }}`, `{% if %}`, and `{% for %}` blocks into Python code, then `exec()`s the generated function in a sandboxed namespace with restricted builtins.

This is the same fundamental approach Jinja2 uses internally.

### What gets built

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

Your content here.
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

[A Template Engine — 500 Lines or Less](https://aosabook.org/en/500L/a-template-engine.html) by Ned Batchelder.
