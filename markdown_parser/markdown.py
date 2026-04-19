def block_tokenizer(raw_text):

    tokens = []

    lines = raw_text.split("\n")

    for line in lines:
        if line.startswith("#"):
            level = 0

            while level < len(line) and line[level] == "#":
                level += 1

            tokens.append(
                {
                    "type": "HEADING",
                    "level": level,
                    "raw": line[level:].strip(),
                }
            )
        elif line.startswith("-"):
            tokens.append({"type": "LIST_ITEM", "raw": line[1:].strip()})
        elif line.strip() == "":
            tokens.append({"type": "BLANK", "raw": ""})
        else:
            tokens.append({"type": "TEXT_LINE", "raw": line})

    return tokens


def block_parser(tokens):
    nodes = []
    current_list = None
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token["type"] == "LIST_ITEM":
            if current_list is None:
                current_list = {
                    "node": "List",
                    "ordered": False,
                    "children": [],
                    "attrs": {},
                }
            current_list["children"].append(
                {
                    "node": "ListItem",
                    "raw_text": token["raw"],
                    "children": [],
                    "attrs": {},
                }
            )

        else:
            # flush list before handling next block
            if current_list:
                nodes.append(current_list)
                current_list = None

            if token["type"] == "HEADING":
                nodes.append(
                    {
                        "node": "Heading",
                        "level": token["level"],
                        "raw_text": token["raw"],
                        "children": [],
                        "attrs": {},
                    }
                )

            elif token["type"] == "TEXT_LINE":
                nodes.append(
                    {
                        "node": "Paragraph",
                        "raw_text": token["raw"],
                        "children": [],
                        "attrs": {},
                    }
                )

        i += 1

    if current_list:
        nodes.append(current_list)

    return nodes


def parse_inline(text):
    root = {"node": "Root", "children": [], "stop": None}
    stack = [root]
    i = 0

    while i < len(text):
        current = stack[-1]
        stop = current["stop"]
        if stop and text[i : i + len(stop)] == stop:
            i += len(stop)
            stack.pop()
            stack[-1]["children"].append(current)
            continue

        if text[i : i + 2] == "**":
            i += 2
            new_node = {"node": "Bold", "children": [], "stop": "**"}
            stack.append(new_node)
        elif text[i] == "*" and text[i + 1 : i + 2] != "*":
            i += 1
            new_node = {"node": "Italic", "children": [], "stop": "*"}
            stack.append(new_node)

        elif text[i : i + 2] == "![":
            i += 2

            link_text = []

            while i < len(text) and text[i] != "]":
                link_text.append(text[i])
                i += 1

            i += 2

            href = []

            while i < len(text) and text[i] != ")":
                href.append(text[i])

                i += 1

            i += 1

            current["children"].append(
                {
                    "node": "Image",
                    "src": "".join(href),
                    "alt": "".join(link_text),
                    "children": [],
                }
            )

        elif text[i] == "[":
            i += 1

            link_text = []

            while i < len(text) and text[i] != "]":
                link_text.append(text[i])
                i += 1

            i += 2

            href = []

            while i < len(text) and text[i] != ")":
                href.append(text[i])

                i += 1

            i += 1

            current["children"].append(
                {
                    "node": "Link",
                    "href": "".join(href),
                    "children": [{"node": "Text", "value": "".join(link_text)}],
                }
            )

        elif text[i] == "`":
            i += 1

            code = []

            while i < len(text) and text[i] != "`":
                code.append(text[i])

                i += 1

            i += 1

            current["children"].append(
                {
                    "node": "Code",
                    "value": "".join(code),
                }
            )

        else:
            start = i
            while i < len(text) and text[i] not in ("*", "`", "[", "!"):
                i += 1
            if i > start:
                current["children"].append({"node": "Text", "value": text[start:i]})

    return root["children"]


def render(node):
    if node["node"] == "Text":
        return node["value"]

    if node["node"] == "Code":
        return f"<code>{node['value']}</code>"

    if node["node"] == "Image":
        return f'<img src="{node["src"]}" alt="{node["alt"]}">'

    if node["node"] == "Link":
        children = render_children(node)
        return f'<a href="{node["href"]}">{children}</a>'

    if node["node"] == "Bold":
        children = render_children(node)
        return f"<strong>{children}</strong>"

    if node["node"] == "Italic":
        children = render_children(node)
        return f"<em>{children}</em>"

    if node["node"] == "Heading":
        children = render_children(node)
        return f"<h{node['level']}>{children}</h{node['level']}>\n"

    if node["node"] == "Paragraph":
        children = render_children(node)
        return f"<p>{children}</p>\n"

    if node["node"] == "List":
        children = render_children(node)
        return f"<ul>\n{children}</ul>\n"

    if node["node"] == "ListItem":
        children = render_children(node)
        return f"  <li>{children}</li>\n"

    return render_children(node)


def render_children(node):
    return "".join(render(child) for child in node.get("children", []))


def render_all(ast):
    return "".join(render(node) for node in ast)


def attach_inline(nodes):
    for node in nodes:
        if "raw_text" in node:
            node["children"] = parse_inline(node["raw_text"])

        if "children" in node:
            attach_inline(node["children"])

    return nodes


def markdown_to_html(raw_text):
    tokenizer = block_tokenizer(raw_text)

    nodes = block_parser(tokenizer)

    final_ast = attach_inline(nodes)

    html = render_all(final_ast)

    return html
