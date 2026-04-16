
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self,text) -> None:
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
            if self.current_char == '#':
                tokens.append(self.heading())
            elif self.current_char == '*':
                if self.text[self.current_cursor:self.current_cursor+2] =='**':
                    tokens.append(self.bold())
                else:
                    tokens.append(self.italic())
            elif self.current_char == '[':
                tokens.append(self.link())
            elif self.current_char == '-':
                tokens.append(self.list_item())
            elif self.current_char == '\n':
                tokens.append(Token('NEWLINE','\n'))
                self.advance_curosr()
            elif self.current_char == '!' and self.text[self.current_cursor:self.current_cursor+2]=='![':
                self.advance_curosr()
                tokens.append(self.link(image_link=True))
            else:
                tokens.append(self.paragraph())

            self.skip_whitespace()

        return tokens
 
    def heading(self):
        heading_count = 0

        while self.current_char == '#':
            heading_count += 1
            self.advance_curosr()

        self.skip_whitespace()

        value = []

        while self.current_char and self.current_char != '\n':
            value.append(self.current_char)
            self.advance_curosr()

        return Token('HEADING',(heading_count,''.join(value)))

    def bold(self):
        # skip first two **
        self.advance_curosr()
        self.advance_curosr()
        value = []

        # get the value between 
        while self.current_char and self.text[self.current_cursor:self.current_cursor+2] != '**':
            value.append(self.current_char)
            self.advance_curosr()

        # skip last two **
        self.advance_curosr()
        self.advance_curosr()

        return Token('BOLD',''.join(value))

    def italic(self):
        self.advance_curosr()
        value = []
        
        while self.current_char and self.current_char != '*':
            value.append(self.current_char)
            self.advance_curosr()

        self.advance_curosr()

        return Token('ITALIC',''.join(value))

    


    def link(self,image_link = False):
        self.advance_curosr()

        text = []

        while self.current_char and self.current_char != ']':
            text.append(self.current_char)
            self.advance_curosr()

        self.advance_curosr() # skip ]

        if self.current_char == '(':
            self.advance_curosr()


        url = []

        while self.current_char and self.current_char != ')':
            url.append(self.current_char)
            self.advance_curosr()

        if self.current_char == ')':
            self.advance_curosr()


        if (image_link):
            return Token('IMAGE',(''.join(text),''.join(url)))

        return Token('LINK',(''.join(text),''.join(url)))


    def list_item(self):
        self.advance_curosr() # skip - 

        self.skip_whitespace()

        value = []

        while self.current_char and self.current_char != '\n':
            value.append(self.current_char)
            self.advance_curosr()

        return Token('LIST_ITEM',''.join(value))

    def paragraph(self):
        value = []

        while self.current_char and self.current_char not in ['#','*','[','-','\n']:
            value.append(self.current_char)
            self.advance_curosr()

        return Token('PARAGRAPH', ''.join(value))



# def tokenize(text):
#     tokens = []
#     i = 0
#     start_of_line = True
#
#     while i < len(text):
#         if start_of_line and text[i] == "#":
#             count = 0
#             while i < len(text) and text[i] == "#":
#                 count += 1
#                 i += 1
#
#             if i < len(text) and text[i] == " ":
#                 i += 1
#                 tokens.append(Token("HEADING", count))
#                 start_of_line = False
#                 continue
#             else:
#                 tokens.append(Token("TEXT", "#" * count))
#                 start_of_line = False
#                 continue
#
#         elif text[i : i + 2] == "**":
#             tokens.append(Token("BOLD"))
#             i += 2
#
#         elif text[i] == "*":
#             tokens.append(Token("ITALIC"))
#             i += 1
#
#         elif text[i] == "`":
#             tokens.append(Token("CODE"))
#             i += 1
#
#         elif text[i] == "\n":
#             tokens.append(Token("NEWLINE"))
#             i += 1
#             start_of_line = True
#             continue
#
#         else:
#             start = i
#             while i < len(text) and text[i] not in "*`\n#":
#                 i += 1
#             tokens.append(Token("TEXT", text[start:i]))
#
#         start_of_line = False
#
#     return tokens
