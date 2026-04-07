import os
import re

base_dir = os.path.dirname(__file__)


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def save_output_files(final_html, content_dir_path):

    public_dir_path = "public"

    output_dir_path = f"{public_dir_path}/{content_dir_path}"

    os.makedirs(output_dir_path, exist_ok=True)

    with open(f"{output_dir_path}/index.html", "w") as f:
        f.write(final_html)


def parse_meta_data_and_content(raw_text):

    text_split = raw_text.split("---", 2)

    meta_data = text_split[1].strip()

    content_data = text_split[2].strip()

    meta = {}

    for data in meta_data.split("\n"):
        key, value = data.split(":", 1)
        meta[key] = value

    return meta, content_data


def parse_markdown_content(text):
    lines = text.split("\n")

    html = []

    for line in lines:
        if line.startswith("# "):
            html.append(f"<h1>{line[2:]} </h1>")
        elif line.strip() == "":
            continue
        else:
            html.append(f"<p>{line}</p>")

    return "/n".join(html)


def compile_template(template):
    tokens = re.split(r"({{.*?}}|{%.*?%})", template)

    code = []
    code.append("def render_template(context):")
    code.append("    result = []")

    indent = "    "

    loop_state = False

    for token in tokens:
        if token.startswith("{{"):
            var = token[2:-2].strip()
            if not loop_state:
                code.append(f'{indent}result.append(str(context["{var}"]))')
            else:
                var_value = var.split(".")

                if all(var_value) and len(var) > 1:
                    root = var_value[0]
                    rest = var_value[1:]

                    final_string = root

                    for p in rest:
                        final_string += f"['{p}']"

                    var = final_string

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


def render_template(generated_code, context):

    print(generated_code)
    safe_builtins = {
        "str": str,
        "int": int,
        "len": len,
        "range": range,
        "enumerate": enumerate,
    }

    safe_namespace = {"__builtins__": safe_builtins}

    exec(generated_code, safe_namespace)

    render_func = safe_namespace["render_template"]

    print(render_func)

    return render_func(context)  # type: ignore


def render(template, context):
    def string_replacer(match):
        matched_string = match.group(1).strip()
        parts = matched_string.split(".")
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, "")
            else:
                value = ""

        return str(value)

    return re.sub(r"{{\s*(.*?)\s*}}", string_replacer, template)


def create_final_html(base_template, final_content):
    base_template = read_file(base_template)

    context = {"content": final_content}

    final_html = render(base_template, context)

    return final_html


def walk_dir(dir="content"):
    base_template_path = "templates/base.html"
    post_template_path = "templates/post.html"
    index_template_path = "templates/index.html"

    save_post_path = "posts/"

    for name in os.listdir(dir):
        path = os.path.join(dir, name)

        if os.path.isfile(path):
            name, ext = os.path.splitext(name)

            if ext == ".md":
                template = read_file(post_template_path)

                save_output_dir = f"{save_post_path}{name}"

                if name == "index":
                    template = read_file(index_template_path)
                    save_output_dir = ""

                raw_text = read_file(path)

                meta_data, markdown_content = parse_meta_data_and_content(raw_text)

                html_content = parse_markdown_content(markdown_content)

                context = {
                    "title": meta_data.get("title", ""),
                    "content": html_content,
                    "date": "02/03/1999",
                    "posts": [
                        {
                            "title": "firstPost",
                            "url": "posts/post1/index.html",
                            "date": "02/03/9999",
                        }
                    ],
                }

                # page_html = render(template, context)

                function_code_string = compile_template(template)

                html_page = render_template(function_code_string, context)

                final_html = create_final_html(base_template_path, html_page)

                print(final_html)

                # save_output_files(final_html, save_output_dir)

        if os.path.isdir(path):
            walk_dir(path)


walk_dir()
