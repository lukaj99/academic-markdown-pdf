#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def markdown_to_html(markdown_content, title="Academic Paper"):
    """Convert markdown to academic HTML with proper structure"""
    
    # Extract title and subtitle
    lines = markdown_content.split('\n')
    main_title = ""
    subtitle = ""
    
    for i, line in enumerate(lines):
        if line.startswith('# ') and not main_title:
            main_title = line[2:].strip()
            lines[i] = ""
            # Check if next non-empty line is italic (subtitle)
            for j in range(i+1, min(i+3, len(lines))):
                if lines[j].strip() and lines[j].strip().startswith('*') and lines[j].strip().endswith('*'):
                    subtitle = lines[j].strip()[1:-1]
                    lines[j] = ""
                    break
            break
    
    content = '\n'.join(lines)
    
    # Convert markdown elements
    content = convert_markdown_elements(content)
    
    # Generate HTML with template
    html = generate_html_template(main_title, subtitle, content)
    return html

def convert_markdown_elements(content):
    """Convert markdown syntax to HTML"""
    
    # Headers (order matters - do 4-level first)
    content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Abstract section (special handling) - include Keywords within abstract
    abstract_pattern = r'<h2>Abstract</h2>\s*\n(.*?)(?=\n---|\n<h[12]|\Z)'
    def abstract_replacer(match):
        abstract_content = match.group(1).strip()
        # Split abstract into proper paragraphs and format each section
        sections = re.split(r'\n\n+', abstract_content)
        formatted_sections = []
        for section in sections:
            section = section.strip()
            if section:
                # Check if this section contains keywords
                if '**Keywords:**' in section:
                    # Format keywords specially
                    keywords_formatted = re.sub(
                        r'\*\*Keywords:\*\*(.*?)$',
                        r'<div class="keywords"><strong>Keywords:</strong>\1</div>',
                        section,
                        flags=re.DOTALL
                    )
                    formatted_sections.append(keywords_formatted)
                else:
                    formatted_sections.append(f'<p>{section}</p>')
        formatted_content = '\n'.join(formatted_sections)
        return f'<section class="abstract"><div class="abstract-title">Abstract</div>\n{formatted_content}\n</section>'
    
    content = re.sub(abstract_pattern, abstract_replacer, content, flags=re.DOTALL)
    
    # Bold and italic (order matters)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', content)
    
    # Blockquotes
    content = re.sub(r'^> (.*?)$', r'<blockquote><p>\1</p></blockquote>', content, flags=re.MULTILINE)
    
    # Tables
    content = convert_tables(content)
    
    # Lists
    content = convert_lists(content)
    
    # Handle statistics highlighting
    content = re.sub(r'(\d+[\d\.,%-]*(?:\s*billion|\s*%|\s*\$))', r'<span class="statistic">\1</span>', content)
    
    # Paragraphs
    content = convert_paragraphs(content)
    
    # Section separators
    content = re.sub(r'^---$', r'<hr class="section-separator">', content, flags=re.MULTILINE)
    
    return content

def convert_tables(content):
    """Convert markdown tables to HTML"""
    table_pattern = r'(\|[^\n]+\|\n)(\|[-:\s\|]+\|\n)((?:\|[^\n]+\|\n?)*)'
    
    def table_replacer(match):
        header_line = match.group(1).strip()
        separator_line = match.group(2).strip()
        data_lines = match.group(3).strip()
        
        # Extract headers
        headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
        
        # Extract data rows
        rows = []
        if data_lines:
            for line in data_lines.split('\n'):
                if line.strip() and '|' in line:
                    row = [cell.strip() for cell in line.split('|')[1:-1]]
                    if row:  # Only add non-empty rows
                        rows.append(row)
        
        # Generate HTML table
        html = '<div class="table-container">\n<table>\n<thead>\n<tr>\n'
        for header in headers:
            html += f'<th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        for row in rows:
            html += '<tr>\n'
            for cell in row:
                html += f'<td>{cell}</td>\n'
            html += '</tr>\n'
        
        html += '</tbody>\n</table>\n</div>\n'
        return html
    
    return re.sub(table_pattern, table_replacer, content, flags=re.MULTILINE)

