from lexer import Lexer
from parser import Parser
from renderer import HTMLGenerator

# Input Markdown
markdown_text = """
# Sample Markdown with Image

This is a paragraph with **bold** and *italic* text.

![Van Gogh Style Nike Dunk](https://example.com/van-gogh-dunk.jpg)

Here’s a [link to Nike](https://www.nike.com).

- List item 1
- List item 2
"""

# Lexing -
lexer = Lexer(markdown_text)
tokens = lexer.tokenize()

# Parsing
parser = Parser(tokens)
ast = parser.parse()

# Generating HTML
generator = HTMLGenerator()
html = generator.generate(ast)
