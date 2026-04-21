import re


def compile_template(template):
    tokens = re.split(r"({{.*?}}|{%.*?%})", template)

    code = []
    code.append("def template_render(context):")
    code.append("    result = []")

    indent = "    "

    loop_state = False

    for token in tokens:
        if token.startswith("{{"):
            var = token[2:-2].strip()
            if not loop_state:
                code.append(f'{indent}result.append(str(context["{var}"]))')
            else:
                code.append(f"{indent}result.append(str({var}))")

        elif token.startswith("{%"):
            tag = token[2:-2].strip()

            if tag.startswith("if"):
                condition = tag.split()[1]

                code.append(f'{indent}if context["{condition}"]:')
                indent += "    "

            elif tag.startswith("endif"):
                indent = indent[:-4]

            if tag.startswith("for"):
                # {% for item in items %}
                _, loop_var, _, context_var = tag.split()
                code.append(f'{indent}for {loop_var} in context["{context_var}"]:')
                indent += "    "
                loop_state = True

            elif tag.startswith("endfor"):
                indent = indent[:-4]
                loop_state = False

        else:
            if token:
                code.append(f"{indent}result.append({repr(token)})")

    code.append(f'{indent}return "".join(result)')

    return "\n".join(code)


template_string = """
<p>Hello {{name}}</p>

{% if is_logged_in %}
<p>Welcome back!</p>
{% endif %}

{% for post in posts %}
<li> hello {{post}} </li>
{% endfor %}
"""


python_code = compile_template(template_string)


safe_builtins = {
    "str": str,
    "int": int,
    "len": len,
    "range": range,
    "enumerate": enumerate,
}

safe_namespace = {"__builtins__": safe_builtins}

exec(python_code, safe_namespace)

render_template = safe_namespace["render"]

context = {"name": "hello wold", "is_logged_in": False, "posts": ["test1", "test2"]}

test = render_template(context)
