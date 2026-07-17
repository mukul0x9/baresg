import os
import shutil
from datetime import datetime
from xml.sax.saxutils import escape
from markdown_parser.markdown import markdown_to_html
from template_engine.engine import Template

import sys

IS_DEV = "--dev" in sys.argv


BASE_DIR = os.path.dirname(__file__)
SITE_URL = "https://mukul0x9.pages.dev"


def format_date(date_str):
    date_str = date_str.strip().strip("\"'")
    return (
        datetime.strptime(date_str, "%Y-%m-%d").strftime("%-d %B %Y")
        if date_str
        else ""
    )


def read_file(path):
    with open(os.path.join(BASE_DIR, path), "r", encoding="utf-8") as f:
        return f.read()


def save_output(html, path_parts):
    output_dir = os.path.join("public", *path_parts)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def parse_meta(raw_text):
    parts = raw_text.split("---", 2)
    if len(parts) < 3:
        return {}, raw_text

    meta = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip("\"'")
    return meta, parts[2].strip()


# Load templates
BASE_TEMPLATE = Template(read_file("templates/base.html"))
POST_TEMPLATE = Template(read_file("templates/post.html"))
BLOG_TEMPLATE = Template(read_file("templates/blog.html"))
TAG_INDEX_TEMPLATE = Template(read_file("templates/tags.html"))
TAG_POST_TEMPLATE = Template(read_file("templates/tag_page.html"))


def create_final_html(content, context=None):
    context = context or {}
    dev_script = ""
    if IS_DEV:
        dev_script = """<script>
        let version = 0;
        setInterval(async () => {
            try {
                const res = await fetch("/version", { cache: "no-store" });
                const data = await res.json();
                if (version === 0) version = data.version;
                else if (version !== data.version) location.reload();
            } catch (_) {}
        }, 1000);
        </script>"""
    return BASE_TEMPLATE.render(
        {
            "content": content,
            "title": context.get("title"),
            "canonical_url": context.get("canonical_url", SITE_URL),
            "dev_script": dev_script,  # Inject the script block or empty string
        }
    )


def collect_content(current_dir="content"):
    posts, pages, tags_index = [], [], {}
    for root, _, files in os.walk(current_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == "index" or ext != ".md":
                continue

            raw_text = read_file(os.path.join(root, file))
            meta, content = parse_meta(raw_text)
            slug = meta.get("slug", name)
            tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
            date_str = meta.get("date", "").strip().strip("\"'")

            item = {
                "title": meta.get("title", ""),
                "slug": slug,
                "date": date_str,
                "formatted_date": format_date(date_str),
                "tags": tags,
                "summary": meta.get("summary", ""),
                "html_content": markdown_to_html(content),
            }

            if meta.get("type") == "page":
                pages.append(item)
            else:
                item["url"] = f"/blog/{slug}"
                posts.append(item)
                for tag in tags:
                    tags_index.setdefault(tag, []).append(
                        {"title": item["title"], "url": item["url"], "name": tag}
                    )

    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts, pages, tags_index


def render_items(items, is_post=True):
    for item in items:
        context = {
            "title": item["title"],
            "content": item["html_content"],
            "date": item["formatted_date"],
            "tags": item["tags"],
            "posts": items if is_post else None,
            "canonical_url": f"{SITE_URL}/blog/{item['slug']}/",
        }
        html = POST_TEMPLATE.render(context)
        dest = ["blog", item["slug"]] if is_post else [item["slug"]]
        save_output(create_final_html(html, context), dest)


def render_blog_archive(posts, tags_index):
    tags_list = sorted(
        [{"name": tag, "count": len(items)} for tag, items in tags_index.items()],
        key=lambda x: (-x["count"], x["name"]),
    )
    context = {
        "title": "",
        "posts": posts,
        "tags": tags_list,
        "canonical_url": f"{SITE_URL}/",
    }
    save_output(create_final_html(BLOG_TEMPLATE.render(context), context), [])


def render_tags(tags_index):
    tags_list = []
    for tag, posts in tags_index.items():
        tags_list.append({"name": tag, "count": len(posts)})
        html = TAG_POST_TEMPLATE.render({"name": tag, "posts": posts})
        context = {"title": tag, "canonical_url": f"{SITE_URL}/tags/{tag}/"}
        save_output(create_final_html(html, context), ["tags", tag])

    html = TAG_INDEX_TEMPLATE.render({"tags": tags_list})
    context = {"title": "Tags", "canonical_url": f"{SITE_URL}/tags/"}
    save_output(create_final_html(html, context), ["tags"])


def generate_sitemap(posts, pages, tags_index):
    now_str = datetime.now().strftime("%Y-%m-%d")
    urls = [{"loc": f"{SITE_URL}/", "lastmod": now_str}]
    urls += [
        {"loc": f"{SITE_URL}/blog/{p['slug']}/", "lastmod": p["date"]} for p in posts
    ]
    urls += [{"loc": f"{SITE_URL}/{p['slug']}/", "lastmod": p["date"]} for p in pages]
    urls += [
        {"loc": f"{SITE_URL}/tags/{tag}/", "lastmod": now_str} for tag in tags_index
    ]

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        xml.extend(
            [
                "<url>",
                f"<loc>{url['loc']}</loc>",
                f"<lastmod>{url['lastmod']}</lastmod>",
                "</url>",
            ]
        )
    xml.append("</urlset>")

    with open("public/sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))


def generate_robots_txt():
    with open("public/robots.txt", "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def generate_rss(posts):
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        "<title>Mukul Makwana</title>",
        f"<link>{SITE_URL}</link>",
        "<description>Personal Blog</description>",
        "<language>en-us</language>",
        f'<atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />',
    ]
    for post in posts[:20]:
        pub_date = (
            datetime.strptime(post["date"], "%Y-%m-%d").strftime(
                "%a, %d %b %Y 00:00:00 GMT"
            )
            if post["date"]
            else ""
        )
        xml.extend(
            [
                "<item>",
                f"<title>{escape(post['title'])}</title>",
                f"<link>{SITE_URL}/blog/{post['slug']}/</link>",
                f"<guid>{SITE_URL}/blog/{post['slug']}/</guid>",
                f"<pubDate>{pub_date}</pubDate>",
            ]
        )
        if post["summary"]:
            xml.append(f"<description>{escape(post['summary'])}</description>")
        xml.append("</item>")
    xml.extend(["</channel>", "</rss>"])
    with open("public/rss.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))


def copy_static_assets():
    if os.path.exists("static"):
        for item in os.listdir("static"):
            src = os.path.join("static", item)
            dst = os.path.join("public", item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)


def build_site():
    posts, pages, tags_index = collect_content()
    render_tags(tags_index)
    render_items(posts, is_post=True)
    render_items(pages, is_post=False)
    render_blog_archive(posts, tags_index)
    generate_sitemap(posts, pages, tags_index)
    generate_rss(posts)
    generate_robots_txt()
    copy_static_assets()


if __name__ == "__main__":
    build_site()
