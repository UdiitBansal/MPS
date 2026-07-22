from pathlib import Path
from datetime import datetime

from backend.config import REPORT_DIR
class ReportExporter:

    def __init__(self):

        self.output_dir = Path(REPORT_DIR)

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    # =====================================================
    # Generate Filename
    # =====================================================

    @staticmethod
    def timestamp():

        return datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

    # =====================================================
    # Save Markdown
    # =====================================================

    def save_markdown(

        self,

        markdown,

        filename="research_brief"

    ):

        file = self.output_dir / (

            f"{filename}_{self.timestamp()}.md"

        )

        with open(

            file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(markdown)

        return str(file)

    # =====================================================
    # Save Plain Text
    # =====================================================

    def save_text(

        self,

        text,

        filename="answer"

    ):

        file = self.output_dir / (

            f"{filename}_{self.timestamp()}.txt"

        )

        with open(

            file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(text)

        return str(file)

    # =====================================================
    # Save HTML
    # =====================================================

    def save_html(

        self,

        markdown,

        filename="research_brief"

    ):

        html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>Research Brief</title>

<style>

body{{
font-family:Arial;
margin:40px;
line-height:1.7;
}}

pre{{
white-space:pre-wrap;
}}

</style>

</head>

<body>

<pre>

{markdown}

</pre>

</body>

</html>
"""

        file = self.output_dir / (

            f"{filename}_{self.timestamp()}.html"

        )

        with open(

            file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(html)

        return str(file)

    # =====================================================
    # Export Research Brief
    # =====================================================

    def export(

        self,

        markdown

    ):

        md_file = self.save_markdown(

            markdown,

            "research_brief"

        )

        html_file = self.save_html(

            markdown,

            "research_brief"

        )

        return {

            "markdown": md_file,

            "html": html_file

        }