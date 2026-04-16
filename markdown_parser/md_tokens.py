from typing import Optional


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, text) -> None:
        self.text = text
        self.current_cursor = 0

        self.current_char = self.text[self.current_cursor] if self.text else None

    def advance_curosr(self):
        self.current_cursor += 1
        if self.current_cursor < len(self.text):
            self.current_char = self.text[self.current_cursor]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance_curosr()

    def tokenize(self):
        tokens = []

        while self.current_char:
            if self.current_char == "#":
                tokens.append(self.heading())
            elif self.current_char == "*":
                if self.text[self.current_cursor : self.current_cursor + 2] == "**":
                    tokens.append(self.bold())
                else:
                    tokens.append(self.italic())
            elif self.current_char == "[":
                tokens.append(self.link())
            elif self.current_char == "-":
                tokens.append(self.list_item())
            elif self.current_char == "\n":
                tokens.append(Token("NEWLINE", "\n"))
                self.advance_curosr()
            elif (
                self.current_char == "!"
                and self.text[self.current_cursor : self.current_cursor + 2] == "!["
            ):
                self.advance_curosr()
                tokens.append(self.link(image_link=True))
            else:
                tokens.append(self.paragraph())

            self.skip_whitespace()

        return tokens

    def heading(self):
        heading_count = 0

        while self.current_char == "#":
            heading_count += 1
            self.advance_curosr()

        self.skip_whitespace()

        value = []

        while self.current_char and self.current_char != "\n":
            value.append(self.current_char)
            self.advance_curosr()

        return Token("HEADING", (heading_count, "".join(value)))

    def bold(self):
        # skip first two **
        self.advance_curosr()
        self.advance_curosr()
        value = []

        # get the value between
        while (
            self.current_char
            and self.text[self.current_cursor : self.current_cursor + 2] != "**"
        ):
            value.append(self.current_char)
            self.advance_curosr()

        # skip last two **
        self.advance_curosr()
        self.advance_curosr()

        return Token("BOLD", "".join(value))

    def italic(self):
        self.advance_curosr()
        value = []

        while self.current_char and self.current_char != "*":
            value.append(self.current_char)
            self.advance_curosr()

        self.advance_curosr()

        return Token("ITALIC", "".join(value))

    def link(self, image_link=False):
        self.advance_curosr()

        text = []

        while self.current_char and self.current_char != "]":
            text.append(self.current_char)
            self.advance_curosr()

        self.advance_curosr()  # skip ]

        if self.current_char == "(":
            self.advance_curosr()

        url = []

        while self.current_char and self.current_char != ")":
            url.append(self.current_char)
            self.advance_curosr()

        if self.current_char == ")":
            self.advance_curosr()

        if image_link:
            return Token("IMAGE", ("".join(text), "".join(url)))

        return Token("LINK", ("".join(text), "".join(url)))

    def list_item(self):
        self.advance_curosr()  # skip -

        self.skip_whitespace()

        value = []

        while self.current_char and self.current_char != "\n":
            value.append(self.current_char)
            self.advance_curosr()

        return Token("LIST_ITEM", "".join(value))

    def paragraph(self):
        value = []

        while self.current_char and self.current_char not in ["#", "*", "[", "-", "\n"]:
            value.append(self.current_char)
            self.advance_curosr()

        return Token("PARAGRAPH", "".join(value))


class ASTNode:
    pass


class Document(ASTNode):
    def __init__(self) -> None:
        self.children = []

    def __repr__(self) -> str:
        return f"Document({self.children})"


class Heading(ASTNode):
    def __init__(self, level, text):
        self.level = level
        self.text = text

    def __repr__(self):
        return f"Heading({self.level}, {self.text})"


class Bold(ASTNode):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"Bold({self.text})"


class Italic(ASTNode):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"Italic({self.text})"


class Link(ASTNode):
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def __repr__(self):
        return f"Link({self.text}, {self.url})"


class Image(ASTNode):
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def __repr__(self):
        return f"Image({self.text}, {self.url})"


class List(ASTNode):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return f"List({self.items})"


class Paragraph(ASTNode):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"Paragraph({self.text})"


class Parser:
    def __init__(self, tokens) -> None:

        self.tokens = tokens
        self.curr_pos = 0
        self.current_token = (
            self.tokens[self.curr_pos] if self.curr_pos < len(self.tokens) else None
        )

    def advance_curosr(self):
        self.curr_pos += 1
        if self.curr_pos < len(self.tokens):
            self.current_token = self.tokens[self.curr_pos]
        else:
            self.current_token = None

    def parse(self):
        document = Document()

        while self.current_token:
            if self.current_token.type == "HEADING":
                document.children.append(self.parse_heading())
            elif self.current_token.type == "BOLD":
                document.children.append(self.parse_bold())
            elif self.current_token.type == "ITALIC":
                document.children.append(self.parse_italic())
            elif self.current_token.type == "LINK":
                document.children.append(self.parse_link())

            elif self.current_token.type == "IMAGE":
                document.children.append(self.parse_image())
            elif self.current_token.type == "LIST_ITEM":
                document.children.append(self.parse_list())
            elif self.current_token.type == "PARAGRAPH":
                document.children.append(self.parse_paragraph())
            self.advance_curosr()
        return document

    def parse_heading(self):
        level, text = self.current_token.value

        return Heading(level, text)

    def parse_bold(self):
        return Bold(self.current_token.value)

    def parse_italic(self):
        return Italic(self.current_token.value)

    def parse_link(self):
        text, url = self.current_token.value
        return Link(text, url)

    def parse_image(self):
        text, url = self.current_token.value
        return Image(text, url)

    def parse_list(self):
        items = []
        while self.current_token and self.current_token.type == "LIST_ITEM":
            items.append(self.current_token.value)
            self.advance_curosr()
        return List(items)

    def parse_paragraph(self):
        return Paragraph(self.current_token.value)


class HTMLGenerator:
    def generate(self, node):
        method_name = f"generate_{type(node).__name__}"
        generator = getattr(self, method_name, self.generic_generate)
        return generator(node)

    def generic_generate(self, node):
        raise Exception(f"No generate method for {type(node).__name__}")

    def generate_Document(self, node):
        return "\n".join(self.generate(child) for child in node.children)

    def generate_Heading(self, node):
        return f"<h{node.level}>{node.text}</h{node.level}>"

    def generate_Bold(self, node):
        return f"<strong>{node.text}</strong>"

    def generate_Italic(self, node):
        return f"<em>{node.text}</em>"

    def generate_Link(self, node):
        return f'<a href="{node.url}">{node.text}</a>'

    def generate_Image(self, node):
        return f'<img href="{node.url}" alt="{node.text}">'

    def generate_List(self, node):
        items = "\n".join(f"<li>{item}</li>" for item in node.items)
        return f"<ul>\n{items}\n</ul>"

    def generate_Paragraph(self, node):
        return f"<p>{node.text}</p>"


# Input Markdown
markdown_text = """
# Sample Markdown with Image

This is a paragraph with **bold** and *italic* text.

![Van Gogh Style Nike Dunk](https://example.com/van-gogh-dunk.jpg)

Here’s a [link to Nike](https://www.nike.com).

- List item 1
- List item 2
"""

# Lexing
lexer = Lexer(markdown_text)
tokens = lexer.tokenize()

# Parsing
parser = Parser(tokens)
ast = parser.parse()


# Generating HTML
generator = HTMLGenerator()
html = generator.generate(ast)
