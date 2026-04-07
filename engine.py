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

    scope_track = []

    def resolve_scope_track(context_var):
        parts = context_var.split(".")
        root = parts[0]
        if root in scope_track:
            final = root
        else:
            final = f'context["{root}"]'

        for p in parts[1:]:
            final += f"['{p}']"

        return final

    for token in tokens:
        if token.startswith("{{"):
            var = token[2:-2].strip()

            final = resolve_scope_track(var)

            code.append(f"{indent}result.append(str({final}))")

        elif token.startswith("{%"):
            tag = token[2:-2].strip()

            if tag.startswith("if "):
                condition = tag[3:].strip()

                final = resolve_scope_track(condition)

                code.append(f"{indent}if {final}:")
                indent += "    "

            elif tag.startswith("elif "):
                indent = indent[:-4]

                condition = tag[5:].strip()
                final = resolve_scope_track(condition)

                code.append(f"{indent}elif {final}:")
                indent += "    "

            elif tag.startswith("endif"):
                indent = indent[:-4]

            if tag.startswith("for "):
                # {% for post in posts.list %}

                parts = tag.split()

                loop_var = parts[1]

                context_var = parts[3]

                final = resolve_scope_track(context_var)

                code.append(f"{indent}for {loop_var} in {final}:")
                indent += "    "
                scope_track.append(loop_var)

            elif tag.startswith("endfor"):
                indent = indent[:-4]
                if scope_track:
                    scope_track.pop()

            elif tag.startswith("else"):
                indent = indent[:-4]
                code.append(f"{indent}else:")
                indent += "    "

        else:
            if token:
                code.append(f"{indent}result.append({repr(token)})")

    code.append(f'{indent}return "".join(result)')

    return "\n".join(code)


def render_template(generated_code, context):

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


def collect_all_post(dir="content"):

    posts = []

    def walk_post_dir(dir="content"):
        for name in os.listdir(dir):
            path = os.path.join(dir, name)

            if os.path.isfile(path):
                name, ext = os.path.splitext(name)

                if name != "index" and ext == ".md":
                    raw_text = read_file(path)
                    meta_data, _ = parse_meta_data_and_content(raw_text)

                    posts.append(
                        {
                            "title": meta_data.get("title", ""),
                            "url": f"/blog/{name}",
                            "date": meta_data.get("date", "02/03/1999"),
                            "source_path": path,
                            "slug": meta_data.get("slug", name),
                        }
                    )
            else:
                walk_post_dir(path)

    walk_post_dir(dir)
    return posts


def render_posts(posts):
    template = read_file("templates/post.html")

    for post in posts:
        raw_text = read_file(post["source_path"])

        meta_data, markdown_content = parse_meta_data_and_content(raw_text)

        html_content = parse_markdown_content(markdown_content)

        context = {
            "title": meta_data.get("title", ""),
            "content": html_content,
            "date": meta_data.get("date", ""),
            "posts": posts,
        }

        function_code_string = compile_template(template)

        html_page = render_template(function_code_string, context)

        final_html = create_final_html("templates/base.html", html_page)

        save_output_files(final_html, f"blog/{post['slug']}")


def render_home(posts):
    template = read_file("templates/index.html")
    raw_text = read_file("content/index.md")
    meta_data, markdown_content = parse_meta_data_and_content(raw_text)

    html_content = parse_markdown_content(markdown_content)

    context = {
        "title": meta_data.get("title", ""),
        "content": html_content,
        "date": meta_data.get("date", ""),
        "posts": posts,
    }

    function_code_string = compile_template(template)

    html_page = render_template(function_code_string, context)

    final_html = create_final_html("templates/base.html", html_page)

    save_output_files(final_html, "")


def render_blog_archive(posts):
    template = read_file("templates/blog.html")

    context = {"title": "Blog", "posts": posts}

    function_code_string = compile_template(template)

    html_page = render_template(function_code_string, context)

    final_html = create_final_html("templates/base.html", html_page)

    save_output_files(final_html, "blog")


all_posts = collect_all_post()

render_posts(all_posts)
render_home(all_posts)
render_blog_archive(all_posts)
