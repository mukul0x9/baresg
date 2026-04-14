from .lexer import tokenize
from .parser import parse
from .renderer import render

text = "# Hello **world**"

tokens = tokenize(text)
print(tokens)  # debug

nodes = parse(tokens)
print(nodes)  # debug

html = "".join(render(n) for n in nodes)
print(html)


def markdown_to_html(text):
    tokens = tokenize(text)
    nodes = parse(tokens)
    return "".join(render(n) for n in nodes)
