import mistune
from mistune.plugins.table import table

from django import template

class SimpleWikiRenderer(mistune.HTMLRenderer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def paragraph(self, text):
        # Check if the paragraph starts with the YouTube video syntax
        if text.startswith("youtube:"):
            video_id = text.split(":")[1].strip() # Extract the YouTube video ID

            # Get width and height if specified
            try:
                width = text.split(":")[2].strip()
            except IndexError:
                width = "100%"
            try:
                height = text.split(":")[3].strip()
            except IndexError:
                height = "720px"

            youtube_frame = f'<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
            
            return youtube_frame

        # Check if the paragraph starts with the Vimeo video syntax
        if text.startswith("vimeo:"):
            video_id = text.split(":")[1].strip() # Extract the Vimeo video ID

            # Get width and height if specified
            try:
                width = text.split(":")[2].strip()
            except IndexError:
                width = "100%"
            try:
                height = text.split(":")[3].strip()
            except IndexError:
                height = "720px"

            vimeo_frame = f'<iframe width="{width}" height="{height}" src="https://player.vimeo.com/video/{video_id}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen=""></iframe>'
            
            return vimeo_frame
        return super().paragraph(text)

def markdown_to_html(text):
    markdown = mistune.create_markdown(escape=True, 
                                       renderer=SimpleWikiRenderer(), 
                                       plugins=['strikethrough', 'url', 'footnotes', 'abbr', 'mark', 'insert', 'superscript', 'subscript'])

    html = markdown(text)

    return html

register = template.Library()
register.filter('markdown', markdown_to_html)

