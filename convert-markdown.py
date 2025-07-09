#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import markdown # Import the markdown library

def extract_title_subtitle(markdown_lines):
    """
    Extracts the main title and subtitle from markdown lines.
    The first H1 is the title.
    An italicized paragraph immediately following the title is the subtitle.
    Modifies the lines list in place by removing title/subtitle lines.
    """
    main_title = ""
    subtitle = ""
    
    title_found = False
    lines_to_remove = 0

    for i, line in enumerate(markdown_lines):
        stripped_line = line.strip()
        if stripped_line.startswith('# ') and not title_found:
            main_title = stripped_line[2:].strip()
            markdown_lines[i] = "" # Mark for removal
            title_found = True
            lines_to_remove +=1
            # Check for subtitle in the next few lines
            for j in range(i + 1, min(i + 3, len(markdown_lines))):
                subtitle_line_stripped = markdown_lines[j].strip()
                if not subtitle_line_stripped: # Skip blank lines
                    lines_to_remove +=1
                    continue
                if subtitle_line_stripped.startswith('*') and subtitle_line_stripped.endswith('*') and not subtitle_line_stripped.startswith('**'):
                    subtitle = subtitle_line_stripped[1:-1].strip()
                    markdown_lines[j] = "" # Mark for removal
                    lines_to_remove +=1
                break # Stop looking for subtitle after first non-blank line
            break # Stop looking for title

    # DO NOT strip all blank lines here, as they are crucial for Markdown parsing.
    # Empty lines from title/subtitle are already handled by being set to ""
    # and will be filtered out if necessary when joining lines or by the parser.
    # The original list structure (including blank lines) should be preserved as much as possible.
    return main_title, subtitle


def process_abstract_and_keywords(markdown_content):
    """
    Finds "## Abstract" and "**Keywords:**" sections.
    Returns the content before abstract, the abstract content, keywords content, and content after.
    This is a simplified approach. A more robust solution might involve
    parsing the full Markdown to HTML and then manipulating the HTML structure.
    """
    abstract_marker = r"## Abstract" # Raw string for consistency
    keywords_marker = r"\*\*Keywords:\*\*" # Escaped asterisks

    before_abstract = markdown_content
    abstract_text = ""
    keywords_text = ""
    after_abstract_keywords = ""

    abstract_match = re.search(rf"^{abstract_marker}\s*\n(.*?)(?=\n## |\n---|\Z)", markdown_content, re.MULTILINE | re.DOTALL)

    if abstract_match:
        before_abstract = markdown_content[:abstract_match.start()]
        abstract_full_text = abstract_match.group(1).strip()
        
        # Look for keywords within the abstract's extracted text
        keywords_match_in_abstract = re.search(rf"^{keywords_marker}(.*?)(?=\n\n|\Z)", abstract_full_text, re.MULTILINE | re.DOTALL)
        
        if keywords_match_in_abstract:
            keywords_text = keywords_match_in_abstract.group(1).strip()
            # Remove keywords section from abstract_text
            abstract_text = abstract_full_text[:keywords_match_in_abstract.start()].strip() + \
                            abstract_full_text[keywords_match_in_abstract.end():].strip()
            abstract_text = abstract_text.strip() # Clean up potential trailing newlines
        else:
            abstract_text = abstract_full_text

        after_abstract_keywords = markdown_content[abstract_match.end():]
        
        # Check if keywords are outside the abstract section (e.g., after a ---)
        if not keywords_text:
            keywords_match_after_abstract = re.search(rf"^{keywords_marker}(.*?)(?=\n\n|\n---|\Z)", after_abstract_keywords, re.MULTILINE | re.DOTALL)
            if keywords_match_after_abstract:
                keywords_text = keywords_match_after_abstract.group(1).strip()
                # Remove keywords from the 'after_abstract_keywords' part
                after_abstract_keywords = after_abstract_keywords[:keywords_match_after_abstract.start()].strip() + \
                                          after_abstract_keywords[keywords_match_after_abstract.end():].strip()
                after_abstract_keywords = after_abstract_keywords.strip()


    return before_abstract.strip(), abstract_text, keywords_text, after_abstract_keywords.strip()


