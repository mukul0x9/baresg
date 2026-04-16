
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
    def __init__(self,tokens) -> None:
        print(tokens)

        self.tokens = tokens 
        self.curr_pos = 0
        self.current_token = self.tokens[self.curr_pos] if self.curr_pos < len(self.tokens) else None
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
            elif self.current_token.type == 'BOLD':
                document.children.append(self.parse_bold())
            elif self.current_token.type == 'ITALIC':
                document.children.append(self.parse_italic())
            elif self.current_token.type == 'LINK':
                document.children.append(self.parse_link())

            elif self.current_token.type == 'IMAGE':
                document.children.append(self.parse_image())
            elif self.current_token.type == 'LIST_ITEM':
                document.children.append(self.parse_list())
            elif self.current_token.type == 'PARAGRAPH':
                document.children.append(self.parse_paragraph())
            else:  
                self.advance_curosr()
        return document

    def parse_heading(self):
        level , text = self.current_token.value 
        self.advance_curosr()

        return Heading(level,text)

    def parse_bold(self):
        value = self.current_token.value
        self.advance_curosr()
        return Bold(value)

    def parse_italic(self):
        value = self.current_token.value 
        self.advance_curosr()
        return Italic(value)

    def parse_link(self):
        text, url = self.current_token.value
        self.advance_curosr()
        return Link(text, url)


    def parse_image(self):
        text, url = self.current_token.value
        self.advance_curosr()
        return Image(text, url)

    def parse_list(self):
        items = []

        while self.current_token and self.current_token.type == 'LIST_ITEM':
            item_tokens = [self.current_token.value]
            self.advance_curosr()

            # Only attach paragraphs directly following a list item
            while self.current_token and self.current_token.type == 'PARAGRAPH':
                item_tokens.append(self.current_token.value)
                self.advance_curosr()

            items.append(" ".join(item_tokens))

        return List(items)

    def parse_paragraph(self):
        value = self.current_token.value 
        self.advance_curosr()
        return Paragraph(value)

