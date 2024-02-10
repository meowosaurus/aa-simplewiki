import mistune
import re

from django import template

from ..markdown import renderer as sw_renderer

def markdown_to_html(text):
    """
    Converts markdown text to HTML using the SimpleWikiRenderer.

    Args:
        text (str): The markdown text to convert.

    Returns:
        str: The resulting HTML.
    """
    markdown = mistune.create_markdown(escape=True, 
                                       renderer=sw_renderer.SimpleWikiRenderer(), 
                                       plugins=['strikethrough', 'url', 'footnotes', 'abbr', 'mark', 'insert', 'superscript', 'subscript', 'table'])

    html = markdown(text)

    return html

def mark_html(text):
    print(text)

    text = text.replace("\r\n", "<br>")

    text = re.sub(r"(?<!#)# (.*?)(?=$|\s)", r"<h1>\1</h1>", text)

    text = re.sub(r"(?<!#)## (.*?)(?=$|\s)", r"<h2>\1</h2>", text)

    text = re.sub(r"(?<!#)### (.*?)(?=$|\s)", r"<h3>\1</h3>", text)

    text = re.sub(r"(?<!#)#### (.*?)(?=$|\s)", r"<h4>\1</h4>", text)

    print(text)

    return text

register = template.Library()
register.filter('markdown', markdown_to_html)
#register.filter('markdown', mark_html)

