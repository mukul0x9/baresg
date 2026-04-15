import os
from datetime import datetime

from markdown_parser.markdown import markdown_to_html
from template_engine.engine import Template

BASE_DIR = os.path.dirname(__file__)


def format_date(date_str):
    date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
    return date.strftime("%-d %B %Y")


def read_file(path):
    with open(os.path.join(BASE_DIR, path), "r", encoding="utf-8") as f:
        return f.read()


def save_output_files(final_html, content_dir_path):

    public_dir_path = "public"

    output_dir_path = f"{public_dir_path}/{content_dir_path}"

    os.makedirs(output_dir_path, exist_ok=True)

    with open(f"{output_dir_path}/index.html", "w") as f:
        f.write(final_html)


def parse_meta_data_and_content(raw_text):

    text_split = raw_text.split("---", 2)

    if len(text_split) < 3:
        return {}, raw_text

    meta_data = text_split[1].strip()

    content_data = text_split[2].strip()

    meta = {}

    def clean(value):
        return value.strip().strip('"').strip("'")

    for data in meta_data.split("\n"):
        if ":" not in data:
            continue
        key, value = data.split(":", 1)

        key = key.strip()

        meta[key] = clean(value)

    return meta, content_data


BASE_TEMPLATE = Template(read_file("templates/base.html"))

POST_TEMPLATE = Template(read_file("templates/post.html"))
INDEX_TEMPLATE = Template(read_file("templates/index.html"))
BLOG_TEMPLATE = Template(read_file("templates/blog.html"))


def create_final_html(final_content, context={}):

    # this is combining final html content to base html
    return BASE_TEMPLATE.render(
        {"content": final_content, "title": context.get("title")}
    )


def collect_all_post(current_dir="content"):

    posts = []

    pages = []

    def walk_post_dir(current_dir):
        for name in os.listdir(current_dir):
            path = os.path.join(current_dir, name)

            if os.path.isfile(path):
                name, ext = os.path.splitext(name)

                if name != "index" and ext == ".md":
                    raw_text = read_file(path)
                    meta_data, _ = parse_meta_data_and_content(raw_text)

                    slug = meta_data.get("slug", name)

                    content_type = meta_data.get("type", "post")

                    item = {
                        "title": meta_data.get("title", ""),
                        "slug": slug,
                        "source_path": path,
                        "date": meta_data.get("date", ""),
                        "formatted_date": format_date(meta_data.get("date", "")),
                    }

                    if content_type == "page":
                        pages.append(item)
                    else:
                        item["url"] = f"/blog/{slug}"
                        posts.append(item)

            else:
                walk_post_dir(path)

    walk_post_dir(current_dir)

    def clean_date(date_str):
        return date_str.strip().strip('"').strip("'")

    posts.sort(
        key=lambda x: datetime.strptime(clean_date(x["date"]), "%Y-%m-%d"), reverse=True
    )

    return posts, pages


def render_pages(pages):

    for page in pages:
        raw_text = read_file(page["source_path"])

        meta_data, markdown_content = parse_meta_data_and_content(raw_text)

        html_content = markdown_to_html(markdown_content)

        context = {
            "title": meta_data.get("title", ""),
            "content": html_content,
            "date": format_date(meta_data.get("date", "")),
        }

        html_page = POST_TEMPLATE.render(context)  # reuse

        final_html = create_final_html(html_page, context)

        save_output_files(final_html, page["slug"])


def render_posts(posts):

    for post in posts:
        raw_text = read_file(post["source_path"])

        meta_data, markdown_content = parse_meta_data_and_content(raw_text)

        html_content = markdown_to_html(markdown_content)

        context = {
            "title": meta_data.get("title", ""),
            "content": html_content,
            "date": format_date(meta_data.get("date", "")),
            "posts": posts,
        }

        html_page = POST_TEMPLATE.render(context)

        final_html = create_final_html(html_page, context)

        save_output_files(final_html, f"blog/{post['slug']}")


def render_home(posts):

    raw_text = read_file("content/index.md")
    meta_data, markdown_content = parse_meta_data_and_content(raw_text)

    html_content = markdown_to_html(markdown_content)

    context = {
        "title": meta_data.get("title", ""),
        "content": html_content,
        "posts": posts[:3],
    }

    html_page = INDEX_TEMPLATE.render(context)

    final_html = create_final_html(html_page, context)

    save_output_files(final_html, "")


def render_blog_archive(posts):

    context = {"title": "", "posts": posts}

    html_page = BLOG_TEMPLATE.render(context)

    final_html = create_final_html(html_page, context)

    save_output_files(final_html, "blog")


def build_site():
    all_posts, pages = collect_all_post()

    render_posts(all_posts)
    render_pages(pages)
    render_home(all_posts)
    render_blog_archive(all_posts)


if __name__ == "__main__":
    build_site()
