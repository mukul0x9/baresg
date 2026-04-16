from .lexer import Lexer
from .parser import Parser
from .renderer import HTMLGenerator


def markdown_to_html(text):
    lexer = Lexer(text)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    generator = HTMLGenerator()
    html = generator.generate(ast)
    return html
