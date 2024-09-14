import mistune

from django import template

class SimpleWikiRenderer(mistune.HTMLRenderer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def paragraph(self, text):
        # Convert \n to a HTML linebreak
        text = text.replace("\\n", "<br>")

        # Check if the paragraph starts with the underline video syntax
        # This will also check if the line doesn't start with '__'
        if "__" in text:
            parts = text.split("__")

            formatted_parts = []
            for i, part in enumerate(parts):
                
                if i % 2 == 1:
                    formatted_parts.append("<u>{}</u>".format(part))
                else:
                    formatted_parts.append(part)
        
            return "".join(formatted_parts) + "<br>"

        # Check if the paragraph starts with the YouTube video syntax
        if text.startswith("youtube:"):
            try:
                video_id = text.split(":")[1].strip() # Extract the YouTube video ID
            except IndexError:
                return text

            if not video_id:
                return text

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

            try:
                alert_type = alert_parts[1].strip()
            except IndexError:
                alert_type = "danger"
            try:
                alert_text = ":".join(alert_parts[2:]).strip()
            except IndexError:
                alert_text = "ERROR: Unable to process alert text!"

            if alert_type == "success":
                alert = f'<div class="alert alert-success" role="alert">{alert_text}</div>'
            elif alert_type == "info":
                alert = f'<div class="alert alert-info" role="alert">{alert_text}</div>'
            elif alert_type == "warning":
                alert = f'<div class="alert alert-warning" role="alert">{alert_text}</div>'
            elif alert_type == "danger":
                alert = f'<div class="alert alert-danger" role="alert">{alert_text}</div>'
            else:
                alert = text

            return alert

        # Check if the paragraph starts with the google drive syntax
        if text.startswith("gdrive:"):
            gdrive_parts = text.split(":")

            try:
                gdrive_folder_id = gdrive_parts[1].strip()
            except IndexError:
                return "Google Drive Syntax error: No folder id provided!"
            try:
                gdrive_type = gdrive_parts[2].strip()
            except IndexError:
                gdrive_type = "list"
            
            try:
                gdrive_width = gdrive_parts[3].strip()
            except IndexError:
                gdrive_width = "100%"
            try:
                gdrive_height = gdrive_parts[4].strip()
            except IndexError:
                gdrive_height = "600px"

            gdrive_html = f'<iframe src="https://drive.google.com/embeddedfolderview?id={gdrive_folder_id}#{gdrive_type}" width="{gdrive_width}" height="{gdrive_height}" style="border:0px;"></iframe>'

            return gdrive_html

        return super().paragraph(text)

    # Overwriting table plugin output to include bootstrap
    def table(self, content):
        table_html = '<table class="table bg-dark">\n' + content + '</table>'

        return table_html