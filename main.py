from pyges.pyges import Site, Config
from pyges.pyges.models import Page
from pyges.pyges.nodes import *

from dataclasses import dataclass
import datetime

config = Config(src="src", out="out")


site = Site(config)


@dataclass
class Post(Scheme):
    name: str
    date: datetime.date


def navbar() -> Nav:
    return Nav(
        [
            Div(
                A("Ariel Alon", attributes={Attribute.HREF: "/"}),
                attributes={Attribute.CLASS: "left-nav"},
            ),
            Div(
                A(
                    Img(
                        attributes={
                            Attribute.SRC: "/assets/github-mark.svg",
                            Attribute.ALT: "Github Icon",
                            Attribute.CLASS: "icon",
                        }
                    ),
                    {Attribute.HREF: "https://github.com/ArielAlon24"},
                ),
                attributes={Attribute.CLASS: "right-nav"},
            ),
        ],
        attributes={Attribute.CLASS: "navbar"},
    )


def head() -> Head:
    return Head(
        [
            Title("Ariel Alon"),
            Link(
                attributes={
                    Attribute.REL: "stylesheet",
                    Attribute.TYPE: "text/css",
                    Attribute.HREF: "/styles.css",
                }
            ),
        ]
    )


@site.add("blogs/", scheme=Post)
def blog(content: str, name: str, date: datetime.date) -> Html:
    return Html(
        [
            head(),
            Body(
                [
                    navbar(),
                    Article(
                        [
                            Div(
                                [H(size=1, value=name), P(format_date(date))],
                                {Attribute.CLASS: "heading"},
                            ),
                            content,
                        ]
                    ),
                ]
            ),
        ]
    )


@site.add("index.md")
def index(content: str) -> Html:
    return Html(
        [
            head(),
            Body(
                [
                    navbar(),
                    Article(
                        [
                            Div(H(size=1, value="Index"), {Attribute.CLASS: "heading"}),
                            content,
                        ]
                    ),
                    Div(
                        [blog_card(b) for b in site.pages(creator=blog)],
                        {Attribute.CLASS: "blog-cards"},
                    ),
                ]
            ),
        ]
    )


def blog_card(blog: Page) -> A:
    return A(
        [
            H(
                size=2,
                value=blog.properties["name"],
                attributes={Attribute.CLASS: "name"},
            ),
            Div(format_date(blog.properties["date"]), {Attribute.CLASS: "date"}),
        ],
        {
            Attribute.CLASS: "blog-card",
            Attribute.HREF: str(blog.out.relative_to(config.out)),
        },
    )


def format_date(d: datetime.date) -> str:
    return d.strftime("%d-%m-%Y")


if __name__ == "__main__":
    site.build()