def markdown_to_html_custom_structure(markdown_body_content, abstract_md="", keywords_md=""):
    """
    Converts the main body of markdown, and separately the abstract and keywords,
    then assembles them into the desired HTML structure.
    """
    extensions = [
        'extra', 'abbr', 'attr_list', 'def_list', 'fenced_code',
        'footnotes', 'md_in_html', 'tables', 'admonition',
        'codehilite', 'legacy_attrs', 'legacy_em', 'meta', # 'nl2br' removed
        'sane_lists', 'smarty', 'toc', 'wikilinks'
    ]

    # Convert main content
    html_body = markdown.markdown(markdown_body_content, extensions=extensions)

    # Convert abstract and keywords if they exist
    html_abstract_content = ""
    if abstract_md:
        # We want the abstract content itself to be paragraphs, so convert it.
        # Each part of the abstract (separated by \n\n in Markdown) should be
        # converted from Markdown to HTML and then wrapped in a <p> tag if it's not already.
        # However, python-markdown will already wrap paragraphs in <p>.
        # So, convert the entire abstract_md, then wrap the result in the section.
        
        processed_abstract_html_content = markdown.markdown(abstract_md, extensions=extensions)
        
        html_abstract_content = f"""
        <section class="abstract">
            <div class="abstract-title">Abstract</div>
            {processed_abstract_html_content}
        """
        if keywords_md:
            # Keywords are often a single line or comma-separated list.
            # The original script put them in a div. Let's replicate that.
            # We'll convert the keyword markdown to basic HTML (e.g. for bold/italic)
            processed_keywords_html = markdown.markdown(keywords_md, extensions=['extra']).strip()
            # Remove surrounding <p> tags if markdown lib added them
            if processed_keywords_html.startswith("<p>") and processed_keywords_html.endswith("</p>"):
                processed_keywords_html = processed_keywords_html[3:-4]
            html_abstract_content += f"""
            <div class="keywords"><strong>Keywords:</strong> {processed_keywords_html}</div>
            """
        html_abstract_content += """
        </section>
        """
        
    # Statistics highlighting (applied to the final HTML body)
    # This regex was in the original script. We apply it post-conversion.
    html_body = re.sub(r'(\d+[\d\.,%-]*(?:\s*billion|\s*%|\s*\$))', r'<span class="statistic">\1</span>', html_body)

    # The python-markdown library's 'extra' extension handles tables well,
    # but the original script wrapped them in a 'table-container' div.
    # We can do this with a regex replacement on the generated HTML.
    html_body = re.sub(r'(<table>.*?</table>)', r'<div class="table-container">\1</div>', html_body, flags=re.DOTALL)
    
    # Section separators --- are converted to <hr> by python-markdown.
    # We need to give them the class "section-separator".
    # The 'extra' extension might do this, or we might need to adjust.
    # For now, let's assume basic <hr> and add class.
    # If python-markdown adds its own classes, this might need refinement.
    html_body = re.sub(r'<hr />', r'<hr class="section-separator" />', html_body) # Handle self-closing
    html_body = re.sub(r'<hr>', r'<hr class="section-separator">', html_body) # Handle non-self-closing

    return html_abstract_content + html_body


def generate_html_template(title, subtitle, body_html, css_file="academic_style.css"):
    """Generate complete HTML document with academic styling, linking to an external CSS file."""
    
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_file}">
    <!--
    To enable MathJax for LaTeX-style math rendering, uncomment the following lines:
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script"></script>
    -->
</head>
<body>
    <article class="article">
        <header class="title-page">
            <h1 class="main-title">{title}</h1>'''
    
    if subtitle:
        template += f'''
            <p class="subtitle">{subtitle}</p>'''
    
    template += f'''
        </header>
        
        {body_html}
    </article>
</body>
</html>'''
    
    return template

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a styled HTML academic paper.",
        formatter_class=argparse.RawTextHelpFormatter  # To allow newlines in help text
    )
    parser.add_argument("input_file", type=str, help="Path to the input Markdown file.")
    parser.add_argument("output_file", type=str, help="Path to the output HTML file.")
    parser.add_argument(
        "--css",
        type=str,
        default="academic_style.css",
        help="Path to the CSS file to use for styling.\n(default: %(default)s, expected in the same directory as the output HTML)"
    )

    args = parser.parse_args()

    input_file = Path(args.input_file)
    output_file = Path(args.output_file)
    css_file_arg = args.css # This will be passed to the template

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Read markdown
    markdown_content_full = input_file.read_text(encoding='utf-8')

    # Extract title and subtitle
    lines = markdown_content_full.split('\n')
    doc_title, doc_subtitle = extract_title_subtitle(lines)
    markdown_after_title = '\n'.join(lines)

    # If no title was found via H1, use a default.
    # The generate_html_template uses its 'title' param for the <title> tag.
    # The .main-title in HTML will be empty if doc_title is empty from extraction.
    effective_doc_title = doc_title if doc_title else "Academic Paper"


    # Process abstract and keywords from the content *after* title/subtitle
    before_abstract_content, abstract_content_md, keywords_content_md, main_body_md = \
        process_abstract_and_keywords(markdown_after_title)

    final_markdown_input_for_body = before_abstract_content + "\n\n" + main_body_md
    final_markdown_input_for_body = final_markdown_input_for_body.strip()
    
    html_content_body = markdown_to_html_custom_structure(
        final_markdown_input_for_body,
        abstract_md=abstract_content_md,
        keywords_md=keywords_content_md
    )
    
    # Generate HTML with template
    final_html = generate_html_template(
        effective_doc_title,
        doc_subtitle,
        html_content_body,
        css_file=css_file_arg  # Pass the CSS file argument here
    )
    
    # Write HTML
    output_file.write_text(final_html, encoding='utf-8')
    print(f"✅ Converted '{input_file}' → '{output_file}' (using CSS '{css_file_arg}')")