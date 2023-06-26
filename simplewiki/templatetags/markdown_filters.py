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

        # Check if the paragraph starts with the alert syntax
        if text.startswith("alert:"):
            alert_parts = text.split(":")
            alertType = alert_parts[1].strip()
            alert_text = ":".join(alert_parts[2:]).strip()

            # Convert \n to a HTML linebreak
            alert_text = alert_text.replace("\\n", "<br>")

            if alertType == "success":
                alert = f'<div class="alert alert-success" role="alert">{alert_text}</div>'
            elif alertType == "info":
                alert = f'<div class="alert alert-info" role="alert">{alert_text}</div>'
            elif alertType == "warning":
                alert = f'<div class="alert alert-warning" role="alert">{alert_text}</div>'
            elif alertType == "danger":
                alert = f'<div class="alert alert-danger" role="alert">{alert_text}</div>'
            else:
                alert = text

            return alert

        return super().paragraph(text)

    # Overwriting table plugin output with bootstrap table
    def table(self, content):
        table_html = '<table class="table table-striped">\n' + content + '</table>'

        return table_html

def markdown_to_html(text):
    markdown = mistune.create_markdown(escape=True, 
                                       renderer=SimpleWikiRenderer(), 
                                       plugins=['strikethrough', 'url', 'footnotes', 'abbr', 'mark', 'insert', 'superscript', 'subscript', 'table'])

    html = markdown(text)

    return html

register = template.Library()
register.filter('markdown', markdown_to_html)

