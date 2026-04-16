# def render(node):
#     if node.type == "TEXT":
#         return node.value
#
#     elif node.type == "BOLD":
#         return "<strong>" + "".join(render(c) for c in node.children) + "</strong>"
#
#     elif node.type == "ITALIC":
#         return "<em>" + "".join(render(c) for c in node.children) + "</em>"
#
#     elif node.type == "CODE":
#         return f"<code>{node.value}</code>"
#
#     elif node.type == "PARAGRAPH":
#         return "<p>" + "".join(render(c) for c in node.children) + "</p>"
#
#     elif node.type == "HEADING":
#         return (
#             f"<h{node.value}>"
#             + "".join(render(c) for c in node.children)
#             + f"</h{node.value}>"
#         )
#
#     return ""



class HTMLGenerator:
    def generate(self, node):
        method_name = f'generate_{type(node).__name__}'
        generator = getattr(self, method_name, self.generic_generate)
        return generator(node)

    def generic_generate(self, node):
        raise Exception(f'No generate method for {type(node).__name__}')

    def generate_Document(self, node):
        return '\n'.join(self.generate(child) for child in node.children)

    def generate_Heading(self, node):
        return f'<h{node.level}>{node.text}</h{node.level}>'

    def generate_Bold(self, node):
        return f'<strong>{node.text}</strong>'

    def generate_Italic(self, node):
        return f'<em>{node.text}</em>'

    def generate_Link(self, node):
        return f'<a href="{node.url}">{node.text}</a>'

    def generate_Image(self,node):
        return f'<img href="{node.url}" alt="{node.text}">'

    def generate_List(self, node):
        items = '\n'.join(f'<li>{item}</li>' for item in node.items)
        return f'<ul>\n{items}\n</ul>'

    def generate_Paragraph(self, node):
        return f'<p>{node.text}</p>'