def convert_lists(content):
    """Convert markdown lists to HTML"""
    # First, let's group consecutive list items together
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a list item
        if stripped.startswith('- ') or re.match(r'^\d+\.\s', stripped):
            # Determine list type
            is_ordered = re.match(r'^\d+\.\s', stripped)
            list_items = []
            
            # Collect all consecutive list items (allowing blank lines between)
            while i < len(lines):
                current_line = lines[i].strip()
                
                # If it's a list item of the same type
                if ((is_ordered and re.match(r'^\d+\.\s', current_line)) or
                    (not is_ordered and current_line.startswith('- '))):
                    if is_ordered:
                        content_match = re.match(r'^\d+\.\s(.+)', current_line)
                        if content_match:
                            list_items.append(content_match.group(1))
                    else:
                        list_items.append(current_line[2:])
                    i += 1
                # If it's a blank line, check if next line is also a list item
                elif not current_line:
                    # Look ahead to see if next non-empty line is a list item
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines):
                        next_line = lines[j].strip()
                        if ((is_ordered and re.match(r'^\d+\.\s', next_line)) or
                            (not is_ordered and next_line.startswith('- '))):
                            i += 1  # Skip the blank line
                            continue
                    break
                else:
                    break
            
            # Generate HTML for the list
            if is_ordered:
                result.append('<ol>')
                for item in list_items:
                    result.append(f'<li>{item}</li>')
                result.append('</ol>')
            else:
                result.append('<ul>')
                for item in list_items:
                    result.append(f'<li>{item}</li>')
                result.append('</ul>')
        else:
            result.append(line)
            i += 1
    
    return '\n'.join(result)

def convert_paragraphs(content):
    """Convert text blocks to paragraphs with tight academic spacing"""
    # Split content into lines and process each
    lines = content.split('\n')
    result = []
    in_section = False
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            result.append('')
            i += 1
            continue
        
        # Check if this is a section start
        if line.startswith('<h1>') or line.startswith('<h2>'):
            in_section = True
            result.append(line)
            i += 1
            continue
            
        # Skip if already HTML or special content
        if (line.startswith('<') or 
            line == '---' or 
            line.startswith('#') or
            line.startswith('|') or
            re.match(r'^\d+\.\s', line) or  # Skip numbered list items
            line.startswith('- ')):  # Skip bullet list items
            result.append(line)
            i += 1
            continue
        
        # This is bare text that needs to be wrapped in <p> tags
        # Collect consecutive bare text lines into a paragraph
        paragraph_lines = []
        while i < len(lines):
            current_line = lines[i].strip()
            if (not current_line or 
                current_line.startswith('<') or 
                current_line == '---' or 
                current_line.startswith('#') or
                current_line.startswith('|') or
                re.match(r'^\d+\.\s', current_line) or  # Stop at numbered lists
                current_line.startswith('- ')):  # Stop at bullet lists
                break
            paragraph_lines.append(current_line)
            i += 1
        
        if paragraph_lines:
            paragraph_text = ' '.join(paragraph_lines)
            if in_section:
                result.append(f'<p class="first-paragraph">{paragraph_text}</p>')
                in_section = False
            else:
                result.append(f'<p>{paragraph_text}</p>')
    
    return '\n'.join(result)

