from .lexer import tokenize
from .parser import parse
from .renderer import render


def markdown_to_html(text):
    tokens = tokenize(text)
    nodes = parse(tokens)
    return "".join(render(n) for n in nodes)
