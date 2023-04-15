import commonmark

from django import template

# Converts markdown to html code
def cm_html(text):
    parser = commonmark.Parser()
    html_renderer = commonmark.HtmlRenderer()

    parsedText = parser.parse(text)
    html = html_renderer.render(parsedText)

    return html

register = template.Library()

# Make cm_html(text) available as 'commonmark' in templates
register.filter('commonmark', cm_html)

