import mistune

from django import template

from ..markdown import renderer as sw_renderer

def markdown_to_html(text):
    markdown = mistune.create_markdown(escape=True, 
                                       renderer=sw_renderer.SimpleWikiRenderer(), 
                                       plugins=['strikethrough', 'url', 'footnotes', 'abbr', 'mark', 'insert', 'superscript', 'subscript', 'table'])

    html = markdown(text)

    return html

register = template.Library()
register.filter('markdown', markdown_to_html)

