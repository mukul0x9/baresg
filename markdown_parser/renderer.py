def render(node):
    if node.type == "TEXT":
        return node.value

    elif node.type == "BOLD":
        return "<strong>" + "".join(render(c) for c in node.children) + "</strong>"

    elif node.type == "ITALIC":
        return "<em>" + "".join(render(c) for c in node.children) + "</em>"

    elif node.type == "CODE":
        return f"<code>{node.value}</code>"

    elif node.type == "PARAGRAPH":
        return "<p>" + "".join(render(c) for c in node.children) + "</p>"

    elif node.type == "HEADING":
        return (
            f"<h{node.value}>"
            + "".join(render(c) for c in node.children)
            + f"</h{node.value}>"
        )

    return ""
