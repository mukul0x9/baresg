from .md_ast import Node


def parse_inline(tokens, i=0, stop_token=None):
    nodes = []

    while i < len(tokens):
        token = tokens[i]

        if stop_token and token.type == stop_token:
            return nodes, i

        if token.type == "TEXT":
            nodes.append(Node("TEXT", value=token.value))
            i += 1

        elif token.type == "BOLD":
            i += 1
            children, i = parse_inline(tokens, i, stop_token="BOLD")
            nodes.append(Node("BOLD", children=children))
            i += 1

        elif token.type == "ITALIC":
            i += 1
            children, i = parse_inline(tokens, i, stop_token="ITALIC")
            nodes.append(Node("ITALIC", children=children))
            i += 1

        elif token.type == "CODE":
            i += 1
            content = ""

            while i < len(tokens) and tokens[i].type != "CODE":
                if tokens[i].type == "TEXT":
                    content += tokens[i].value
                i += 1

            nodes.append(Node("CODE", value=content))
            i += 1

        else:
            i += 1

    return nodes, i


def parse(tokens):
    nodes = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token.type == "HEADING":
            level = token.value
            i += 1

            inline_tokens = []
            while i < len(tokens) and tokens[i].type != "NEWLINE":
                inline_tokens.append(tokens[i])
                i += 1

            children, _ = parse_inline(inline_tokens)
            nodes.append(Node("HEADING", value=level, children=children))

        elif token.type != "NEWLINE":
            inline_tokens = []
            while i < len(tokens) and tokens[i].type != "NEWLINE":
                inline_tokens.append(tokens[i])
                i += 1

            children, _ = parse_inline(inline_tokens)
            nodes.append(Node("PARAGRAPH", children=children))

        i += 1

    return nodes