def generate_html_template(title, subtitle, content):
    """Generate complete HTML document with academic styling"""
    
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Load Gulliver Elsevier Fonts */
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Text.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Text.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Italic-Text.otf') format('opentype');
            font-weight: 400;
            font-style: italic;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Italic-Text.otf') format('opentype');
            font-weight: 700;
            font-style: italic;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Display';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Display.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Display';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Display.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Caption';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Regular-Caption.otf') format('opentype');
            font-weight: 400;
            font-style: normal;
        }}
        
        @font-face {{
            font-family: 'Gulliver Elsevier Caption';
            src: url('/Users/lukaj/GulliverFonts/fonts/elsevier-fonts/Gulliver-Elsevier-Bold-Caption.otf') format('opentype');
            font-weight: 700;
            font-style: normal;
        }}

        /* Page Setup - Clean with no headers/footers */
        @page {{
            size: A4;
            margin: 32mm 25mm 28mm 25mm;
        }}

        /* Reset and Base Typography */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Gulliver Elsevier', Times, serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000000;
            background: #ffffff;
            text-align: justify;
            hyphens: auto;
            orphans: 2;
            widows: 2;
            word-spacing: 0.01em;
            letter-spacing: 0.005em;
        }}

        .article {{
            max-width: 210mm;
            margin: 0 auto;
        }}

        /* Typography Hierarchy */
        h1 {{
            font-family: 'Gulliver Elsevier Display', serif;
            font-size: 14pt;
            font-weight: 700;
            line-height: 1.2;
            color: #000000;
            margin: 18pt 0 10pt 0;
            text-align: left;
            page-break-after: avoid;
            letter-spacing: -0.01em;
        }}

        h2 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 12pt;
            font-weight: 700;
            color: #1a365d;
            margin: 14pt 0 6pt 0;
            text-align: left;
            page-break-after: avoid;
        }}

        h3 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 11pt;
            font-weight: 700;
            color: #2d3748;
            margin: 16pt 0 8pt 0;
            text-align: left;
            page-break-after: avoid;
        }}

        h4 {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 10pt;
            font-weight: 700;
            color: #4a5568;
            margin: 14pt 0 6pt 0;
            text-align: left;
            page-break-after: avoid;
            font-style: italic;
        }}

        /* Title Page */
        .title-page {{
            text-align: center;
            margin-bottom: 32pt;
            page-break-after: avoid;
        }}

        .main-title {{
            font-family: 'Gulliver Elsevier Display', serif;
            font-size: 16pt;
            font-weight: 700;
            line-height: 1.4;
            color: #000000;
            margin-bottom: 20pt;
            letter-spacing: -0.02em;
            max-width: 80%;
            margin-left: auto;
            margin-right: auto;
        }}

        .subtitle {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 11pt;
            font-weight: 400;
            color: #4a5568;
            font-style: italic;
            margin-bottom: 32pt;
            line-height: 1.5;
        }}

        /* Abstract */
        .abstract {{
            background: #f8f9fa;
            border-left: 2pt solid #1a365d;
            padding: 16pt 20pt;
            margin: 20pt 0 28pt 0;
            font-size: 10pt;
            line-height: 1.5;
            page-break-inside: avoid;
        }}

        .abstract-title {{
            font-family: 'Gulliver Elsevier', serif;
            font-size: 9pt;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 12pt;
            text-transform: uppercase;
            letter-spacing: 1pt;
        }}

        .keywords {{
            margin-top: 12pt;
            font-size: 9pt;
            color: #666;
        }}

        .keywords strong {{
            font-weight: 700;
            color: #333;
        }}

        /* Content */
        p {{
            margin-bottom: 8pt;
            text-indent: 0;
            line-height: 1.4;
        }}

        .first-paragraph {{
            text-indent: 0;
            margin-bottom: 8pt;
        }}

        section p + p {{
            text-indent: 12pt;
            margin-bottom: 8pt;
        }}
        
        /* Remove extra spacing between paragraphs */
        p + p {{
            margin-top: 0pt;
        }}

        /* Lists */
        ul, ol {{
            margin: 10pt 0 12pt 20pt;
            padding: 0;
        }}

        li {{
            margin-bottom: 6pt;
            line-height: 1.5;
        }}

        /* Tables */
        .table-container {{
            margin: 16pt 0;
            page-break-inside: avoid;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
            line-height: 1.2;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 700;
            padding: 4pt 6pt;
            border: 0.5pt solid #bbb;
            text-align: left;
            vertical-align: top;
        }}

        td {{
            padding: 4pt 6pt;
            border: 0.5pt solid #ddd;
            vertical-align: top;
        }}

        /* Blockquotes */
        blockquote {{
            margin: 12pt 0;
            padding: 8pt 16pt;
            border-left: 2pt solid #ddd;
            font-style: italic;
            background: #fafafa;
            page-break-inside: avoid;
        }}

        blockquote p {{
            margin-bottom: 6pt;
        }}

        /* Emphasis */
        strong, b {{
            font-weight: 700;
        }}

        em, i {{
            font-style: italic;
        }}

        .statistic {{
            font-weight: 700;
            color: #d63384;
        }}

        /* Section Separators */
        .section-separator {{
            border: none;
            height: 0.5pt;
            background: #d0d0d0;
            margin: 28pt 0;
        }}

        /* Page Breaks */
        .page-break {{
            page-break-before: always;
        }}

        .avoid-break {{
            page-break-inside: avoid;
        }}

        /* Print Optimizations */
        @media print {{
            body {{
                font-size: 10.5pt;
                line-height: 1.5;
            }}
            
            .main-title {{
                font-size: 15pt;
            }}
            
            h1 {{ font-size: 13pt; }}
            h2 {{ font-size: 11.5pt; }}
            h3 {{ font-size: 10.5pt; }}
            h4 {{ font-size: 9.5pt; }}
            
            .abstract {{
                font-size: 9.5pt;
            }}
            
            table {{
                font-size: 8.5pt;
            }}
            
            p {{
                margin-bottom: 11pt;
            }}
            
            section p + p {{
                text-indent: 13pt;
            }}
        }}
    </style>
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
        
        {content}
    </article>
</body>
</html>'''
    
    return template

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert-markdown.py input.md output.html")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    # Read markdown
    markdown_content = input_file.read_text(encoding='utf-8')
    
    # Extract title
    title_match = re.search(r'^# (.+)$', markdown_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Academic Paper"
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content, title)
    
    # Write HTML
    output_file.write_text(html_content, encoding='utf-8')
    print(f"✅ Converted {input_file} → {output_file}")