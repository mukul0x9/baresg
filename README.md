# Baresg

**The world definitely needed another SSG that doesn't work.**

A bare-bones attempt at turning Markdown into blog posts or HTML pages using a compiler approach (that I'm still figuring out as I go)
---

### The "Noob" Execution Model
Instead of simple string replacement, I'm compiling templates directly into Python code for execution:

1. **Scan:** Identify template tags, variables, and logic blocks.
2. **Compile:** Convert the template structure into valid Python code using Regex and string building (generating a function on the fly).
3. **Exec:** Run the compiled code within a controlled context to "emit" the final HTML.

### Resources
- [A Template Engine (500 Lines or Less)](https://aosabook.org/en/500L/a-template-engine.html)
